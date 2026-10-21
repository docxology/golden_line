import hashlib
import json
from dataclasses import asdict, fields

from .envelope import (
    ReportEnvelope,
    envelope_matches_report,
    validate_instrument_envelope,
)
from .models import (
    HorizonEntry,
    HorizonFinding,
    HorizonReport,
    HorizonStatus,
    IntakeDisposition,
)
from .serialization import canonical_report

ARCHIVE_SCHEMA = "golden-line.archive/1.0"
INTAKE_SCHEMA = "golden-line.intake/1.0"


def _json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _intake_payload(report: HorizonReport) -> dict:
    records = []
    for disposition in report.intake_archive:
        record = asdict(disposition)
        if disposition.entry is not None:
            record["entry"]["observed_markers"] = sorted(
                disposition.entry.observed_markers
            )
            record["entry"]["counter_signals"] = sorted(
                disposition.entry.counter_signals
            )
        records.append(record)
    return {"schema_version": INTAKE_SCHEMA, "records": records}


def intake_digest(report: HorizonReport) -> str:
    return hashlib.sha256(_json(_intake_payload(report)).encode("utf-8")).hexdigest()


def canonical_archive(report: HorizonReport) -> str:
    """Archive the unchanged native report and a separately hashed intake log.

    Native report digests ignore finding order and retain their original byte
    contract. The envelope restores presentation order; intake_ref binds only
    supplied normalized intake data, never authenticity of a source batch.
    Malformed payload bytes must be retained separately by the caller.
    """
    return _json(
        {
            "schema_version": ARCHIVE_SCHEMA,
            "report": json.loads(canonical_report(report)),
            "intake": _intake_payload(report),
            "intake_ref": intake_digest(report),
        }
    )


def _strings(value: object) -> tuple[str, ...]:
    if type(value) is not list or any(type(item) is not str for item in value):
        raise ValueError("expected an array of strings")
    return tuple(value)


def _object(value: object, names: set[str]) -> dict:
    if type(value) is not dict or set(value) != names:
        raise ValueError("object fields do not match the archive schema")
    return value


def _parse(value: object) -> object:
    return json.loads(value) if isinstance(value, str) else value


