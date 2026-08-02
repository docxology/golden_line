---
name: golden-line
description: Operate the Golden Line aspirational-direction instrument — a versioned registry plus staged progress_report evaluator and a pure descriptive-analysis layer, returning bounded directional readings, never scores, safety claims, or permission. USE WHEN reading long-horizon aspirations, recording markers/counter-signals, checking registry soundness, or drawing signal/horizon/currentness figures.
---

# Golden Line local skill

Golden Line records what work is *reaching toward* over a long horizon and reads
observable movement toward it. It emits one of four directional readings per
aspiration and never a grade. A reading describes a *record*, not a person,
project, virtue, safety state, legality, or permission.

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
2. `DRIFTING` — a declared counter-signal was recorded. Precedence is absolute:
   a positive marker can never launder a recorded drift, even when stale.
3. `INQUIRY` — named but evidence is empty, partial, stale, or not
   currentness-auditable. Uncertainty reopens the question; it never condemns.
4. `TOWARD` — every declared marker observed, no counter-signal, and (when
   temporal review is on) currentness auditable.

## Staged intake semantics

`progress_report` runs three stages and never raises on malformed or hostile
input — it *records* the problem:

1. **Intake screening** — one entry per known id (first valid wins); unknown ids,
   duplicates, and malformed records are set aside and named in `intake_notes`.
   JSON-style token lists are normalized to sets.
2. **Matching** — observed tokens are intersected with the *declared* markers and
   counter-signals. Undeclared tokens are ignored and noted; they can never
   determine a status.
3. **Decision** — matched sets plus optional temporal quality select one reading.

## Temporal review

Enabled only when `stale_after_days` is set. A missing or non-ISO `observed_on`
sets `date_issue=True` — not fatal, but it cannot certify currentness, so a
fully-marked record reverts to `INQUIRY`. A future-dated or over-threshold
observation is `stale` and also reverts to `INQUIRY`. A recorded counter-signal
still yields `DRIFTING` regardless of age.

## Descriptive analysis layer

Four pure, deterministic helpers in `golden_line.analysis` read the frozen
registry or replay the evaluator; none changes semantics or emits a score.

```python
from golden_line import (
    signal_inventory, horizon_distribution,
    temporal_currentness_sweep, report_overview,
)

signal_inventory()          # declared-token vocabulary: 18 markers / 9 counter-signals,
                            # all distinct — reachability, not fulfilment.
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
`batch_reading_overview`, embedded in `manuscript/03_aspirations.md`,
`02a_formalism.md`, and `04a_batch_reading.md`. Bands widen reach; the order is
a reading aid, never a rank. The lattice replays the sweep for all nine
aspirations at once, and `counter_signal_dominance` in
`manuscript/04_examples.md` replays clause precedence for all nine — both are
executed evaluator output, not drawn assertions.

## The report envelope (cross-instrument transport)

```python
from golden_line import report_envelope, canonical_envelope, envelope_matches_report

envelope = report_envelope(report, subject_id="your reference for what was reviewed")
archived = canonical_envelope(envelope)   # store beside canonical_report(report)
envelope_matches_report(envelope, report) # read-back check for an archived pair
```

One `line.report-envelope/1.0` record pointing at the complete canonical
report by SHA-256. `native_status` is the complete ordered per-aspiration
readings — no aggregate is invented — and the instrument's non-claims travel
inside the record. Never compare, rank, average, or merge `native_status`
across lines.

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

- Version authority is `manuscript/config.yaml`. The literal is unavoidably
  duplicated in `pyproject.toml` and `src/golden_line/version.py`, so bump all
  three together; `tests/test_api.py::test_version_markers_agree_with_the_declared_authority`
  compares the copies to the authority and fails if one lags.
- New figure files must be BOTH built by `scripts/build_figures.py` AND embedded
  in a `manuscript/*.md`; `check_artifacts.py` fails on stale/uncited figures.
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
