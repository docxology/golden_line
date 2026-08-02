import dataclasses
from pathlib import Path

import pytest

from golden_line import IntakeSetAsideReason, classify_intake_entries
from golden_line.artifacts import check_artifacts
from golden_line.figures import FIGURES, build_figures


def test_figure_builder_is_deterministic(tmp_path: Path) -> None:
    first = build_figures(tmp_path)
    bytes_first = {path.name: path.read_bytes() for path in first}
    second = build_figures(tmp_path)
    assert {path.name: path.read_bytes() for path in second} == bytes_first
    assert first[0].read_bytes().startswith(b"\x89PNG\r\n\x1a\n")


def test_generated_artifact_chain_is_self_consistent(tmp_path: Path) -> None:
    build_figures(tmp_path)
    (tmp_path / "manuscript").mkdir()
    # Anchors and prose cross-references are separate obligations in the gate,
    # so a stand-in manuscript has to carry both.
    body = " ".join(
        f"![caption](../output/figures/{name}.png){{#{label} width=95%}} see [@{label}]"
        for name, label, *_ in FIGURES
    )
    (tmp_path / "manuscript" / "00_test.md").write_text(body, encoding="utf-8")
    assert check_artifacts(tmp_path) == []


def test_figure_build_fails_when_no_rasterizer_is_on_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Without a converter on PATH the builder refuses rather than guessing a location."""
    monkeypatch.setenv("PATH", "")
    with pytest.raises(RuntimeError, match="rsvg-convert"):
        build_figures(tmp_path)


def _builder(name: str):
    return next(entry[2] for entry in FIGURES if entry[0] == name)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _normalized(path: Path) -> str:
    """Whitespace-normalized file text so bindings survive markdown wrapping."""
    return " ".join(path.read_text(encoding="utf-8").split())


def test_analysis_figures_are_registered() -> None:
    names = {entry[0] for entry in FIGURES}
    assert {
        "temporal_currentness_sweep",
        "signal_inventory",
        "horizon_bands",
        "batch_reading_overview",
    } <= names


def test_sweep_figure_draws_real_evaluator_statuses() -> None:
    from golden_line.analysis import temporal_currentness_sweep
    from golden_line.figures import SWEEP_AGES, SWEEP_AS_OF, SWEEP_STALE_AFTER_DAYS
    from golden_line.registry import GOLDEN_ASPIRATIONS

    svg = _builder("temporal_currentness_sweep")()
    points = temporal_currentness_sweep(
        GOLDEN_ASPIRATIONS[0].id,
        SWEEP_AGES,
        as_of=SWEEP_AS_OF,
        stale_after_days=SWEEP_STALE_AFTER_DAYS,
    )
    for point in points:
        assert point.observed_on in svg
        assert point.status.value in svg
    assert "exclusive boundary" in svg


def test_inventory_figure_carries_registry_totals() -> None:
    from golden_line.analysis import signal_inventory

    inventory = signal_inventory()
    svg = _builder("signal_inventory")()
    assert (
        f"{inventory.total_markers} declared markers, "
        f"{inventory.total_counter_signals} counter-signals" in svg
    )


def test_horizon_bands_figure_names_every_band() -> None:
    from golden_line.analysis import HORIZON_BANDS

    svg = _builder("horizon_bands")()
    for band_name, _ in HORIZON_BANDS:
        assert band_name.upper() in svg


def test_horizon_bands_counts_derive_from_the_registry() -> None:
    """Subtitle and caption counts re-derive; registry growth cannot strand them."""
    from golden_line.analysis import horizon_distribution
    from golden_line.registry import GOLDEN_ASPIRATIONS

    bands = horizon_distribution()
    total = sum(len(band.aspiration_ids) for band in bands)
    assert total == len(GOLDEN_ASPIRATIONS)
    svg = _builder("horizon_bands")()
    assert f"{total} horizons, {len(bands)} reaches of visibility" in svg
    caption = next(entry[3] for entry in FIGURES if entry[0] == "horizon_bands")
    assert f"The {total} aspiration horizons grouped into {len(bands)}" in caption


def test_sweep_captions_derive_from_the_sweep_constants() -> None:
    """Spec caption and 02a embed re-derive; an ages/threshold change cannot strand them."""
    from golden_line.figures import SWEEP_AGES, SWEEP_STALE_AFTER_DAYS

    caption = next(
        entry[3] for entry in FIGURES if entry[0] == "temporal_currentness_sweep"
    )
    alt = next(
        entry[4] for entry in FIGURES if entry[0] == "temporal_currentness_sweep"
    )
    assert f"at {len(SWEEP_AGES)} observation ages" in caption
    assert f"stale_after_days = {SWEEP_STALE_AFTER_DAYS}" in caption
    assert (
        f"TOWARD through age {SWEEP_STALE_AFTER_DAYS} and reverts to INQUIRY "
        f"from age {SWEEP_STALE_AFTER_DAYS + 1}" in caption
    )
    assert f"{len(SWEEP_AGES)} age-labelled cells" in alt
    assert f"{SWEEP_STALE_AFTER_DAYS}-day staleness boundary" in alt
    embed = _normalized(PROJECT_ROOT / "manuscript" / "02a_formalism.md")
    assert (
        f"at {len(SWEEP_AGES)} observation ages with "
        f"stale_after_days = {SWEEP_STALE_AFTER_DAYS}" in embed
    )
    assert (
        f"TOWARD through age {SWEEP_STALE_AFTER_DAYS}, "
        f"INQUIRY from age {SWEEP_STALE_AFTER_DAYS + 1}" in embed
    )


def test_shipped_registry_signal_literals_are_pinned() -> None:
    """Bind the manuscript's 18/9 all-distinct prose class to the executed inventory."""
    from golden_line.analysis import signal_inventory

    inventory = signal_inventory()
    assert (inventory.total_markers, inventory.unique_markers) == (18, 18)
    assert (inventory.total_counter_signals, inventory.unique_counter_signals) == (
        9,
        9,
    )
    numerals = (
        f"{inventory.total_markers} markers and "
        f"{inventory.total_counter_signals} counter-signals"
    )
    assert numerals in _normalized(PROJECT_ROOT / "manuscript" / "02_method.md")
    aspirations = _normalized(PROJECT_ROOT / "manuscript" / "03_aspirations.md")
    assert numerals in aspirations
    assert (
        f"all {inventory.unique_markers} marker tokens and all "
        f"{inventory.unique_counter_signals} counter-signal tokens distinct"
        in aspirations
    )
    # Word-form sites pin to the same executed totals via the 18/9 equality above.
    assert "eighteen markers and nine counter-signals" in _normalized(
        PROJECT_ROOT / "manuscript" / "05_limits.md"
    )
    assert "eighteen markers and nine counter-signals" in _normalized(
        PROJECT_ROOT / "manuscript" / "04a_batch_reading.md"
    )
    assert (
        f"{inventory.total_markers} markers / "
        f"{inventory.total_counter_signals} counter-signals"
        in _normalized(PROJECT_ROOT / ".agents" / "skills" / "golden-line" / "SKILL.md")
    )


