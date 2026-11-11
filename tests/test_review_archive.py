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
    envelope = gl.report_envelope(report)
    envelope_json = gl.canonical_envelope(envelope)
    native_only = gl.decode_archive(gl.canonical_report(report), envelope_json)
    assert native_only.intake_archive is None
    assert native_only.findings == report.findings
    restored = gl.decode_archive(gl.canonical_archive(report), envelope_json)
    assert restored == report
    assert restored.intake_archive[1].admitted is False
    assert restored.intake_archive[1].set_aside_reason == "duplicate"
    assert restored.intake_archive[1].entry == countered
    assert gl.envelope_matches_report(envelope, restored)


@pytest.mark.parametrize("aspiration", gl.GOLDEN_ASPIRATIONS, ids=lambda a: a.id)
def test_archive_retains_admission_and_optional_temporal_transitions(aspiration):
    complete = gl.HorizonEntry(aspiration.id, frozenset(aspiration.markers))
    malformed = replace(complete, observed_markers=None)
    cases = (
        ([], None, gl.HorizonStatus.NOT_OBSERVED),
        ([malformed], None, gl.HorizonStatus.NOT_OBSERVED),
        ([gl.HorizonEntry(aspiration.id)], None, gl.HorizonStatus.INQUIRY),
        ([malformed, complete], None, gl.HorizonStatus.TOWARD),
        ([complete], None, gl.HorizonStatus.TOWARD),
        ([complete], 1, gl.HorizonStatus.INQUIRY),
        ([replace(complete, observed_on="2026-10-19")], 1, gl.HorizonStatus.TOWARD),
        ([replace(complete, observed_on="2026-10-18")], 1, gl.HorizonStatus.INQUIRY),
        ([replace(complete, observed_on="2026-10-21")], 1, gl.HorizonStatus.INQUIRY),
        (
            [replace(complete, counter_signals=frozenset(aspiration.counter_signals))],
            1,
            gl.HorizonStatus.DRIFTING,
        ),
    )
    for entries, window, status in cases:
        report = gl.progress_report(
            entries, (aspiration,), as_of="2026-10-20", stale_after_days=window
        )
        restored = gl.decode_archive(
            gl.canonical_archive(report),
            gl.canonical_envelope(gl.report_envelope(report)),
        )
        assert restored == report
        assert restored.findings[0].status is status
        assert restored.currentness_evaluated is (window is not None)


def test_original_native_fixture_decodes_without_digest_migration():
    fixture = json.loads(
        (Path(__file__).parent / "fixtures" / "native_report_v040.json").read_text()
    )
    report = gl.decode_archive(fixture["report"], fixture["envelope"])
    assert gl.report_digest(report) == fixture["envelope"]["report_ref"]


@pytest.mark.parametrize(
    "entries",
    [[], [None], [gl.HorizonEntry(A.id, frozenset(A.markers))]],
)
def test_native_only_custody_is_unavailable_not_an_evaluated_empty_log(entries):
    original = gl.progress_report(entries, as_of="2026-10-20")
    envelope = gl.canonical_envelope(gl.report_envelope(original))
    native = gl.canonical_report(original)
    restored = gl.decode_archive(native, envelope)
    assert restored.intake_archive is None
    assert gl.canonical_report(restored) == native
    assert restored.intake_notes == original.intake_notes
    for export in (gl.canonical_archive, gl.intake_digest):
        with pytest.raises(ValueError, match="custody is unavailable"):
            export(restored)
    complete = gl.decode_archive(gl.canonical_archive(original), envelope)
    assert complete == original
    assert complete.intake_archive is not None
    if not entries:
        assert complete.intake_archive == ()
        assert complete != restored


@pytest.mark.parametrize("identifier", [A.id, "local-direction"])
def test_custom_registry_archive_checks_retained_fields_not_default_vocabulary(
    identifier,
):
    aspiration = replace(A, id=identifier, markers=("local marker",))
    entry = gl.HorizonEntry(
        aspiration.id,
        frozenset(("local marker", "undeclared \U00010348")),
        frozenset(("undeclared counter",)),
        note="révisé \U00010348",
        observed_on="2026-10-20",
    )
    report = gl.progress_report([entry], (aspiration,), as_of="2026-10-20")
    restored = gl.decode_archive(
        gl.canonical_archive(report),
        gl.canonical_envelope(gl.report_envelope(report)),
    )
    assert restored == report
    assert restored.findings[0].status is gl.HorizonStatus.TOWARD
    assert restored.findings[0].ignored_markers == ("undeclared \U00010348",)
