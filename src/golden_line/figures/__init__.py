"""Build deterministic Golden Line figures and the source-linked registries."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from golden_line.analysis import horizon_distribution
from golden_line.models import HorizonStatus
from golden_line.paths import PROJECT_ROOT
from golden_line.registry import (
    GOLDEN_ASPIRATIONS,
    founding_aspirations,
    further_aspirations,
)
from golden_line.serialization import canonical_registry, registry_digest
from golden_line.version import REGISTRY_VERSION

from .analysis_figures import (
    SWEEP_AGES,
    SWEEP_AS_OF,
    SWEEP_STALE_AFTER_DAYS,
    WORKED_BATCH_ENTRIES,
    _WORKED_BATCH_COUNTS,
    _WORKED_BATCH_OVERVIEW,
    _svg_batch_overview,
    _svg_currentness_lattice,
    _svg_currentness_sweep,
    _svg_horizon_bands,
    _svg_signal_inventory,
    lattice_deviations,
    lattice_rows,
)
from .core_schematics import (
    PRECEDENCE_AS_OF,
    PRECEDENCE_STALE_AFTER_DAYS,
    _svg_counter_signal_dominance,
    _svg_decision_path,
    _svg_evidence_state_matrix,
    _svg_pipeline,
    _svg_registry_map,
    _svg_thread,
    precedence_cells,
)
from .record_figures import (
    FIELD_MATRIX_CONDITIONS,
    RECORD_AS_OF,
    RECORD_STALE_AFTER_DAYS,
    _svg_finding_field_matrix,
    _svg_marker_completeness,
    always_carried_fields,
    completeness_rows,
    completeness_toward_total,
    field_matrix_rows,
    field_matrix_statuses,
    marker_subsets,
)

ROOT = PROJECT_ROOT

# Written into figure_registry.json as generated_by; this names the user-facing
# build entry point, not the internal module location.
BUILD_PROVENANCE = "scripts/build_figures.py"

#: Schema markers stamped into the two generated registries. The artifact gate
#: imports these rather than hardcoding a literal, so a bump has one home.
GOLDEN_REGISTRY_SCHEMA = "1.0"
FIGURE_REGISTRY_SCHEMA = "1.2"


# Executed once at import so the two replay figures below can quote their own
# results in their captions instead of restating them by hand.
_COMPLETENESS_ROWS = completeness_rows()
_COMPLETENESS_SUBSETS = len(_COMPLETENESS_ROWS[0].cells)
_COMPLETENESS_TOWARD = completeness_toward_total(_COMPLETENESS_ROWS)
_FIELD_MATRIX_ROWS = field_matrix_rows()
_FIELD_MATRIX_ALWAYS = always_carried_fields(_FIELD_MATRIX_ROWS)


FIGURES = (
    (
        "golden_horizon_thread",
        "fig:golden_horizon_thread",
        _svg_thread,
        "The four founding aspirations held in a revisable loop. Titles, horizons, and marker/counter-signal counts come from the versioned registry; the connecting loop and icons are interpretive, not a ranking.",
        "A source-derived four-way loop for attention, usefulness, repair, and human flourishing, with interpretive icons; direction is not a score.",
    ),
    (
        "aspiration_registry_map",
        "fig:aspiration_registry_map",
        _svg_registry_map,
        f"The full {len(GOLDEN_ASPIRATIONS)}-entry aspiration registry: {len(founding_aspirations())} founding aspirations and "
        f"{len(further_aspirations())} further entries, drawn from the versioned source. Each row shows a horizon and declared "
        "marker/counter-signal counts; the layout is a taxonomy, not a performance scale.",
        f"A two-group taxonomy of {len(GOLDEN_ASPIRATIONS)} aspirations, each row showing its title, horizon, and declared marker "
        "and counter-signal counts; the rows do not rank performance.",
    ),
    (
        "horizon_decision_path",
        "fig:horizon_decision_path",
        _svg_decision_path,
        "The evaluator's ordered decision rule, terminating in the four HorizonStatus values TOWARD, INQUIRY, DRIFTING, and NOT_OBSERVED. Counter-signal precedence is explicit; TOWARD requires complete markers and auditable currentness when temporal review is enabled. The path reads a record; it is not a compliance verdict.",
        "A vertical decision flow of ordered clauses branching to four directional readings, with TOWARD reached only after complete markers, no counter-signal, and auditable currentness when temporal review is enabled.",
    ),
    (
        "staged_evaluation_pipeline",
        "fig:staged_evaluation_pipeline",
        _svg_pipeline,
        "A batch of horizon entries passes through three stages: intake screening, signal matching, and decision. Records that fail intake — malformed, unknown-id, or duplicate — are set aside into visible intake notes (quoted verbatim from a real progress_report replay), undeclared tokens are ignored and noted, and the output is one bounded finding per registry aspiration. Findings are directional readings, never grades.",
        "Three stacked stage boxes — intake screening, matching, decision — with a dashed set-aside branch carrying malformed, unknown-id, and duplicate records into an intake-notes channel, an ignored-undeclared-tokens note, and one bounded finding per aspiration as output.",
    ),
    (
        "evidence_state_matrix",
        "fig:evidence_state_matrix",
        _svg_evidence_state_matrix,
        "The four HorizonStatus readings mapped to bounded evidence conditions: no admitted entry; incomplete, stale, or unauditable evidence; a declared counter-signal; and complete current/auditable evidence. The matrix explicitly rejects a good-to-bad ranking.",
        "A four-row evidence-state matrix for NOT_OBSERVED, INQUIRY, DRIFTING, and TOWARD, showing the record condition and interpretive limit for each without ranking them.",
    ),
    (
        "temporal_currentness_sweep",
        "fig:temporal_currentness_sweep",
        _svg_currentness_sweep,
        f"A fully-marked, counter-signal-free entry for the first registry aspiration replayed through the real evaluator at {len(SWEEP_AGES)} observation ages with stale_after_days = {SWEEP_STALE_AFTER_DAYS}. Every cell names the status progress_report actually returned, so the reading does not depend on colour; the reading stays TOWARD through age {SWEEP_STALE_AFTER_DAYS} and reverts to INQUIRY from age {SWEEP_STALE_AFTER_DAYS + 1} and for future-dated observations. Age reopens the question; it never manufactures drift.",
        f"A grid of {len(SWEEP_AGES)} age-labelled cells read left to right, each printing the evaluator's actual status for that observation age, with a dashed line at the exclusive {SWEEP_STALE_AFTER_DAYS}-day staleness boundary where TOWARD becomes INQUIRY.",
    ),
    (
        "marker_completeness",
        "fig:marker_completeness",
        _svg_marker_completeness,
        f"Every observed-marker subset for each of the {len(GOLDEN_ASPIRATIONS)} aspirations, filed as an entry and "
        f"evaluated: {len(GOLDEN_ASPIRATIONS) * _COMPLETENESS_SUBSETS} executed progress_report calls at review date "
        f"{RECORD_AS_OF}, every observation current. Each cell prints the status the evaluator returned and how many "
        "declared markers remain unmet, so the grid reads without colour; only the complete subset reaches TOWARD, and an "
        f"entry missing one marker reads exactly as one missing all of them. The {_COMPLETENESS_TOWARD} filled cells "
        "describe records, never the quality of the work or its author.",
        f"A {len(GOLDEN_ASPIRATIONS)}-row by {_COMPLETENESS_SUBSETS}-column grid of executed readings, one column per "
        "observed-marker subset ordered from none to all, each cell filled for TOWARD and outlined otherwise and labelled "
        "with its status and its count of unmet markers; only the final column is filled.",
    ),
    (
        "finding_field_matrix",
        "fig:finding_field_matrix",
        _svg_finding_field_matrix,
        f"The {len(_FIELD_MATRIX_ROWS)} structured fields of a finding against {len(FIELD_MATRIX_CONDITIONS)} evidence "
        f"conditions, one executed progress_report call per column at review date {RECORD_AS_OF}. Filled cells are fields "
        "the returned record carries and outlined cells are empty, and every cell prints which it is, so the matrix reads "
        f"without colour. The fields carried under every condition are {', '.join(_FIELD_MATRIX_ALWAYS)}, so no reading "
        "arrives unexplained. An empty field records an absent observation; it never asserts that what it names is false.",
        f"A {len(_FIELD_MATRIX_ROWS)}-row by {len(FIELD_MATRIX_CONDITIONS)}-column matrix of finding fields against "
        "evidence conditions, each cell either filled and labelled carried or outlined and labelled empty, with the "
        "status each condition returned printed above its column.",
    ),
    (
        "signal_inventory",
        "fig:signal_inventory",
        _svg_signal_inventory,
        "The aggregate declared-signal vocabulary of the registry, one unit block per token: filled blocks for markers, outlined blocks for counter-signals, with per-registry totals and token-uniqueness counts. The blocks describe what the evaluator can match, never fulfilment or performance.",
        f"{len(GOLDEN_ASPIRATIONS)} registry rows, each showing filled marker blocks and outlined counter-signal blocks per "
        "aspiration, with aggregate totals in the header; the blocks are vocabulary, not points.",
    ),
    (
        "horizon_bands",
        "fig:horizon_bands",
        _svg_horizon_bands,
        f"The {len(GOLDEN_ASPIRATIONS)} aspiration horizons grouped into "
        f"{len(horizon_distribution())} temporal-reach bands — immediate, recurring cycle, at handoff, and open-ended — an interpretive reading aid declared in the analysis layer. Band order widens reach; it is not a maturity ladder and not part of the registry contract.",
        f"{len(horizon_distribution())} stacked band rows, each holding chips for its member aspirations with their horizon phrases, ordered from immediate reach to open-ended reach without ranking.",
    ),
    (
        "currentness_lattice",
        "fig:currentness_lattice",
        _svg_currentness_lattice,
        f"The same currentness replay run across the whole registry: {len(GOLDEN_ASPIRATIONS)} aspiration rows by "
        f"{len(SWEEP_AGES)} observation ages, {len(GOLDEN_ASPIRATIONS) * len(SWEEP_AGES)} executed progress_report calls, at "
        f"stale_after_days = {SWEEP_STALE_AFTER_DAYS}. Filled cells are TOWARD and outlined cells are INQUIRY, so the grid reads without colour; "
        f"the FLIPS AT column gives each row's own TOWARD-to-INQUIRY age and the footer counts rows that differ. "
        "Uniform ageing is a fact about the evaluator's code path — it is never evidence that any aspiration is being served.",
        f"A {len(GOLDEN_ASPIRATIONS)}-row by {len(SWEEP_AGES)}-column lattice of executed evaluator readings, each cell filled for TOWARD and outlined "
        "for INQUIRY, with a per-row flip-age column and a footer counting rows whose flip age differs from the first row's.",
    ),
    (
        "counter_signal_dominance",
        "fig:counter_signal_dominance",
        _svg_counter_signal_dominance,
        f"Counter-signal precedence replayed rather than drawn: for each of the {len(GOLDEN_ASPIRATIONS)} aspirations, four "
        f"progress_report calls at review date {PRECEDENCE_AS_OF} with stale_after_days = {PRECEDENCE_STALE_AFTER_DAYS}. "
        "Complete markers with no counter-signal read TOWARD; adding one declared counter-signal returns DRIFTING even though every "
        "marker is still present, and it still returns DRIFTING when the same observation is stale. Filled cells are DRIFTING and "
        "outlined cells are not, so the panel reads without colour. The panel characterizes clause order; it is never a grade of any work or person.",
        f"A {len(GOLDEN_ASPIRATIONS)}-row panel with four executed-status columns per aspiration — complete markers, complete markers plus a "
        "counter-signal, counter-signal alone, and a stale counter-signal record — with DRIFTING cells filled and every other status outlined.",
    ),
    (
        "batch_reading_overview",
        "fig:batch_reading_overview",
        _svg_batch_overview,
        f"The {len(WORKED_BATCH_ENTRIES)}-entry worked batch of the batch-reading section replayed through the real evaluator: "
        f"{_WORKED_BATCH_COUNTS['TOWARD']} TOWARD, {_WORKED_BATCH_COUNTS['INQUIRY']} INQUIRY, "
        f"{_WORKED_BATCH_COUNTS['DRIFTING']} DRIFTING, and {_WORKED_BATCH_COUNTS['NOT_OBSERVED']} NOT_OBSERVED across "
        f"{len(GOLDEN_ASPIRATIONS)} findings — one per registry aspiration whether or not an entry was filed — with "
        f"{_WORKED_BATCH_OVERVIEW.intake_note_count} intake set-asides and "
        f"{_WORKED_BATCH_OVERVIEW.ignored_marker_total} ignored undeclared token quoted verbatim from the report. "
        "The groupings count readings in this record; they do not grade the work or the people behind it.",
        f"{len(WORKED_BATCH_ENTRIES)} submitted entry chips fanning through one evaluator arrow into "
        f"{len(GOLDEN_ASPIRATIONS)} findings grouped into four status boxes, with an intake accounting strip quoting the report's set-aside notes verbatim; counts describe the record, not a grade.",
    ),
)


def build_figures(project_root: Path | None = None) -> list[Path]:
    """Write every figure SVG+PNG plus the canonical registry snapshot."""

    root = project_root or ROOT
    figure_dir = root / "output" / "figures"
    figure_dir.mkdir(parents=True, exist_ok=True)
    converter = shutil.which("rsvg-convert")
    if converter is None:
        raise RuntimeError(
            "rsvg-convert is required to build deterministic PNG figures"
        )

    png_paths: list[Path] = []
    figure_records = []
    for name, label, builder, caption, alt in FIGURES:
        svg_path = figure_dir / f"{name}.svg"
        png_path = figure_dir / f"{name}.png"
        svg_path.write_text(builder(), encoding="utf-8")
        subprocess.run([converter, "-o", str(png_path), str(svg_path)], check=True)
        png_paths.append(png_path)
        figure_records.append(
            {
                "label": label,
                "filename": png_path.name,
                "caption": caption,
                "alt": alt,
                "source": "golden_line aspiration registry and status enum",
                "generated_by": BUILD_PROVENANCE,
                "format": "PNG rasterized from deterministic SVG",
            }
        )

    registry_path = figure_dir / "golden_registry.json"
    registry_path.write_text(
        json.dumps(
            {
                "schema_version": GOLDEN_REGISTRY_SCHEMA,
                "registry_version": REGISTRY_VERSION,
                "digest": registry_digest(GOLDEN_ASPIRATIONS),
                "aspirations": json.loads(canonical_registry(GOLDEN_ASPIRATIONS)),
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    figure_registry_path = figure_dir / "figure_registry.json"
    figure_registry_path.write_text(
        json.dumps(
            {
                "schema_version": FIGURE_REGISTRY_SCHEMA,
                "registry_version": REGISTRY_VERSION,
                "registry_digest": registry_digest(GOLDEN_ASPIRATIONS),
                "status_values": [status.value for status in HorizonStatus],
                "figures": figure_records,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    return png_paths


__all__ = [
    "BUILD_PROVENANCE",
    "FIELD_MATRIX_CONDITIONS",
    "FIGURES",
    "PRECEDENCE_AS_OF",
    "PRECEDENCE_STALE_AFTER_DAYS",
    "RECORD_AS_OF",
    "RECORD_STALE_AFTER_DAYS",
    "ROOT",
    "SWEEP_AGES",
    "SWEEP_AS_OF",
    "SWEEP_STALE_AFTER_DAYS",
    "WORKED_BATCH_ENTRIES",
    "always_carried_fields",
    "build_figures",
    "completeness_rows",
    "completeness_toward_total",
    "field_matrix_rows",
    "field_matrix_statuses",
    "lattice_deviations",
    "lattice_rows",
    "marker_subsets",
    "precedence_cells",
]
