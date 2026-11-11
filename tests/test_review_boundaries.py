import json
from dataclasses import replace
from datetime import date, datetime, timezone

import pytest

import golden_line as gl
from golden_line import (
    GOLDEN_ASPIRATIONS,
    HorizonEntry,
    progress_report,
    registry_sound,
    report_envelope,
    temporal_currentness_sweep,
)

A = GOLDEN_ASPIRATIONS[0]


@pytest.mark.parametrize(
    "registry",
    [
        (A, A),
        (object(),),
        None,
        "registry",
        {A.id: A},
        (),
        (replace(A, id=" "),),
        (replace(A, markers="ab"),),
        (replace(A, markers=b"ab"),),
        (replace(A, markers={"a": 1}),),
        (replace(A, markers=iter(("a",))),),
        (replace(A, markers=()),),
        (replace(A, title=None),),
    ],
)
def test_invalid_registry_rejected_before_entries_are_read(registry):
    with pytest.raises(ValueError, match="registry") as caught:
        progress_report([], registry, as_of="2026-10-20")
    assert caught.value.issues


def test_battery_does_not_consume_one_shot_signal_fields():
    tokens = iter(("a", "b"))
    assert not registry_sound((replace(A, markers=tokens),))
    assert next(tokens) == "a"


def test_subset_identity_and_immutable_replay():
    report = progress_report([], (A,), as_of="2026-10-20")
    assert report.registry_version.startswith("custom:")
    assert report == progress_report([], (A,), as_of="2026-10-20")


@pytest.mark.parametrize("window", [None, 30])
def test_date_only_rejects_timestamp_in_both_modes(window):
    with pytest.raises(TypeError, match="as_of must be an ISO date string"):
        progress_report(
            [HorizonEntry(A.id, observed_on="2026-10-20")],
            as_of=datetime(2026, 10, 20, 12, tzinfo=timezone.utc),
            stale_after_days=window,
        )


@pytest.mark.parametrize("age", [True, False, 1.5, "2"])
def test_sweep_ages_are_exact_integers(age):
    with pytest.raises(ValueError, match="integer"):
        temporal_currentness_sweep(A.id, [age], as_of="2026-10-20", stale_after_days=30)


def test_sweep_rejects_datetime():
    with pytest.raises(TypeError, match="date"):
        temporal_currentness_sweep(
            A.id,
            [0],
            as_of=datetime(2026, 10, 20, tzinfo=timezone.utc),
            stale_after_days=30,
        )


def _raising_tokens():
    raise RuntimeError("must not execute token iterators")
    yield "unreachable"


@pytest.mark.parametrize("tokens", [{"a": 1}, iter(()), _raising_tokens()])
def test_unsupported_token_containers_are_set_aside_without_iteration(tokens):
    report = progress_report([HorizonEntry(A.id, tokens)], as_of="2026-10-20")
    assert report.findings[0].status.value == "NOT_OBSERVED"
    assert report.intake_notes


def test_currentness_is_explicitly_not_evaluated():
    report = progress_report([], as_of=date(2026, 10, 20))
    assert report.currentness_evaluated is False


@pytest.mark.parametrize(
    "refs", ["snapshot-1", b"snap", {"snap": 1}, None, (1,), (" ",)]
)
def test_envelope_rejects_invalid_reference_containers(refs):
    with pytest.raises((TypeError, ValueError), match="source_snapshot_refs"):
        report_envelope(
            progress_report([], as_of="2026-10-20"), source_snapshot_refs=refs
        )


def test_reference_order_and_duplicates_are_preserved():
    refs = ["b", "a", "b"]
    envelope = report_envelope(
        progress_report([], as_of="2026-10-20"), source_snapshot_refs=refs
    )
    assert envelope.source_snapshot_refs == tuple(refs)


NONCALENDAR_DATES = (
    "20261020",
    "2026-W43-2",
    "2026-1-20",
    "2026-10-2",
    "２０２６-１０-２０",
    "2026-10-20\n",
    "2026-10-20T00:00:00",
    "2026-02-30",
)


@pytest.mark.parametrize("value", NONCALENDAR_DATES)
def test_noncalendar_review_dates_are_rejected_at_all_review_boundaries(value):
    with pytest.raises(ValueError):
        progress_report([], as_of=value)
    with pytest.raises(ValueError):
        temporal_currentness_sweep(A.id, [0], as_of=value, stale_after_days=0)
    envelope = report_envelope(progress_report([], as_of="2026-10-20"))
    assert gl.validate_instrument_envelope(replace(envelope, review_date=value))


