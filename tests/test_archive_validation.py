import hashlib
import json
from dataclasses import replace

import pytest

import golden_line as gl


@pytest.mark.parametrize(
    "change",
    [
        {"review_date": "timestamp"},
        {"subject_id": 1},
        {"registry_version": ""},
        {"registry_digest": "bad"},
        {"report_ref": None},
        {"native_status": ()},
        {"native_status": (("id", "not-a-status"),)},
        {"source_snapshot_refs": "scalar"},
    ],
)
def test_strict_envelope_rejects_malformed_fields(change):
    envelope = gl.report_envelope(gl.progress_report([], as_of="2026-10-20"))
    assert gl.validate_instrument_envelope(replace(envelope, **change))


def test_strict_envelope_rejects_nonrecord():
    assert gl.validate_instrument_envelope(None)


@pytest.mark.parametrize(
    "mutation",
    [
        "schema",
        "array",
        "findings-array",
        "duplicate-finding",
        "text",
        "tokens",
        "flag",
        "threshold",
        "counts",
        "intake-hash",
        "intake-schema",
        "ordinal",
        "reason",
        "entry-text",
        "admission",
    ],
)
def test_archive_rejects_malformed_shape_and_consistently_rehashed_intake(mutation):
    report = gl.progress_report(
        [gl.HorizonEntry(gl.GOLDEN_ASPIRATIONS[0].id), None], as_of="2026-10-20"
    )
    data = json.loads(gl.canonical_archive(report))
    envelope = json.loads(gl.canonical_envelope(gl.report_envelope(report)))
    if mutation == "schema":
        data["schema_version"] = "unsupported"
    elif mutation == "array":
        data = []
    elif mutation == "findings-array":
        data["report"]["findings"] = None
    elif mutation == "duplicate-finding":
        data["report"]["findings"].append(data["report"]["findings"][0])
    elif mutation == "text":
        data["report"]["findings"][0]["note"] = None
    elif mutation == "tokens":
        data["report"]["findings"][0]["observed"] = "scalar"
    elif mutation == "flag":
        data["report"]["findings"][0]["stale"] = 0
    elif mutation == "threshold":
        data["report"]["stale_after_days"] = True
    elif mutation == "counts":
        data["report"]["counts"]["NOT_OBSERVED"] = 100
    elif mutation == "intake-hash":
        data["intake_ref"] = "0" * 64
    else:
        if mutation == "intake-schema":
            data["intake"]["schema_version"] = "unsupported"
        elif mutation == "ordinal":
            data["intake"]["records"][0]["ordinal"] = True
        elif mutation == "reason":
            data["intake"]["records"][0]["set_aside_reason"] = "invented"
        elif mutation == "entry-text":
            data["intake"]["records"][0]["entry"]["note"] = None
        else:
            data["intake"]["records"][0]["admitted"] = False
        data["intake_ref"] = hashlib.sha256(
            json.dumps(
                data["intake"],
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode()
        ).hexdigest()
    with pytest.raises(ValueError, match="invalid Golden Line archive"):
        gl.decode_archive(data, envelope)


def test_string_archive_input_and_malformed_dispositions_round_trip():
    report = gl.progress_report([None], as_of="2026-10-20")
    assert (
        gl.decode_archive(
            gl.canonical_archive(report),
            gl.canonical_envelope(gl.report_envelope(report)),
        )
        == report
    )


@pytest.mark.parametrize(
    "mutation",
    ["duplicate-admitted", "known-set-aside", "unknown-admitted", "blank-id", "notes"],
)
def test_rehashed_intake_cannot_contradict_native_admission(mutation):
    identifier = gl.GOLDEN_ASPIRATIONS[0].id
    report = gl.progress_report(
        [gl.HorizonEntry(identifier), gl.HorizonEntry(identifier)],
        as_of="2026-11-06",
    )
    data = json.loads(gl.canonical_archive(report))
    records = data["intake"]["records"]
    if mutation == "duplicate-admitted":
        records[1].update(admitted=True, set_aside_reason=None, note=None)
    elif mutation == "known-set-aside":
        records[0].update(
            admitted=False, set_aside_reason="unknown_id", note="set aside"
        )
    elif mutation == "unknown-admitted":
        records[0]["entry"]["aspiration_id"] = "outside-the-report"
    elif mutation == "blank-id":
        records[0]["entry"]["aspiration_id"] = ""
    else:
        records[1]["note"] = "different rejection note"
    data["intake_ref"] = hashlib.sha256(
        json.dumps(
            data["intake"], ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode()
    ).hexdigest()
    with pytest.raises(ValueError, match="invalid Golden Line archive"):
        gl.decode_archive(data, gl.canonical_envelope(gl.report_envelope(report)))


def _rehash_intake(data):
    data["intake_ref"] = hashlib.sha256(
        json.dumps(
            data["intake"], ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
    ).hexdigest()


@pytest.mark.parametrize(
    "mutation",
    [
        "removed",
        "markers",
        "counters",
        "ignored-marker",
        "ignored-counter",
        "note",
        "date",
    ],
)
def test_rehashed_admitted_intake_must_correspond_to_retained_finding(mutation):
    aspiration = gl.GOLDEN_ASPIRATIONS[0]
    entry = gl.HorizonEntry(
        aspiration.id,
        frozenset((*aspiration.markers, "extra marker")),
        frozenset(("extra counter",)),
        note="original note",
        observed_on="2026-10-20",
    )
    report = gl.progress_report([entry], as_of="2026-10-20")
    data = json.loads(gl.canonical_archive(report))
    raw = data["intake"]["records"][0]["entry"]
    if mutation == "removed":
        data["intake"]["records"].clear()
    elif mutation == "markers":
        raw["observed_markers"].remove(aspiration.markers[0])
    elif mutation == "counters":
        raw["counter_signals"].append(aspiration.counter_signals[0])
    elif mutation == "ignored-marker":
        raw["observed_markers"].remove("extra marker")
    elif mutation == "ignored-counter":
        raw["counter_signals"].remove("extra counter")
    elif mutation == "note":
        raw["note"] = "different note"
    else:
        raw["observed_on"] = "2026-10-19"
    _rehash_intake(data)
    with pytest.raises(ValueError, match="do not correspond"):
        gl.decode_archive(data, gl.canonical_envelope(gl.report_envelope(report)))


def test_rehashed_intake_cannot_admit_an_unobserved_finding():
    report = gl.progress_report([], as_of="2026-10-20")
    data = json.loads(gl.canonical_archive(report))
    data["intake"]["records"].append(
        {
            "ordinal": 1,
            "entry": {
                "aspiration_id": gl.GOLDEN_ASPIRATIONS[0].id,
                "observed_markers": [],
                "counter_signals": [],
                "note": "",
                "observed_on": "",
            },
            "admitted": True,
            "set_aside_reason": None,
            "note": None,
        }
    )
    _rehash_intake(data)
    with pytest.raises(ValueError, match="do not correspond"):
        gl.decode_archive(data, gl.canonical_envelope(gl.report_envelope(report)))


def test_rehashed_rejected_duplicate_may_change_without_changing_native_finding():
    aspiration = gl.GOLDEN_ASPIRATIONS[0]
    positive = gl.HorizonEntry(aspiration.id, frozenset(aspiration.markers))
    report = gl.progress_report([positive, positive], as_of="2026-10-20")
    data = json.loads(gl.canonical_archive(report))
    raw = data["intake"]["records"][1]["entry"]
    raw["note"] = "later contrary observation"
    raw["counter_signals"] = sorted(aspiration.counter_signals)
    _rehash_intake(data)
    restored = gl.decode_archive(
        data, gl.canonical_envelope(gl.report_envelope(report))
    )
    assert restored.findings == report.findings
    assert restored.intake_archive[1].entry.note == raw["note"]
    assert restored.intake_archive[1].entry.counter_signals == frozenset(
        aspiration.counter_signals
    )


def test_archive_null_intake_is_not_a_native_only_read():
    report = gl.progress_report([], as_of="2026-10-20")
    data = json.loads(gl.canonical_archive(report))
    data["intake"] = None
    _rehash_intake(data)
    with pytest.raises(ValueError, match="archive schema"):
        gl.decode_archive(data, gl.canonical_envelope(gl.report_envelope(report)))


@pytest.mark.parametrize("field", ["observed", "countered"])
def test_admitted_token_partition_cannot_overlap_its_ignored_tokens(field):
    aspiration = gl.GOLDEN_ASPIRATIONS[0]
    entry = gl.HorizonEntry(
        aspiration.id,
        frozenset(aspiration.markers),
        frozenset(aspiration.counter_signals),
    )
    report = gl.progress_report([entry], as_of="2026-10-20")
    finding = report.findings[0]
    ignored = "ignored_markers" if field == "observed" else "ignored_counter_signals"
    contradictory = replace(finding, **{ignored: getattr(finding, field)})
    report = replace(report, findings=(contradictory, *report.findings[1:]))
    with pytest.raises(ValueError, match="do not correspond"):
        gl.decode_archive(
            gl.canonical_archive(report),
            gl.canonical_envelope(gl.report_envelope(report)),
        )


@pytest.mark.parametrize(
    "location",
    [
        "native-note",
        "native-tokens",
        "native-metadata",
        "intake-note",
        "intake-tokens",
        "disposition",
    ],
)
def test_decoder_rejects_surrogates_at_text_boundary_before_utf8_hashing(location):
    aspiration = gl.GOLDEN_ASPIRATIONS[0]
    report = gl.progress_report([gl.HorizonEntry(aspiration.id)], as_of="2026-10-20")
    data = json.loads(gl.canonical_archive(report))
    if location == "native-note":
        data["report"]["findings"][0]["note"] = "\ud800"
    elif location == "native-tokens":
        data["report"]["findings"][0]["reasons"] = ["\ud800"]
    elif location == "native-metadata":
        data["report"]["registry_version"] = "\ud800"
    elif location == "intake-note":
        data["intake"]["records"][0]["entry"]["note"] = "\ud800"
    elif location == "intake-tokens":
        data["intake"]["records"][0]["entry"]["observed_markers"] = ["\ud800"]
    else:
        data["intake"]["records"][0]["note"] = "\ud800"
    with pytest.raises(ValueError) as caught:
        gl.decode_archive(data, gl.canonical_envelope(gl.report_envelope(report)))
    assert not isinstance(caught.value.__cause__, UnicodeError)
