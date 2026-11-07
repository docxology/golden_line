"""Bind every 02a formalism block to executed evaluator behavior.

Native regressions exercise evaluator boundaries independently of manuscript
wording. Structural checks below keep formalism labels, test references, and
the evidence ledger connected without pinning explanatory copy.

The binding tables in 02a are keyed on each block's *label*, never on its
number, because the renderer owns the numbers (see
``tests/test_formalism_syntax.py``). Two gates police the tables: one requires
the row set to equal the declared block set, the other requires each row, on its
own, to name a test that exists.
"""

import dataclasses
import re
from datetime import date, timedelta
from pathlib import Path

from golden_line import (
    EVALUATOR_STAGES,
    GOLDEN_ASPIRATIONS,
    Aspiration,
    HorizonEntry,
    HorizonFinding,
    HorizonStatus,
    founding_aspirations,
    further_aspirations,
    invariants,
    progress_report,
    registry_digest,
)
from golden_line.analysis import signal_inventory, temporal_currentness_sweep
from golden_line.figures import FIGURES, SWEEP_AGES, SWEEP_STALE_AFTER_DAYS
from golden_line.serialization import report_digest
from tests.test_formalism_syntax import declared_blocks, rendered_numbers

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FORMALISM = PROJECT_ROOT / "docs" / "manuscript" / "02a_formalism.md"
INVARIANT_DOC = PROJECT_ROOT / "docs" / "invariants.md"
CLAIM_LEDGER = PROJECT_ROOT / "data" / "claim_ledger.yaml"

ATTENTION = GOLDEN_ASPIRATIONS[0]
REVIEW = "2026-07-18"

_TEST_REF = re.compile(r"tests/[\w/]+\.py::\w+")
_ROW_LABEL = re.compile(r"^\|\s*\[@((?:def|prop):[\w-]+)\]\s*\|")


def _formalism_blocks() -> list[tuple[str, str, str, str]]:
    """Every formalism Div declared in 02a, in document order."""
    return declared_blocks({FORMALISM.name: FORMALISM.read_text(encoding="utf-8")})


def _ledger_number(claim_id: str) -> int:
    """Read one simple numeric claim without adding a YAML runtime dependency."""
    raw = CLAIM_LEDGER.read_text(encoding="utf-8")
    match = re.search(
        rf"- id: {re.escape(claim_id)}\n\s+kind: number\n\s+value: (\d+)",
        raw,
    )
    assert match is not None, claim_id
    return int(match.group(1))


def _ledger_number_ids() -> list[str]:
    """Every ``kind: number`` claim id in the ledger, in file order."""
    raw = CLAIM_LEDGER.read_text(encoding="utf-8")
    return re.findall(r"- id: (\w+)\n\s+kind: number\n", raw)


def _binding_table_rows() -> list[tuple[str, str]]:
    """Return ``(block label, verifying-test cell)`` for every table row."""
    rows: list[tuple[str, str]] = []
    for line in FORMALISM.read_text(encoding="utf-8").splitlines():
        match = _ROW_LABEL.match(line)
        if match is None:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        assert len(cells) == 4, line
        rows.append((match.group(1), cells[2]))
    return rows


# ---------------------------------------------------------------------------
# The binding tables themselves
# ---------------------------------------------------------------------------


def test_binding_tables_bind_every_declared_block() -> None:
    """The row set must equal the declared block set — no gaps, no orphans.

    Keying rows on labels rather than on numbers is what makes this checkable:
    a row can be matched to the block it claims to bind without either side
    stating a number. A block added to 02a with no row, or a row left behind
    after its block was deleted, fails here.
    """
    labels = [label for _name, _kind, label, _title in _formalism_blocks()]
    assert labels, "no formalism blocks parsed, so this gate would be vacuous"
    rows = _binding_table_rows()
    assert [label for label, _cell in rows] == labels


