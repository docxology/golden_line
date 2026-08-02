# Development

Use the standard-library implementation through `uv`:

```bash
uv run pytest tests/ --cov=src --cov-branch --cov-report=term-missing
uv run python scripts/check_registry.py
uv run python scripts/build_figures.py
uv run python scripts/check_artifacts.py
```

These four commands are the canonical local validation surface. They run from
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
# A direct child of projects/ with src/ and tests/ is discovered by its bare
# directory name, so the qualified name here is simply `golden_line`.
ln -sfn "${GOLDEN_LINE_ROOT}" "${TEMPLATE_ROOT}/projects/golden_line"

cd "${TEMPLATE_ROOT}"
uv run python scripts/pipeline/stage_03_render.py --project golden_line
uv run python scripts/pipeline/stage_04_validate.py --project golden_line
uv run python -m infrastructure.validation.cli pdf \
  projects/golden_line/output/pdf/golden_line_combined.pdf
```

If instead you link this repository through the engine's private-projects root,
the qualified name becomes the path under `projects/` that the link produced
(for example `working/golden_line`); pass that name to the same commands.

The engine's strict `publication-audit` and rendered methods gates are
public-release checks that run in the engine checkout, not here. Their
repository-boundary findings describe where a project is linked from, not
whether its evaluator or manuscript is sound. Do not weaken the public
validator or describe this project as published; use the local artifact gate
plus the rendered PDF/HTML validation above.

The manuscript keeps its compact publication geometry in
`manuscript/config.yaml` (`metadata.geometry: "left=0.33in,right=0.33in,top=0.58in,bottom=0.58in"`).
The founding-four
visual is intentionally source-derived and interpretive: its loop and symbols
make the aspirations more memorable without turning them into a ranking or an
empirical result.

The publication cover is configured in the same file under
`paper.cover.image`, relative to `manuscript/`. The checked-in cover is a text-
free, full-frame illustration in `manuscript/assets/`; its visual motifs are
documented there so the art remains relevant to the instrument rather than
decorative metadata. `rendering.cover_height_fraction` gives it deliberate
title-page presence while leaving the manuscript's compact geometry separate.
Render after changing either the cover or the manuscript, then inspect the title
page as an artifact.
