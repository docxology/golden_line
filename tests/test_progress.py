"""Evaluator semantics: screening, staleness, reasons trails, summaries."""

from datetime import date, timedelta

import pytest

from golden_line import (
    GOLDEN_ASPIRATIONS,
    HorizonEntry,
    HorizonStatus,
    IntakeSetAsideReason,
    classify_intake_entries,
    progress_report,
)

ATTENTION = GOLDEN_ASPIRATIONS[0]


def _full_entry(aspiration, **kwargs) -> HorizonEntry:
    return HorizonEntry(aspiration.id, frozenset(aspiration.markers), **kwargs)


def test_unknown_aspiration_id_is_noted_not_fatal() -> None:
    report = progress_report([HorizonEntry("not-a-real-id'); DROP TABLE--")])
    assert any("unknown aspiration" in note for note in report.intake_notes)
    assert all(
        finding.status is HorizonStatus.NOT_OBSERVED for finding in report.findings
    )


def test_duplicate_entries_first_wins_and_is_noted() -> None:
    first = _full_entry(ATTENTION)
    second = HorizonEntry(ATTENTION.id)
    report = progress_report([first, second])
    assert report.findings[0].status is HorizonStatus.TOWARD
    assert any("duplicate entry" in note for note in report.intake_notes)


def test_undeclared_markers_are_ignored_with_reason() -> None:
    entry = HorizonEntry(ATTENTION.id, frozenset({"fabricated marker"}))
    finding = progress_report([entry]).findings[0]
    assert finding.status is HorizonStatus.INQUIRY
    assert any(
        "undeclared markers were ignored" in reason for reason in finding.reasons
    )


def test_undeclared_counter_signals_are_ignored_with_reason() -> None:
    entry = _full_entry(ATTENTION, counter_signals=frozenset({"fabricated counter"}))
    finding = progress_report([entry]).findings[0]
    assert finding.status is HorizonStatus.TOWARD
    assert any(
        "undeclared counter-signals were ignored" in reason
        for reason in finding.reasons
    )


def test_stale_observation_reverts_toward_to_inquiry() -> None:
    entry = _full_entry(ATTENTION, observed_on="2026-01-01")
    finding = progress_report(
        [entry], as_of="2026-07-17", stale_after_days=90
    ).findings[0]
    assert finding.status is HorizonStatus.INQUIRY
    assert any("older than 90 days" in reason for reason in finding.reasons)


def test_fresh_observation_stays_toward() -> None:
    entry = _full_entry(ATTENTION, observed_on="2026-07-10")
    finding = progress_report(
        [entry], as_of="2026-07-17", stale_after_days=90
    ).findings[0]
    assert finding.status is HorizonStatus.TOWARD


def test_future_dated_observation_is_treated_as_stale() -> None:
    entry = _full_entry(ATTENTION, observed_on="2027-01-01")
    finding = progress_report(
        [entry], as_of="2026-07-17", stale_after_days=90
    ).findings[0]
    assert finding.status is HorizonStatus.INQUIRY
    assert any("after the review date" in reason for reason in finding.reasons)


def test_malformed_observation_date_is_noted_not_fatal() -> None:
    entry = _full_entry(ATTENTION, observed_on="not-a-date")
    finding = progress_report(
        [entry], as_of="2026-07-17", stale_after_days=90
    ).findings[0]
    assert finding.status is HorizonStatus.INQUIRY
    assert finding.date_issue
    assert any("not an ISO date" in reason for reason in finding.reasons)


def test_malformed_entry_is_set_aside_and_reported() -> None:
    report = progress_report([HorizonEntry(ATTENTION.id, observed_markers=None)])
    assert report.findings[0].status is HorizonStatus.NOT_OBSERVED
    assert any("observed_markers" in note for note in report.intake_notes)


def test_json_like_token_lists_are_normalized() -> None:
    entry = HorizonEntry(ATTENTION.id, observed_markers=list(ATTENTION.markers))
    finding = progress_report([entry]).findings[0]
    assert finding.status is HorizonStatus.TOWARD


def test_non_entry_is_set_aside_and_reported() -> None:
    report = progress_report([{"aspiration_id": ATTENTION.id}])
    assert report.findings[0].status is HorizonStatus.NOT_OBSERVED
    assert any("expected a HorizonEntry" in note for note in report.intake_notes)