def test_horizon_band_membership_counts_match_the_prose() -> None:
    """Per-band counts in 03 and SKILL.md re-derive from horizon_distribution().

    The figure renders each band's size dynamically and the older tests only
    checked the total and the number of bands, both invariant under a
    re-partition — so moving one aspiration between bands falsified two
    documents while the suite stayed green. These are the per-band numbers.
    """
    from golden_line.analysis import horizon_distribution

    counts = {band.band: len(band.aspiration_ids) for band in horizon_distribution()}
    assert sum(counts.values()) == 9

    aspirations = _normalized(PROJECT_ROOT / "manuscript" / "03_aspirations.md")
    assert (
        f"immediate ({counts['immediate']} aspiration, at the next decision), "
        f"recurring cycle ({counts['recurring cycle']}, at revision or tool turnover), "
        f"at handoff ({counts['at handoff']}, when the work reaches another person), and "
        f"open-ended ({counts['open-ended']}, over years)" in aspirations
    )
    skill = _normalized(
        PROJECT_ROOT / ".agents" / "skills" / "golden-line" / "SKILL.md"
    )
    assert (
        f"(immediate {counts['immediate']}, recurring cycle {counts['recurring cycle']}, "
        f"at handoff {counts['at handoff']}, open-ended {counts['open-ended']})"
        in skill
    )


