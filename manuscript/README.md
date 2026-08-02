# Manuscript

This folder contains the prose and render inputs for the Golden Line paper:
the section files, `config.yaml`, `config.yaml.example`, `preamble.md`,
`references.bib`, and the cover asset folder in `assets/`.

After changing figure references or captions, run `uv run python scripts/build_figures.py`
and `uv run python scripts/check_artifacts.py`. Rendered PDF and HTML checks
need the external publication engine and run from a checkout of it, wherever
that lives; the path-independent commands are in `../docs/development.md`.

See [AGENTS.md](AGENTS.md) for the working contract.
