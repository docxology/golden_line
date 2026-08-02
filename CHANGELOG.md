# Changelog

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
- `manuscript/02a_formalism.md` gained `def:report_envelope` and
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
