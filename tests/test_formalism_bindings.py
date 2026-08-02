"""Bind every 02a formalism block to executed evaluator behavior.

Each test here first *derives* a constant, a field list, or a clause ordering by
running the real code, then asserts the manuscript states exactly that.
Corrupting a definition or proposition in the manuscript makes the matching test
fail; corrupting the code makes the derivation assertions fail. Nothing is
asserted that was not first executed.

The binding tables in 02a are keyed on each block's *label*, never on its
number, because the renderer owns the numbers (see
``tests/test_formalism_syntax.py``). Two gates police the tables: one requires
the row set to equal the declared block set, the other requires each row, on its
own, to name a test that exists.
"""

import dataclasses
import inspect
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
from golden_line.analysis import signal_inventory
from golden_line.analysis import temporal_currentness_sweep
from golden_line.figures import FIGURES, SWEEP_AGES, SWEEP_STALE_AFTER_DAYS
from golden_line.serialization import report_digest
from tests.test_formalism_syntax import declared_blocks, rendered_numbers

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FORMALISM = PROJECT_ROOT / "manuscript" / "02a_formalism.md"
INVARIANT_DOC = PROJECT_ROOT / "docs" / "invariants.md"
CLAIM_LEDGER = PROJECT_ROOT / "data" / "claim_ledger.yaml"

ATTENTION = GOLDEN_ASPIRATIONS[0]
REVIEW = "2026-07-18"

_TEST_REF = re.compile(r"tests/[\w/]+\.py::\w+")
_ROW_LABEL = re.compile(r"^\|\s*\[@((?:def|prop):[\w-]+)\]\s*\|")

_COUNT_WORDS = {
    0: "Zero",
    1: "One",
    2: "Two",
    3: "Three",
    4: "Four",
    5: "Five",
    6: "Six",
    7: "Seven",
    8: "Eight",
    9: "Nine",
    10: "Ten",
    11: "Eleven",
    12: "Twelve",
    13: "Thirteen",
}


def _normalized() -> str:
    """Whitespace-normalized manuscript text so bindings survive wrapping."""
    return " ".join(FORMALISM.read_text(encoding="utf-8").split())


def _formalism_blocks() -> list[tuple[str, str, str, str]]:
    """Every formalism Div declared in 02a, in document order."""
    return declared_blocks({FORMALISM.name: FORMALISM.read_text(encoding="utf-8")})


def _tuple_arity(left_hand_side: str) -> int:
    """Count the components of the manuscript tuple ``lhs = (...)``."""
    match = re.search(
        rf"{re.escape(left_hand_side)} = \((?P<body>[^)]*)\)", _normalized()
    )
    assert match is not None, left_hand_side
    return len(re.split(r",\\ ", match.group("body")))


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


def test_aspiration_tuple_matches_the_dataclass() -> None:
    """The aspiration tuple's arity and field names come from ``Aspiration``."""
    fields = [field.name for field in dataclasses.fields(Aspiration)]
    assert _tuple_arity("a") == len(fields)
    text = _normalized()
    for name in fields:
        if name in {"markers", "counter_signals"}:
            continue
        assert "\\mathrm{" + name + "}" in text, name
    assert "$M$ (Markers)" in text
    assert "$C$ (Counter-signals)" in text
    assert f"the {_COUNT_WORDS[len(fields)].lower()}-tuple" in text


def test_registry_definition_matches_the_source_tuple() -> None:
    """Registry size and the founding/further split are read off the source."""
    founding = founding_aspirations()
    further = further_aspirations()
    assert founding + further == GOLDEN_ASPIRATIONS  # founding entries come first
    text = _normalized()
    assert f"aspirations with $n = {len(GOLDEN_ASPIRATIONS)}$" in text
    assert f"{_COUNT_WORDS[len(founding)].lower()} founding aspirations" in text
    assert f"followed by {_COUNT_WORDS[len(further)].lower()} further ones" in text


def test_horizon_entry_tuple_matches_the_dataclass() -> None:
    """The entry tuple's arity, and the optionality of its date, are derived."""
    fields = dataclasses.fields(HorizonEntry)
    assert _tuple_arity("e") == len(fields)
    observed_on = next(field for field in fields if field.name == "observed_on")
    assert observed_on.default == ""  # optional in the code, optional in the prose
    assert "$\\mathrm{d_{obs}}$ is an optional ISO date" in _normalized()