def test_band_count_binding_rejects_a_planted_repartition() -> None:
    """Proof of detection: a re-banded registry no longer matches the prose."""
    from golden_line.analysis import horizon_distribution

    planted_map = (
        ("immediate", ("next decision",)),
        ("recurring cycle", ("tool turnover",)),
        (
            "at handoff",
            (
                "next learner",
                "collaborator or public reader",
                "public claim",
                "shared pool",
                "revision cycle",
            ),
        ),
        ("open-ended", ("long horizon", "multi-year inquiry")),
    )
    from golden_line.registry import GOLDEN_ASPIRATIONS

    planted_counts = {
        band: sum(1 for item in GOLDEN_ASPIRATIONS if item.horizon in horizons)
        for band, horizons in planted_map
    }
    real_counts = {
        band.band: len(band.aspiration_ids) for band in horizon_distribution()
    }
    assert planted_counts != real_counts
    aspirations = _normalized(PROJECT_ROOT / "manuscript" / "03_aspirations.md")
    assert (
        f"recurring cycle ({planted_counts['recurring cycle']}, at revision or tool turnover)"
        not in aspirations
    )


def test_lattice_cells_are_executed_evaluator_readings() -> None:
    """Every lattice cell re-derives from a real temporal_currentness_sweep call."""
    from golden_line.analysis import temporal_currentness_sweep
    from golden_line.figures import SWEEP_AGES, SWEEP_AS_OF, SWEEP_STALE_AFTER_DAYS
    from golden_line.figures.analysis_figures import lattice_rows
    from golden_line.registry import GOLDEN_ASPIRATIONS

    rows = lattice_rows()
    assert len(rows) == len(GOLDEN_ASPIRATIONS)
    for row, item in zip(rows, GOLDEN_ASPIRATIONS):
        assert row.aspiration_id == item.id
        expected = temporal_currentness_sweep(
            item.id,
            SWEEP_AGES,
            as_of=SWEEP_AS_OF,
            stale_after_days=SWEEP_STALE_AFTER_DAYS,
        )
        assert row.statuses == tuple(point.status for point in expected)
    svg = _builder("currentness_lattice")()
    assert f"{len(rows)} aspirations × {len(SWEEP_AGES)} observation ages" in svg
    assert f"{len(rows) * len(SWEEP_AGES)} executed evaluator calls" in svg


def test_lattice_reports_a_uniform_flip_age() -> None:
    """The registry-wide flip age is derived, and the footer states that number."""
    from golden_line.figures import SWEEP_STALE_AFTER_DAYS
    from golden_line.figures.analysis_figures import lattice_deviations, lattice_rows

    rows = lattice_rows()
    flip_ages = {row.flip_age for row in rows}
    assert flip_ages == {SWEEP_STALE_AFTER_DAYS + 1}
    assert lattice_deviations(rows) == ()
    svg = _builder("currentness_lattice")()
    assert (
        f"0 rows of {len(rows)} flip at an age other than "
        f"{SWEEP_STALE_AFTER_DAYS + 1} d" in svg
    )


def test_lattice_deviation_count_detects_a_planted_outlier() -> None:
    """Proof of detection: one row with a different flip age is counted."""
    from golden_line.figures.analysis_figures import lattice_deviations, lattice_rows

    rows = lattice_rows()
    planted = (
        rows[:1]
        + (dataclasses.replace(rows[1], flip_age=rows[1].flip_age + 30),)
        + rows[2:]
    )
    assert lattice_deviations(planted) == (rows[1].aspiration_id,)
    assert len(lattice_deviations(planted)) == 1


