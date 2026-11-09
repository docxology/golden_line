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
from .progress import _classify_intake_entries
from .serialization import canonical_report
from .validation import _is_scalar_text

ARCHIVE_SCHEMA = "golden-line.archive/1.0"
INTAKE_SCHEMA = "golden-line.intake/1.0"


def _json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _intake_payload(report: HorizonReport) -> dict:
    if report.intake_archive is None:
        raise ValueError(
            "normalized intake custody is unavailable; retain native report and "
            "envelope instead of emitting a complete archive"
        )
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
    """Hash complete normalized intake; raise ValueError if custody is unavailable."""
    return hashlib.sha256(_json(_intake_payload(report)).encode("utf-8")).hexdigest()


def canonical_archive(report: HorizonReport) -> str:
    """Archive the unchanged native report and a separately hashed intake log.

    Native report digests ignore finding order and retain their original byte
    contract. The envelope restores presentation order; intake_ref binds only
    supplied normalized intake data, never authenticity of a source batch.
    Malformed payload bytes must be retained separately by the caller.
    Native-only decoded reports have unavailable intake custody and are refused;
    a freshly evaluated empty intake remains a complete, exportable empty log.
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
    if type(value) is not list or any(
        type(item) is not str or not _is_scalar_text(item) for item in value
    ):
        raise ValueError("expected an array of Unicode scalar strings")
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
    malformed structures, and unsupported schemas. With a sidecar, check
    first-valid custody and intrinsic admitted-entry/finding correspondence,
    not custom-registry evaluation. Native-only reads leave intake unavailable.
    This checks supplied consistency, not unedited history or observation truth.
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
        has_intake = type(payload) is dict and "schema_version" in payload
        if has_intake:
            payload = _object(
                payload, {"schema_version", "report", "intake", "intake_ref"}
            )
            if payload["schema_version"] != ARCHIVE_SCHEMA:
                raise ValueError("unsupported archive schema")
            intake_data = payload["intake"]
            intake_ref = payload["intake_ref"]
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
                if type(item[name]) is not str or not _is_scalar_text(item[name]):
                    raise ValueError(f"{name} must be Unicode scalar text")
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
        for name in ("registry_version", "registry_digest", "as_of"):
            if type(payload[name]) is not str or not _is_scalar_text(payload[name]):
                raise ValueError(f"{name} must be Unicode scalar text")
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
        if has_intake:
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
                ) or (
                    raw["note"] is not None
                    and (
                        type(raw["note"]) is not str or not _is_scalar_text(raw["note"])
                    )
                ):
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
                        type(entry[name]) is not str or not _is_scalar_text(entry[name])
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
            classifications = _classify_intake_entries(
                (item.entry for item in dispositions), frozenset(findings)
            )
            if any(
                item.entry != classification.entry
                or item.admitted != classification.admitted
                or item.set_aside_reason != classification.set_aside_reason
                for item, classification in zip(dispositions, classifications)
            ):
                raise ValueError("intake dispositions contradict the admission rule")
            if report.intake_notes != tuple(
                item.note for item in dispositions if item.note is not None
            ):
                raise ValueError("intake notes do not correspond to dispositions")
            admitted = {
                item.entry.aspiration_id: item.entry
                for item in dispositions
                if item.admitted and item.entry is not None
            }
            if set(admitted) != {
                item.aspiration_id
                for item in report.findings
                if item.status is not HorizonStatus.NOT_OBSERVED
            }:
                raise ValueError(
                    "admitted intake and observed findings do not correspond"
                )
            for identifier, admitted_entry in admitted.items():
                finding = findings[identifier]
                if (
                    finding.note != admitted_entry.note
                    or finding.observed_on != admitted_entry.observed_on
                ):
                    raise ValueError(
                        "admitted intake text and finding do not correspond"
                    )
                for matched, ignored, tokens in (
                    (
                        finding.observed,
                        finding.ignored_markers,
                        admitted_entry.observed_markers,
                    ),
                    (
                        finding.countered,
                        finding.ignored_counter_signals,
                        admitted_entry.counter_signals,
                    ),
                ):
                    matched_tokens = set(matched)
                    ignored_tokens = set(ignored)
                    if (
                        matched_tokens & ignored_tokens
                        or matched_tokens | ignored_tokens != tokens
                    ):
                        raise ValueError(
                            "admitted intake tokens and finding do not correspond"
                        )
            if _intake_payload(report) != intake_data:
                raise ValueError("noncanonical intake payload")
            if (
                hashlib.sha256(_json(intake_data).encode("utf-8")).hexdigest()
                != intake_ref
            ):
                raise ValueError("intake digest mismatch")
        return report
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"invalid Golden Line archive: {exc}") from exc
