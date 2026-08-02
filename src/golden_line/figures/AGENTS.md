# Figure package contract

`src/golden_line/figures/` splits figure work into five modules with fixed
boundaries.

## Modules

- `__init__.py` owns `FIGURES`, `BUILD_PROVENANCE`, and `build_figures(project_root: Path | None = None) -> list[Path]`.
- `analysis_figures.py` draws the five analysis-backed figures: `temporal_currentness_sweep`, `currentness_lattice`, `signal_inventory`, `horizon_bands`, and `batch_reading_overview`.
- `core_schematics.py` draws the six registry and evaluator schematics: `golden_horizon_thread`, `aspiration_registry_map`, `horizon_decision_path`, `staged_evaluation_pipeline`, `evidence_state_matrix`, and `counter_signal_dominance`.
- `record_figures.py` replays the evaluator for the marker-completeness panel and the finding-field matrix — two figures that show what the evaluator actually returns rather than how it is described.
- `svg.py` holds the shared palette, layout constants, and text helpers used by every SVG builder.

## Invariants

- `FIGURES` is the canonical figure order used by the builder and the artifact gate.
- SVG builders must stay deterministic. Repeated `build_figures()` runs should write byte-stable SVG and JSON outputs.
- PNGs are rasterized from those SVGs with `rsvg-convert`; do not replace that path with a different renderer without updating tests and artifacts together.
- `BUILD_PROVENANCE` must stay `scripts/build_figures.py`. That value is written into `output/figures/figure_registry.json` as `generated_by` and names the user-facing build entry point, not a package import path.

## Validation

- `uv run python scripts/build_figures.py`
- `uv run python scripts/check_artifacts.py`
- `uv run pytest tests/test_figures.py tests/test_artifacts.py -q`