def test_status_codomain_matches_the_enumeration() -> None:
    """$\\Sigma$ is the enumeration, spelled in enum order, and nothing else."""
    values = [status.value for status in HorizonStatus]
    rendered = ",\\ ".join(
        "\\texttt{" + value.replace("_", "\\_") + "}" for value in values
    )
    text = _normalized()
    assert f"\\Sigma = \\{{{rendered}\\}}" in text
    assert f"the {_COUNT_WORDS[len(values)].lower()}-element set" in text


def test_finding_tuple_matches_the_dataclass() -> None:
    """The finding tuple has one component per ``HorizonFinding`` field.

    The manuscript previously pooled the two ignored-token fields into a single
    ``ignored`` component, so the stated tuple was one shorter than the record
    the code returns. The arity is now derived rather than transcribed.
    """
    fields = [field.name for field in dataclasses.fields(HorizonFinding)]
    ignored = [name for name in fields if name.startswith("ignored_")]
    assert len(ignored) == 2
    assert _tuple_arity("f") == len(fields)
    text = _normalized()
    assert "\\mathrm{ign}_M,\\ \\mathrm{ign}_C" in text
    assert (
        f"{_COUNT_WORDS[len(fields)].lower()} fields, ignored markers kept apart"
        in text
    )


def test_report_function_signature_matches_manuscript() -> None:
    """Parameter count, keyword-only names, and stage names are introspected."""
    parameters = list(inspect.signature(progress_report).parameters.values())
    keyword_only = [
        parameter.name
        for parameter in parameters
        if parameter.kind is inspect.Parameter.KEYWORD_ONLY
    ]
    assert keyword_only  # the review context is not positional
    match = re.search(r"progress\\_report\} : \((?P<body>[^)]*)\)", _normalized())
    assert match is not None
    assert len(re.split(r",\\ ", match.group("body"))) == len(parameters)

    text = _normalized()
    assert "$\\mathrm{as\\_of}$ and $\\tau$ are keyword-only" in text
    assert "`stale_after_days`" in text
    assert f"It runs {_COUNT_WORDS[len(EVALUATOR_STAGES)].lower()} stages" in text
    assert ", ".join(EVALUATOR_STAGES[:-1]) + ", and " + EVALUATOR_STAGES[-1] in text


def test_intake_screening_tests_records_in_the_stated_order() -> None:
    """Shape, then registry membership, then prior admission — each derived.

    Every step of the order is shown by a record that would be classified
    differently if the steps were reordered, so the claim is executed rather
    than transcribed from the source's control flow.
    """
    # Shape precedes membership: a malformed record bearing an unknown id is
    # reported as malformed, not as an unknown id.
    malformed_unknown = progress_report(
        [HorizonEntry("not-a-real-id", observed_markers=None)]  # type: ignore[arg-type]
    )
    assert len(malformed_unknown.intake_notes) == 1
    assert "observed_markers must be" in malformed_unknown.intake_notes[0]
    assert "unknown aspiration" not in malformed_unknown.intake_notes[0]

    # Membership precedes prior admission: two entries sharing an *unknown* id
    # are both unknown-id set-asides, never a duplicate.
    repeated_unknown = progress_report(
        [HorizonEntry("not-a-real-id"), HorizonEntry("not-a-real-id")]
    )
    assert len(repeated_unknown.intake_notes) == 2
    assert all("unknown aspiration" in note for note in repeated_unknown.intake_notes)
    assert not any("duplicate" in note for note in repeated_unknown.intake_notes)

    # Notes index submitted records from 1, not from 0.
    indexed = progress_report(["not a record"])  # type: ignore[list-item]
    assert indexed.intake_notes[0].startswith("entry #1 ")

    text = _normalized()
    assert "shape, then registry membership, then prior admission" in text
    assert "indices counted from 1 in the intake notes" in text


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
    assert "Screening never raises on malformed or unexpected input" in _normalized()


def test_matching_set_operations_match_manuscript() -> None:
    """The three matching sets are read off a real finding, then stated."""
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

    text = _normalized()
    assert "\\mathrm{observed}(a,e) = O \\cap M" in text
    assert "\\mathrm{unmet}(a,e) = M \\setminus O" in text
    assert "\\mathrm{countered}(a,e) = K \\cap C" in text
    assert "they can never determine a status" in text


def _fully_marked(observed_on: str) -> HorizonEntry:
    """A complete, counter-signal-free entry dated ``observed_on``."""
    return HorizonEntry(
        ATTENTION.id, frozenset(ATTENTION.markers), observed_on=observed_on
    )