@pytest.mark.parametrize("value", NONCALENDAR_DATES)
def test_noncalendar_observation_cannot_establish_currentness(value):
    entry = HorizonEntry(A.id, frozenset(A.markers), observed_on=value)
    finding = progress_report([entry], as_of="2026-10-20", stale_after_days=0).findings[
        0
    ]
    assert finding.status is gl.HorizonStatus.INQUIRY
    assert finding.date_issue is True
    assert finding.observed_on == value
    disabled = progress_report([entry], as_of="2026-10-20").findings[0]
    assert disabled.status is gl.HorizonStatus.TOWARD
    assert disabled.date_issue is False
    countered = progress_report(
        [replace(entry, counter_signals=frozenset(A.counter_signals))],
        as_of="2026-10-20",
        stale_after_days=0,
    ).findings[0]
    assert countered.status is gl.HorizonStatus.DRIFTING
    assert countered.date_issue is True


@pytest.mark.parametrize("day", ["0001-01-01", "2024-02-29", "9999-12-31"])
def test_exact_calendar_dates_remain_current_and_transportable(day):
    entry = HorizonEntry(A.id, frozenset(A.markers), observed_on=day)
    report = progress_report([entry], as_of=day, stale_after_days=0)
    assert report.findings[0].status is gl.HorizonStatus.TOWARD
    assert report.findings[0].date_issue is False
    envelope = report_envelope(report)
    assert gl.validate_instrument_envelope(envelope) == ()
    assert (
        gl.decode_archive(gl.canonical_archive(report), gl.canonical_envelope(envelope))
        == report
    )
    points = temporal_currentness_sweep(A.id, [0], as_of=day, stale_after_days=0)
    assert points[0].observed_on == day
    assert points[0].status is gl.HorizonStatus.TOWARD


@pytest.mark.parametrize("codepoint", [0xD800, 0xDFFF])
@pytest.mark.parametrize(
    "field",
    ["aspiration_id", "note", "observed_on", "observed_markers", "counter_signals"],
)
def test_surrogate_entry_is_malformed_before_admission_or_duplicate_custody(
    codepoint, field
):
    surrogate = chr(codepoint)
    positive = HorizonEntry(A.id, frozenset(A.markers), observed_on="2026-10-20")
    value = (
        frozenset((surrogate,)) if field.endswith(("markers", "signals")) else surrogate
    )
    malformed = replace(positive, **{field: value})
    for entries, malformed_index in (
        ([malformed, positive], 0),
        ([positive, malformed], 1),
    ):
        report = progress_report(entries, as_of="2026-10-20")
        assert report.findings[0].status is gl.HorizonStatus.TOWARD
        disposition = report.intake_archive[malformed_index]
        assert disposition.set_aside_reason == "malformed"
        assert disposition.entry is None
        assert not disposition.admitted
        archive = gl.canonical_archive(report)
        archive.encode("utf-8")
        assert (
            gl.decode_archive(archive, gl.canonical_envelope(report_envelope(report)))
            == report
        )


@pytest.mark.parametrize(
    "field", ["id", "title", "thread", "horizon", "markers", "counter_signals"]
)
def test_surrogate_registry_text_is_rejected_structurally(field):
    value = ("\ud800",) if field in ("markers", "counter_signals") else "\ud800"
    with pytest.raises(gl.RegistryValidationError) as caught:
        progress_report([], (replace(A, **{field: value}),), as_of="2026-10-20")
    assert any(issue.path.endswith("." + field) for issue in caught.value.issues)


def test_unicode_scalar_text_preserves_native_and_custody_values():
    text = json.loads('"caf\\u00e9 \\ud800\\udf48"')
    aspiration = replace(
        A,
        id="direction:" + text,
        title=text,
        markers=(text,),
        counter_signals=("contre",),
    )
    entry = HorizonEntry(aspiration.id, frozenset((text,)), note=text)
    report = progress_report([entry], (aspiration,), as_of="2026-10-20")
    envelope = report_envelope(report, subject_id=text, source_snapshot_refs=(text,))
    assert gl.validate_instrument_envelope(envelope) == ()
    native = gl.canonical_report(report)
    assert text in native
    assert b"caf\xc3\xa9" in native.encode("utf-8")
    restored = gl.decode_archive(
        gl.canonical_archive(report), gl.canonical_envelope(envelope)
    )
    assert restored == report
    assert restored.findings[0].note == text
    assert restored.intake_archive[0].entry == entry


@pytest.mark.parametrize("field", ["subject_id", "source_snapshot_refs"])
def test_envelope_caller_text_rejects_surrogates(field):
    value = ("\ud800",) if field == "source_snapshot_refs" else "\ud800"
    report = progress_report([], as_of="2026-10-20")
    with pytest.raises(ValueError):
        report_envelope(report, **{field: value})
    malformed = replace(report_envelope(report), **{field: value})
    assert gl.validate_instrument_envelope(malformed)
