"""Descriptive analysis helpers: inventory, bands, sweep, report overview."""

import ast
from datetime import date
from pathlib import Path

import pytest

from golden_line import analysis
from golden_line import (
    GOLDEN_ASPIRATIONS,
    HORIZON_BANDS,
    Aspiration,
    HorizonEntry,
    HorizonStatus,
    horizon_distribution,
    progress_report,
    report_overview,
    signal_inventory,
    temporal_currentness_sweep,
)

ATTENTION = GOLDEN_ASPIRATIONS[0]
REVIEW = "2026-07-18"


def _full_entry(aspiration, **kwargs) -> HorizonEntry:
    return HorizonEntry(aspiration.id, frozenset(aspiration.markers), **kwargs)


# --- signal_inventory -------------------------------------------------------


def test_inventory_totals_match_registry() -> None:
    inventory = signal_inventory()
    assert inventory.total_markers == sum(
        len(item.markers) for item in GOLDEN_ASPIRATIONS
    )
    assert inventory.total_counter_signals == sum(
        len(item.counter_signals) for item in GOLDEN_ASPIRATIONS
    )


def test_inventory_rows_preserve_registry_order_and_counts() -> None:
    inventory = signal_inventory()
    assert len(inventory.rows) == len(GOLDEN_ASPIRATIONS)
    for row, item in zip(inventory.rows, GOLDEN_ASPIRATIONS):
        assert row.aspiration_id == item.id
        assert row.horizon == item.horizon
        assert row.marker_count == len(item.markers)
        assert row.counter_signal_count == len(item.counter_signals)


def test_inventory_unique_counts_match_distinct_tokens() -> None:
    inventory = signal_inventory()
    markers = {token for item in GOLDEN_ASPIRATIONS for token in item.markers}
    counters = {token for item in GOLDEN_ASPIRATIONS for token in item.counter_signals}
    assert inventory.unique_markers == len(markers)
    assert inventory.unique_counter_signals == len(counters)


def test_inventory_detects_shared_tokens_in_custom_registry() -> None:
    twin_a = Aspiration("a", "A", "t", "next decision", ("same token",), ("c1",))
    twin_b = Aspiration("b", "B", "t", "next decision", ("same token",), ("c2",))
    inventory = signal_inventory((twin_a, twin_b))
    assert inventory.total_markers == 2
    assert inventory.unique_markers == 1
    assert inventory.unique_counter_signals == 2


def test_inventory_of_empty_registry_is_all_zero() -> None:
    inventory = signal_inventory(())
    assert inventory.rows == ()
    assert inventory.total_markers == 0
    assert inventory.unique_counter_signals == 0


# --- horizon_distribution ---------------------------------------------------


def test_band_map_classifies_every_registry_horizon() -> None:
    classified = {h for _, horizons in HORIZON_BANDS for h in horizons}
    assert {item.horizon for item in GOLDEN_ASPIRATIONS} <= classified


def test_distribution_partitions_the_registry() -> None:
    bands = horizon_distribution()
    placed = [aid for band in bands for aid in band.aspiration_ids]
    assert sorted(placed) == sorted(item.id for item in GOLDEN_ASPIRATIONS)
    assert len(placed) == len(set(placed))


def test_distribution_band_order_and_shape_are_stable() -> None:
    bands = horizon_distribution()
    assert tuple(band.band for band in bands) == tuple(
        name for name, _ in HORIZON_BANDS
    )
    for band, (_, horizons) in zip(bands, HORIZON_BANDS):
        assert band.horizons == horizons


def test_distribution_members_carry_matching_horizons() -> None:
    for band in horizon_distribution():
        for aspiration_id in band.aspiration_ids:
            item = next(a for a in GOLDEN_ASPIRATIONS if a.id == aspiration_id)
            assert item.horizon in band.horizons


def test_distribution_keeps_empty_bands_for_subsets() -> None:
    bands = horizon_distribution((ATTENTION,))
    assert len(bands) == len(HORIZON_BANDS)
    assert bands[0].aspiration_ids == (ATTENTION.id,)
    assert all(band.aspiration_ids == () for band in bands[1:])


def test_unclassified_horizon_raises() -> None:
    stranger = Aspiration("odd", "Odd", "t", "someday maybe", ("m",), ("c",))
    with pytest.raises(ValueError, match="someday maybe"):
        horizon_distribution((stranger,))


# --- temporal_currentness_sweep ---------------------------------------------


def test_sweep_flips_toward_to_inquiry_at_exclusive_boundary() -> None:
    points = temporal_currentness_sweep(
        ATTENTION.id, (0, 89, 90, 91, 120), as_of=REVIEW, stale_after_days=90
    )
    statuses = {p.age_days: p.status for p in points}
    assert statuses[0] is HorizonStatus.TOWARD
    assert statuses[89] is HorizonStatus.TOWARD
    assert statuses[90] is HorizonStatus.TOWARD
    assert statuses[91] is HorizonStatus.INQUIRY
    assert statuses[120] is HorizonStatus.INQUIRY


def test_sweep_marks_stale_points_beyond_threshold() -> None:
    points = temporal_currentness_sweep(
        ATTENTION.id, (90, 91), as_of=REVIEW, stale_after_days=90
    )
    assert points[0].stale is False
    assert points[1].stale is True
    assert all(p.date_issue is False for p in points)


def test_sweep_future_dated_age_reverts_to_inquiry() -> None:
    (point,) = temporal_currentness_sweep(
        ATTENTION.id, (-7,), as_of=REVIEW, stale_after_days=90
    )
    assert point.age_days == -7
    assert point.status is HorizonStatus.INQUIRY
    assert point.stale is True


