"""Types for the Golden Line's horizon records."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class HorizonStatus(str, Enum):
    TOWARD = "TOWARD"
    INQUIRY = "INQUIRY"
    DRIFTING = "DRIFTING"
    NOT_OBSERVED = "NOT_OBSERVED"


@dataclass(frozen=True)
class Aspiration:
    """One entry in the aspiration registry.

    ``markers`` are observable signs of movement toward the aspiration;
    ``counter_signals`` are observable signs of movement away from it. Both
    describe a record, not a person.
    """

    id: str
    title: str
    thread: str
    horizon: str
    markers: tuple[str, ...]
    counter_signals: tuple[str, ...]

    def canonical(self) -> dict[str, object]:
        return {
            "id": self.id,
            "title": self.title,
            "thread": self.thread,
            "horizon": self.horizon,
            "markers": list(self.markers),
            "counter_signals": list(self.counter_signals),
        }


@dataclass(frozen=True)
class HorizonEntry:
    """One dated observation against a single aspiration.

    ``observed_on`` is an optional ISO date (``YYYY-MM-DD``). It is only
    consulted when the caller enables temporal review; a missing or malformed
    date is noted in the finding's reasons rather than raised.
    """

    aspiration_id: str
    observed_markers: frozenset[str] = frozenset()
    counter_signals: frozenset[str] = frozenset()
    note: str = ""
    observed_on: str = ""


@dataclass(frozen=True)
class HorizonFinding:
    """The directional reading for one aspiration, with its full reasons trail.

    ``observed`` lists the declared markers actually seen; ``unmet`` lists the
    declared markers not yet seen. ``countered`` and the ignored-token fields
    expose the other matching results so a consumer never has to parse prose
    in ``reasons`` to understand the derivation.
    """

    aspiration_id: str
    status: HorizonStatus
    reasons: tuple[str, ...]
    observed: tuple[str, ...] = ()
    unmet: tuple[str, ...] = ()
    countered: tuple[str, ...] = ()
    ignored_markers: tuple[str, ...] = ()
    ignored_counter_signals: tuple[str, ...] = ()
    note: str = ""
    observed_on: str = ""
    stale: bool = False
    date_issue: bool = False


@dataclass(frozen=True)
class HorizonReport:
    """A full directional report plus provenance and intake notes.

    ``registry_version`` and ``registry_digest`` identify the registry that
    supplied the vocabulary. ``as_of`` and ``stale_after_days`` identify the
    optional temporal review context. They are metadata, not a score.
    """

    findings: tuple[HorizonFinding, ...]
    intake_notes: tuple[str, ...] = ()
    registry_version: str = ""
    registry_digest: str = ""
    as_of: str = ""
    stale_after_days: int | None = None

    def counts(self) -> dict[str, int]:
        """Tally findings per status value; a summary, not a score."""
        tally = {status.value: 0 for status in HorizonStatus}
        for finding in self.findings:
            tally[finding.status.value] += 1
        return tally
