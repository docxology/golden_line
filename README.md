# Golden Line

Golden Line is the aspirational thread of the founding four. Current membership
belongs to the [Line Set declaration](https://github.com/docxology/line_set). It
asks what a project is worth reaching toward over a longer horizon, then
records markers and counter-signals without turning aspiration into a
compliance verdict.

The executable `progress_report` returns `TOWARD`, `INQUIRY`, `DRIFTING`, or
`NOT_OBSERVED` for a versioned aspiration registry of nine entries. Reporting
is staged: entries are screened at intake (unknown IDs, duplicates, and
malformed records are set aside and noted), undeclared markers are ignored with
a reason, and temporal review can optionally test whether dated observations
are current. With temporal review enabled, missing or malformed dates prevent
`TOWARD`. Without it, currentness is unevaluated, even for an undated `TOWARD`.
No admitted entry means `NOT_OBSERVED`; an admitted empty entry means `INQUIRY`;
all declared markers with no admitted counter-signal mean `TOWARD`, subject to
enabled temporal review. Rejected material does not mean that nobody looked.
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
reachability count, not fulfillment); `horizon_distribution` groups the nine
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
[White Line](https://github.com/docxology/white_line) is declared in the reader,
[`line_set`](https://github.com/docxology/line_set), whose
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
envelope/report pair. It establishes present correspondence, not an unedited
archive, authenticity, or observation truth. `validate_instrument_envelope`
separately checks shape, schema, line identity, and mandatory non-claims.
Subject and source references remain unverified caller metadata.

`canonical_report` keeps its original sorted-finding byte contract.
`canonical_archive` adds a versioned intake sidecar, including discarded
duplicates; `decode_archive` restores finding order from the envelope and
rejects non-bijective IDs, inconsistent statuses, intake dispositions that
contradict first-valid admission, or rejection notes that differ from the report.
Admitted IDs must agree with `NOT_OBSERVED` versus observed findings; retained
notes, observation-date text, and matched/ignored token partitions must agree
with each admitted entry. This is intrinsic correspondence, not evaluation
against an unavailable custom registry or authentication of history.
`intake_digest` changes when a normalized discarded contradiction changes,
without rewriting old native report digests. Malformed raw payloads need
separate source custody.

Native-only `decode_archive` reads remain supported, but their
`intake_archive` is `None` (custody unavailable), not `()` (a genuinely empty
evaluated intake). Both `canonical_archive` and `intake_digest` raise
`ValueError` for unavailable custody. Retain the native report and envelope;
missing normalized intake cannot be reconstructed from findings or notes.

Retain the archive **and** envelope for transport, not just the native report:

```python
from golden_line import (
    GOLDEN_ASPIRATIONS, HorizonEntry, HorizonStatus, canonical_archive,
    canonical_envelope, decode_archive, envelope_matches_report, progress_report,
    report_envelope,
)

aspiration = GOLDEN_ASPIRATIONS[0]
positive = HorizonEntry(aspiration.id, frozenset(aspiration.markers))
contrary = HorizonEntry(
    aspiration.id,
    counter_signals=frozenset(aspiration.counter_signals),
    note="Recipient disputes the earlier observation.",
    observed_on="2026-10-19",
)
report = progress_report([positive, contrary], as_of="2026-10-20")
envelope = report_envelope(report)
archive_json = canonical_archive(report)
envelope_json = canonical_envelope(envelope)
restored = decode_archive(archive_json, envelope_json)
assert restored == report
assert restored.findings[0].status is HorizonStatus.TOWARD
assert restored.intake_archive[1].entry == contrary
assert envelope_matches_report(envelope, restored)
```

First valid entry wins: the later contrary duplicate is retained, not evaluated.
Counter-signal precedence applies only within the admitted entry. This undated
positive entry has no temporal review, so `TOWARD` does not establish freshness.
The native digest remains unchanged; the intake sidecar has its own digest.
Keep original source bytes separately, including malformed input that cannot be
normalized. Neither archive nor envelope authenticates history or source truth.

Custom registries pass `validate_registry` before evaluation and are labeled
`custom:` with the content digest authoritative. Empty scopes are rejected.
Review-date strings use exact ASCII `YYYY-MM-DD` calendar spelling; `date`
objects are also supported, but timestamps, basic ISO dates, week dates, and
non-ASCII digits are not. Observation dates outside that grammar cannot
establish currentness when temporal review is enabled; without a window they
remain uninterpreted text and currentness is unevaluated. All supported text
must contain Unicode scalar values: lone surrogates are malformed, while
legitimate non-ASCII and supplementary characters are preserved. See
[claim boundaries](docs/claim_boundaries.md) for the supported passive data domain.

Optional `ObservationProvenance` and `AspirationConflict` side records retain
self-report, contestation, source pointers, and human-owned unresolved tension.
They never change a directional finding and must be retained separately via
`canonical_evidence_records`: neither `canonical_archive` nor the envelope
bundles them. This exporter validates IDs and tokens only against bundled
`GOLDEN_ASPIRATIONS`, not a custom registry, even when custom IDs reuse default
names. Retain custom-registry evidence separately; no custom-registry evidence
validation is provided here. Worked records and the design decision are in
[evidence records](docs/evidence-records.md).

## When to use this template project

Use Golden Line when a project needs a revisable long-horizon direction and a
small record of observable movement toward it. Use Red Line for refusal, Black
Line for positive operating discipline, and White Line for absence,
unknowability, and restraint. A Golden Line status cannot substitute for any of
those instruments.

## Configuration and source of truth

The live metadata is in `docs/manuscript/config.yaml`; its standalone shape is shown
in `docs/manuscript/config.yaml.example`. Registry and evaluator truth lives in
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
refresh it. `docs/manuscript/config.yaml` is the source of truth either way: the
block is a rendering of that file, so read the config when the two could have
drifted.
The retained generated block below describes the previous 0.6.1 configuration,
not a current release inventory. Version 0.7.0 refines archive custody and
calendar/Unicode boundaries; verified prior source-archive identities belong in
[publication guidance](docs/publication.md), separate from adapter capabilities.

<!-- PUBLISHING-STATUS:START (generated by infrastructure.publishing.status_report) -->
**Golden Line: Toward What Matters** · v0.6.1 · CC-BY-4.0 (prose); MIT (code) · Daniel Ari Friedman

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

_Status legend: ✅ published (durable identifier recorded in `config.yaml`) · 🔵 reserved (identifier reserved but not yet registered by final publication) · ⚪ available (adapter implemented and locally verifiable) · 🟡 planned. This block is generated — edit `docs/manuscript/config.yaml`, then regenerate with `uv run python -m infrastructure.publishing.status_report --project <path> --write`._
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

## The Line Set

The [current Line Set declaration](https://github.com/docxology/line_set) owns
membership. The instruments remain separate from their reader and the Witness
Register, which co-registers report envelopes without aggregation:

- [Black Line](https://github.com/docxology/black_line) — declared practice and evidence-label coverage
- [Red Line](https://github.com/docxology/red_line) — the cognitive-security registry of self-assessments
- [White Line](https://github.com/docxology/white_line) — the absence and omission ledger
- [Silver Line](https://github.com/docxology/silver_line) — the memory-and-succession instrument
- Violet Line — affected-party consent (access-controlled source; see the Line Set declaration)
- [Blue Line](https://github.com/docxology/blue_line) — the stewardship instrument for maintained commitments
- [Green Line](https://github.com/docxology/green_line) — the capacity-under-development instrument
- Copper Line — dimensioned finite resource use, outstanding commitments, and attributed burdens (access-controlled source)
- Iron Line — recorded recovery exercises compared with scenario-specific targets (access-controlled source)
- [The Line Set](https://github.com/docxology/line_set) — the cross-line set reader holding instruments apart
- [The Witness Register](https://github.com/docxology/witness_register) — co-registration without aggregation

The founding four describe history, not the current family boundary. The roster
declares distinct scopes; source availability and access controls vary by
instrument. A citation or link does not establish installation or public access,
and Golden Line does not require sibling sources to run.
Copper's quantities are not aspiration priorities or evidence of fairness.
Iron's recorded target comparisons are not aspirational progress or a promise
of future recovery. Neither grants permission or offsets another line's finding.
