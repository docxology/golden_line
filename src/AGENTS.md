# Source tree contract

`src/` is a src-layout container. The only import package here is
`golden_line/`; `src/__init__.py` is a package marker, and
`src/golden_line.egg-info/` is generated packaging metadata when local builds
have run.

- Keep the `pythonpath = [".", "src"]` wiring in `pyproject.toml` aligned with this layout.
- Put implementation in `src/golden_line/`. Do not move evaluator or artifact logic into `scripts/` or `tests/`.
- If the package path changes, update imports and `pyproject.toml` together, then run `uv run pytest tests/ --cov=src --cov-branch --cov-report=term-missing`.