def test_precedence_panel_cells_are_executed_progress_reports() -> None:
    """Every dominance cell is a real evaluator return, not a drawn assertion."""
    from golden_line.figures.core_schematics import precedence_cells
    from golden_line.models import HorizonStatus
    from golden_line.registry import GOLDEN_ASPIRATIONS

    rows = precedence_cells()
    assert len(rows) == len(GOLDEN_ASPIRATIONS)
    for (aspiration_id, statuses), item in zip(rows, GOLDEN_ASPIRATIONS):
        assert aspiration_id == item.id
        assert len(statuses) == 4
        assert statuses[0] is HorizonStatus.TOWARD
        # Complete markers plus a counter-signal, fresh and stale alike.
        assert statuses[1] is HorizonStatus.DRIFTING
        assert statuses[2] is HorizonStatus.DRIFTING
        assert statuses[3] is HorizonStatus.DRIFTING

    dominated = sum(1 for _, statuses in rows if statuses[1] is HorizonStatus.DRIFTING)
    svg = _builder("counter_signal_dominance")()
    assert f"{dominated} of {len(rows)} aspirations still read DRIFTING" in svg
    assert f"returns DRIFTING for {dominated} of {len(rows)} aspirations" in svg


def test_precedence_panel_would_report_a_marker_that_outranked_a_counter_signal() -> (
    None
):
    """Proof of detection: the panel's summary counts, it does not assert.

    If clause 2 stopped preceding clauses 3-6, the middle column would return
    something other than DRIFTING and the derived headline count would drop.
    """
    from golden_line.figures.core_schematics import precedence_cells
    from golden_line.models import HorizonStatus

    rows = precedence_cells()
    planted = tuple(
        (aspiration_id, (statuses[0], HorizonStatus.TOWARD) + statuses[2:])
        if index == 0
        else (aspiration_id, statuses)
        for index, (aspiration_id, statuses) in enumerate(rows)
    )
    dominated = sum(
        1 for _, statuses in planted if statuses[1] is HorizonStatus.DRIFTING
    )
    assert dominated == len(rows) - 1


def test_every_figure_carries_the_boundary_footer() -> None:
    """Every figure keeps the SOURCE-DRIVEN epistemic-boundary convention."""
    assert FIGURES, "no figures registered, so this convention check is vacuous"
    for name, _, builder, *_ in FIGURES:
        assert "SOURCE-DRIVEN SCHEMATIC" in builder(), name


def test_every_caption_keeps_a_boundary_clause() -> None:
    """Every registry caption states an interpretive limit, not just content."""
    markers = ("not a ", "never", "not part", "do not", "rejects")
    for name, _, _, caption, _ in FIGURES:
        lowered = caption.lower()
        assert any(marker in lowered for marker in markers), name


def test_pipeline_figure_draws_real_intake_setasides() -> None:
    """The set-aside branch quotes the evaluator's own intake notes verbatim."""
    from golden_line import HorizonEntry, progress_report
    from golden_line.registry import GOLDEN_ASPIRATIONS

    first = GOLDEN_ASPIRATIONS[0]
    report = progress_report(
        [
            "not a record",
            HorizonEntry("not-a-real-id"),
            HorizonEntry(first.id),
            HorizonEntry(first.id),
        ]
    )
    svg = _builder("staged_evaluation_pipeline")()
    assert f"SET ASIDE · {len(report.intake_notes)} kinds" in svg
    for label in ("MALFORMED RECORD", "UNKNOWN ID", "DUPLICATE ENTRY"):
        assert label in svg
    assert "not-a-real-id" in svg
    assert "HorizonEntry" in svg  # fragment of the verbatim malformed-record note


