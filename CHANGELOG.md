# Changelog

## 0.7.0 — 2026-11-09

- Distinguish unavailable normalized intake custody (`None`) on native-only
  decode from a genuinely empty evaluated intake. Refuse complete archive export
  and intake hashing without custody; reject explicit null archive sidecars.
- Require admitted intake to correspond to observed findings, including retained
  notes, dates, and complete disjoint matched/ignored token partitions. This is
  supplied consistency, not semantic reevaluation or source authentication.
- Require exact ASCII `YYYY-MM-DD` calendar dates at review boundaries and for
  observation currentness. Retain malformed observation dates as text; disabled
  currentness and counter-evidence precedence retain their existing meanings.
- Reject non-scalar Unicode before UTF-8 identity operations; set aside malformed
  entry text before admission and duplicate handling. Preserve valid non-ASCII
  and supplementary text.
- Clarify that evidence-record export validates the bundled aspiration registry,
  not custom registries. Archive, intake, and envelope schemas are unchanged;
  historical artifacts remain tied to their original producers.
- Inspect Git state and source bytes without optional index refreshes; evidence
  collection leaves a stat-only, otherwise clean checkout's index unchanged.
- Limit setuptools discovery to `golden_line` and its regular subpackages.
  Retain the template source-root marker without installing a stray top-level
  `__init__.py` beside the public package.
- Validate staleness controls before temporal sweeps, including empty age
  sequences, instead of letting an empty sweep bypass the evaluator's control
  admission. Valid empty sweeps still return an empty trajectory.

## 0.6.2 — 2026-11-08

- Documentation-only patch: use the current Line Set declaration and access-aware
  Copper/Iron roles without confusing resource quantities or recorded recovery
  target comparisons with aspiration priorities.
- Delete incidental sibling-count, default-object identity, module-attribution,
  and authored prose/gate-name assertions; retain reference validity, verified
  DOI, metadata consistency, registry behavior, and historical byte-custody checks.
- Synchronize current descriptive version metadata. Native evaluator semantics,
  registry identity, schemas, canonical golden archives, and original DOI and
  citation identities are unchanged. No artifacts, deposit, or new release
  verification are asserted here.

## 0.6.1 — 2026-11-08

Restore the existing Python 3.10–3.15 runtime contract. Use `timezone.utc`
instead of the Python 3.11-only `UTC` alias in release evidence and datetime
boundary tests, and resolve the locked development environment for Python 3.10.
UTC timestamps retain the same ISO format. The evaluator, registry, archive,
envelope, and vocabulary contracts are unchanged.

Remove source-wiring and prose-wording tests while retaining real repository-local
link and bibliography closure checks. Keep the existing CI matrix, native gate
commands, coverage floor, and immutable `v0.6.0` release unchanged.

## 0.6.0 — 2026-11-06

Reject archive intake sidecars whose consistently rehashed dispositions contradict
the native first-valid admission rule or whose rejection notes differ from the
native report. Reuse the evaluator's intake classifier, including custom report
identifiers; retain original malformed bytes separately. Native findings, status
vocabulary, registry revision, serialization, and transport schemas are unchanged.

Release evidence now binds every current tracked/non-ignored source file and its
aggregate digest, including dirty working source. Source stability is measured
independently of cleanliness; dirty source, changed source, partial commands, or
any failed gate still cannot pass.

Preserve the noncanonical root formalism file under
`docs/releases/legacy-manuscript/` instead of the renderer's discovery root.
The configured current manuscript must not be shadowed by legacy source.

Emit figure registry 2.0 with the canonical `alt_text` accessibility field and
validate that field against the authored descriptions. Generation determinism
covers both registries and all SVG/PNG bytes; mutation controls reject legacy-only,
missing, caption-substituted, and changed alternative text. The external renderer
must not infer alternative text from captions. Historical registries and native
evaluation, archive, envelope, and vocabulary schemas retain their identities.

