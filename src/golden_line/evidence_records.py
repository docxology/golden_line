import json
from dataclasses import asdict, dataclass

from .registry import GOLDEN_ASPIRATIONS
from .validation import MAX_COLLECTION_SIZE

EVIDENCE_SCHEMA = "golden-line.evidence/1.0"


@dataclass(frozen=True)
class ObservationProvenance:
    observation_ref: str
    aspiration_id: str
    authorship: str
    source_refs: tuple[str, ...]
    observer_role: str
    collection_method: str
    review_scope: str
    token_sources: tuple[tuple[str, tuple[str, ...]], ...] = ()
    contests: tuple[str, ...] = ()
    supersedes: tuple[str, ...] = ()


@dataclass(frozen=True)
class AspirationConflict:
    record_id: str
    aspiration_ids: tuple[str, ...]
    affected_perspectives: tuple[str, ...]
    unresolved_alternatives: tuple[str, ...]
    decision_owner: str
    review_note: str
    related_instruments: tuple[str, ...] = ()


def _text(value: object, name: str) -> None:
    if type(value) is not str or not value.strip():
        raise ValueError(f"{name} must be nonblank text")


def _texts(value: object, name: str, *, required: bool = False) -> None:
    if (
        type(value) is not tuple
        or len(value) > MAX_COLLECTION_SIZE
        or (required and not value)
    ):
        raise ValueError(f"{name} must be a finite tuple")
    for item in value:
        _text(item, name)


def canonical_evidence_records(
    observations: tuple[ObservationProvenance, ...] = (),
    conflicts: tuple[AspirationConflict, ...] = (),
) -> str:
    """Export optional human evidence records without evaluating disagreement.

    References identify claims and sources; their contents remain unverified.
    These records never enter progress_report or override another instrument.
    A decision_owner names the human review role, not a machine authorization.
    """
    registry = {item.id: item for item in GOLDEN_ASPIRATIONS}
    seen: set[str] = set()
    if (
        type(observations) is not tuple
        or type(conflicts) is not tuple
        or max(len(observations), len(conflicts)) > MAX_COLLECTION_SIZE
    ):
        raise ValueError("evidence records must be finite tuples")
    for observation in observations:
        if type(observation) is not ObservationProvenance:
            raise ValueError("expected ObservationProvenance")
        for name in (
            "observation_ref",
            "observer_role",
            "collection_method",
            "review_scope",
        ):
            _text(getattr(observation, name), name)
        if observation.observation_ref in seen:
            raise ValueError("duplicate observation_ref")
        seen.add(observation.observation_ref)
        if (
            type(observation.aspiration_id) is not str
            or observation.aspiration_id not in registry
        ):
            raise ValueError("unknown aspiration_id")
        if observation.authorship not in (
            "self_report",
            "independent_observation",
            "unspecified",
        ):
            raise ValueError("unsupported authorship")
        for name in ("source_refs", "contests", "supersedes"):
            _texts(getattr(observation, name), name)
        if (
            type(observation.token_sources) is not tuple
            or len(observation.token_sources) > MAX_COLLECTION_SIZE
        ):
            raise ValueError("token_sources must be a finite tuple")
        aspiration = registry[observation.aspiration_id]
        tokens_seen: set[str] = set()
        for pair in observation.token_sources:
            if type(pair) is not tuple or len(pair) != 2:
                raise ValueError("invalid token_sources pair")
            token, refs = pair
            _text(token, "token")
            if (
                token not in (*aspiration.markers, *aspiration.counter_signals)
                or token in tokens_seen
            ):
                raise ValueError("unknown or duplicate token_sources token")
            tokens_seen.add(token)
            _texts(refs, "token source refs", required=True)
            if not set(refs) <= set(observation.source_refs):
                raise ValueError("token references must be declared source_refs")
    conflict_ids: set[str] = set()
    for conflict in conflicts:
        if type(conflict) is not AspirationConflict:
            raise ValueError("expected AspirationConflict")
        for name in ("record_id", "decision_owner", "review_note"):
            _text(getattr(conflict, name), name)
        if conflict.record_id in conflict_ids:
            raise ValueError("duplicate conflict record_id")
        conflict_ids.add(conflict.record_id)
        for name in (
            "aspiration_ids",
            "affected_perspectives",
            "unresolved_alternatives",
        ):
            _texts(getattr(conflict, name), name, required=True)
        if len(set(conflict.aspiration_ids)) != len(conflict.aspiration_ids) or not set(
            conflict.aspiration_ids
        ) <= set(registry):
            raise ValueError(
                "conflict aspiration_ids must be distinct declared identifiers"
            )
        _texts(conflict.related_instruments, "related_instruments")
    return json.dumps(
        {
            "schema_version": EVIDENCE_SCHEMA,
            "source_content_verified": False,
            "grants_permission": False,
            "observations": [asdict(item) for item in observations],
            "conflicts": [asdict(item) for item in conflicts],
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def worked_evidence_records() -> tuple[
    tuple[ObservationProvenance, ...], tuple[AspirationConflict, ...]
]:
    observations = (
        ObservationProvenance(
            "example:self-report",
            "useful-to-others",
            "self_report",
            ("example:handoff-note",),
            "author",
            "self-reported handoff note",
            "one handoff; no independent verification",
            (("handoff used", ("example:handoff-note",)),),
        ),
        ObservationProvenance(
            "example:contestation",
            "useful-to-others",
            "independent_observation",
            ("example:recipient-note",),
            "recipient",
            "recorded recipient disagreement",
            "same handoff; source contents unverified",
            contests=("example:self-report",),
        ),
    )
    conflicts = (
        AspirationConflict(
            "example:commons-confidentiality",
            ("commons-returned",),
            ("contributors seeking reuse", "collaborator requiring confidentiality"),
            ("release a redacted method", "withhold sensitive material"),
            "human collaboration steward",
            "Unresolved commons return versus confidentiality; consent and absence require separate records.",
            (
                "https://github.com/docxology/violet_line",
                "https://github.com/docxology/white_line",
                "https://github.com/docxology/silver_line",
            ),
        ),
        AspirationConflict(
            "example:useful-unhurried",
            ("useful-to-others", "unhurried-questions"),
            (
                "reader awaiting a useful handoff",
                "researcher protecting exploratory time",
            ),
            ("publish a bounded interim handoff", "continue inquiry before transfer"),
            "human inquiry owner",
            "Usefulness and unhurried inquiry remain in tension; no automatic priority.",
        ),
        AspirationConflict(
            "example:flourishing-local-effects",
            ("wide-human-flourishing",),
            (
                "people anticipating broad benefit",
                "local participants describing adverse effects",
            ),
            (
                "revise the proposal with affected participants",
                "pause the proposed application",
            ),
            "human affected-party review owner",
            "A flourishing marker cannot cancel locally adverse effects or substitute for consent.",
            ("https://github.com/docxology/violet_line",),
        ),
    )
    return observations, conflicts
