# Golden Line package

`src/golden_line/` contains the executable contract for this project: the
registry, the staged evaluator, the structural checks, the descriptive-analysis
helpers, the deterministic figure builders, and the artifact validator.

Start with `progress.py`, `registry.py`, and `models.py` for the evaluator
surface. Use `uv run pytest tests/ --cov=src --cov-branch --cov-report=term-missing`
for the full package check, or `uv run python scripts/check_artifacts.py` when
you are changing figures, labels, or generated registries.

See [AGENTS.md](AGENTS.md) for the working contract.
