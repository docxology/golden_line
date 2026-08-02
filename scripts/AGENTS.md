# Script contract

Every file in `scripts/` is a thin CLI over `src/`. Business logic belongs in
`src/golden_line/`, not here.

## Files

- `__init__.py` — package marker
- `build_figures.py` — calls `golden_line.figures.build_figures()` and prints the output paths
- `check_artifacts.py` — validates the figure registry and golden registry against source
- `check_registry.py` — runs structural checks over the aspiration registry

## Canonical commands

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90 --cov-report=term-missing
uv run ruff check src tests scripts && uv run ruff format --check src tests scripts
uv run python scripts/check_registry.py
uv run python scripts/build_figures.py
uv run python scripts/check_artifacts.py
```
