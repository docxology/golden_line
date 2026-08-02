# Source tree

`src/` holds the importable package for this project. The source lives in
`src/golden_line/`; `src/golden_line.egg-info/` may appear after local build
steps and is not part of the handwritten source tree.

`pyproject.toml` wires this layout into pytest with `pythonpath = [".", "src"]`.
For a local check, run `uv run pytest tests/ --cov=src --cov-branch --cov-report=term-missing`.

See [AGENTS.md](AGENTS.md) for the working contract.
