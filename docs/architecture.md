# Architecture

Golden Line is a small modular package. Each module answers one question and
none of them import any other line project.

| Module | Question it answers |
| --- | --- |
| `src/golden_line/version.py` | Which package and registry revision is this? |
| `src/golden_line/paths.py` | Where is the project root, independent of module depth? |
| `src/golden_line/models.py` | What are the record types (aspiration, entry, finding, report)? |
| `src/golden_line/registry.py` | What are the nine versioned aspirations? |
| `src/golden_line/progress.py` | How is a directional report produced, and how is a record admitted or set aside? |
| `src/golden_line/serialization.py` | What is the canonical form and digest of a registry or report? |
| `src/golden_line/envelope.py` | How does a complete report travel to a co-registration layer without being reinterpreted? |
| `src/golden_line/invariants.py` | Is the registry structurally sound? |
| `src/golden_line/analysis.py` | What does the registry vocabulary and the evaluator's behaviour look like? |
| `src/golden_line/figures/` | How is each figure drawn deterministically from source? |
| `src/golden_line/artifacts.py` | Do the generated artifacts still agree with the source? |

## Staged reporting

`progress_report` is deliberately staged so a bad record cannot crash the
report or vanish silently:

1. **Screening.** Entries are checked for the expected record shape. Unknown
   aspiration ids, duplicates, and malformed records are set aside and
   recorded in the report's `intake_notes`. The first valid entry for an
   aspiration stands. JSON-like token lists are normalized to frozensets.
2. **Signal reading.** Observed markers and counter-signals that the
   aspiration never declared are ignored, with a reason on the finding — an
   entry cannot invent its own evidence vocabulary.
3. **Temporal review** (optional, additive). When the caller passes
   `stale_after_days`, a dated observation older than the window — or dated
   after the review date — reverts a would-be `TOWARD` to `INQUIRY`. A missing
   or malformed date also prevents currentness from being certified. A
   recorded counter-signal is never erased by age: `DRIFTING` stands.
4. **Structured derivation.** Every finding carries non-empty `reasons`, plus
   `observed`, `unmet`, `countered`, ignored-token lists, the source note, and
   temporal flags, so a consumer need not parse prose to audit the status.
5. **Report provenance.** Every report records the registry version/digest and
   the review date and staleness threshold used to produce it.

The original call form `progress_report(entries)` is unchanged; the staleness
parameters and the new finding/report fields are additive. Invalid control
parameters fail loudly; invalid entry records are visible set-asides.

## Digest semantics

`registry_digest` and `report_digest` are review and drift-detection
instruments: two readers or two revisions compare a short hex string to
confirm they hold the same content. A digest carries no safety, warranty, or
attestation semantics, and no status in this project is a compliance verdict.

`artifacts.py` extends this boundary to generated outputs through
`check_artifacts()`, which checks the source-derived registry snapshot, figure
registry metadata, SVG/PNG pairs, expected figure set, and manuscript label
citations. `scripts/check_artifacts.py` is the CLI over that function.

## Common report envelope

`envelope.py` exports the cross-instrument report envelope
(`line.report-envelope/1.0`): `report_envelope` wraps a `HorizonReport` in a
frozen record whose `report_ref` is the SHA-256 of `canonical_report`, whose
`native_status` is the complete ordered per-aspiration readings (this
instrument has no single overall verdict and none is invented), and whose
`scope_and_nonclaims` carries the instrument boundary inside the record.
`canonical_envelope` gives the stable JSON archive form and
`envelope_matches_report` verifies an archived pair. The envelope points at
the native report and never reinterprets it; sibling instruments export the
same shape by publishing the same schema string, never by import. Design
provenance is recorded in [correspondence.md](correspondence.md).

## Structural soundness

`invariants.py` holds the structural check battery described in
[invariants.md](invariants.md). `scripts/check_registry.py` runs the battery
and exits non-zero if any check fails, then prints the registry version,
entry count, and digest.

## Descriptive analysis layer

`analysis.py` holds four pure, deterministic helpers that read the frozen
registry or replay `progress_report`. None changes evaluator semantics or emits
a score:

- `signal_inventory` tallies the declared marker and counter-signal vocabulary
  per aspiration and in aggregate — a reachability count, not fulfilment.
- `horizon_distribution` groups aspirations into the declared `HORIZON_BANDS`
  (an interpretive reading aid, not part of the registry contract); an
  unclassified horizon raises rather than being silently dropped.
- `temporal_currentness_sweep` replays one fully-marked, counter-signal-free
  entry through the real evaluator across a range of observation ages, exposing
  the `TOWARD` → `INQUIRY` currentness boundary.
- `report_overview` regroups an existing `HorizonReport` by status with intake
  and ignored-token totals, adding no claim the findings did not carry.

`figures/analysis_figures.py` turns these helpers into five of the thirteen
figures: `signal_inventory`, `horizon_bands`, `temporal_currentness_sweep`,
`currentness_lattice`, and `batch_reading_overview`. The layer is wired
into the method (`domain_profile.yaml` gates and `experiment_plan.yaml`
conditions are named in `manuscript/02_method.md`).

## Figure package

`figures/` is split by concern so no single module owns the whole drawing
surface: `svg.py` holds the palette and text primitives, `core_schematics.py`
draws the registry and evaluator schematics, `analysis_figures.py` draws the
analysis-backed figures, `record_figures.py` replays the evaluator for the
marker-completeness panel and the finding-field matrix, and `__init__.py` owns
the `FIGURES` tuple and `build_figures`. The batch figure does not restate the intake rule; it consumes
`classify_intake_entries` from `progress.py` and maps the returned
classification to display text, so the figure and the evaluator cannot drift.