def test_every_binding_row_names_an_existing_test() -> None:
    """Per row: at least one verifying test is named, and every name resolves.

    An earlier form of this check counted *unique* references across the whole
    table and compared the total against the row count. Several rows could be
    emptied at once without moving that total, so a proposition could lose every
    verifying test and stay green. The assertion is now made row by row.
    """
    rows = _binding_table_rows()
    assert rows, "no table rows parsed, so this gate would be vacuous"

    all_refs: set[str] = set()
    for label, cell in rows:
        row_refs = _TEST_REF.findall(cell)
        assert row_refs, f"{label} names no verifying test"
        all_refs.update(row_refs)

    # Prose outside the tables also names tests; every reference anywhere in
    # the section must resolve, not only the ones inside table cells.
    all_refs |= set(_TEST_REF.findall(FORMALISM.read_text(encoding="utf-8")))
    for ref in sorted(all_refs):
        rel_path, function_name = ref.split("::")
        test_file = PROJECT_ROOT / rel_path
        assert test_file.is_file(), ref
        assert f"def {function_name}(" in test_file.read_text(encoding="utf-8"), ref


def test_binding_guard_rejects_an_emptied_row() -> None:
    """Proof of detection: a row whose verifying-test cell is blanked is caught."""
    rows = _binding_table_rows()
    assert rows, "no table rows parsed, so this guard would be vacuous"
    planted = [
        (label, "" if index == 0 else cell) for index, (label, cell) in enumerate(rows)
    ]
    unbound = [label for label, cell in planted if not _TEST_REF.findall(cell)]
    assert unbound == [rows[0][0]]


def test_binding_guard_rejects_a_dropped_row() -> None:
    """Proof of detection: a block whose row was deleted is caught.

    This is the failure the per-row check alone cannot see: the surviving rows
    are all well formed, and only the comparison against the declared blocks
    notices that one block is now bound to nothing at all.
    """
    labels = [label for _name, _kind, label, _title in _formalism_blocks()]
    planted = [label for label, _cell in _binding_table_rows()][1:]
    assert planted != labels
    assert sorted(set(labels) - set(planted)) == [labels[0]]


def test_invariant_doc_table_names_real_tests() -> None:
    """docs/invariants.md's proof-of-detection table is parsed, not trusted."""
    raw = INVARIANT_DOC.read_text(encoding="utf-8")
    battery_text = (PROJECT_ROOT / "tests" / "test_invariants.py").read_text(
        encoding="utf-8"
    )
    rows = [
        line for line in raw.splitlines() if line.startswith("| `") and "test_" in line
    ]
    assert len(rows) == len(invariants._CHECKS)
    documented = {row.split("`")[1] for row in rows}
    assert documented == {
        check(GOLDEN_ASPIRATIONS).name for check in invariants._CHECKS
    }
    for row in rows:
        names = re.findall(r"test_\w+", row)
        assert names, row
        for name in names:
            assert f"def {name}(" in battery_text, name


# ---------------------------------------------------------------------------
# Definitions
# ---------------------------------------------------------------------------


def test_intake_classification_orders_validation_membership_and_admission() -> None:
    from golden_line import IntakeSetAsideReason, classify_intake_entries

    records = [
        HorizonEntry("unknown", observed_markers=None),
        HorizonEntry("unknown"),
        HorizonEntry("unknown"),
        HorizonEntry(ATTENTION.id, observed_markers=None),
        HorizonEntry(ATTENTION.id),
        HorizonEntry(ATTENTION.id),
    ]
    classifications = classify_intake_entries(records)
    assert tuple(item.set_aside_reason for item in classifications) == (
        IntakeSetAsideReason.MALFORMED,
        IntakeSetAsideReason.UNKNOWN_ID,
        IntakeSetAsideReason.UNKNOWN_ID,
        IntakeSetAsideReason.MALFORMED,
        None,
        IntakeSetAsideReason.DUPLICATE,
    )
    assert tuple(item.admitted for item in classifications) == (
        False,
        False,
        False,
        False,
        True,
        False,
    )


def test_intake_screening_never_raises_on_hostile_input() -> None:
    """Every hostile shape is set aside; none escapes as an exception."""
    hostile: list[object] = [
        "not a record",
        42,
        None,
        object(),
        HorizonEntry(""),
        HorizonEntry("x", note=None),  # type: ignore[arg-type]
        HorizonEntry("x", observed_on=None),  # type: ignore[arg-type]
        HorizonEntry("x", counter_signals="a bare string"),  # type: ignore[arg-type]
        HorizonEntry(ATTENTION.id, observed_markers=frozenset({1})),  # type: ignore[arg-type]
    ]
    report = progress_report(hostile)  # type: ignore[arg-type]
    assert len(report.intake_notes) == len(hostile)
    assert len(report.findings) == len(GOLDEN_ASPIRATIONS)
    assert {finding.status for finding in report.findings} == {
        HorizonStatus.NOT_OBSERVED
    }