def test_sweep_never_produces_drifting_or_not_observed() -> None:
    points = temporal_currentness_sweep(
        ATTENTION.id, range(-10, 200, 5), as_of=REVIEW, stale_after_days=90
    )
    assert {p.status for p in points} <= {HorizonStatus.TOWARD, HorizonStatus.INQUIRY}


def test_sweep_observed_on_dates_are_derived_from_as_of() -> None:
    points = temporal_currentness_sweep(
        ATTENTION.id, (0, 1, 30), as_of=REVIEW, stale_after_days=90
    )
    assert points[0].observed_on == REVIEW
    assert points[1].observed_on == "2026-07-17"
    assert points[2].observed_on == "2026-06-18"


def test_sweep_module_constructs_no_status_of_its_own() -> None:
    """Proposition 8's delegation clause, checked structurally rather than by replay.

    Comparing a sweep point against a second ``progress_report`` call compares
    the same code path with itself: the sweep *calls* the evaluator, so the
    comparison is true by construction and cannot fail. The falsifiable form of
    the claim is architectural — no ``HorizonStatus`` is ever constructed in
    ``analysis.py`` — so that is what is asserted here, over the module's real
    parse tree rather than a substring search.
    """
    source = Path(analysis.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    constructions = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id == "HorizonStatus"
    ]
    assert constructions == [], [node.attr for node in constructions]
    assert "HorizonStatus(" not in source

    # And the positive control: the check can fail. A module that does build a
    # status is rejected by the same predicate.
    planted = ast.parse("from x import HorizonStatus\ns = HorizonStatus.TOWARD\n")
    planted_hits = [
        node
        for node in ast.walk(planted)
        if isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id == "HorizonStatus"
    ]
    assert [node.attr for node in planted_hits] == ["TOWARD"]


def test_sweep_point_fields_come_from_the_finding_it_replays() -> None:
    """Every SweepPoint field is copied from the evaluator's own finding."""
    for age in (10, 91):
        (point,) = temporal_currentness_sweep(
            ATTENTION.id, (age,), as_of=REVIEW, stale_after_days=90
        )
        direct = progress_report(
            [_full_entry(ATTENTION, observed_on=point.observed_on)],
            (ATTENTION,),
            as_of=REVIEW,
            stale_after_days=90,
        ).findings[0]
        assert point.status is direct.status
        assert point.stale == direct.stale
        assert point.date_issue == direct.date_issue
        assert point.observed_on == direct.observed_on


def test_sweep_accepts_date_object_and_empty_ages() -> None:
    assert (
        temporal_currentness_sweep(
            ATTENTION.id, (), as_of=date(2026, 7, 18), stale_after_days=90
        )
        == ()
    )


def test_sweep_unknown_aspiration_raises() -> None:
    with pytest.raises(ValueError, match="unknown aspiration"):
        temporal_currentness_sweep(
            "not-a-real-id", (0,), as_of=REVIEW, stale_after_days=90
        )


def test_sweep_invalid_as_of_type_raises() -> None:
    with pytest.raises(TypeError):
        temporal_currentness_sweep(
            ATTENTION.id,
            (0,),
            as_of=7,
            stale_after_days=90,  # type: ignore[arg-type]
        )


def test_sweep_propagates_invalid_threshold() -> None:
    with pytest.raises(ValueError):
        temporal_currentness_sweep(
            ATTENTION.id, (0,), as_of=REVIEW, stale_after_days=-1
        )


# --- report_overview --------------------------------------------------------


def _mixed_report():
    repair = GOLDEN_ASPIRATIONS[2]
    flourishing = GOLDEN_ASPIRATIONS[3]
    entries = [
        _full_entry(ATTENTION, observed_on=REVIEW),
        HorizonEntry(
            repair.id,
            counter_signals=frozenset(repair.counter_signals),
            observed_on=REVIEW,
        ),
        _full_entry(flourishing, observed_on="2020-01-01"),
        HorizonEntry("unknown-id"),
        HorizonEntry(
            GOLDEN_ASPIRATIONS[1].id,
            observed_markers=frozenset({"undeclared token"}),
            observed_on=REVIEW,
        ),
    ]
    return progress_report(entries, as_of=REVIEW, stale_after_days=90)


def test_overview_groups_every_aspiration_exactly_once() -> None:
    overview = report_overview(_mixed_report())
    placed = [aid for ids in overview.by_status.values() for aid in ids]
    assert sorted(placed) == sorted(item.id for item in GOLDEN_ASPIRATIONS)


def test_overview_by_status_has_all_four_keys_in_enum_order() -> None:
    overview = report_overview(_mixed_report())
    assert list(overview.by_status) == [status.value for status in HorizonStatus]


def test_overview_statuses_match_expected_groupings() -> None:
    overview = report_overview(_mixed_report())
    assert ATTENTION.id in overview.by_status["TOWARD"]
    assert GOLDEN_ASPIRATIONS[2].id in overview.by_status["DRIFTING"]
    assert GOLDEN_ASPIRATIONS[3].id in overview.by_status["INQUIRY"]
    assert GOLDEN_ASPIRATIONS[1].id in overview.by_status["INQUIRY"]


def test_overview_totals_count_flags_and_notes() -> None:
    overview = report_overview(_mixed_report())
    assert overview.ignored_marker_total == 1
    assert overview.ignored_counter_signal_total == 0
    assert overview.stale_count == 1
    assert overview.date_issue_count == 0
    assert overview.intake_note_count == 1


def test_overview_of_empty_report_is_all_not_observed() -> None:
    overview = report_overview(progress_report([]))
    assert overview.by_status["NOT_OBSERVED"] == tuple(
        item.id for item in GOLDEN_ASPIRATIONS
    )
    assert overview.ignored_marker_total == 0
    assert overview.intake_note_count == 0
