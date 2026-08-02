# Golden Line

Golden Line is the aspirational thread of the four-line governance set. It
asks what a project is worth reaching toward over a longer horizon, then
records markers and counter-signals without turning aspiration into a
compliance verdict.

The executable `progress_report` returns `TOWARD`, `INQUIRY`, `DRIFTING`, or
`NOT_OBSERVED` for a versioned aspiration registry of nine entries. Reporting
is staged: entries are screened at intake (unknown ids, duplicates, and
malformed records are set aside and noted), undeclared markers are ignored with
a reason, and temporal review can optionally test whether dated observations
are current. Missing or malformed dates cannot certify currentness.
`NOT_OBSERVED` means no valid entry was admitted; it does not mean that nobody
looked.
Every finding carries a full reasons trail plus structured matched/ignored
tokens, the original note, and temporal flags. Reports identify the registry
digest and review context that produced them. These statuses describe a record,
not a person; they are not a safety score, accreditation, moral authority, or
permission mechanism.

A structural check battery (`all_invariants`) guards the registry's shape —
distinct ids, populated fields, reachable statuses, sound signal text, unique
and disjoint signals, and a stable order-independent digest — and every check is
proof-of-detection tested against a planted-bad registry. The digest is a
review and drift-detection instrument only; it makes no safety claim.

A pure descriptive-analysis layer (`golden_line.analysis`) characterizes the
registry and replays the evaluator without changing its semantics:
`signal_inventory` tallies the declared marker/counter-signal vocabulary (a
reachability count, not fulfilment); `horizon_distribution` groups the nine
aspirations into declared temporal-reach bands (a reading aid, not a rank);
`temporal_currentness_sweep` replays one fully-marked entry through the real
evaluator across observation ages to expose the `TOWARD` → `INQUIRY` currentness
boundary; and `report_overview` regroups an existing report by status with
intake and ignored-token totals, adding no claim the findings did not carry.
These layers draw the `signal_inventory`, `horizon_bands`,
`temporal_currentness_sweep`, `currentness_lattice`, and
`batch_reading_overview` figures, embedded in the manuscript alongside the
founding-four thread, the registry map, the decision path, the pipeline, the
evidence-state matrix, the marker-completeness panel, the finding-field matrix,
and the counter-signal precedence panel — thirteen figures in total. Six of
them replay the evaluator rather than diagram it, and three of those six run the
replay across the whole registry rather than for one entry: the lattice runs 126
dated readings to show that the currentness boundary belongs to the evaluator,
the precedence panel shows that complete markers plus one counter-signal still
return `DRIFTING` for every aspiration, and the completeness panel files every
marker subset of every aspiration to show that one missing marker reads exactly
as none. The remaining new panel, the finding-field matrix, reports which of a
finding's twelve fields carry content under six evidence conditions for a single
aspiration. A project-local agent skill at
`.agents/skills/golden-line/SKILL.md` documents the operating surface.