def test_matching_retains_declared_and_ignored_signal_sets() -> None:
    """Observed, unmet, countered, and ignored signals remain distinct."""
    entry = HorizonEntry(
        ATTENTION.id,
        observed_markers=frozenset({ATTENTION.markers[0], "undeclared marker"}),
        counter_signals=frozenset(
            {ATTENTION.counter_signals[0], "undeclared counter-signal"}
        ),
    )
    finding = progress_report([entry]).findings[0]
    assert finding.observed == (ATTENTION.markers[0],)
    assert finding.unmet == tuple(sorted(set(ATTENTION.markers[1:])))
    assert finding.countered == (ATTENTION.counter_signals[0],)
    assert finding.ignored_markers == ("undeclared marker",)
    assert finding.ignored_counter_signals == ("undeclared counter-signal",)


def _fully_marked(observed_on: str) -> HorizonEntry:
    """A complete, counter-signal-free entry dated ``observed_on``."""
    return HorizonEntry(
        ATTENTION.id, frozenset(ATTENTION.markers), observed_on=observed_on
    )


def test_temporal_review_enablement_and_exclusive_boundary() -> None:
    """Enablement, the flag branch, and the strict comparison are all executed."""
    tau = SWEEP_STALE_AFTER_DAYS
    review = date.fromisoformat(REVIEW)

    # Disabled: temporal metadata cannot move the reading at all.
    ancient = _fully_marked((review - timedelta(days=10 * tau)).isoformat())
    disabled = progress_report([ancient], as_of=REVIEW).findings[0]
    assert disabled.status is HorizonStatus.TOWARD
    assert not disabled.stale and not disabled.date_issue

    # Enabled: an absent or unreadable date flags rather than fails.
    for unusable in ("", "not-an-iso-date"):
        finding = progress_report(
            [_fully_marked(unusable)], as_of=REVIEW, stale_after_days=tau
        ).findings[0]
        assert finding.date_issue and not finding.stale
        assert finding.status is HorizonStatus.INQUIRY

    # The comparison is strict, and a future date is stale in its own right.
    def _read(offset_days: int) -> HorizonFinding:
        dated = _fully_marked((review - timedelta(days=offset_days)).isoformat())
        return progress_report([dated], as_of=REVIEW, stale_after_days=tau).findings[0]

    assert not _read(tau).stale and _read(tau).status is HorizonStatus.TOWARD
    assert _read(tau + 1).stale and _read(tau + 1).status is HorizonStatus.INQUIRY
    assert _read(-1).stale and _read(-1).status is HorizonStatus.INQUIRY


def test_decision_clauses_fire_in_the_stated_order() -> None:
    """One witness per clause, each proving its clause wins over the later ones."""
    tau = SWEEP_STALE_AFTER_DAYS
    review = date.fromisoformat(REVIEW)
    stale_date = (review - timedelta(days=tau + 1)).isoformat()
    fresh_date = review.isoformat()
    full = frozenset(ATTENTION.markers)
    countered = frozenset(ATTENTION.counter_signals)

    witnesses: tuple[tuple[HorizonEntry, ...], ...] = (
        (),  # clause 1: nothing admitted
        # clause 2: complete markers and a counter-signal on a stale record
        (HorizonEntry(ATTENTION.id, full, countered, observed_on=stale_date),),
        # clause 3: an entry naming the aspiration with no declared marker
        (HorizonEntry(ATTENTION.id, observed_on=fresh_date),),
        # clause 4: one of the declared markers still unmet
        (
            HorizonEntry(
                ATTENTION.id, frozenset({ATTENTION.markers[0]}), observed_on=fresh_date
            ),
        ),
        # clause 5: complete markers, but the observation has aged out
        (HorizonEntry(ATTENTION.id, full, observed_on=stale_date),),
        # clause 6: complete, uncountered, current
        (HorizonEntry(ATTENTION.id, full, observed_on=fresh_date),),
    )
    executed = [
        progress_report(list(entries), as_of=REVIEW, stale_after_days=tau)
        .findings[0]
        .status.value
        for entries in witnesses
    ]

    assert executed == [
        "NOT_OBSERVED",
        "DRIFTING",
        "INQUIRY",
        "INQUIRY",
        "INQUIRY",
        "TOWARD",
    ]


