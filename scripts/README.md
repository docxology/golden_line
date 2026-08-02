# Scripts

`scripts/` contains the command-line entry points for local validation and
artifact generation. These files decide nothing; they import the installed
`golden_line` package and delegate to it. None of them takes an option, but
each parses its command line anyway and exits non-zero on an argument it cannot
honour, so a mistyped flag cannot read as a clean run.

The commands people run here are `uv run python scripts/build_figures.py`,
`uv run python scripts/check_artifacts.py`, and
`uv run python scripts/check_registry.py`.

See [AGENTS.md](AGENTS.md) for the working contract.