def test_batch_overview_figure_draws_real_overview_numbers() -> None:
    """Every count in the batch overview figure is an executed report result."""
    from golden_line.analysis import report_overview
    from golden_line.figures import WORKED_BATCH_ENTRIES
    from golden_line.models import HorizonStatus
    from golden_line.progress import progress_report
    from golden_line.registry import GOLDEN_ASPIRATIONS

    report = progress_report(list(WORKED_BATCH_ENTRIES))
    overview = report_overview(report)
    counts = report.counts()
    assert len(report.findings) == len(GOLDEN_ASPIRATIONS)
    svg = _builder("batch_reading_overview")()
    assert (
        f"{len(WORKED_BATCH_ENTRIES)} entries in, "
        f"{len(report.findings)} findings out" in svg
    )
    for status in HorizonStatus:
        assert f"{status.value} · {counts[status.value]}" in svg
    assert f"{overview.intake_note_count} records set aside" in svg
    assert f"{overview.ignored_marker_total} undeclared token ignored" in svg
    assert "not-a-real-id" in svg  # from the verbatim quoted intake note


def test_batch_overview_fates_derive_from_public_intake_classification() -> None:
    from golden_line.analysis import report_overview
    from golden_line.figures import WORKED_BATCH_ENTRIES
    from golden_line.progress import progress_report

    fates = []
    for classification in classify_intake_entries(WORKED_BATCH_ENTRIES):
        if classification.admitted:
            fates.append("admitted")
        elif classification.set_aside_reason is IntakeSetAsideReason.UNKNOWN_ID:
            fates.append("set aside · unknown id")
        elif classification.set_aside_reason is IntakeSetAsideReason.DUPLICATE:
            fates.append("set aside · duplicate")
        else:
            raise AssertionError(
                f"unexpected worked-batch intake classification: {classification}"
            )
    assert fates == [
        "admitted",
        "admitted",
        "admitted",
        "admitted",
        "set aside · unknown id",
        "set aside · duplicate",
    ]

    report = progress_report(list(WORKED_BATCH_ENTRIES))
    overview = report_overview(report)
    assert sum(fate != "admitted" for fate in fates) == overview.intake_note_count

    svg = _builder("batch_reading_overview")()
    for entry, fate in zip(WORKED_BATCH_ENTRIES, fates):
        assert entry.aspiration_id in svg
        assert fate in svg


def test_batch_overview_caption_and_manuscript_match_execution() -> None:
    """Caption and 04a literals restate exactly the executed batch partition."""
    from golden_line.analysis import report_overview
    from golden_line.figures import WORKED_BATCH_ENTRIES
    from golden_line.progress import progress_report

    report = progress_report(list(WORKED_BATCH_ENTRIES))
    overview = report_overview(report)
    counts = report.counts()
    partition = (
        f"{counts['TOWARD']} TOWARD, {counts['INQUIRY']} INQUIRY, "
        f"{counts['DRIFTING']} DRIFTING, and {counts['NOT_OBSERVED']} NOT_OBSERVED"
    )
    caption = next(
        entry[3] for entry in FIGURES if entry[0] == "batch_reading_overview"
    )
    assert partition in caption
    assert f"{overview.intake_note_count} intake set-asides" in caption

    text = _normalized(PROJECT_ROOT / "manuscript" / "04a_batch_reading.md")
    assert "batch_reading_overview.png" in text
    assert "#fig:batch_reading_overview" in text
    assert f"{partition} across {len(report.findings)} findings" in text
    words = {0: "zero", 1: "one", 2: "two", 3: "three", 4: "four", 5: "five"}
    assert (
        f"{words[counts['TOWARD']]} `TOWARD`, {words[counts['INQUIRY']]} `INQUIRY`, "
        f"{words[counts['DRIFTING']]} `DRIFTING`, and "
        f"{words[counts['NOT_OBSERVED']]} `NOT_OBSERVED`" in text
    )
    assert f"`intake_note_count` is **{overview.intake_note_count}**" in text
    assert f"`ignored_marker_total` is **{overview.ignored_marker_total}**" in text
    for note in report.intake_notes:
        assert note in text  # 04a quotes both intake notes verbatim