Golden Line is standalone and lives in its own repository. Its relationship to
[Red Line](https://github.com/docxology/red_line),
[Black Line](https://github.com/docxology/black_line), and
[White Line](https://github.com/docxology/white_line) is declared in the fifth
work of the set, [`line_set`](https://github.com/docxology/line_set), whose
manuscript is the long form of that map. This work only links to those
boundaries and does not copy their prose or code; none of those repositories
has to be present for anything in this one to run.

## Common report envelope

For co-registration beside the other line instruments, `report_envelope` wraps
a complete `HorizonReport` in the cross-instrument envelope
(`line.report-envelope/1.0`): a SHA-256 pointer to the existing
`canonical_report` serialization, the review date, the registry version and
digest the report recorded, and the instrument's non-claims riding inside the
record. `native_status` is the complete ordered per-aspiration readings in
this instrument's own vocabulary — Golden Line has no single overall verdict
and the envelope does not invent one. The envelope points at the native
report; it never reinterprets it, and envelopes from different lines must not
be compared, ranked, averaged, or merged on `native_status`. Sibling
instruments align by publishing the same schema string, never by import.
`envelope_matches_report` is the read-back check for an archived
envelope/report pair.

## When to use this template project

Use Golden Line when a project needs a revisable long-horizon direction and a
small record of observable movement toward it. Use Red Line for refusal, Black
Line for positive operating discipline, and White Line for absence,
unknowability, and restraint. A Golden Line status cannot substitute for any of
those instruments.

## Configuration and source of truth

The live metadata is in `manuscript/config.yaml`; its standalone shape is shown
in `manuscript/config.yaml.example`. Registry and evaluator truth lives in
`src/golden_line/`, while generated figures and registry snapshots live under
`output/figures/` and must be rebuilt rather than hand-edited.

## Rendering: one declared external dependency

Everything this repository claims for itself runs from this repository alone —
the package, the test suite, the registry battery, the deterministic figure
build, and the artifact gate. No network, no sibling project.

Only the typeset PDF/HTML manuscript needs an outside tool: the publication
engine at [`docxology/template`](https://github.com/docxology/template), which
you clone wherever you like. That is a declared external dependency, not a
hidden one, and the path-independent invocation is in
[`docs/development.md`](docs/development.md). Without it you still get the
package, the tests, the figures, and the artifact gate; you do not get a
rendered PDF or HTML.

## Validation and publication boundaries

The local artifact gate checks source-to-figure/manuscript consistency and is
the gate this repository owns. The template renderer and its PDF/HTML
validation check rendered structure and belong to the external toolchain, so a
checkout without that toolchain cannot run them — that is a stated limit, not a
passing result. The strict public publication audit likewise runs in the
template checkout, and its repository-path findings are not evidence that the
evaluator or manuscript is unsound. None of these gates proves that an
aspiration is universally correct or that a directional reading is a safety or
permission decision.

## Publication and rendering

The table below is generated, and its regeneration command belongs to the
external [`docxology/template`](https://github.com/docxology/template)
toolchain, not to this repository — a checkout without that toolchain cannot
refresh it. `manuscript/config.yaml` is the source of truth either way: the
block is a rendering of that file, so read the config when the two could have
drifted.

<!-- PUBLISHING-STATUS:START (generated by infrastructure.publishing.status_report) -->
**Golden Line: Toward What Matters** · v0.4.0 · CC-BY-4.0 (prose); MIT (code) · Daniel Ari Friedman

Publishing surface — 20 platforms, 0 published:

| Platform | Tier | Status | Reference | Credentials |
| --- | --- | --- | --- | --- |
| zenodo | first-class | ⚪ available | — | `ZENODO_API_TOKEN` |
| github | first-class | ⚪ available | — | `GITHUB_TOKEN` |
| arxiv | first-class | ⚪ available | — | — |
| pypi | first-class | ⚪ available | — | `PYPI_TOKEN`, `TESTPYPI_TOKEN` |
| ipfs_pinata | first-class | ⚪ available | — | `PINATA_JWT` |
| ipfs_web3storage | first-class | ⚪ available | — | `WEB3_STORAGE_TOKEN` |
| software_heritage | first-class | ⚪ available | — | — |
| github_pages | first-class | ⚪ available | — | `GITHUB_TOKEN` |
| cloudflare_pages | first-class | ⚪ available | — | `CLOUDFLARE_API_TOKEN` |
| netlify | first-class | ⚪ available | — | `NETLIFY_AUTH_TOKEN` |
| huggingface_hub | first-class | ⚪ available | — | `HUGGINGFACE_TOKEN`, `HF_TOKEN` |
| osf | first-class | ⚪ available | — | `OSF_TOKEN` |
| amazon_kdp | documented | 🟡 planned | — | `AMAZON_KDP_EMAIL`, `AMAZON_KDP_PASSWORD` |
| google_play_books | documented | 🟡 planned | — | `GOOGLE_PLAY_BOOKS_SERVICE_ACCOUNT_JSON` |
| gumroad | documented | 🟡 planned | — | `GUMROAD_ACCESS_TOKEN` |
| leanpub | documented | 🟡 planned | — | `LEANPUB_API_KEY` |
| lulu | documented | 🟡 planned | — | `LULU_CLIENT_KEY`, `LULU_CLIENT_SECRET` |
| draft2digital | documented | 🟡 planned | — | `DRAFT2DIGITAL_API_TOKEN` |
| stripe | documented | 🟡 planned | — | `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY` |
| ingramspark | documented | 🟡 planned | — | `INGRAMSPARK_CLIENT_ID`, `INGRAMSPARK_CLIENT_SECRET` |

_Status legend: ✅ published (durable identifier recorded in `config.yaml`) · 🔵 reserved (identifier reserved but not yet registered by final publication) · ⚪ available (adapter implemented and locally verifiable) · 🟡 planned. This block is generated — edit `manuscript/config.yaml`, then regenerate with `uv run python -m infrastructure.publishing.status_report --project <path> --write`._
<!-- PUBLISHING-STATUS:END -->

## Quick start

Python is the only language runtime required — the package declares no
third-party dependencies. The figure build additionally needs one system tool,
`rsvg-convert` from librsvg (`brew install librsvg`,
`apt-get install librsvg2-bin`); `scripts/build_figures.py` raises a clear
error rather than degrading silently when it is missing.

Run the four canonical local gates in [`docs/development.md`](docs/development.md).
The executable contract is covered by the `tests/` suite, run with
`uv run pytest tests/ --cov=src --cov-branch --cov-report=term-missing`.
`check_artifacts.py` is the local source-to-artifact boundary: it verifies that
generated JSON, SVG, PNG, figure labels, registry digests, and manuscript
citations still agree. Rendered PDF/HTML validation belongs to the external
publication engine at [`docxology/template`](https://github.com/docxology/template),
cloned wherever you like, and runs after the local artifact chain passes; the
path-independent invocation is in [`docs/development.md`](docs/development.md).

See [AGENTS.md](AGENTS.md) for the working contract.