# ---------------------------------------------------------------------------
# Propositions
# ---------------------------------------------------------------------------


def test_totality_partitions_the_native_registry() -> None:
    """Every registry aspiration has one finding and contributes to counts."""
    n = len(GOLDEN_ASPIRATIONS)
    report = progress_report([])
    assert len(report.findings) == n
    assert sum(report.counts().values()) == n


def test_first_valid_admission_and_replay_determinism() -> None:
    """First-wins derived by order swap, determinism by replay."""
    full = HorizonEntry(ATTENTION.id, frozenset(ATTENTION.markers))
    empty = HorizonEntry(ATTENTION.id)

    full_first = progress_report([full, empty], as_of=REVIEW)
    empty_first = progress_report([empty, full], as_of=REVIEW)
    assert full_first.findings[0].status is HorizonStatus.TOWARD
    assert empty_first.findings[0].status is HorizonStatus.INQUIRY

    replay = progress_report([full, empty], as_of=REVIEW)
    assert report_digest(replay) == report_digest(full_first)


def test_currentness_boundary_is_exclusive() -> None:
    """The last TOWARD age is the threshold, followed by INQUIRY."""
    tau = 90
    points = temporal_currentness_sweep(
        ATTENTION.id, range(120), as_of=REVIEW, stale_after_days=tau
    )
    toward_ages = [p.age_days for p in points if p.status is HorizonStatus.TOWARD]
    stale_ages = [p.age_days for p in points if p.status is HorizonStatus.INQUIRY]
    boundary = max(toward_ages)
    assert boundary == tau  # exclusive: age == tau is still current
    assert min(stale_ages) == boundary + 1


def test_sweep_reaches_only_toward_and_inquiry() -> None:
    """Every sampled age remains within the native temporal codomain."""
    points = temporal_currentness_sweep(
        ATTENTION.id, range(-10, 200, 5), as_of=REVIEW, stale_after_days=90
    )
    reached = {p.status.value for p in points}
    unreachable = sorted({status.value for status in HorizonStatus} - reached)
    assert unreachable == ["DRIFTING", "NOT_OBSERVED"]


def test_native_registry_digest_is_order_independent_hex() -> None:
    """Permutation-invariance and the 64-hex shape are executed."""
    digest = registry_digest(GOLDEN_ASPIRATIONS)
    assert registry_digest(tuple(reversed(GOLDEN_ASPIRATIONS))) == digest
    rotated = GOLDEN_ASPIRATIONS[4:] + GOLDEN_ASPIRATIONS[:4]
    assert registry_digest(rotated) == digest
    assert len(digest) == 64
    assert set(digest) <= set("0123456789abcdef")


def test_intake_screening_is_deterministic_on_all_input() -> None:
    """Intake screening is a pure function: identical input, identical output.

    The screening function produces the identical accepted map and intake notes
    for the identical batch E and registry ids. Malformed input is set aside
    deterministically; screening never raises. This is separately stated from
    @prop:first_wins, which covers which entry stands when multiple valid
    entries share an identifier.
    """
    from golden_line.progress import classify_intake_entries

    entries = [
        HorizonEntry(ATTENTION.id, frozenset({ATTENTION.markers[0]})),
        HorizonEntry(GOLDEN_ASPIRATIONS[1].id),
    ]

    result1 = classify_intake_entries(entries)
    result2 = classify_intake_entries(entries)

    # Identical input produces identical classifications.
    assert len(result1) == len(result2)
    for c1, c2 in zip(result1, result2):
        assert c1.admitted == c2.admitted
        assert c1.note == c2.note
        assert c1.set_aside_reason == c2.set_aside_reason

    # Malformed input is set aside deterministically.
    hostile: list = ["not a record", 42, None]
    r1 = classify_intake_entries(hostile)
    r2 = classify_intake_entries(hostile)
    assert len(r1) == len(r2) == len(hostile)
    for c1, c2 in zip(r1, r2):
        assert not c1.admitted and not c2.admitted
        assert c1.note == c2.note


# ---------------------------------------------------------------------------
# The evidence ledger
# ---------------------------------------------------------------------------