def test_completeness_panel_cells_are_executed_evaluator_readings() -> None:
    """Every completeness cell re-derives from an independent progress_report call."""
    from golden_line.figures.record_figures import (
        RECORD_AS_OF,
        RECORD_STALE_AFTER_DAYS,
        completeness_rows,
        marker_subsets,
    )
    from golden_line.models import HorizonEntry
    from golden_line.progress import progress_report
    from golden_line.registry import GOLDEN_ASPIRATIONS

    rows = completeness_rows()
    assert len(rows) == len(GOLDEN_ASPIRATIONS)
    for row, item in zip(rows, GOLDEN_ASPIRATIONS):
        assert row.aspiration_id == item.id
        subsets = marker_subsets(len(item.markers))
        assert len(row.cells) == len(subsets)
        for cell, indices in zip(row.cells, subsets):
            entry = HorizonEntry(
                item.id,
                frozenset(item.markers[index] for index in indices),
                observed_on=RECORD_AS_OF,
            )
            finding = progress_report(
                [entry],
                (item,),
                as_of=RECORD_AS_OF,
                stale_after_days=RECORD_STALE_AFTER_DAYS,
            ).findings[0]
            assert cell.status is finding.status
            assert cell.unmet_count == len(finding.unmet)
            assert cell.observed_count == len(indices)


def test_completeness_panel_gives_no_partial_credit() -> None:
    """Exactness: only the complete marker subset reads TOWARD, for every row.

    This is the verifying test the exactness proposition's binding row names.
    Every non-complete subset — including one that is a single marker short —
    must read INQUIRY, and the panel's own headline count must equal the number
    of complete subsets, one per aspiration.
    """
    from golden_line.figures.record_figures import (
        completeness_rows,
        completeness_toward_total,
    )
    from golden_line.models import HorizonStatus
    from golden_line.registry import GOLDEN_ASPIRATIONS

    rows = completeness_rows()
    for row in rows:
        complete = max(cell.observed_count for cell in row.cells)
        for cell in row.cells:
            if cell.observed_count == complete:
                assert cell.status is HorizonStatus.TOWARD, row.aspiration_id
                assert cell.unmet_count == 0
            else:
                assert cell.status is HorizonStatus.INQUIRY, row.aspiration_id
                assert cell.unmet_count == complete - cell.observed_count

    toward = completeness_toward_total(rows)
    assert toward == len(GOLDEN_ASPIRATIONS)
    svg = _builder("marker_completeness")()
    total = sum(len(row.cells) for row in rows)
    assert f"{toward} of {total} readings reach TOWARD" in svg
    assert f"{toward} cells, one per aspiration" in svg


def test_completeness_headline_detects_a_planted_partial_credit() -> None:
    """Proof of detection: the headline counts, it does not assert.

    If a one-marker-short entry started reading TOWARD, the derived headline
    would exceed one filled cell per aspiration.
    """
    import dataclasses as _dataclasses

    from golden_line.figures.record_figures import (
        completeness_rows,
        completeness_toward_total,
    )
    from golden_line.models import HorizonStatus
    from golden_line.registry import GOLDEN_ASPIRATIONS

    rows = completeness_rows()
    planted_cells = (
        _dataclasses.replace(rows[0].cells[1], status=HorizonStatus.TOWARD),
    ) + rows[0].cells[2:]
    planted = (
        _dataclasses.replace(rows[0], cells=(rows[0].cells[0],) + planted_cells),
    ) + rows[1:]
    assert completeness_toward_total(planted) == len(GOLDEN_ASPIRATIONS) + 1


def test_completeness_panel_refuses_a_ragged_registry() -> None:
    """A registry with differing marker counts has no grid, and is refused."""
    from golden_line.figures.record_figures import completeness_rows
    from golden_line.models import Aspiration
    from golden_line.registry import GOLDEN_ASPIRATIONS

    ragged = GOLDEN_ASPIRATIONS[:1] + (
        Aspiration(
            "ragged",
            "One marker only",
            "thread",
            "next decision",
            ("only marker",),
            ("only counter-signal",),
        ),
    )
    with pytest.raises(ValueError, match="differing marker counts"):
        completeness_rows(ragged)