def test_temporal_review_rule_matches_manuscript() -> None:
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

    text = _normalized()
    assert "temporal review is enabled exactly when $\\tau$ is set" in text
    assert "$\\mathrm{d_{obs}} > d$ (a future observation)" in text
    assert "d - \\mathrm{d_{obs}} > \\tau$" in text


def _decision_clause_statuses() -> list[str]:
    """The status each numbered clause of the decision rule terminates in."""
    block = _normalized().split("The status $\\sigma(a, e)$ is determined by")[1]
    block = block.split(":::")[0]
    return [
        name.replace("\\_", "_")
        for name in re.findall(r"\\texttt\{([A-Z\\_]+)\}", block)
    ]


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

    clauses = _decision_clause_statuses()
    assert len(clauses) == len(witnesses), (
        "the decision rule lists a different number of clauses than this test "
        "has witnesses for; add or retire a witness deliberately"
    )
    assert clauses == executed


# ---------------------------------------------------------------------------
# Propositions
# ---------------------------------------------------------------------------


def test_totality_count_matches_manuscript() -> None:
    """Totality's n = 9 is the executed registry and report size."""
    n = len(GOLDEN_ASPIRATIONS)
    report = progress_report([])
    assert len(report.findings) == n
    assert sum(report.counts().values()) == n
    text = _normalized()
    assert f"a report contains $n = {n}$ findings" in text
    assert f"counts partition $n = {n}$" in text


def test_intake_first_wins_and_replay_determinism_match_manuscript() -> None:
    """First-wins derived by order swap, determinism by replay."""
    full = HorizonEntry(ATTENTION.id, frozenset(ATTENTION.markers))
    empty = HorizonEntry(ATTENTION.id)

    full_first = progress_report([full, empty], as_of=REVIEW)
    empty_first = progress_report([empty, full], as_of=REVIEW)
    assert full_first.findings[0].status is HorizonStatus.TOWARD
    assert empty_first.findings[0].status is HorizonStatus.INQUIRY
    assert any("the first entry stands" in note for note in full_first.intake_notes)

    replay = progress_report([full, empty], as_of=REVIEW)
    assert report_digest(replay) == report_digest(full_first)

    text = _normalized()
    assert (
        "the first valid entry bearing an identifier stands, and every later "
        "entry with that identifier is set aside with a duplicate note" in text
    )
    assert "reproduces the identical report, digest for digest" in text


def test_currentness_boundary_constants_match_manuscript() -> None:
    """The 90/91 boundary is derived, exclusive, and stated."""
    tau = 90
    points = temporal_currentness_sweep(
        ATTENTION.id, range(0, 120), as_of=REVIEW, stale_after_days=tau
    )
    toward_ages = [p.age_days for p in points if p.status is HorizonStatus.TOWARD]
    stale_ages = [p.age_days for p in points if p.status is HorizonStatus.INQUIRY]
    boundary = max(toward_ages)
    assert boundary == tau  # exclusive: age == tau is still current
    assert min(stale_ages) == boundary + 1

    text = _normalized()
    assert f"$\\tau = {tau}$" in text
    assert (
        f"at age exactly {boundary} days and reverts from age {boundary + 1} days"
        in text
    )


def test_sweep_codomain_matches_manuscript() -> None:
    """The unreachable statuses are derived, then stated."""
    points = temporal_currentness_sweep(
        ATTENTION.id, range(-10, 200, 5), as_of=REVIEW, stale_after_days=90
    )
    reached = {p.status.value for p in points}
    unreachable = sorted({status.value for status in HorizonStatus} - reached)
    assert unreachable == ["DRIFTING", "NOT_OBSERVED"]

    latex_names = " and ".join(
        "$\\texttt{" + name.replace("_", "\\_") + "}$" for name in unreachable
    )
    assert f"{latex_names} are unreachable in a sweep" in _normalized()


def test_lattice_call_count_matches_manuscript() -> None:
    """The registry-wide replay size is derived from the registry and the ages."""
    rows = len(GOLDEN_ASPIRATIONS)
    columns = len(SWEEP_AGES)
    assert f"${rows} \\times {columns} = {rows * columns}$ executed" in _normalized()


