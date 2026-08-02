# Figure builders

This package contains the deterministic figure builders for Golden Line. The
shared registry lives in `__init__.py`; the analysis-backed drawings live in
`analysis_figures.py`; the registry and evaluator schematics live in
`core_schematics.py`; and `svg.py` provides the shared palette and text
primitives.

Run `uv run python scripts/build_figures.py` to regenerate the figure set, then
run `uv run python scripts/check_artifacts.py` to confirm the generated files
and manuscript citations still agree.

See [AGENTS.md](AGENTS.md) for the working contract.
