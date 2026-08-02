# Tests

This folder holds the executable checks for the Golden Line package and its
generated artifacts. The modules are grouped by concern: API surface, progress
evaluation, registry and serialization, analysis, figures and their fail-closed
guards, print legibility in `test_figure_legibility.py`, artifact consistency,
manuscript bindings in `test_formalism_bindings.py`, the skill's executable
examples in `test_skill.py`, the command-line entry points in
`test_scripts_cli.py`, and lexical guardrails in `test_no_mocks.py`.

Run `uv run pytest tests/ --cov=src --cov-branch --cov-report=term-missing`.
The project keeps a `90` coverage floor in `pyproject.toml`.

See [AGENTS.md](AGENTS.md) for the working contract.
