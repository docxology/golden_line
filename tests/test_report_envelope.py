"""The common report envelope: pointer, not reinterpretation.

Every case here runs the real ``progress_report`` and wraps real reports; the
envelope's completeness claim is proven against the canonical serialization
the digest is computed from, not against a restatement of it. The envelope
follows the shape the 2026-07-29 design review proposed for the whole line
set, declared here under this repository's own ``line.report-envelope/1.0``
literal.
"""

from __future__ import annotations

import dataclasses
import json

import pytest

from golden_line import (
    ENVELOPE_SCHEMA,
    GOLDEN_ASPIRATIONS,
    GOLDEN_LINE_ID,
    REGISTRY_VERSION,
    SCOPE_AND_NONCLAIMS,
    HorizonEntry,
    HorizonReport,
    ReportEnvelope,
    canonical_envelope,
    canonical_report,
    envelope_matches_report,
    progress_report,
    report_digest,
    report_envelope,
)

AS_OF = "2026-07-29"


def _worked_entries() -> list[object]:
    """Every intake arm at once: admitted, malformed, unknown id, duplicate."""

    attention = GOLDEN_ASPIRATIONS[0]
    repair = GOLDEN_ASPIRATIONS[2]
    return [
        "not an entry at all",
        HorizonEntry("no-such-aspiration", frozenset()),
        HorizonEntry(attention.id, frozenset(attention.markers)),
        HorizonEntry(attention.id, frozenset()),
        HorizonEntry(repair.id, counter_signals=frozenset(repair.counter_signals)),
    ]


def _worked_report() -> HorizonReport:
    return progress_report(_worked_entries(), as_of=AS_OF)


# ---------------------------------------------------------------------------
# Canonical report completeness: the reference target holds the whole state.
# ---------------------------------------------------------------------------


def test_canonical_report_is_deterministic_and_serializes_every_arm() -> None:
    """Two identical evaluations produce byte-identical canonical strings,
    and every set-aside note and ``None`` arm is present in the payload."""

    first = canonical_report(_worked_report())
    second = canonical_report(_worked_report())
    assert first == second
    payload = json.loads(first)
    assert payload["as_of"] == AS_OF
    assert payload["stale_after_days"] is None
    assert payload["registry_version"] == REGISTRY_VERSION
    assert len(payload["findings"]) == len(GOLDEN_ASPIRATIONS)
    notes = payload["intake_notes"]
    assert any("expected a HorizonEntry" in note for note in notes)
    assert any("unknown aspiration" in note for note in notes)
    assert any("duplicate entry" in note for note in notes)
    statuses = {item["status"] for item in payload["findings"]}
    assert {"TOWARD", "DRIFTING", "NOT_OBSERVED"} <= statuses
    unobserved = next(
        item for item in payload["findings"] if item["status"] == "NOT_OBSERVED"
    )
    assert unobserved["observed"] == []
    assert unobserved["observed_on"] == ""


# ---------------------------------------------------------------------------
# The envelope points at the native report without reinterpreting it.
# ---------------------------------------------------------------------------


def test_the_envelope_points_at_the_native_report_without_reinterpreting_it() -> None:
    report = _worked_report()
    envelope = report_envelope(
        report, subject_id="worked-example", source_snapshot_refs=("snapshot-1",)
    )
    assert envelope.schema_version == ENVELOPE_SCHEMA
    assert envelope.line_id == GOLDEN_LINE_ID
    assert envelope.subject_id == "worked-example"
    assert envelope.review_date == report.as_of
    assert envelope.registry_version == report.registry_version
    assert envelope.registry_digest == report.registry_digest
    assert envelope.report_ref == report_digest(report)
    assert envelope.source_snapshot_refs == ("snapshot-1",)


def test_native_status_is_the_complete_ordered_per_aspiration_readings() -> None:
    """Golden Line has no single overall verdict, so the envelope exports the
    ordered per-aspiration readings exactly — never an invented aggregate."""

    report = _worked_report()
    envelope = report_envelope(report)
    assert envelope.native_status == tuple(
        (finding.aspiration_id, finding.status.value) for finding in report.findings
    )
    assert len(envelope.native_status) == len(GOLDEN_ASPIRATIONS)
    assert not isinstance(envelope.native_status, str)


def test_the_nonclaims_travel_inside_the_envelope() -> None:
    """The instrument boundary rides inside every envelope, so a stored copy
    cannot outgrow what the instrument was allowed to say."""

    envelope = report_envelope(_worked_report())
    assert envelope.scope_and_nonclaims == SCOPE_AND_NONCLAIMS
    assert any("not a safety score" in claim for claim in envelope.scope_and_nonclaims)
    assert any(
        "aspiration is not authorization" in claim
        for claim in envelope.scope_and_nonclaims
    )
    payload = json.loads(canonical_envelope(envelope))
    assert payload["scope_and_nonclaims"] == list(SCOPE_AND_NONCLAIMS)


def test_canonical_envelope_round_trips_and_is_deterministic() -> None:
    report = _worked_report()
    first = canonical_envelope(report_envelope(report, subject_id="worked-example"))
    second = canonical_envelope(report_envelope(report, subject_id="worked-example"))
    assert first == second
    payload = json.loads(first)
    assert payload["schema_version"] == ENVELOPE_SCHEMA
    assert payload["line_id"] == GOLDEN_LINE_ID
    assert payload["report_ref"] == report_digest(report)
    assert payload["native_status"][0][0] == report.findings[0].aspiration_id
    assert set(payload) == {field.name for field in dataclasses.fields(ReportEnvelope)}


# ---------------------------------------------------------------------------
# Read-back: an archived pair can be verified, and tampering is visible.
# ---------------------------------------------------------------------------


def test_envelope_matches_report_verifies_an_archived_pair() -> None:
    report = _worked_report()
    envelope = report_envelope(report, subject_id="worked-example")
    assert envelope_matches_report(envelope, report)
    other = progress_report([], as_of="2026-07-19")
    assert not envelope_matches_report(envelope, other)


@pytest.mark.parametrize(
    "tamper",
    [
        {"report_ref": "0" * 64},
        {"review_date": "2020-01-01"},
        {"registry_version": "1999.01.01"},
        {"registry_digest": "0" * 64},
        {"native_status": ()},
    ],
    ids=lambda tamper: next(iter(tamper)),
)
def test_a_tampered_envelope_field_no_longer_matches(tamper: dict) -> None:
    report = _worked_report()
    envelope = report_envelope(report)
    assert not envelope_matches_report(dataclasses.replace(envelope, **tamper), report)


def test_envelope_input_validation_fails_closed() -> None:
    report = _worked_report()
    with pytest.raises(ValueError, match="non-blank strings"):
        report_envelope(report, source_snapshot_refs=("",))
    with pytest.raises(ValueError, match="non-blank strings"):
        report_envelope(report, source_snapshot_refs=(42,))  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="subject_id must be a string"):
        report_envelope(report, subject_id=7)  # type: ignore[arg-type]
