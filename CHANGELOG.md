# Changelog

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
