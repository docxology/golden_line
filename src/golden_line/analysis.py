"""Descriptive analysis over the registry and the staged evaluator.

Every helper here is pure and deterministic: it reads the frozen aspiration
registry, or replays the public :func:`golden_line.progress.progress_report`
evaluator, and returns typed summaries. Nothing in this module changes the
evaluator's semantics, and none of its outputs is a score, a certification,
or a permission mechanism — they characterize the declared vocabulary and
the evaluator's behaviour so both can be inspected and drawn.

Three families of helpers are provided:

* :func:`signal_inventory` — aggregate declared marker and counter-signal
  counts across a registry (the signal vocabulary, not its fulfilment);
* :func:`horizon_distribution` — an interpretive grouping of aspirations by
  the temporal reach of their horizons, declared in :data:`HORIZON_BANDS`;
* :func:`temporal_currentness_sweep` — a replay of one fully-marked entry
  through the real evaluator across a range of observation ages, exposing
  the ``TOWARD`` → ``INQUIRY`` currentness boundary; and
* :func:`report_overview` — a per-status regrouping of an existing
  :class:`~golden_line.models.HorizonReport` with intake and ignored-token
  totals, so a batch can be characterized without re-parsing findings.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date, timedelta

from .models import Aspiration, HorizonEntry, HorizonReport, HorizonStatus
from .progress import progress_report
from .registry import GOLDEN_ASPIRATIONS, find_aspiration


@dataclass(frozen=True)
class SignalCount:
    """Declared signal counts for one aspiration; reachability, not performance."""

    aspiration_id: str
    horizon: str
    marker_count: int
    counter_signal_count: int


@dataclass(frozen=True)
class SignalInventory:
    """Aggregate declared-signal counts across a registry.

    ``unique_markers`` and ``unique_counter_signals`` count distinct token
    strings; when they equal the totals, no declared token is shared between
    aspirations. The inventory describes the vocabulary the evaluator can
    match against — it says nothing about what has been observed.
    """

    rows: tuple[SignalCount, ...]
    total_markers: int
    total_counter_signals: int
    unique_markers: int
    unique_counter_signals: int


def signal_inventory(
    aspirations: tuple[Aspiration, ...] = GOLDEN_ASPIRATIONS,
) -> SignalInventory:
    """Tally declared markers and counter-signals across ``aspirations``.

    The result is pure over the input tuple and preserves registry order.
    """
    rows = tuple(
        SignalCount(
            aspiration_id=item.id,
            horizon=item.horizon,
            marker_count=len(item.markers),
            counter_signal_count=len(item.counter_signals),
        )
        for item in aspirations
    )
    all_markers = [token for item in aspirations for token in item.markers]
    all_counters = [token for item in aspirations for token in item.counter_signals]
    return SignalInventory(
        rows=rows,
        total_markers=len(all_markers),
        total_counter_signals=len(all_counters),
        unique_markers=len(set(all_markers)),
        unique_counter_signals=len(set(all_counters)),
    )


#: Interpretive grouping of the registry's horizon phrases by temporal reach.
#: The bands are declared here, in the analysis layer — they are not part of
#: the registry contract, and their order (narrowing to widening reach) is a
#: reading aid, never a ranking of importance or merit.
HORIZON_BANDS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("immediate", ("next decision",)),
    ("recurring cycle", ("revision cycle", "tool turnover")),
    (
        "at handoff",
        (
            "next learner",
            "collaborator or public reader",
            "public claim",
            "shared pool",
        ),
    ),
    ("open-ended", ("long horizon", "multi-year inquiry")),
)


@dataclass(frozen=True)
class HorizonBand:
    """One temporal-reach band with its horizons and member aspirations."""

    band: str
    horizons: tuple[str, ...]
    aspiration_ids: tuple[str, ...]


def horizon_distribution(
    aspirations: tuple[Aspiration, ...] = GOLDEN_ASPIRATIONS,
) -> tuple[HorizonBand, ...]:
    """Group ``aspirations`` into the declared :data:`HORIZON_BANDS`.

    Every band is always present (possibly empty) so the result has a stable
    shape; within a band, aspiration order follows the input registry order.
    An aspiration whose horizon is not classified by :data:`HORIZON_BANDS`
    raises ``ValueError`` — a registry change must force this map to be
    revisited rather than silently dropping an entry.
    """
    classified = {horizon for _, horizons in HORIZON_BANDS for horizon in horizons}
    for item in aspirations:
        if item.horizon not in classified:
            raise ValueError(
                f"horizon '{item.horizon}' of aspiration '{item.id}' is not "
                "classified in HORIZON_BANDS; update the band map deliberately"
            )
    return tuple(
        HorizonBand(
            band=band,
            horizons=horizons,
            aspiration_ids=tuple(
                item.id for item in aspirations if item.horizon in horizons
            ),
        )
        for band, horizons in HORIZON_BANDS
    )


@dataclass(frozen=True)
class SweepPoint:
    """The evaluator's reading for one observation age in a sweep."""

    age_days: int
    observed_on: str
    status: HorizonStatus
    stale: bool
    date_issue: bool


