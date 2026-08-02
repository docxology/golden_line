"""Describe movement toward aspirations without producing compliance verdicts.

The report is deliberately staged. Incoming entries are screened first, then
each admitted entry is normalized and read against its aspiration's declared
markers and counter-signals. Optional temporal review is conservative: a
missing or malformed date cannot support a currentness claim, and a
counter-signal is never erased by age. Every finding carries structured
derivation fields and a human-readable reasons trail.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Any

from .models import (
    Aspiration,
    HorizonEntry,
    HorizonFinding,
    HorizonReport,
    HorizonStatus,
)
from .registry import GOLDEN_ASPIRATIONS
from .serialization import registry_digest
from .version import REGISTRY_VERSION


#: The stages :func:`progress_report` runs, in order. Named here so the count
#: quoted in the manuscript, the evidence ledger, and the pipeline figure all
#: read one source instead of three hand-kept copies.
EVALUATOR_STAGES: tuple[str, ...] = ("intake screening", "matching", "decision")


class IntakeSetAsideReason(str, Enum):
    """Why an entry was set aside during intake screening."""

    DUPLICATE = "duplicate"
    MALFORMED = "malformed"
    UNKNOWN_ID = "unknown_id"


@dataclass(frozen=True)
class IntakeClassification:
    """The intake outcome for one submitted record."""

    entry: HorizonEntry | None
    admitted: bool
    set_aside_reason: IntakeSetAsideReason | None = None
    note: str | None = None


def _review_date(as_of: str | date | None) -> date:
    """Resolve the review date; a string must be a valid ISO date."""
    if as_of is None:
        return date.today()
    if isinstance(as_of, str):
        return date.fromisoformat(as_of)
    if isinstance(as_of, date):
        return as_of
    raise TypeError("as_of must be an ISO date string, a date, or None")


def _validate_staleness_threshold(stale_after_days: int | None) -> None:
    """Reject an invalid control parameter before it can change semantics."""
    if stale_after_days is not None and (
        isinstance(stale_after_days, bool)
        or not isinstance(stale_after_days, int)
        or stale_after_days < 0
    ):
        raise ValueError("stale_after_days must be a non-negative integer or None")


def _normalise_entry(entry: Any, index: int) -> tuple[HorizonEntry | None, str | None]:
    """Validate and normalize one incoming record without trusting its fields.

    The public type is intentionally small, but callers often construct records
    from JSON where arrays are natural. Arrays of strings are accepted and
    normalized to frozensets; malformed records are set aside rather than
    allowed to create a partial or crashing finding.
    """
    if not isinstance(entry, HorizonEntry):
        return None, f"entry #{index} was set aside: expected a HorizonEntry record"
    if not isinstance(entry.aspiration_id, str) or not entry.aspiration_id.strip():
        return (
            None,
            f"entry #{index} was set aside: aspiration_id must be non-blank text",
        )
    if not isinstance(entry.note, str):
        return (
            None,
            f"entry #{index} for '{entry.aspiration_id}' was set aside: note must be text",
        )
    if not isinstance(entry.observed_on, str):
        return None, (
            f"entry #{index} for '{entry.aspiration_id}' was set aside: observed_on must be text"
        )

    normalized: dict[str, frozenset[str]] = {}
    for field_name in ("observed_markers", "counter_signals"):
        value = getattr(entry, field_name)
        if isinstance(value, (str, bytes)) or value is None:
            return None, (
                f"entry #{index} for '{entry.aspiration_id}' was set aside: "
                f"{field_name} must be an iterable of text tokens"
            )
        try:
            tokens = tuple(value)
            if not all(isinstance(token, str) for token in tokens):
                raise TypeError
            normalized[field_name] = frozenset(tokens)
        except (TypeError, ValueError):
            return None, (
                f"entry #{index} for '{entry.aspiration_id}' was set aside: "
                f"{field_name} must contain only text tokens"
            )
    return (
        HorizonEntry(
            aspiration_id=entry.aspiration_id,
            observed_markers=normalized["observed_markers"],
            counter_signals=normalized["counter_signals"],
            note=entry.note,
            observed_on=entry.observed_on,
        ),
        None,
    )


def _screen_entries(
    entries: Iterable[HorizonEntry],
    known_ids: frozenset[str],
) -> tuple[dict[str, HorizonEntry], tuple[str, ...]]:
    """Accept one normalized entry per known aspiration; note everything else."""
    accepted: dict[str, HorizonEntry] = {}
    notes: list[str] = []
    for classification in _classify_intake_entries(entries, known_ids):
        if classification.note is not None:
            notes.append(classification.note)
        if not classification.admitted:
            continue
        if classification.entry is None:
            raise RuntimeError(
                "admitted intake classification is missing its normalized HorizonEntry"
            )
        accepted[classification.entry.aspiration_id] = classification.entry
    return accepted, tuple(notes)


def _classify_intake_entries(
    entries: Iterable[HorizonEntry],
    known_ids: frozenset[str],
) -> tuple[IntakeClassification, ...]:
    """Classify every submitted record under the first-wins intake rule."""
    seen: set[str] = set()
    classifications: list[IntakeClassification] = []
    for index, raw_entry in enumerate(entries, start=1):
        entry, malformed_note = _normalise_entry(raw_entry, index)
        if malformed_note is not None:
            classifications.append(
                IntakeClassification(
                    entry=None,
                    admitted=False,
                    set_aside_reason=IntakeSetAsideReason.MALFORMED,
                    note=malformed_note,
                )
            )
            continue
        if entry is None:
            raise RuntimeError(
                f"entry #{index} produced no HorizonEntry and no intake note"
            )
        if entry.aspiration_id not in known_ids:
            classifications.append(
                IntakeClassification(
                    entry=entry,
                    admitted=False,
                    set_aside_reason=IntakeSetAsideReason.UNKNOWN_ID,
                    note=(
                        f"entry for unknown aspiration '{entry.aspiration_id}' was set aside"
                    ),
                )
            )
            continue
        if entry.aspiration_id in seen:
            classifications.append(
                IntakeClassification(
                    entry=entry,
                    admitted=False,
                    set_aside_reason=IntakeSetAsideReason.DUPLICATE,
                    note=(
                        f"duplicate entry for '{entry.aspiration_id}' was set aside; "
                        "the first entry stands"
                    ),
                )
            )
            continue
        seen.add(entry.aspiration_id)
        classifications.append(IntakeClassification(entry=entry, admitted=True))
    return tuple(classifications)


def classify_intake_entries(
    entries: Iterable[HorizonEntry],
    aspirations: Iterable[Aspiration] = GOLDEN_ASPIRATIONS,
) -> tuple[IntakeClassification, ...]:
    """Replay the public intake rule and return one classification per record."""
    aspiration_list = tuple(aspirations)
    return _classify_intake_entries(
        entries, frozenset(item.id for item in aspiration_list)
    )


def _staleness(
    entry: HorizonEntry,
    review_date: date,
    stale_after_days: int | None,
) -> tuple[bool, tuple[str, ...], bool]:
    """Return ``(is_stale, reasons, date_issue)``.

    A missing or unreadable date is not fatal, but it cannot support a
    currentness claim when temporal review is enabled. That distinction
    prevents incomplete temporal metadata from producing a false ``TOWARD``
    result.
    """
    if stale_after_days is None:
        return False, (), False
    if not entry.observed_on:
        return (
            False,
            ("observation has no date; currentness could not be established",),
            True,
        )
    try:
        observed_on = date.fromisoformat(entry.observed_on)
    except ValueError:
        return (
            False,
            (
                f"observation date '{entry.observed_on}' is not an ISO date; currentness could not be established",
            ),
            True,
        )
    if observed_on > review_date:
        return (
            True,
            (
                f"observation is dated {entry.observed_on}, after the review date; it must be re-observed",
            ),
            False,
        )
    if (review_date - observed_on).days > stale_after_days:
        return (
            True,
            (
                f"observation from {entry.observed_on} is older than {stale_after_days} days; "
                "movement must be re-observed",
            ),
            False,
        )
    return False, (), False


def _finding(
    aspiration: Aspiration,
    entry: HorizonEntry | None,
    review_date: date,
    stale_after_days: int | None,
) -> HorizonFinding:
    if entry is None:
        return HorizonFinding(
            aspiration.id,
            HorizonStatus.NOT_OBSERVED,
            ("no admitted horizon entry was available",),
        )

    reasons: list[str] = []
    declared_markers = set(aspiration.markers)
    declared_counters = set(aspiration.counter_signals)
    ignored_markers = tuple(sorted(entry.observed_markers - declared_markers))
    ignored_counters = tuple(sorted(entry.counter_signals - declared_counters))
    if ignored_markers:
        reasons.append("undeclared markers were ignored: " + ", ".join(ignored_markers))
    if ignored_counters:
        reasons.append(
            "undeclared counter-signals were ignored: " + ", ".join(ignored_counters)
        )

    stale, stale_reasons, date_issue = _staleness(entry, review_date, stale_after_days)
    reasons.extend(stale_reasons)
    observed = tuple(sorted(entry.observed_markers & declared_markers))
    unmet = tuple(sorted(declared_markers - entry.observed_markers))
    countered = tuple(sorted(entry.counter_signals & declared_counters))

    common = {
        "observed": observed,
        "unmet": unmet,
        "countered": countered,
        "ignored_markers": ignored_markers,
        "ignored_counter_signals": ignored_counters,
        "note": entry.note,
        "observed_on": entry.observed_on,
        "stale": stale,
        "date_issue": date_issue,
    }
    if countered:
        # A recorded counter-signal stays worth discussing even when the
        # observation is stale; staleness never erases drift.
        reasons.append(
            "a declared counter-signal was recorded: " + ", ".join(countered)
        )
        return HorizonFinding(
            aspiration.id, HorizonStatus.DRIFTING, tuple(reasons), **common
        )
    if not observed:
        reasons.append("the aspiration is named but no declared marker is observed")
        return HorizonFinding(
            aspiration.id, HorizonStatus.INQUIRY, tuple(reasons), **common
        )
    if unmet:
        reasons.append(
            "markers observed ("
            + ", ".join(observed)
            + ") while others remain unmet ("
            + ", ".join(unmet)
            + "); the direction remains open"
        )
        return HorizonFinding(
            aspiration.id, HorizonStatus.INQUIRY, tuple(reasons), **common
        )
    if stale or date_issue:
        if date_issue:
            reasons.append(
                "the positive observation is not currentness-auditable; the direction remains open"
            )
        else:
            reasons.append(
                "all declared markers were observed, but the observation is stale; "
                "the direction reverts to inquiry"
            )
        return HorizonFinding(
            aspiration.id, HorizonStatus.INQUIRY, tuple(reasons), **common
        )

    reasons.append("all declared markers are observed: " + ", ".join(observed))
    return HorizonFinding(aspiration.id, HorizonStatus.TOWARD, tuple(reasons), **common)


def progress_report(
    entries: Iterable[HorizonEntry],
    aspirations: Iterable[Aspiration] = GOLDEN_ASPIRATIONS,
    *,
    as_of: str | date | None = None,
    stale_after_days: int | None = None,
) -> HorizonReport:
    """Return a directional report; no status is a moral score or certification.

    ``progress_report(entries)`` remains the compact call form. The optional
    staleness parameters add temporal review, while the returned report always
    records registry and review provenance for reproducible comparison.
    """
    aspiration_list = tuple(aspirations)
    _validate_staleness_threshold(stale_after_days)
    review_date = _review_date(as_of)
    accepted, notes = _screen_entries(
        entries, frozenset(item.id for item in aspiration_list)
    )
    findings = tuple(
        _finding(item, accepted.get(item.id), review_date, stale_after_days)
        for item in aspiration_list
    )
    return HorizonReport(
        findings,
        notes,
        REGISTRY_VERSION,
        registry_digest(aspiration_list),
        review_date.isoformat(),
        stale_after_days,
    )