def decode_archive(archive: object, envelope_data: object) -> HorizonReport:
    """Decode original native JSON or archive/1.0 using envelope ID order.

    Reject non-bijective IDs, inconsistent statuses, counts, digest pointers,
    malformed structures, and unsupported schemas. This checks supplied
    consistency, not unedited history or the truth of any observation.
    """
    try:
        envelope_dict = _object(
            _parse(envelope_data), {field.name for field in fields(ReportEnvelope)}
        )
        values = dict(envelope_dict)
        rows = values["native_status"]
        if type(rows) is not list or any(type(row) is not list for row in rows):
            raise ValueError("native_status must be an array of arrays")
        values["native_status"] = tuple(tuple(row) for row in rows)
        for name in ("source_snapshot_refs", "scope_and_nonclaims"):
            values[name] = _strings(values[name])
        envelope = ReportEnvelope(**values)
        issues = validate_instrument_envelope(envelope)
        if issues:
            raise ValueError("; ".join(issues))
        payload = _parse(archive)
        intake_data = None
        if type(payload) is dict and "schema_version" in payload:
            payload = _object(
                payload, {"schema_version", "report", "intake", "intake_ref"}
            )
            if payload["schema_version"] != ARCHIVE_SCHEMA:
                raise ValueError("unsupported archive schema")
            intake_data = payload["intake"]
            if (
                hashlib.sha256(_json(intake_data).encode("utf-8")).hexdigest()
                != payload["intake_ref"]
            ):
                raise ValueError("intake digest mismatch")
            payload = payload["report"]
        payload = _object(
            payload,
            {
                "findings",
                "intake_notes",
                "counts",
                "registry_version",
                "registry_digest",
                "as_of",
                "stale_after_days",
            },
        )
        if type(payload["findings"]) is not list:
            raise ValueError("findings must be an array")
        findings = {}
        for raw in payload["findings"]:
            raw = _object(raw, {field.name for field in fields(HorizonFinding)})
            item = dict(raw)
            for name in (
                "reasons",
                "observed",
                "unmet",
                "countered",
                "ignored_markers",
                "ignored_counter_signals",
            ):
                item[name] = _strings(item[name])
            for name in ("aspiration_id", "note", "observed_on"):
                if type(item[name]) is not str:
                    raise ValueError(f"{name} must be text")
            if any(type(item[name]) is not bool for name in ("stale", "date_issue")):
                raise ValueError("temporal flags must be boolean")
            item["status"] = HorizonStatus(item["status"])
            finding = HorizonFinding(**item)
            if finding.aspiration_id in findings:
                raise ValueError("duplicate finding identifier")
            findings[finding.aspiration_id] = finding
        if set(findings) != {identifier for identifier, _ in envelope.native_status}:
            raise ValueError("native_status and findings must be a bijection")
        window = payload["stale_after_days"]
        if window is not None and (type(window) is not int or window < 0):
            raise ValueError("invalid staleness threshold")
        report = HorizonReport(
            tuple(findings[identifier] for identifier, _ in envelope.native_status),
            _strings(payload["intake_notes"]),
            payload["registry_version"],
            payload["registry_digest"],
            payload["as_of"],
            window,
        )
        if _json(json.loads(canonical_report(report))) != _json(
            payload
        ) or not envelope_matches_report(envelope, report):
            raise ValueError("native report and envelope do not correspond")
        if intake_data is not None:
            intake_data = _object(intake_data, {"schema_version", "records"})
            if (
                intake_data["schema_version"] != INTAKE_SCHEMA
                or type(intake_data["records"]) is not list
            ):
                raise ValueError("unsupported intake schema")
            dispositions = []
            for index, raw in enumerate(intake_data["records"], start=1):
                raw = dict(
                    _object(raw, {field.name for field in fields(IntakeDisposition)})
                )
                if (
                    type(raw["ordinal"]) is not int
                    or raw["ordinal"] != index
                    or type(raw["admitted"]) is not bool
                ):
                    raise ValueError("invalid intake ordinal or admission flag")
                if raw["set_aside_reason"] not in (
                    None,
                    "duplicate",
                    "unknown_id",
                    "malformed",
                ) or (raw["note"] is not None and type(raw["note"]) is not str):
                    raise ValueError("invalid intake disposition")
                if raw["entry"] is not None:
                    entry = dict(
                        _object(
                            raw["entry"], {field.name for field in fields(HorizonEntry)}
                        )
                    )
                    for name in ("observed_markers", "counter_signals"):
                        entry[name] = frozenset(_strings(entry[name]))
                    if any(
                        type(entry[name]) is not str
                        for name in ("aspiration_id", "note", "observed_on")
                    ):
                        raise ValueError("invalid intake entry text")
                    raw["entry"] = HorizonEntry(**entry)
                if raw["admitted"]:
                    if (
                        raw["entry"] is None
                        or raw["set_aside_reason"] is not None
                        or raw["note"] is not None
                    ):
                        raise ValueError("inconsistent admitted intake disposition")
                elif raw["set_aside_reason"] is None or raw["note"] is None:
                    raise ValueError("set-aside intake requires a reason and note")
                if (raw["set_aside_reason"] == "malformed") != (raw["entry"] is None):
                    raise ValueError("malformed intake must omit normalized entry")
                dispositions.append(IntakeDisposition(**raw))
            from dataclasses import replace

            report = replace(report, intake_archive=tuple(dispositions))
            if _intake_payload(report) != intake_data:
                raise ValueError("noncanonical intake payload")
        return report
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"invalid Golden Line archive: {exc}") from exc