def test_blank_or_non_text_aspiration_id_is_set_aside() -> None:
    """An unusable id cannot address an aspiration, so intake stops there.

    ``HorizonEntry`` is frozen but not validating: records rebuilt from JSON
    can carry a blank or non-text id. Screening must set them aside rather
    than let them reach the matcher.
    """
    report = progress_report([HorizonEntry("   "), HorizonEntry(7)])
    assert len(report.intake_notes) == 2
    assert all(
        "aspiration_id must be non-blank text" in note for note in report.intake_notes
    )
    assert all(
        finding.status is HorizonStatus.NOT_OBSERVED for finding in report.findings
    )


def test_non_text_note_is_set_aside() -> None:
    classification = classify_intake_entries([HorizonEntry(ATTENTION.id, note=3)])[0]
    assert not classification.admitted
    assert classification.set_aside_reason is IntakeSetAsideReason.MALFORMED
    assert classification.note is not None
    assert "note must be text" in classification.note


def test_non_text_observed_on_is_set_aside() -> None:
    report = progress_report([HorizonEntry(ATTENTION.id, observed_on=20260717)])
    assert any("observed_on must be text" in note for note in report.intake_notes)
    assert report.findings[0].status is HorizonStatus.NOT_OBSERVED


def test_non_text_token_in_a_marker_collection_is_set_aside() -> None:
    report = progress_report(
        [HorizonEntry(ATTENTION.id, observed_markers=frozenset({3}))]
    )
    assert any(
        "observed_markers must contain only text tokens" in note
        for note in report.intake_notes
    )
    assert report.findings[0].status is HorizonStatus.NOT_OBSERVED


def test_non_iterable_counter_signals_is_set_aside() -> None:
    report = progress_report([HorizonEntry(ATTENTION.id, counter_signals=7)])
    assert any(
        "counter_signals must contain only text tokens" in note
        for note in report.intake_notes
    )
    assert report.findings[0].status is HorizonStatus.NOT_OBSERVED


def test_public_intake_classification_replays_first_wins_screening() -> None:
    duplicate = HorizonEntry(ATTENTION.id)
    classifications = classify_intake_entries(
        [HorizonEntry("not-a-real-id"), _full_entry(ATTENTION), duplicate]
    )
    assert [item.admitted for item in classifications] == [False, True, False]
    assert [item.set_aside_reason for item in classifications] == [
        IntakeSetAsideReason.UNKNOWN_ID,
        None,
        IntakeSetAsideReason.DUPLICATE,
    ]
    assert (
        classifications[0].note
        == "entry for unknown aspiration 'not-a-real-id' was set aside"
    )
    assert (
        classifications[2].note
        == f"duplicate entry for '{ATTENTION.id}' was set aside; the first entry stands"
    )


def test_public_intake_classification_marks_malformed_records() -> None:
    classification = classify_intake_entries(
        [HorizonEntry(ATTENTION.id, observed_markers=None)]
    )[0]
    assert not classification.admitted
    assert classification.entry is None
    assert classification.set_aside_reason is IntakeSetAsideReason.MALFORMED
    assert classification.note is not None
    assert "observed_markers" in classification.note


def test_staleness_disabled_by_default() -> None:
    entry = _full_entry(ATTENTION, observed_on="2000-01-01")
    finding = progress_report([entry], as_of="2026-07-17").findings[0]
    assert finding.status is HorizonStatus.TOWARD


def test_undated_entry_cannot_certify_currentness() -> None:
    entry = _full_entry(ATTENTION)
    finding = progress_report([entry], as_of="2026-07-17", stale_after_days=1).findings[
        0
    ]
    assert finding.status is HorizonStatus.INQUIRY
    assert finding.date_issue
    assert any("no date" in reason for reason in finding.reasons)


def test_drifting_survives_staleness() -> None:
    entry = HorizonEntry(
        ATTENTION.id,
        counter_signals=frozenset(ATTENTION.counter_signals),
        observed_on="2020-01-01",
    )
    finding = progress_report(
        [entry], as_of="2026-07-17", stale_after_days=30
    ).findings[0]
    assert finding.status is HorizonStatus.DRIFTING


