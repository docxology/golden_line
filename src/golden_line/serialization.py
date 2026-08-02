"""Deterministic serialization for the registry and its reports.

The digests here are review and drift-detection instruments: two people (or
two revisions) can compare a short hex string to see whether they are reading
the same registry or the same report. A digest carries no safety, warranty,
or attestation semantics of any kind.
"""

from __future__ import annotations

import hashlib
import json

from .models import Aspiration, HorizonReport


def canonical_registry(aspirations: tuple[Aspiration, ...]) -> str:
    """Order-independent canonical JSON for a registry tuple."""
    payload = [
        item.canonical() for item in sorted(aspirations, key=lambda item: item.id)
    ]
    return json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )


def registry_digest(aspirations: tuple[Aspiration, ...]) -> str:
    """SHA-256 of the canonical registry; a drift-review handle, nothing more."""
    return hashlib.sha256(canonical_registry(aspirations).encode("utf-8")).hexdigest()


def canonical_report(report: HorizonReport) -> str:
    """Order-independent canonical JSON for a horizon report."""
    payload = {
        "findings": [
            {
                "aspiration_id": finding.aspiration_id,
                "status": finding.status.value,
                "reasons": list(finding.reasons),
                "observed": list(finding.observed),
                "unmet": list(finding.unmet),
                "countered": list(finding.countered),
                "ignored_markers": list(finding.ignored_markers),
                "ignored_counter_signals": list(finding.ignored_counter_signals),
                "note": finding.note,
                "observed_on": finding.observed_on,
                "stale": finding.stale,
                "date_issue": finding.date_issue,
            }
            for finding in sorted(
                report.findings, key=lambda finding: finding.aspiration_id
            )
        ],
        "intake_notes": list(report.intake_notes),
        "counts": report.counts(),
        "registry_version": report.registry_version,
        "registry_digest": report.registry_digest,
        "as_of": report.as_of,
        "stale_after_days": report.stale_after_days,
    }
    return json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )


def report_digest(report: HorizonReport) -> str:
    """SHA-256 of the canonical report, for comparing report revisions."""
    return hashlib.sha256(canonical_report(report).encode("utf-8")).hexdigest()
