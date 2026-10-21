import json
from dataclasses import replace
from pathlib import Path

import pytest

import golden_line as gl

A = gl.GOLDEN_ASPIRATIONS[0]


@pytest.mark.parametrize(
    "change",
    [
        {"schema_version": "wrong"},
        {"line_id": "other"},
        {"scope_and_nonclaims": ()},
        {"scope_and_nonclaims": ("invented",)},
    ],
)
def test_strict_instrument_validation_rejects_identity_and_nonclaims(change):
    report = gl.progress_report([], as_of="2026-10-20")
    envelope = replace(gl.report_envelope(report), **change)
    assert gl.envelope_matches_report(envelope, report)
    assert gl.validate_instrument_envelope(envelope)


def test_consistent_rewrite_and_rehash_is_still_correspondence():
    original = gl.progress_report([], as_of="2026-10-20")
    rewritten = replace(original, as_of="2026-10-19")
    envelope = gl.report_envelope(
        rewritten,
        subject_id="unverified author claim",
        source_snapshot_refs=("unverified source",),
    )
    assert gl.envelope_matches_report(envelope, rewritten)
    assert gl.validate_instrument_envelope(envelope) == ()
    assert gl.report_digest(original) != envelope.report_ref


@pytest.mark.parametrize(
    "registry",
    [
        gl.GOLDEN_ASPIRATIONS,
        tuple(reversed(gl.GOLDEN_ASPIRATIONS)),
        tuple(sorted(gl.GOLDEN_ASPIRATIONS, key=lambda a: a.id)),
    ],
)
def test_export_parse_typed_reconstruction_round_trip(registry):
    report = gl.progress_report([gl.HorizonEntry(A.id)], registry, as_of="2026-10-20")
    envelope = gl.report_envelope(report)
    rebuilt = gl.decode_archive(
        json.loads(gl.canonical_archive(report)),
        json.loads(gl.canonical_envelope(envelope)),
    )
    assert rebuilt == report
    assert gl.envelope_matches_report(envelope, rebuilt)


@pytest.mark.parametrize("mutation", ["duplicate", "missing", "extra", "status"])
def test_decoder_requires_native_status_bijection(mutation):
    report = gl.progress_report([], as_of="2026-10-20")
    data = json.loads(gl.canonical_envelope(gl.report_envelope(report)))
    if mutation == "duplicate":
        data["native_status"].append(data["native_status"][0])
    elif mutation == "missing":
        data["native_status"].pop()
    elif mutation == "extra":
        data["native_status"].append(["unknown", "INQUIRY"])
    else:
        data["native_status"][0][1] = "INQUIRY"
    with pytest.raises(ValueError):
        gl.decode_archive(json.loads(gl.canonical_archive(report)), data)


def test_permutations_have_equal_native_digest_and_distinct_envelope_bytes():
    report = gl.progress_report([], as_of="2026-10-20")
    reversed_report = replace(report, findings=tuple(reversed(report.findings)))
    assert gl.report_digest(report) == gl.report_digest(reversed_report)
    assert gl.canonical_envelope(gl.report_envelope(report)) != gl.canonical_envelope(
        gl.report_envelope(reversed_report)
    )


def test_discarded_contradiction_retained_separately_from_native_digest():
    positive = gl.HorizonEntry(A.id, frozenset(A.markers))
    countered = gl.HorizonEntry(
        A.id,
        counter_signals=frozenset(A.counter_signals),
        note="disputed",
        observed_on="2026-10-19",
    )
    report = gl.progress_report([positive, countered], as_of="2026-10-20")
    changed = gl.progress_report(
        [positive, replace(countered, note="another dispute")], as_of="2026-10-20"
    )
    reverse = gl.progress_report([countered, positive], as_of="2026-10-20")
    assert report.findings[0].status is gl.HorizonStatus.TOWARD
    assert reverse.findings[0].status is gl.HorizonStatus.DRIFTING
    assert report.intake_archive[1].entry == countered
    assert gl.report_digest(report) == gl.report_digest(changed)
    assert gl.intake_digest(report) != gl.intake_digest(changed)


def test_original_native_fixture_decodes_without_digest_migration():
    fixture = json.loads(
        (Path(__file__).parent / "fixtures" / "native_report_v040.json").read_text()
    )
    report = gl.decode_archive(fixture["report"], fixture["envelope"])
    assert gl.report_digest(report) == fixture["envelope"]["report_ref"]