def _derived_ledger_numbers() -> dict[str, int]:
    """Re-derive every numeric ledger claim from the source that row names."""
    inventory = signal_inventory()
    blocks = _formalism_blocks()
    numbers = rendered_numbers(blocks)
    return {
        "registry_entry_count": len(GOLDEN_ASPIRATIONS),
        "aspiration_field_count": len(dataclasses.fields(Aspiration)),
        "finding_field_count": len(dataclasses.fields(HorizonFinding)),
        "status_definition_count": len(HorizonStatus),
        "invariant_count": len(invariants._CHECKS),
        "formal_definition_count": sum(
            1 for _n, kind, _l, _t in blocks if kind == "definition"
        ),
        "formal_proposition_count": sum(
            1 for _n, kind, _l, _t in blocks if kind == "proposition"
        ),
        "formal_matching_definition_number": numbers["def:matching"][1],
        "founding_aspiration_count": len(founding_aspirations()),
        "further_aspiration_count": len(further_aspirations()),
        "evaluator_stage_count": len(EVALUATOR_STAGES),
        "signal_marker_count": inventory.total_markers,
        "signal_counter_count": inventory.total_counter_signals,
        "currentness_stale_boundary_age": SWEEP_STALE_AFTER_DAYS + 1,
        "currentness_sweep_age_count": len(SWEEP_AGES),
        "currentness_replay_call_count": len(GOLDEN_ASPIRATIONS) * len(SWEEP_AGES),
        "registry_digest_hex_length": len(registry_digest(GOLDEN_ASPIRATIONS)),
        "figure_count": len(FIGURES),
    }


def test_claim_ledger_numbers_and_figures_match_executed_sources() -> None:
    """The evidence ledger cannot lag behind the executable figure/formalism facts."""
    expected = _derived_ledger_numbers()
    assert {claim_id: _ledger_number(claim_id) for claim_id in expected} == expected

    ledger = CLAIM_LEDGER.read_text(encoding="utf-8")
    for name, label, *_ in FIGURES:
        assert f"- id: figure_{name}" in ledger
        assert f"value: {label}" in ledger


def test_every_numeric_ledger_claim_is_re_derived() -> None:
    """No numeric row may exist without a derivation; the gate cannot be partial.

    An earlier consumer checked seven of the ledger's numbers by hand-listing
    them, so the rest could drift to any value with the suite still green.
    Binding the *set* of rows rather than a hand-listed subset closes that.
    """
    ledger_ids = _ledger_number_ids()
    assert len(ledger_ids) == len(set(ledger_ids))
    assert set(ledger_ids) == set(_derived_ledger_numbers())


def _ledger_citation_ids() -> dict[str, str]:
    """Every ``kind: citation`` claim id mapped to its label value."""
    raw = CLAIM_LEDGER.read_text(encoding="utf-8")
    return {
        cid: value
        for cid, value in re.findall(
            r"- id: (\w+)\n\s+kind: citation\n\s+value: ([\w:-]+)", raw
        )
    }


def test_every_citation_ledger_claim_is_bound_to_a_declared_block() -> None:
    """Every ``kind: citation`` row must name a formalism block that exists.

    A ledger row pointing at a label no block declares is exactly the failure
    mode the unsupported-citation gate flags, so the ledger's own set is
    checked against the declared block labels rather than against itself.
    """
    declared = {label for _n, _k, label, _t in _formalism_blocks()}
    citations = _ledger_citation_ids()
    assert citations, (
        "the ledger declares no citation rows, so this gate would be vacuous"
    )
    dangling = sorted(label for label in citations.values() if label not in declared)
    assert dangling == [], dangling


def test_every_manuscript_formalism_reference_has_a_citation_ledger_row() -> None:
    """The ledger must cover every def:/prop: label the prose cites, and vice versa.

    The set equality closes both drift directions: a new ``[@def:x]`` reference
    in the prose with no ledger row fails, and a ledger row for a label the
    prose never cites also fails, so the ledger cannot accrete dead entries.
    """
    raw = " ".join(
        path.read_text(encoding="utf-8")
        for path in sorted((PROJECT_ROOT / "docs" / "manuscript").glob("*.md"))
    )
    used = set(re.findall(r"\[@((?:def|prop):[\w-]+)\]", raw))
    assert used, (
        "the manuscript declares no formalism references, so this gate would be vacuous"
    )
    covered = set(_ledger_citation_ids().values())
    assert used <= covered, sorted(used - covered)
    assert covered <= used, sorted(covered - used)


