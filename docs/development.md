# Development

Use uv and Python 3.11 or newer. The CI matrix exercises Python 3.11 through
3.15. Install librsvg before running the local checks:

```bash
uv sync --locked
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
The figure registry uses metadata schema `2.0`: every figure carries its
authored `alt_text`, distinct from its caption. There is no serialized `alt`
alias or caption fallback. The artifact gate checks the authored description,
so legacy-only, absent, or changed alternative text requires regeneration.
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
records source commit, dirty state, current source-file and aggregate SHA-256
bindings, Python runtime, lock digest, renderer identity, registry digest, and
artifact hashes. The working-source binding identifies uncommitted bytes without
claiming a clean revision. Every failed exit status is retained and prevents
success; dirty or changing source also prevents success. Source stability is
reported separately from cleanliness. Run it on the committed release tree.
Rendering is recorded as `not_run` by this local runner and requires a separate
external-toolchain receipt.

Source observations disable optional Git index writes and the filesystem-monitor
cache per command. The collector reads current bytes and dirtiness without
changing the host Git configuration or refreshing the source index.

The no-sibling-checkout CI matrix runs the declared supported Python releases
with a locked dependency resolution and archives evidence keyed by source SHA,
including failed runs. A fresh checkout needs only this repository, uv, and
librsvg for local validation. Coverage measures exercised code, not semantic
completeness or the truth of observations.

The release-evidence regression snapshots current working source into a clean
temporary Git repository with its own package environment and import path, then
runs the complete real command surface. It deliberately gives pytest an invalid
option and requires the remaining gates to succeed while the evidence manifest
still records failure. Install the locked development environment before running
the suite; missing dependencies are not evidence that this failure control
exercised pytest. The original checkout is neither committed nor modified.

### Current outputs and retained history

`output/figures/` and `data/formalism_claim_ledger.json` are current generated
artifacts. Refresh them with `uv run python scripts/build_figures.py` and
`uv run python scripts/gen_formalism_ledger.py`; do not edit their bytes by hand.
The figure build requires librsvg as described above.

`docs/releases/v0.4.0.md`, `docs/releases/v0.5.0.md`,
`docs/releases/v0.6.0.md`, `docs/releases/v0.6.1.md`, and `docs/reviews/2026-10-20.md` are historical
receipts, not current verification.
Keep their original wording and identities, including original British spelling.
Likewise, `tests/fixtures/native_report_v040.json` is a historical digest-bound
native report and the CFF schema fixture retains its external enum identities.
The noncanonical `docs/releases/legacy-manuscript/02a_formalism.md` is retained
legacy source outside renderer discovery, not the current evaluator contract;
use `docs/manuscript/` for current
prose. Do not rewrite these records or imply that regenerating current artifacts
refreshes an old release's evidence.

## Rendering the manuscript (external toolchain)

Render the [canonical manuscript](manuscript/README.md) with the external
[docxology/template](https://github.com/docxology/template) engine. Run the
local validation and figure build above first. Install Python 3.14 for the
pinned engine, Pandoc with a compatible `pandoc-crossref`, and XeLaTeX
with its packages on `PATH`.

Run from the root of a committed Golden Line checkout named `golden_line`.
Use an unused location for the engine clone:

```bash
GOLDEN_LINE_ROOT="$(pwd -P)"
TEMPLATE_ROOT="$GOLDEN_LINE_ROOT/../golden-line-render-template"
git clone https://github.com/docxology/template.git "$TEMPLATE_ROOT"
git -C "$TEMPLATE_ROOT" switch --detach 87704feae0a4490ef7dad9c931d268e8c30273c2

cd "$TEMPLATE_ROOT"
uv sync --locked --no-dev --python 3.14
mkdir -p projects/working
ln -s "$GOLDEN_LINE_ROOT" projects/working/golden_line
uv run --no-sync python scripts/pipeline/stage_03_render.py --project working/golden_line --skip-manuscript-hydration
uv run --no-sync python scripts/pipeline/stage_04_validate.py --project working/golden_line
```

The lifecycle alias supplies the project path for provenance. The hydration
flag preserves the authored source. Keep both Git indexes available for the
provenance checks. The project checkout receives:

- `output/pdf/golden_line_combined.pdf`
- `output/web/index.html`
- `output/epub/golden_line_combined.epub`
- `output/reports/validation_report.json` and
  `output/reports/rendered_provenance.json`

Stage 04 checks the rendered structure and source provenance. The engine's
strict publication audit is a separate release check. These checks do not
establish the truth of an observation or the usefulness of an aspiration.

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
