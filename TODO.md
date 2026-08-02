# Deferred work

## Completed — 2026-08-01 figure-geometry consistency pass

- [x] Figure-geometry claim drift fixed and gated. `manuscript/config.yaml` had
      moved to a four-sided `metadata.geometry`
      (`left=0.33in,right=0.33in,top=0.58in,bottom=0.58in`), but
      `tests/test_figure_legibility.py`'s `_page_margin_inches()` still parsed a
      single `margin=…in` form, so five tests failed (the print-floor gate, its
      two proof-of-detection cases, the measured-floor check, and the
      rendered-log cross-check); `docs/development.md` and
      `manuscript/config.yaml.example` still carried the stale single-margin
      form. `_page_margins_inches()` now parses the four-sided geometry into
      horizontal/vertical per-side margins, matching the rendered LaTeX log
      (textwidth 566.60pt, textheight 711.14pt). The example and docs were
      realigned, and a new regression test
      (`test_geometry_is_four_sided_and_matches_its_own_example`) pins that the
      geometry is four-sided and that the example matches the live config, so
      this exact drift cannot silently return.
- [x] Ruff hygiene restored to a clean gate: fixed the pre-existing E712
      (`== False`) in `tests/test_formalism_bindings.py` and reapplied the
      `ruff format` drift (10 files) left by a newer ruff than the tree was
      formatted with, so both `ruff check` and `ruff format --check` pass.
      No figure output or evaluator logic changed — the deterministic rebuild
      stayed byte-stable.
- [x] Measured at close (2026-08-01): full suite 267 passed (0 skipped, 0
      failed), branch coverage 99.44% (floor 90%), registry battery 7/7 PASS at
      `registry_version=2026.07.18`, figure build 13/13, artifact chain PASS at
      digest `3e0a7e38ecec…`.

## Completed — 2026-07-29 common report envelope

- [x] Cross-instrument report envelope (`src/golden_line/envelope.py`,
      `line.report-envelope/1.0`): `ReportEnvelope`, `report_envelope`,
      `canonical_envelope`, `envelope_matches_report`, and transportable
      non-claims (`SCOPE_AND_NONCLAIMS`), pointing at the existing
      `canonical_report`/`report_digest` serialization without changing the
      evaluator, the registry, or any digest. `native_status` exports the
      complete ordered per-aspiration readings; no aggregate is invented.
- [x] `tests/test_report_envelope.py` (12 tests: determinism and completeness
      of the canonical target, field-by-field envelope binding, per-field
      tamper detection via `dataclasses.replace`, fail-closed input
      validation, and the non-claims traveling inside the envelope).
      Measured this window (2026-07-29): 257 tests passed; total branch
      coverage 99.56% (floor 90%); `envelope.py` 100.00% branch; registry
      battery 7/7 PASS; figure build 13/13; artifact chain PASS at
      registry_version=2026.07.18.
- [x] `docs/correspondence.md` records the 2026-07-29 "Space Between the
      Lines" review and the adopted/deferred/declined mapping; README and
      `docs/architecture.md` document the envelope surface.

## Completed — 2026-07-29 second window: the envelope stated formally

- [x] `manuscript/02a_formalism.md` gains "The report envelope":
      `def:report_envelope` (the ten fields in order, bound to
      `dataclasses.fields(ReportEnvelope)`; `native_status` the complete
      ordered per-aspiration pairs, never a summary — the aggregate this
      instrument refuses everywhere else is refused here too) and
      `prop:envelope_pointer` (the pointer agreement, every stated field
      edit visible), each with a binding-table row in a third table that
      keeps the label-order gate satisfied. Two new binding tests re-derive
      the field roster and the pointer property from a live
      `progress_report` → `report_envelope` flow; both were proven to bite
      by planting drifts in the real manuscript (a dropped
      `native_status` component, a weakened "editing any of them" claim) and
      watching exactly the named test fail before byte-identical
      restoration. The claim ledger's formal block counts moved 10 → 11
      definitions and 11 → 12 propositions.
- [x] Version bump 0.3.0 → 0.4.0 taken with the window, in the four bound
      sites (version.py, pyproject.toml, manuscript/config.yaml, README).
- [x] Measured at close (2026-07-29, my own runs): 259 tests passed
      (257 + 2), total branch coverage 99.56%, registry battery 7/7 PASS at
      digest `3e0a7e38ecec…`, figure build 13/13, artifact chain PASS,
      re-rendered through the external engine with zero undefined
      references, stage-04 validation passing (two engine bookkeeping
      warnings, non-critical), PDF staged to
      `~/Downloads/golden_line_combined_0.4.0_2026-07-29.pdf`.

## Open — from the 2026-07-29 window, deferred with a stated reason

- The shared witness register the review proposes (co-registration of the
  instruments' envelopes, cross-line relations, append-only history) is a
  separate work by design and is deliberately not implemented in this
  repository. Golden Line's contribution is the envelope export above; see
  [docs/correspondence.md](docs/correspondence.md).

## Current validation evidence

The applicable evidence boundary is the four local commands named in
[`docs/development.md`](docs/development.md) — the test suite (which includes
the print-legibility gate over the figures), the registry battery, the
deterministic figure build, and the artifact gate — followed by rendered
PDF/HTML validation in a checkout of the external publication engine
(<https://github.com/docxology/template>). A future release should attach the
exact report outputs to its release packet. The strict publication and methods
audits run in that engine checkout rather than here; their repository-boundary
findings describe where a project is linked from and are not evidence that the
evaluator or manuscript is unsound.

## Integrity and template-status gaps

No external attestation or independent observation provenance is claimed. The
project is its own repository, but no release packet with attached report
outputs has been published yet.

## Configurable-surface gaps

The registry is source-configured in Python rather than loaded from an external
editable data file. Moving it to a data file would require a new validation and
provenance contract.

## Documentation and signposting gaps

The four-line set remains cross-linked by repository references; it is not
merged into one evaluator. Keep those references current when the companion
repositories change, and never let one become a relative path out of this
repository.

## Test and validator gaps

The evaluator does not independently verify who supplied an observation or
whether a marker is true in the world.

- [Low] `mypy` is not configured for this repository (no `[tool.mypy]`, no
  `mypy.ini`/`.mypy.ini`/`setup.cfg`, and `mypy` absent from the dev
  dependency group), so `uv run mypy` is not part of the local gate; the
  canonical surface is the four commands in `docs/development.md` plus ruff
  (see `scripts/AGENTS.md`). Running mypy on the src-layout package currently
  reports only src-layout module-resolution noise (`import-not-found`,
  duplicate-module), not type errors. If type-checking is desired, wire a
  `[tool.mypy]`/`MYPYPATH=src` config and add `mypy` to `[dependency-groups]
  dev` — affected paths: `pyproject.toml`, `src/golden_line/`. Not done this
  window to avoid adding an unrequested gate.

## Ordered improvement ladder

1. Preserve the structural and artifact gates.
2. Add independently authored observation provenance only with a testable
   contract.
3. Add a human-reviewed conflict record without introducing an aggregate score.

- Add an independently authored observation ledger format when the surrounding
  DAF workflow has a stable provenance requirement; the current package accepts
  caller-supplied `HorizonEntry` records but does not verify who observed them.
- Add a separate, human-reviewed conflict record for cases where two
  aspirations pull in opposite directions; the evaluator intentionally refuses
  to aggregate or resolve those tensions.
- Run the external publication engine's rendered PDF/HTML audit whenever the
  manuscript is published or that engine changes.