def test_digest_order_independence_matches_manuscript() -> None:
    """Permutation-invariance and the 64-hex shape are executed."""
    digest = registry_digest(GOLDEN_ASPIRATIONS)
    assert registry_digest(tuple(reversed(GOLDEN_ASPIRATIONS))) == digest
    rotated = GOLDEN_ASPIRATIONS[4:] + GOLDEN_ASPIRATIONS[:4]
    assert registry_digest(rotated) == digest
    assert len(digest) == 64
    assert set(digest) <= set("0123456789abcdef")

    assert f"exactly {len(digest)} lowercase hexadecimal characters" in _normalized()


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

    text = _normalized()
    assert "intake screening function" in text
    assert "never raises on malformed or unexpected input" in text


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


_LIMITS = PROJECT_ROOT / "manuscript" / "05_limits.md"
_LIMIT_WORDS = {2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six"}


def _limit_bullets() -> list[str]:
    """The top-level bullets of 05_limits' hard-limits list, in order."""
    raw = _LIMITS.read_text(encoding="utf-8")
    body = raw.split("The sharpest risk")[0]
    return re.findall(r"^- \*(Commitment|Enforced [^*]+)\.\*", body, flags=re.MULTILINE)


def test_limits_enforcement_split_matches_its_own_labels() -> None:
    """05's claim about how many limits the code enforces is counted, not asserted.

    The section used to say "most of them are enforced in the code", which was
    an overclaim: three of the six are commitments the evaluator cannot hold.
    The prose now labels every bullet, and this test counts the labels.
    """
    bullets = _limit_bullets()
    assert bullets, "no labelled limit bullets parsed; the check would be vacuous"
    enforced = [label for label in bullets if label.startswith("Enforced")]
    commitments = [label for label in bullets if label == "Commitment"]
    assert len(enforced) + len(commitments) == len(bullets)

    text = " ".join(_LIMITS.read_text(encoding="utf-8").split())
    assert f"carries {_LIMIT_WORDS[len(bullets)].lower()} hard limits" in text
    assert f"{_LIMIT_WORDS[len(enforced)]} of them have a mechanical core" in text
    assert f"the other {_LIMIT_WORDS[len(commitments)].lower()} are commitments" in text


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


def test_limits_split_guard_rejects_the_earlier_overclaim() -> None:
    """Proof of detection: the retired "most of them" wording must not pass."""
    bullets = _limit_bullets()
    enforced = [label for label in bullets if label.startswith("Enforced")]
    assert len(enforced) * 2 <= len(bullets), (
        "a majority of the limits would now be code-enforced, so the retired "
        '"most of them are enforced" wording would need re-examining'
    )
    text = " ".join(_LIMITS.read_text(encoding="utf-8").split())
    assert "most of them are enforced in the code" not in text


def test_abstract_figure_count_matches_the_builder() -> None:
    """The abstract's figure count is bound to len(FIGURES), never hand-kept."""
    abstract = " ".join(
        (PROJECT_ROOT / "manuscript" / "00_abstract.md")
        .read_text(encoding="utf-8")
        .split()
    )
    assert f"{_COUNT_WORDS[len(FIGURES)]} code-derived **figures**" in abstract
    for count, word in _COUNT_WORDS.items():
        if count != len(FIGURES):
            assert f"{word} code-derived" not in abstract


def test_abstract_figure_count_guard_rejects_a_stale_count() -> None:
    """Proof of detection: the pre-analysis-layer count must not pass the guard."""
    stale = "Five code-derived **figures** render the registry."
    assert f"{_COUNT_WORDS[len(FIGURES)]} code-derived **figures**" not in stale


def test_report_envelope_tuple_matches_the_dataclass() -> None:
    """The envelope tuple has one component per ``ReportEnvelope`` field.

    The arity and the schema string are derived from the running package, not
    transcribed: a field added to or removed from the record, or a changed
    schema literal, fails here before any archived envelope can drift from
    the definition a reader was given.
    """
    from golden_line import ENVELOPE_SCHEMA, ReportEnvelope

    fields = [field.name for field in dataclasses.fields(ReportEnvelope)]
    assert _tuple_arity("v") == len(fields)
    text = _normalized()
    assert (
        f"with exactly those {_COUNT_WORDS[len(fields)].lower()} fields, in order"
        in text
    )
    assert f"`{ENVELOPE_SCHEMA}`" in text
    for name in fields:
        assert name.replace("_", "\\_") in text, name


def test_envelope_pointer_matches_manuscript() -> None:
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
    text = _normalized()
    assert "editing any of them afterwards makes the check return false" in text
    assert "says nothing about the truth of the report" in text