def _sweep_review_date(as_of: str | date) -> date:
    """Resolve the sweep's review date; sweeps never default to today."""
    if isinstance(as_of, str):
        return date.fromisoformat(as_of)
    if isinstance(as_of, date):
        return as_of
    raise TypeError("as_of must be an ISO date string or a date")


def temporal_currentness_sweep(
    aspiration_id: str,
    ages: Sequence[int],
    *,
    as_of: str | date,
    stale_after_days: int,
    aspirations: tuple[Aspiration, ...] = GOLDEN_ASPIRATIONS,
) -> tuple[SweepPoint, ...]:
    """Replay one fully-marked entry through the evaluator across ``ages``.

    For each age in ``ages`` (days before ``as_of``; negative ages produce
    future-dated observations) a fully-marked, counter-signal-free entry for
    ``aspiration_id`` is evaluated by the real public
    :func:`~golden_line.progress.progress_report` with temporal review
    enabled. The returned trajectory shows where the reading flips from
    ``TOWARD`` to ``INQUIRY`` as currentness is lost — the sweep observes the
    evaluator, it never re-implements or overrides it.

    ``as_of`` is required so the sweep is reproducible; ``aspiration_id``
    must exist in ``aspirations`` or ``ValueError`` is raised.
    """
    aspiration = find_aspiration(aspiration_id, aspirations)
    if aspiration is None:
        raise ValueError(f"unknown aspiration id: '{aspiration_id}'")
    review_date = _sweep_review_date(as_of)

    points: list[SweepPoint] = []
    for age in ages:
        observed_on = (review_date - timedelta(days=int(age))).isoformat()
        entry = HorizonEntry(
            aspiration_id=aspiration.id,
            observed_markers=frozenset(aspiration.markers),
            observed_on=observed_on,
        )
        report = progress_report(
            [entry],
            (aspiration,),
            as_of=review_date,
            stale_after_days=stale_after_days,
        )
        finding = report.findings[0]
        points.append(
            SweepPoint(
                age_days=int(age),
                observed_on=observed_on,
                status=finding.status,
                stale=finding.stale,
                date_issue=finding.date_issue,
            )
        )
    return tuple(points)


@dataclass(frozen=True)
class ReportOverview:
    """Per-status groupings and intake totals for one report; not a grade.

    ``by_status`` maps every status value (in enum order, always all four
    keys) to the aspiration ids that received that reading. The totals count
    ignored undeclared tokens, temporal flags, and intake notes across the
    whole report so a batch can be characterized without re-parsing prose.
    """

    by_status: dict[str, tuple[str, ...]]
    ignored_marker_total: int
    ignored_counter_signal_total: int
    stale_count: int
    date_issue_count: int
    intake_note_count: int


def report_overview(report: HorizonReport) -> ReportOverview:
    """Regroup an existing :class:`HorizonReport` by status with intake totals.

    Purely derived from the report's structured fields; it adds no claim the
    findings did not already carry.
    """
    by_status: dict[str, list[str]] = {status.value: [] for status in HorizonStatus}
    ignored_markers = 0
    ignored_counters = 0
    stale_count = 0
    date_issue_count = 0
    for finding in report.findings:
        by_status[finding.status.value].append(finding.aspiration_id)
        ignored_markers += len(finding.ignored_markers)
        ignored_counters += len(finding.ignored_counter_signals)
        stale_count += int(finding.stale)
        date_issue_count += int(finding.date_issue)
    return ReportOverview(
        by_status={status: tuple(ids) for status, ids in by_status.items()},
        ignored_marker_total=ignored_markers,
        ignored_counter_signal_total=ignored_counters,
        stale_count=stale_count,
        date_issue_count=date_issue_count,
        intake_note_count=len(report.intake_notes),
    )
