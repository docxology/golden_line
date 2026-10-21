# Development

Use the standard-library implementation through `uv`:

```bash
uv run pytest tests/ --cov=src --cov-branch --cov-report=term-missing
uv run python scripts/check_registry.py
uv run python scripts/build_figures.py
uv run python scripts/check_artifacts.py
uv run ruff check src tests scripts
uv run ruff format --check src tests scripts
uv run mypy src/golden_line
uv run python scripts/gen_formalism_ledger.py --check
```

The first four commands remain the core local validation surface; lint, format,
type and generated-ledger checks complete the release gate surface. They run from
this repository alone, offline, with no sibling project present. Rebuild the
ignored generated outputs before running `check_artifacts.py`; never hand-edit
files under `output/`.

One prerequisite is outside Python: `rsvg-convert` from librsvg
(`brew install librsvg` on macOS, `apt-get install librsvg2-bin` on Debian or
Ubuntu). `scripts/build_figures.py` uses it for the deterministic SVG-to-PNG
step and raises `rsvg-convert is required to build deterministic PNG figures`
rather than degrading silently when it is absent. Install it before the figure
build and the artifact gate; the test suite rebuilds figures on demand, so it
needs the tool too.

The figure builder writes thirteen SVG/PNG pairs, the source-derived registry
snapshot, and a provenance-bearing figure registry under `output/figures/`.
Five of the thirteen — `signal_inventory`, `horizon_bands`,
`temporal_currentness_sweep`, `currentness_lattice`, and
`batch_reading_overview` — are drawn from the descriptive-analysis layer in
`src/golden_line/analysis.py`; two more — `marker_completeness` and
`finding_field_matrix` — replay `progress_report` directly from
`src/golden_line/figures/record_figures.py`.
`check_artifacts.py` must pass after generation; it fails if a figure is stale,
missing, associated with the wrong registry digest, carrying a hand-edited
caption, embedded without a prose cross-reference, or cross-referenced without
being embedded.

The gate also validates exact manifest cardinality, filename/label pairing,
safe basenames and path containment, SVG bytes replayed from source, PNG bytes
replayed through the current converter, and manifest checksums. The manifest
records the full converter/library version output and executable SHA-256.
A changed renderer is reported as a rebuild requirement. An editable manifest
hash alone is insufficient: the gate independently replays source. These checks
establish source consistency and byte integrity, not visual quality or truth.

## Release evidence and CI

`uv run python -m golden_line.release_evidence` executes the complete local
surface and writes `output/evidence/manifest.json` and per-command logs. It
records source commit, tracked-dirty state, Python runtime, lock digest, renderer
identity, registry digest, and artifact hashes. Every failed exit status is
retained and prevents success; dirty or changing tracked source also prevents
success. Run it on the committed release tree. Rendering is recorded as
`not_run` by this local runner and requires a separate external-toolchain receipt.

The no-sibling-checkout CI matrix runs the declared supported Python releases
with a locked dependency resolution and archives evidence keyed by source SHA,
including failed runs. A fresh checkout needs only this repository, uv, and
librsvg for local validation. Coverage measures exercised code, not semantic
completeness or the truth of observations.

## Rendering the manuscript (external toolchain)

The typeset PDF and HTML are the one thing this repository cannot produce by
itself. Rendering is done by a separate publication engine,
<https://github.com/docxology/template>, which you clone wherever you like.
This is a declared external dependency: without it, the four gates above still
pass and the package, tests, and figures are all still real; you simply have no
rendered PDF or HTML.

Nothing below assumes a particular directory layout. Set the two roots to
wherever the two repositories actually live:

```bash
GOLDEN_LINE_ROOT=$(pwd)                 # this repository, from its root
TEMPLATE_ROOT=${TEMPLATE_ROOT:-$HOME/src/template}

git clone https://github.com/docxology/template.git "${TEMPLATE_ROOT}"   # once

# Make this repository visible to the engine under a qualified project name.
# External sources require a managed lifecycle leaf for provenance validation.
mkdir -p "${TEMPLATE_ROOT}/projects/working"
ln -sfn "${GOLDEN_LINE_ROOT}" "${TEMPLATE_ROOT}/projects/working/golden_line"

cd "${TEMPLATE_ROOT}"
uv run python scripts/pipeline/stage_03_render.py --project working/golden_line
uv run python scripts/pipeline/stage_04_validate.py --project working/golden_line
uv run python -m infrastructure.validation.cli pdf \
  projects/working/golden_line/output/pdf/golden_line_combined.pdf
```

The qualified name is the path under `projects/` (`working/golden_line` here).
The lifecycle alias supplies a repository boundary for rendered provenance;
it does not change this repository's public visibility. A bare direct-child
link can render but fails the current engine's provenance validation.
Use a Git-backed checkout or detached worktree of the engine: current rendered
provenance also binds cached stage implementation files, which an archive-only
export cannot supply.

The engine's strict `publication-audit` and rendered methods gates are
public-release checks that run in the engine checkout, not here. Their
repository-boundary findings describe where a project is linked from, not
whether its evaluator or manuscript is sound. Do not weaken the public
validator or describe this project as published; use the local artifact gate
plus the rendered PDF/HTML validation above.

The manuscript keeps its compact publication geometry in
`docs/manuscript/config.yaml` (`metadata.geometry: "left=0.33in,right=0.33in,top=0.58in,bottom=0.58in"`).
The founding-four
visual is intentionally source-derived and interpretive: its loop and symbols
make the aspirations more memorable without turning them into a ranking or an
empirical result.

The publication cover is configured in the same file under
`paper.cover.image`, relative to `docs/manuscript/`. The checked-in cover is a text-
free, full-frame illustration in `docs/manuscript/assets/`; its visual motifs are
documented there so the art remains relevant to the instrument rather than
decorative metadata. `rendering.cover_height_fraction` gives it deliberate
title-page presence while leaving the manuscript's compact geometry separate.
Render after changing either the cover or the manuscript, then inspect the title
page as an artifact.