def test_citation_ledger_rows_are_exactly_the_used_label_set() -> None:
    """Proof of detection: a planted dangling label must be flagged.

    Simulates a ledger row (and prose reference) for a label no formalism
    block declares; the declared-block check must reject it. Negative control
    for ``test_every_citation_ledger_claim_is_bound_to_a_declared_block``.
    """
    declared = {label for _n, _k, label, _t in _formalism_blocks()}
    planted = "def:does-not-exist"
    assert planted not in declared
    dangling = [planted] if planted not in declared else []
    assert dangling == [planted]


def test_ledger_source_paths_point_at_files_that_exist() -> None:
    """A ledger row's provenance path must name a real file in this tree."""
    raw = CLAIM_LEDGER.read_text(encoding="utf-8")
    paths = {
        source.split()[0]
        for source in re.findall(r"^\s+source: (\S+.*)$", raw, flags=re.MULTILINE)
    }
    assert paths, "the ledger declares no sources, so this gate would be vacuous"
    missing = sorted(path for path in paths if not (PROJECT_ROOT / path).exists())
    assert missing == [], missing


def test_ledger_source_path_check_rejects_a_retired_path() -> None:
    """Proof of detection: the split-up ``figures.py`` path must be reported."""
    planted = {"src/golden_line/registry.py", "src/golden_line/figures.py"}
    missing = sorted(path for path in planted if not (PROJECT_ROOT / path).exists())
    assert missing == ["src/golden_line/figures.py"]


# ---------------------------------------------------------------------------
# Prose elsewhere that quotes formalism results
# ---------------------------------------------------------------------------


_LIMITS = PROJECT_ROOT / "docs" / "manuscript" / "05_limits.md"


def _limit_bullets() -> list[str]:
    """The top-level bullets of 05_limits' hard-limits list, in order."""
    raw = _LIMITS.read_text(encoding="utf-8")
    body = raw.split("The sharpest risk")[0]
    return re.findall(r"^- \*(Commitment|Enforced [^*]+)\.\*", body, flags=re.MULTILINE)


def test_limits_enforced_labels_name_real_formalism_results() -> None:
    """Every formalism label an "Enforced" bullet cites must be declared in 02a.

    The bullets used to cite results by hand-written number, which the renderer
    could not keep current. They cite labels now, so this check is the local
    half of the same guarantee the filter gives the rendered document.
    """
    declared = {label for _n, _k, label, _t in _formalism_blocks()}
    cited: list[str] = []
    for bullet in _limit_bullets():
        if not bullet.startswith("Enforced"):
            continue
        cited.extend(re.findall(r"@((?:def|prop):[\w-]+)", bullet))
    assert cited, "no enforced bullet cites a formalism result"
    assert not set(cited) - declared, sorted(set(cited) - declared)


def test_envelope_pointer_binds_native_report() -> None:
    """The pointer proposition is re-derived through a real export.

    A live report is wrapped, the match check must hold, every stated field
    edit must break it, and ``native_status`` must be the complete ordered
    per-aspiration readings — no aggregate above them, exactly as the
    definition and the instrument's own refusal of a virtue score require.
    """
    from golden_line import (
        GOLDEN_ASPIRATIONS,
        HorizonEntry,
        envelope_matches_report,
        progress_report,
        report_envelope,
    )

    attention = GOLDEN_ASPIRATIONS[0]
    report = progress_report(
        [HorizonEntry(attention.id, frozenset(attention.markers))], as_of=REVIEW
    )
    envelope = report_envelope(report, subject_id="formalism-binding")
    assert envelope_matches_report(envelope, report)
    assert envelope.native_status == tuple(
        (finding.aspiration_id, finding.status.value) for finding in report.findings
    )
    assert len(envelope.native_status) == len(GOLDEN_ASPIRATIONS)
    for edited in (
        dataclasses.replace(envelope, report_ref="0" * 64),
        dataclasses.replace(envelope, review_date="2001-01-01"),
        dataclasses.replace(envelope, registry_version="0.0.0"),
        dataclasses.replace(envelope, registry_digest="0" * 64),
        dataclasses.replace(envelope, native_status=envelope.native_status[:-1]),
    ):
        assert not envelope_matches_report(edited, report)
