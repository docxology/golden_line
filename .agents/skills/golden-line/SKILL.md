---
name: golden-line
description: Operate the Golden Line aspirational-direction instrument — a versioned registry plus staged progress_report evaluator and a pure descriptive-analysis layer, returning bounded directional readings, never scores, safety claims, or permission. USE WHEN reading long-horizon aspirations, recording markers/counter-signals, checking registry soundness, or drawing signal/horizon/currentness figures.
---

# Golden Line local skill

Golden Line records what work is *reaching toward* over a long horizon and reads
observable movement toward it. It emits one of four directional readings per
aspiration and never a grade. A reading describes a *record*, not a person,
project, virtue, safety state, legality, or permission.

The founding four describe the origin; the current family has eight instruments,
one reader, and one witness register. Golden direction does not establish Green
capacity, Blue commitment, or Violet consent.
Sibling source availability and access controls are separate from this declared
roster; no sibling source is required to operate Golden Line.

## What the instrument is (and is not)

- IS: a directional record over a versioned nine-entry aspiration registry, plus
  a pure analysis layer that characterizes the registry and replays the evaluator.
- IS NOT: a compliance score, accreditation, moral authority, or permission
  mechanism. `NOT_OBSERVED` means no valid entry was admitted — never that the
  aspiration is absent or that nobody looked.

## Quick start (from project root)

Run the canonical local gate sequence in
[`docs/development.md`](../../../docs/development.md) with `uv`. It covers the
contract suite, registry battery, deterministic thirteen-figure build, and
source-to-artifact gate.

## Core API — `progress_report`

```python
from golden_line import HorizonEntry, progress_report

report = progress_report(
    [
        HorizonEntry(
            aspiration_id="repairable-systems",
            observed_markers=frozenset({"failure named", "revision attempted"}),
            counter_signals=frozenset(),
            note="Failure recorded before the release note was written.",
            observed_on="2026-07-18",
        )
    ],
    as_of="2026-07-20",           # optional review date
    stale_after_days=30,          # optional — enables temporal review
)
report.counts()  # tally per status; a summary, not a score
```

Every finding carries a full `reasons` trail **plus** structured fields
(`observed`, `unmet`, `countered`, `ignored_markers`, `ignored_counter_signals`,
`note`, `observed_on`, `stale`, `date_issue`) so a reader never parses prose to
recover the derivation. The report also records `registry_version`,
`registry_digest`, `as_of`, and `stale_after_days`.

## The four readings (decision order — first match wins)

1. `NOT_OBSERVED` — no admitted entry for that aspiration.
2. `DRIFTING` — a declared counter-signal occurs in the admitted entry. Within
   that entry it takes precedence over every marker and date condition; a
   rejected contrary duplicate does not change the admitted entry's reading.
3. `INQUIRY` — an admitted entry has empty or partial declared markers, or its
   positive evidence fails an enabled temporal review.
4. `TOWARD` — every declared marker observed in the admitted entry, no declared
   counter-signal there, and (when temporal review is on) currentness auditable.

## Staged intake semantics

`progress_report` runs three stages and records supported malformed passive
entry data. Arbitrary executable iterators and invalid controls are outside
that promise; see [claim boundaries](../../../docs/claim_boundaries.md).

1. **Intake screening** — one entry per known id (first valid wins); unknown ids,
   duplicates, and malformed records are set aside and named in `intake_notes`.
   JSON-style token lists are normalized to sets.
   A malformed entry does not reserve an ID. A duplicate requires an earlier
   valid admitted entry for that ID, so it cannot by itself cause that
   aspiration to read `NOT_OBSERVED`. No admitted entry means `NOT_OBSERVED`;
   a valid empty entry means `INQUIRY`.
2. **Matching** — observed tokens are intersected with the *declared* markers and
   counter-signals. Undeclared tokens are ignored and noted; they can never
   determine a status.
3. **Decision** — matched sets plus optional temporal quality select one reading.

## Temporal review

Enabled only when `stale_after_days` is set. A missing or non-ISO `observed_on`
sets `date_issue=True` — not fatal, but it cannot certify currentness, so a
fully-marked record reverts to `INQUIRY`. A future-dated or over-threshold
observation is `stale` and also reverts to `INQUIRY`; age exactly at the threshold
remains current. A counter-signal in the admitted entry still yields `DRIFTING`
regardless of age. Without a window, `currentness_evaluated` is false and an
undated complete-marker entry can be `TOWARD` without any freshness claim.

## Descriptive analysis layer

Four pure, deterministic helpers in `golden_line.analysis` read the frozen
registry or replay the evaluator; none changes semantics or emits a score.

```python
from golden_line import (
    signal_inventory, horizon_distribution,
    temporal_currentness_sweep, report_overview,
)

signal_inventory()          # declared-token vocabulary: 18 markers / 9 counter-signals,
                            # all distinct — reachability, not fulfillment.
horizon_distribution()      # groups 9 aspirations into 4 declared HORIZON_BANDS
                            # (immediate 1, recurring cycle 2, at handoff 4, open-ended 2);
                            # a registry horizon outside the map raises — no silent drop.
temporal_currentness_sweep( # replays one fully-marked entry across observation ages;
    "repairable-systems", [0, 15, 30, 45],
    as_of="2026-07-20", stale_after_days=30,
)                           # TOWARD at ages 0/15/30, flips to INQUIRY (stale) at 45.
report_overview(report)     # regroups an existing report by status with intake/ignored
                            # totals; adds no claim the findings did not carry.
```