def test_as_of_accepts_date_object() -> None:
    entry = _full_entry(ATTENTION, observed_on="2026-01-01")
    report = progress_report([entry], as_of=date(2026, 7, 17), stale_after_days=30)
    assert report.findings[0].status is HorizonStatus.INQUIRY


def test_as_of_defaults_to_today() -> None:
    report = progress_report([_full_entry(ATTENTION)])
    assert report.findings[0].status is HorizonStatus.TOWARD


def test_invalid_as_of_string_raises() -> None:
    with pytest.raises(ValueError):
        progress_report([], as_of="never")


def test_invalid_as_of_type_raises() -> None:
    with pytest.raises(TypeError):
        progress_report([], as_of=3)  # type: ignore[arg-type]


def test_negative_staleness_threshold_raises() -> None:
    with pytest.raises(ValueError):
        progress_report([], stale_after_days=-1)


def test_finding_preserves_note_and_structured_matching_fields() -> None:
    entry = HorizonEntry(
        ATTENTION.id,
        observed_markers=frozenset({ATTENTION.markers[0], "unlisted"}),
        counter_signals=frozenset({ATTENTION.counter_signals[0], "unlisted counter"}),
        note="reviewed in context",
        observed_on="2026-07-17",
    )
    finding = progress_report(
        [entry], as_of="2026-07-17", stale_after_days=90
    ).findings[0]
    assert finding.countered == ATTENTION.counter_signals
    assert finding.ignored_markers == ("unlisted",)
    assert finding.ignored_counter_signals == ("unlisted counter",)
    assert finding.note == "reviewed in context"
    assert finding.observed_on == "2026-07-17"


def test_every_finding_carries_reasons() -> None:
    report = progress_report([_full_entry(ATTENTION)])
    assert all(finding.reasons for finding in report.findings)


def test_observed_and_unmet_fields_are_populated() -> None:
    partial = HorizonEntry(ATTENTION.id, frozenset({ATTENTION.markers[0]}))
    finding = progress_report([partial]).findings[0]
    assert finding.observed == (ATTENTION.markers[0],)
    assert finding.unmet == tuple(
        sorted(set(ATTENTION.markers) - {ATTENTION.markers[0]})
    )
    assert any("remains open" in reason for reason in finding.reasons)


def test_counts_summary() -> None:
    report = progress_report([_full_entry(ATTENTION)])
    tally = report.counts()
    assert tally["TOWARD"] == 1
    assert tally["NOT_OBSERVED"] == len(GOLDEN_ASPIRATIONS) - 1
    assert sum(tally.values()) == len(GOLDEN_ASPIRATIONS)


def test_empty_entries_yield_all_not_observed() -> None:
    report = progress_report([])
    assert report.intake_notes == ()
    assert report.counts()["NOT_OBSERVED"] == len(GOLDEN_ASPIRATIONS)


def test_custom_aspiration_subset_is_respected() -> None:
    subset = (ATTENTION,)
    report = progress_report([_full_entry(ATTENTION)], subset)
    assert len(report.findings) == 1
    assert report.findings[0].status is HorizonStatus.TOWARD


def test_observation_exactly_at_staleness_boundary_stays_fresh() -> None:
    """Boundary: age == stale_after_days is fresh (the cutoff is exclusive).

    Pins the `> stale_after_days` comparison so flipping it to `>=` (which
    would mark a boundary-age observation stale) makes a test go red — the
    branch is not merely executed, its boundary value is asserted.
    """
    review = date(2026, 7, 17)
    boundary = review - timedelta(days=90)
    finding = progress_report(
        [_full_entry(ATTENTION, observed_on=boundary.isoformat())],
        as_of=review,
        stale_after_days=90,
    ).findings[0]
    assert finding.status is HorizonStatus.TOWARD
    assert not any("older than 90 days" in reason for reason in finding.reasons)


def test_observation_one_day_past_staleness_boundary_is_stale() -> None:
    """Boundary+1: age == stale_after_days + 1 is stale."""
    review = date(2026, 7, 17)
    over = review - timedelta(days=91)
    finding = progress_report(
        [_full_entry(ATTENTION, observed_on=over.isoformat())],
        as_of=review,
        stale_after_days=90,
    ).findings[0]
    assert finding.status is HorizonStatus.INQUIRY
    assert any("older than 90 days" in reason for reason in finding.reasons)
