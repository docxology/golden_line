<!-- Note (2026-07-29): reviewer attribution has been anonymized pending explicit
consent for inclusion in permanently archived DOI records. Attribution will be
restored on confirmation. -->

# Correspondence: design reviews received

This page records external design reviews of Golden Line and what this
repository did about them. It is a decision record, not an endorsement chain:
each item names what was adopted, what was deferred with a reason, and what
was declined with a reason.

## 2026-07-29 — "The Space Between the Lines" (an external reviewer, with an analytic reader)

A two-voiced review of the collected line set (dated source: *The Line Set:
The Collected Volume*, 2026-07-27). Its reading of Golden Line: the
aspirational instrument's selected status is a safe projection that must not
become the whole state — strong support and strong resistance co-present are
not the same as no evidence. Its central proposal for the set: each line
should export one common report envelope pointing at, never reinterpreting,
its complete native report, and the missing layer is a *shared witness
register* that co-registers those envelopes without ranking, averaging,
merging, or overriding any line — "precedence without information
destruction."

**Already answered by existing structure:**

- The projection concern lands more softly here than elsewhere in the set,
  because every `HorizonFinding` already carries its full derivation as typed
  data beside the selected status: `observed`, `unmet`, and `countered`
  co-present on the same finding, ignored tokens, the source note, temporal
  flags, and a non-empty reasons trail. A fully-marked record with one
  recorded counter-signal reads `DRIFTING` while its complete marker evidence
  stays readable on the finding — support and resistance co-present, exactly
  the state the review insists must survive the projection. No factorization
  layer was needed; the whole state was already the exported record.

**Adopted here:**

- *The common report envelope.* `envelope.py` exports the review's first
  implementable piece under `line.report-envelope/1.0`: a digest pointer
  (`report_ref`, the SHA-256 of the existing `canonical_report`
  serialization), the review date, the registry version and digest the report
  recorded, caller-supplied source snapshot references, and the instrument's
  non-claims riding inside every envelope. `native_status` is the complete
  ordered per-aspiration readings in this instrument's own vocabulary —
  Golden Line has no single overall verdict, and the envelope does not invent
  an aggregate. `envelope_matches_report` is the read-back check for an
  archived pair. The canonical serialization and digest the envelope points
  at already existed (`serialization.py`); nothing about the evaluator, the
  registry, or the digests changed.

**Deferred (stated in TODO):** manuscript formalism definitions for the
envelope await the next manuscript window, because every formalism edit
requires a binding-table row, a re-render through the external publication
engine, and an artifact pass; the code, tests, and docs shipped first so the
surface exists before the prose that formalizes it.

**Declined, by design:**

- The shared witness register itself. The review is explicit that it should
  not be smuggled into any existing line, and this repository agrees: Golden
  Line ships its envelope export and stops. A register that stores cross-line
  relations and keeps append-only history is a separate work with its own
  tests and its own claim boundaries.
- Any change that would let the envelope carry a merged verdict, a score, or
  a cross-line comparison. `native_status` is this instrument's readings in
  this instrument's vocabulary; the envelope documentation forbids comparing,
  ranking, averaging, or merging on it, and the non-claims travel inside the
  envelope so a stored copy cannot outgrow them.


### Wave-3 update (2026-07-29, later the same day)

The deferred manuscript window landed: `def:report_envelope` and
`prop:envelope_pointer` in `manuscript/02a_formalism.md` with binding-table
rows, two new binding tests proven to bite via planted drifts, claim-ledger
block counts moved, and the version bump 0.3.0 -> 0.4.0 taken with the
window as this file promised. Re-rendered with zero undefined references.
The skill descriptor gained the envelope surface. The companion register
now exists and accepted this line's actually-exported envelope unmodified.