These map to figures `signal_inventory`, `horizon_bands`,
`temporal_currentness_sweep`, `currentness_lattice`, and
`batch_reading_overview`, embedded in `docs/manuscript/03_aspirations.md`,
`02a_formalism.md`, and `04a_batch_reading.md`. Bands widen reach; the order is
a reading aid, never a rank. The lattice replays the sweep for all nine
aspirations at once, and `counter_signal_dominance` in
`docs/manuscript/04_examples.md` replays clause precedence for all nine — both are
executed evaluator output, not drawn assertions.

## The report envelope (cross-instrument transport)

```python
from golden_line import (
    GOLDEN_ASPIRATIONS, HorizonStatus, canonical_archive, canonical_envelope,
    decode_archive, envelope_matches_report, report_envelope,
)

aspiration = GOLDEN_ASPIRATIONS[0]
positive = HorizonEntry(aspiration.id, frozenset(aspiration.markers))
contrary = HorizonEntry(
    aspiration.id,
    counter_signals=frozenset(aspiration.counter_signals),
    note="Recipient disputes the earlier observation.",
    observed_on="2026-10-19",
)
transport_report = progress_report([positive, contrary], as_of="2026-10-20")
envelope = report_envelope(
    transport_report, subject_id="your reference for what was reviewed"
)
archive_json = canonical_archive(transport_report)
envelope_json = canonical_envelope(envelope)
restored = decode_archive(archive_json, envelope_json)
assert restored == transport_report
assert restored.findings[0].status is HorizonStatus.TOWARD
assert restored.intake_archive[1].entry == contrary
assert envelope_matches_report(envelope, restored)
```

One `line.report-envelope/1.0` record pointing at the complete canonical
report by SHA-256. `native_status` is the complete ordered per-aspiration
readings — no aggregate is invented — and the instrument's non-claims travel
inside the record. Never compare, rank, average, or merge `native_status`
across lines.

`validate_instrument_envelope` checks identity and mandatory non-claims separately
from correspondence. Agreement does not prove an unedited archive. The unchanged
native serialization sorts findings by ID; the archive adds separately hashed
normalized intake without changing native digest identity. `decode_archive`
restores order through an envelope ID bijection. The rejected contrary duplicate
above remains inspectable but does not determine the reading. No temporal review
was requested, so the undated `TOWARD` does not establish freshness.
Keep original source bytes separately, especially malformed input that cannot be
normalized. Source references remain unverified caller metadata; tuple/list
reference order and duplicates are preserved.

Custom registries must pass `validate_registry`; empty scopes and one-shot
signal iterators are rejected. Their version is explicitly labeled custom.
Optional provenance/conflict side records preserve human disagreement without
changing readings. Retain their `canonical_evidence_records` export separately:
neither the archive nor envelope bundles it. See
[evidence records](../../../docs/evidence-records.md).

## Invariant battery

`all_invariants(GOLDEN_ASPIRATIONS)` runs seven pure structural checks over the
registry *shape* (distinct ids, populated fields, reachable statuses, signal
text, signal uniqueness, signal disjointness, digest stability);
`registry_sound(...)` is their conjunction. Each check is proof-of-detection
tested — it must both pass on the real registry and fail on a planted-bad one.
A passing battery is evidence of structural integrity only, never of any
aspiration being true or any work being good. The `registry_digest` is a review
and drift-detection handle with no safety or attestation semantics.

## Gotchas

- Version authority is `docs/manuscript/config.yaml`. The literal is unavoidably
  duplicated in `pyproject.toml` and `src/golden_line/version.py`, so bump all
  three together; `tests/test_api.py::test_version_markers_agree_with_the_declared_authority`
  compares the copies to the authority and fails if one lags.
- New figure files must be BOTH built by `scripts/build_figures.py` AND embedded
  in a `docs/manuscript/*.md`; `check_artifacts.py` fails on stale/uncited figures.
- Standalone invariant: never copy prose, registry entries, or code from Red,
  Black, or White Line, and never import them. They are separate repositories
  and are referenced by URL, never by a relative path out of this one.
- No mocks: tests use real data, real files (`tmp_path`), fixed seeds.

## Change discipline

Any registry, status, or method change must update tests, docs, manuscript,
`output/figures/`, and the artifact gate together. Run the commands in the
project `docs/development.md` and validate the source-to-artifact chain before
asking the rendering toolchain to render. Rendering runs in a separate checkout
of <https://github.com/docxology/template>, cloned anywhere, with this
repository linked in under a qualified project name; the path-independent
commands are in `docs/development.md`. Strict public publication auditing runs
there rather than here — do not weaken that public validator or call this
project published.
