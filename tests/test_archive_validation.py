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
