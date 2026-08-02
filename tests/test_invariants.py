"""Invariant battery: pass on the real registry, fail on planted-bad ones.

Every check gets a proof-of-detection test — a deliberately corrupted
registry built with ``dataclasses.replace`` that the check must reject. A
green check that never saw a bad input would not be evidence of anything.
"""

import dataclasses

from golden_line import GOLDEN_ASPIRATIONS, all_invariants, registry_sound
from golden_line.invariants import (
    check_digest_stability,
    check_distinct_aspiration_ids,
    check_fields_populated,
    check_reachable_statuses,
    check_signal_disjointness,
    check_signal_text,
    check_signal_uniqueness,
)

REAL = GOLDEN_ASPIRATIONS


def test_battery_passes_on_real_registry() -> None:
    results = all_invariants(REAL)
    assert len(results) == 7
    assert all(result.passed for result in results)
    assert all(result.detail == "ok" for result in results)
    names = [result.name for result in results]
    assert len(names) == len(set(names))
    assert registry_sound(REAL)


def test_battery_defaults_to_real_registry() -> None:
    """The default argument *is* the shipped registry object, not a copy of it.

    Asserting ``all_invariants() == all_invariants(REAL)`` compared a call with
    its own default against itself and could never fail. Binding the default to
    the registry object carries the information that was intended.
    """
    assert all_invariants.__defaults__ == (GOLDEN_ASPIRATIONS,)
    assert registry_sound.__defaults__ == (GOLDEN_ASPIRATIONS,)
    assert all_invariants.__defaults__[0] is GOLDEN_ASPIRATIONS
    assert registry_sound()


def test_distinct_ids_detects_duplicate() -> None:
    assert check_distinct_aspiration_ids(REAL).passed
    planted = REAL + (dataclasses.replace(REAL[0], title="an impostor"),)
    result = check_distinct_aspiration_ids(planted)
    assert not result.passed
    assert REAL[0].id in result.detail


def test_fields_populated_detects_blank() -> None:
    assert check_fields_populated(REAL).passed
    planted = REAL[:-1] + (dataclasses.replace(REAL[-1], thread="   "),)
    result = check_fields_populated(planted)
    assert not result.passed
    assert REAL[-1].id in result.detail


def test_reachable_statuses_detects_markerless() -> None:
    assert check_reachable_statuses(REAL).passed
    planted = REAL[:-1] + (dataclasses.replace(REAL[-1], markers=()),)
    result = check_reachable_statuses(planted)
    assert not result.passed
    assert REAL[-1].id in result.detail


def test_reachable_statuses_detects_counter_signalless() -> None:
    planted = REAL[:-1] + (dataclasses.replace(REAL[-1], counter_signals=()),)
    assert not check_reachable_statuses(planted).passed


def test_signal_disjointness_detects_overlap() -> None:
    assert check_signal_disjointness(REAL).passed
    tangled = dataclasses.replace(REAL[0], counter_signals=(REAL[0].markers[0],))
    planted = (tangled,) + REAL[1:]
    result = check_signal_disjointness(planted)
    assert not result.passed
    assert REAL[0].id in result.detail


def test_signal_text_detects_blank_token() -> None:
    assert check_signal_text(REAL).passed
    planted = REAL[:-1] + (dataclasses.replace(REAL[-1], markers=("", "still here")),)
    assert not check_signal_text(planted).passed


def test_signal_text_detects_non_string_token() -> None:
    planted = REAL[:-1] + (dataclasses.replace(REAL[-1], counter_signals=(3,)),)
    result = check_signal_text(planted)
    assert not result.passed
    assert "3" in result.detail


def test_signal_uniqueness_detects_repeated_token() -> None:
    assert check_signal_uniqueness(REAL).passed
    planted = REAL[:-1] + (dataclasses.replace(REAL[-1], markers=("same", "same")),)
    result = check_signal_uniqueness(planted)
    assert not result.passed
    assert "same" in result.detail


def test_signal_disjointness_detects_non_string_token() -> None:
    planted = REAL[:-1] + (dataclasses.replace(REAL[-1], markers=(3,)),)
    result = check_signal_disjointness(planted)
    assert not result.passed
    assert REAL[-1].id in result.detail


def test_every_check_rejects_a_planted_non_aspiration_entry() -> None:
    """A stray non-Aspiration entry is reported by position, never raised on.

    The registry is typed, but it is still data: a tuple assembled by hand or
    rebuilt from elsewhere can carry an object that is not an ``Aspiration``.
    Every check must fail closed and name the offending index.
    """
    index = len(REAL)
    planted = REAL + (object(),)

    distinct = check_distinct_aspiration_ids(planted)
    assert not distinct.passed
    assert f"indexes: [{index}]" in distinct.detail

    for check in (
        check_fields_populated,
        check_reachable_statuses,
        check_signal_text,
        check_signal_uniqueness,
        check_signal_disjointness,
    ):
        result = check(planted)
        assert not result.passed, f"{check.__name__} accepted a non-Aspiration entry"
        assert f"index {index}" in result.detail, check.__name__

    assert not registry_sound(planted)


def test_checks_reject_malformed_registry_fields_without_raising() -> None:
    malformed = REAL[:-1] + (dataclasses.replace(REAL[-1], title=3, markers=None),)
    assert not check_fields_populated(malformed).passed
    assert not check_signal_text(malformed).passed
    assert not check_signal_disjointness(malformed).passed
    assert not check_signal_uniqueness(malformed).passed


def test_digest_stability_detects_missing_fields_without_raising() -> None:
    malformed = REAL[:-1] + (object(),)
    result = check_digest_stability(malformed)
    assert not result.passed
    assert "unserializable" in result.detail


def test_digest_stability_detects_unserializable() -> None:
    assert check_digest_stability(REAL).passed
    planted = REAL[:-1] + (dataclasses.replace(REAL[-1], markers=(object(),)),)
    result = check_digest_stability(planted)
    assert not result.passed
    assert "unserializable" in result.detail


def test_digest_stability_detects_order_dependence() -> None:
    # Two entries sharing an id but differing in content make the sorted
    # canonical order unstable, so the digest depends on input order.
    twin = dataclasses.replace(REAL[0], title="same id, other title")
    planted = (REAL[0], twin) + REAL[1:]
    result = check_digest_stability(planted)
    assert not result.passed
    assert "order" in result.detail


def test_registry_sound_false_on_any_planted_bad() -> None:
    planted = REAL[:-1] + (dataclasses.replace(REAL[-1], markers=()),)
    assert not registry_sound(planted)