Preserve normalized rejected contrary intake in the primary archive/envelope
transport examples and distinguish original-source and optional evidence-record
custody. Clarify no admission versus valid-empty evidence, admitted-record-only
counter precedence, first-valid duplicate handling, and optional temporal review.
The evaluator, registry vocabulary, archive schemas, and native digest formats
are unchanged. Maintained prose and owned names use American English:
`STATUS_COLORS` replaces `STATUS_COLOURS`, `pipeline_stages(..., colors=...)`
replaces `colours=`, and the internal helper is `_normalize_entry`. No aliases
remain. Historical source, release evidence, and pinned external fixtures retain
their original identities and wording. Current family orientation distinguishes
the eight instruments from their reader and witness companion, independently of
source availability.
Replace affected wording/source-text guards with native archive, admission,
temporal-transition, and schema-identity regressions; retain executable skill
examples and structural cross-reference checks without pinning prose.

Refresh the generated dependency lock against the declared development floors.
Keep the failed-canonical-gate release-evidence control on the complete real
command surface in a clean temporary snapshot of the current source, with its
own package environment and import path. A failed test gate must block success
even when every other local gate succeeds. Use the Python 3.11+ UTC alias.

Maintenance pass, no behavior change: CI action majors current
(`actions/checkout@v7`, `astral-sh/setup-uv@v10`,
`actions/upload-artifact@v7`), development floors raised to the versions the
locked tree is validated against (`pytest`, `pytest-cov`, `ruff`, `mypy`,
`jsonschema`, `pyyaml`, build `setuptools`), and documentation corrected
(package/test module maps, the `gen_formalism_ledger.py --check` flag, sibling
DOIs aligned with `CITATION.cff`). Evaluator, registry, figures, and the four
statuses unchanged.

## 0.5.0 — 2026-10-21

Implement the October review across registry/input boundaries, strict instrument
envelopes, order-aware archive reconstruction, retained intake contradictions,
source-replayed artifact integrity, exact-revision release evidence, and optional
human provenance/conflict records. Preserve the four directional statuses,
first-valid intake, existing native report digests, and the non-compensation
boundary. Custom registries are explicit; malformed containers and timestamp
controls fail predictably.

Synchronize the manuscript, figures, family descriptions, metadata and tested
claim boundaries. Add standalone CI, mypy, generated-ledger verification, a
legacy-format fixture, and mutation controls. The new archive sidecar is versioned
separately from the unchanged native serialization. See
[the full disposition](docs/reviews/2026-10-20.md) for G1–G11 and adaptations.

The existing verified Zenodo DOI is retained; a new deposition requires Daniel's
reserve-first step. The dated release packet records the actual gates and render
checksums.

## 0.4.1 — 2026-09-18

Publication reversion: the 0.4.x tree was re-deposited under the new Zenodo
version DOI `10.5281/zenodo.22833506`, updating `CITATION.cff` and
`docs/manuscript/config.yaml` only. No evaluator, registry, or figure change.

## 0.4.0 — 2026-07-29

The envelope window: the cross-instrument report envelope plus its manuscript
formalism, version bumped with the window as TODO promised.

### Envelope and formalism

- `envelope.py` exports the common report envelope under
  `line.report-envelope/1.0`: a digest pointer (`report_ref`, the SHA-256 of
  the existing `canonical_report` serialization), the review date, the registry
  version and digest the report recorded, caller-supplied source snapshot
  references, and the instrument's non-claims riding inside every envelope.
  `native_status` is the complete ordered per-aspiration readings in this
  instrument's own vocabulary — Golden Line has no single overall verdict, and
  the envelope does not invent an aggregate. `envelope_matches_report` is the
  read-back check for an archived pair.
- `docs/manuscript/02a_formalism.md` gained `def:report_envelope` and
  `prop:envelope_pointer` with binding-table rows, two new binding tests proven
  to bite via planted drifts, and claim-ledger block counts moved.
- Re-rendered with zero undefined references.

### Other

- 13 SVG figures gained accessibility markup (`role="img"`,
  `aria-labelledby`, `<title>`, `<desc>`) via `_canvas()` modification.
- 13 section labels added to the manuscript; navigation paragraph added to
  `01_introduction.md`.
- `tests/AGENTS.md` corrected to list all 20 test files accurately.
- `scripts/AGENTS.md` corrected (removed stale test reference).
- `src/golden_line/AGENTS.md` gained `envelope.py`.
- All READMEs with sibling AGENTS.md now redirect to it (10 READMEs fixed).

### Gates

- Full suite: 265 passed.
- Registry battery: 7/7 PASS at `registry_version=2026.07.18`, digest
  `3e0a7e38ecec…`.
- Figure build: 13/13; artifact chain PASS.
