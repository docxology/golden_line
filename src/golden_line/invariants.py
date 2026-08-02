"""Structural soundness checks over the aspiration registry.

These pure-compute checks validate the registry's declared vocabulary rather
than the truth of any aspiration. Each check returns a frozen
:class:`SoundnessResult`; the companion tests prove detection with planted-bad
registries. A passing battery is evidence of structural integrity only.
"""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass

from .models import Aspiration
from .registry import GOLDEN_ASPIRATIONS
from .serialization import canonical_registry, registry_digest


@dataclass(frozen=True)
class SoundnessResult:
    """One structural check outcome."""

    name: str
    passed: bool
    detail: str


def check_distinct_aspiration_ids(
    aspirations: tuple[Aspiration, ...],
) -> SoundnessResult:
    """Aspiration ids must be distinct; a duplicate makes findings ambiguous."""
    ids = [
        item.id
        for item in aspirations
        if isinstance(item, Aspiration) and isinstance(item.id, str)
    ]
    invalid = [
        index
        for index, item in enumerate(aspirations)
        if not isinstance(item, Aspiration)
    ]
    duplicates = sorted(
        identifier for identifier, count in Counter(ids).items() if count > 1
    )
    ok = not duplicates and not invalid
    if invalid:
        detail = f"non-Aspiration registry entries at indexes: {invalid}"
    else:
        detail = "ok" if ok else f"duplicate aspiration ids: {duplicates}"
    return SoundnessResult("distinct_aspiration_ids", ok, detail)


def check_fields_populated(aspirations: tuple[Aspiration, ...]) -> SoundnessResult:
    """id, title, thread, and horizon must all be non-blank text."""
    blank: list[str] = []
    for index, item in enumerate(aspirations):
        if not isinstance(item, Aspiration):
            blank.append(f"index {index}")
            continue
        fields = (item.id, item.title, item.thread, item.horizon)
        if not all(isinstance(field, str) and field.strip() for field in fields):
            blank.append(item.id if isinstance(item.id, str) else f"index {index}")
    ok = not blank
    return SoundnessResult(
        "fields_populated",
        ok,
        "ok" if ok else f"blank or invalid required fields on: {blank}",
    )


def check_reachable_statuses(aspirations: tuple[Aspiration, ...]) -> SoundnessResult:
    """Every aspiration needs at least one marker and one counter-signal."""
    unreachable: list[str] = []
    for index, item in enumerate(aspirations):
        if not isinstance(item, Aspiration):
            unreachable.append(f"index {index}")
        elif not item.markers or not item.counter_signals:
            unreachable.append(item.id)
    ok = not unreachable
    return SoundnessResult(
        "reachable_statuses",
        ok,
        "ok" if ok else f"aspirations with unreachable statuses: {unreachable}",
    )


def check_signal_text(aspirations: tuple[Aspiration, ...]) -> SoundnessResult:
    """Every marker and counter-signal must be an iterable of non-blank text."""
    bad: list[str] = []
    for index, item in enumerate(aspirations):
        if not isinstance(item, Aspiration):
            bad.append(f"index {index}: not an Aspiration")
            continue
        for field_name in ("markers", "counter_signals"):
            try:
                tokens = tuple(getattr(item, field_name))
            except TypeError:
                bad.append(f"{item.id}:{field_name} is not iterable")
                continue
            for token in tokens:
                if not isinstance(token, str) or not token.strip():
                    bad.append(f"{item.id}:{token!r}")
    ok = not bad
    return SoundnessResult(
        "signal_text", ok, "ok" if ok else f"blank or non-string signals: {bad}"
    )


def check_signal_uniqueness(aspirations: tuple[Aspiration, ...]) -> SoundnessResult:
    """Markers and counter-signals must not repeat within one declaration."""
    duplicates: list[str] = []
    for index, item in enumerate(aspirations):
        if not isinstance(item, Aspiration):
            duplicates.append(f"index {index}")
            continue
        for field_name in ("markers", "counter_signals"):
            try:
                tokens = tuple(getattr(item, field_name))
            except TypeError:
                duplicates.append(f"{item.id}:{field_name}")
                continue
            counts = Counter(token for token in tokens if isinstance(token, str))
            duplicates.extend(
                f"{item.id}:{field_name}:{token!r}"
                for token, count in counts.items()
                if count > 1
            )
    ok = not duplicates
    return SoundnessResult(
        "signal_uniqueness",
        ok,
        "ok" if ok else f"repeated signal declarations: {duplicates}",
    )


def check_signal_disjointness(aspirations: tuple[Aspiration, ...]) -> SoundnessResult:
    """Markers and counter-signals must not overlap within an aspiration."""
    tangled: list[str] = []
    for index, item in enumerate(aspirations):
        if not isinstance(item, Aspiration):
            tangled.append(f"index {index}")
            continue
        try:
            markers = tuple(item.markers)
            counters = tuple(item.counter_signals)
        except TypeError:
            tangled.append(item.id if isinstance(item.id, str) else f"index {index}")
            continue
        if any(not isinstance(token, str) for token in (*markers, *counters)):
            tangled.append(item.id if isinstance(item.id, str) else f"index {index}")
        elif set(markers) & set(counters):
            tangled.append(item.id)
    ok = not tangled
    return SoundnessResult(
        "signal_disjointness",
        ok,
        "ok"
        if ok
        else f"marker/counter-signal overlap or invalid tokens on: {tangled}",
    )


def check_digest_stability(aspirations: tuple[Aspiration, ...]) -> SoundnessResult:
    """The canonical form must serialize, and its digest must ignore order."""
    try:
        json.loads(canonical_registry(tuple(aspirations)))
        forward = registry_digest(tuple(aspirations))
        reverse = registry_digest(tuple(reversed(tuple(aspirations))))
    except (AttributeError, TypeError, ValueError) as exc:
        return SoundnessResult(
            "digest_stability", False, f"canonical form is unserializable: {exc}"
        )
    ok = forward == reverse
    return SoundnessResult(
        "digest_stability", ok, "ok" if ok else "digest depends on registry order"
    )


_CHECKS = (
    check_distinct_aspiration_ids,
    check_fields_populated,
    check_reachable_statuses,
    check_signal_text,
    check_signal_uniqueness,
    check_signal_disjointness,
    check_digest_stability,
)


def all_invariants(
    aspirations: tuple[Aspiration, ...] = GOLDEN_ASPIRATIONS,
) -> tuple[SoundnessResult, ...]:
    """Run every structural check over ``aspirations`` and return the battery."""
    return tuple(check(aspirations) for check in _CHECKS)


def registry_sound(aspirations: tuple[Aspiration, ...] = GOLDEN_ASPIRATIONS) -> bool:
    """True iff every structural check passes on ``aspirations``."""
    return all(result.passed for result in all_invariants(aspirations))