def test_field_matrix_cells_are_executed_findings() -> None:
    """Every field-matrix cell reports a real finding's real field content."""
    from golden_line.figures.record_figures import (
        FIELD_MATRIX_CONDITIONS,
        field_matrix_findings,
        field_matrix_rows,
        field_matrix_statuses,
    )
    from golden_line.models import HorizonFinding

    findings = field_matrix_findings()
    assert len(findings) == len(FIELD_MATRIX_CONDITIONS)
    rows = field_matrix_rows()
    fields = [field.name for field in dataclasses.fields(HorizonFinding)]
    assert [name for name, _carried in rows] == fields
    for name, carried in rows:
        assert carried == tuple(bool(getattr(f, name)) for f in findings)
    assert field_matrix_statuses() == tuple(f.status for f in findings)


def test_field_matrix_conditions_reach_every_status_and_every_field() -> None:
    """The column set is non-vacuous: no dead row, and all four readings appear."""
    from golden_line.figures.record_figures import (
        always_carried_fields,
        field_matrix_rows,
        field_matrix_statuses,
    )
    from golden_line.models import HorizonStatus

    rows = field_matrix_rows()
    assert set(field_matrix_statuses()) == set(HorizonStatus)
    dead = [name for name, carried in rows if not any(carried)]
    assert dead == [], dead
    always = always_carried_fields(rows)
    assert "reasons" in always  # no reading arrives without its derivation trail
    svg = _builder("finding_field_matrix")()
    assert (
        f"{len(rows)} fields × {len(field_matrix_statuses())} evidence conditions"
        in svg
    )
    assert (
        f"{len(always)} fields carried under every condition: " + ", ".join(always)
        in svg
    )


def test_field_matrix_always_carried_detects_a_planted_empty_reasons() -> None:
    """Proof of detection: a reading returned without reasons drops the count."""
    from golden_line.figures.record_figures import (
        always_carried_fields,
        field_matrix_rows,
    )

    rows = field_matrix_rows()
    planted = tuple(
        (name, (False,) + carried[1:]) if name == "reasons" else (name, carried)
        for name, carried in rows
    )
    assert "reasons" not in always_carried_fields(planted)
    assert len(always_carried_fields(planted)) == len(always_carried_fields(rows)) - 1


def test_field_matrix_manuscript_literals_match_the_replay() -> None:
    """02c's field and condition counts are derived, never hand-kept."""
    from golden_line.figures.record_figures import (
        FIELD_MATRIX_CONDITIONS,
        always_carried_fields,
        field_matrix_rows,
    )

    rows = field_matrix_rows()
    always = always_carried_fields(rows)
    words = {3: "Three", 6: "six", 9: "nine", 12: "twelve"}
    text = _normalized(PROJECT_ROOT / "manuscript" / "02c_evidence_protocol.md")
    assert (
        f"The {words[len(rows)]} structured fields of a finding against "
        f"{words[len(FIELD_MATRIX_CONDITIONS)]} evidence conditions" in text
    )
    assert f"{words[len(always)]} fields are carried under every condition" in text
    assert f"the remaining {words[len(rows) - len(always)]} are carried exactly" in text


def test_new_replay_figures_are_registered_and_embedded() -> None:
    """Both new panels ship in the builder and are cited by the manuscript."""
    names = {entry[0] for entry in FIGURES}
    assert {"marker_completeness", "finding_field_matrix"} <= names
    formalism = _normalized(PROJECT_ROOT / "manuscript" / "02a_formalism.md")
    assert "marker_completeness.png" in formalism
    assert "@fig:marker_completeness" in formalism
    evidence = _normalized(PROJECT_ROOT / "manuscript" / "02c_evidence_protocol.md")
    assert "finding_field_matrix.png" in evidence
    assert "@fig:finding_field_matrix" in evidence
