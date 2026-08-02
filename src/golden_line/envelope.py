"""The common report envelope Golden Line exports for co-registration.

A reader holding reports from several independent instruments needs one
uniform way to say "this instrument, about this subject, at this review
moment, said this — and here is the pointer to its complete native report."
The envelope is that data contract and nothing more. It points to the full
canonical report by digest instead of copying or reinterpreting its fields,
so this instrument remains authoritative about its own vocabulary, and it
carries the instrument's non-claims with it, so a stored envelope cannot
quietly outgrow what the instrument was allowed to say.

The shared shape is declared per instrument under the schema string
``line.report-envelope/1.0``; sibling instruments that export the same shape
do so by publishing the same schema string, never by importing one another.
``native_status`` is deliberately typed as this line's own vocabulary — for
Golden Line, the complete ordered per-aspiration directional readings,
because this instrument has no single overall verdict and none is invented
here — and envelopes from different lines must not be compared, ranked,
averaged, or merged on it. An envelope is a witness record, not a score.
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass

from .models import HorizonReport
from .serialization import report_digest

#: The cross-instrument envelope shape this module exports.
ENVELOPE_SCHEMA = "line.report-envelope/1.0"

#: This instrument's identity inside an envelope.
GOLDEN_LINE_ID = "golden_line"

#: The non-claims every envelope carries, restating the instrument boundary
#: from the README, ``manuscript/05_limits.md``, and
#: ``docs/evidence-protocol.md`` in transportable form.
SCOPE_AND_NONCLAIMS: tuple[str, ...] = (
    "records directional readings of aspiration records against a versioned "
    "registry at a stated review date",
    "statuses describe a record, not a person; they are not a safety score, "
    "accreditation, moral authority, or permission mechanism",
    "NOT_OBSERVED means no valid entry was admitted; it does not mean that "
    "nobody looked",
    "TOWARD says only that declared markers were observed with no recorded "
    "counter-signal; it does not prove the work good, safe, lawful, or "
    "beneficial",
    "aspiration is not authorization: no reading here overrides a refusal, "
    "discipline, or absence instrument",
    "does not rank, merge, or evaluate the other line instruments",
)


@dataclass(frozen=True)
class ReportEnvelope:
    """One instrument's complete report, referenced without reinterpretation.

    ``report_ref`` is the SHA-256 of the canonical native report, which
    contains the full derivation — every finding with its reasons trail,
    matched and ignored tokens, temporal flags, and every intake note.
    ``native_status`` is the complete ordered per-aspiration readings in this
    line's own vocabulary; it is not a summary and must not become one.
    ``registry_version`` is the reviewed registry revision the report itself
    recorded; registry content is pinned by ``registry_digest`` either way.
    ``source_snapshot_refs`` is caller-supplied provenance for the material
    the entries were filed about; the envelope stores, and does not verify,
    those references.
    """

    schema_version: str
    line_id: str
    subject_id: str
    review_date: str
    registry_version: str
    registry_digest: str
    native_status: tuple[tuple[str, str], ...]
    report_ref: str
    source_snapshot_refs: tuple[str, ...]
    scope_and_nonclaims: tuple[str, ...]


def report_envelope(
    report: HorizonReport,
    subject_id: str = "",
    source_snapshot_refs: Iterable[str] = (),
) -> ReportEnvelope:
    """Wrap a report in the common envelope, pointing at — never re-reading —
    its complete canonical form.

    ``subject_id`` names what was reviewed, in the caller's own reference
    scheme; the evaluator does not verify it. The envelope's ``report_ref``
    is computed from the exact report supplied, so an envelope can only ever
    point at the derivation that produced its readings.
    """

    refs = tuple(source_snapshot_refs)
    if not all(isinstance(ref, str) and ref.strip() for ref in refs):
        raise ValueError("source_snapshot_refs must be non-blank strings")
    if not isinstance(subject_id, str):
        raise TypeError("subject_id must be a string")
    return ReportEnvelope(
        ENVELOPE_SCHEMA,
        GOLDEN_LINE_ID,
        subject_id,
        report.as_of,
        report.registry_version,
        report.registry_digest,
        tuple(
            (finding.aspiration_id, finding.status.value) for finding in report.findings
        ),
        report_digest(report),
        refs,
        SCOPE_AND_NONCLAIMS,
    )


def canonical_envelope(envelope: ReportEnvelope) -> str:
    """Serialize an envelope to stable JSON for archiving beside its report.

    Store this string next to the ``canonical_report`` output it points at;
    the pair is the smallest archive from which a later review can verify
    that the envelope and the derivation still agree.
    """

    payload = {
        "schema_version": envelope.schema_version,
        "line_id": envelope.line_id,
        "subject_id": envelope.subject_id,
        "review_date": envelope.review_date,
        "registry_version": envelope.registry_version,
        "registry_digest": envelope.registry_digest,
        "native_status": [list(pair) for pair in envelope.native_status],
        "report_ref": envelope.report_ref,
        "source_snapshot_refs": list(envelope.source_snapshot_refs),
        "scope_and_nonclaims": list(envelope.scope_and_nonclaims),
    }
    return json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )


def envelope_matches_report(envelope: ReportEnvelope, report: HorizonReport) -> bool:
    """Return whether an envelope still points at exactly this report.

    This is the read-back check for an archived pair: the digest, the review
    date, the registry version and digest, and the per-aspiration readings
    must all agree. A mismatch means one of the two was edited after export;
    the check cannot say which, and it says nothing about the truth of either.
    """

    return (
        envelope.report_ref == report_digest(report)
        and envelope.review_date == report.as_of
        and envelope.registry_version == report.registry_version
        and envelope.registry_digest == report.registry_digest
        and envelope.native_status
        == tuple(
            (finding.aspiration_id, finding.status.value) for finding in report.findings
        )
    )


__all__ = [
    "ENVELOPE_SCHEMA",
    "GOLDEN_LINE_ID",
    "ReportEnvelope",
    "SCOPE_AND_NONCLAIMS",
    "canonical_envelope",
    "envelope_matches_report",
    "report_envelope",
]
