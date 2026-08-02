# Method: aspiration as a directional record {#sec:method}

## The registry entry

An aspiration has six fields: an identifier, a plain-language title, a thread
that explains its direction, a horizon at which the direction becomes visible,
and two short lists. **Markers** are observable signs that the work is moving in
the declared direction. **Counter-signals** are observable signs that it is
drifting away from it. Neither list is exhaustive, and neither is a
questionnaire; they are the small, concrete anchors that let a direction be
discussed rather than merely admired. The registry ships nine such entries: four
founding aspirations and five further ones that fill out the long-horizon
picture.

## The horizon entry

An observer records movement by filing a **horizon entry**: the aspiration
identifier, the set of markers actually observed, the set of counter-signals
actually observed, a free note, and an optional ISO observation date. The entry
describes a *record* of work at a moment, not a person and not a project as a
whole.

## The staged evaluator

`progress_report` reads a batch of horizon entries against the versioned
registry in three stages, and every finding it returns carries a full reasons
trail plus structured derivation fields so no reading arrives unexplained.

1. **Intake screening.** Each incoming entry is checked for the expected record
   shape and against the known aspiration identifiers. An entry for an unknown
   aspiration is set aside with a note; a second valid entry for an aspiration
   already seen is set aside, and the first entry stands. JSON-like token lists
   are normalized to sets. Malformed or hostile input is *recorded*, never
   raised. A sloppy record cannot crash the report or vanish silently.
2. **Matching.** For each aspiration, the observed markers are intersected with
   the declared markers, and the observed counter-signals with the declared
   counter-signals. Tokens the observer supplied that the registry never
   declared are ignored and noted; they cannot smuggle in a status.
3. **Decision.** With optional temporal review folded in, the matched sets
   and temporal quality determine one of four directional readings. There is no
   numeric score or aggregate grade.

The four readings are:

- `TOWARD` means every declared marker is observed, no counter-signal is
  recorded, and (if temporal review is enabled) currentness is auditable: the
  observation date is present, parseable, and within the declared window.
- `INQUIRY` means the aspiration is named but the evidence is partial, empty, or
  stale, so the direction remains honestly open.
- `DRIFTING` means a declared counter-signal is present. It describes the record,
  not the person or project as a whole.
- `NOT_OBSERVED` means no valid horizon entry was admitted for that aspiration.
  An entry can be present in the input but fail intake because it is malformed,
  unknown, or a duplicate set aside by the first-valid-entry rule.

The finding also preserves the note, observed date, declared counter-signals,
and undeclared tokens that were ignored. This makes the status machine-readable
without requiring a downstream reader to reverse-engineer human-readable
reason strings.

## Conservative precedence

The precedence is intentionally conservative. A counter-signal is surfaced
before any markers are counted, and staleness never erases a recorded drift: a
declared counter-signal yields `DRIFTING` even when the same observation is old.
Partial, stale, or currentness-un-auditable positive evidence reverts to
`INQUIRY` rather than being rounded up to `TOWARD`. This mirrors a satisficing
stance: the evaluator looks for *good enough and current* evidence of direction
and refuses to over-read thin signals [@simon1956rational].

The result is a directional report. It is not an evaluator of worth, a
certification, or a substitute for the Red Line, Black Line, or White Line
instruments.

## Evidence and artifact boundary

The machine has four layers: the versioned registry declares the vocabulary; an
admitted entry records a local observation; the evaluator derives a bounded
reading; and the generated registries and figures preserve what source was
used. No layer is allowed to add a claim that the earlier layer did not carry.
The report's registry version, registry digest, review date, and staleness
threshold therefore travel with the findings. The local artifact gate checks
that the generated JSON, SVG, PNG, and manuscript figure labels still agree
before a sibling template render is attempted.

## The descriptive analysis layer

A small analysis module sits beside the evaluator and is deliberately weaker
than it: every helper is pure, deterministic, and read-only, and none can
change what a reading means. Four helpers are provided.

- `signal_inventory` tallies the declared markers and counter-signals across a
  registry — for the shipped registry, 18 markers and 9 counter-signals, with
  every token distinct — describing the vocabulary the evaluator can match,
  never its fulfilment.
- `horizon_distribution` groups aspirations into four declared temporal-reach
  bands (immediate, recurring cycle, at handoff, open-ended). The band map
  lives in the analysis layer, not the registry contract, and an unclassified
  horizon raises an error so a registry change must revisit the map
  deliberately.
- `temporal_currentness_sweep` replays one fully-marked entry through the
  public `progress_report` across a range of observation ages, exposing the
  exclusive staleness boundary (current at age 90, stale at 91 for a 90-day
  window) as an observed trajectory rather than a claim.
- `report_overview` regroups an existing report by status and totals its
  ignored tokens, temporal flags, and intake notes, so a batch can be
  characterized without re-parsing prose reasons.

The analysis layer is also where the project's experiment plan is grounded. The
repository ships a `domain_profile.yaml` naming the validation gates: structural
invariants, evidence grounding, artifact chain, render validation, and
publication readiness. It also ships an `experiment_plan.yaml` whose three
conditions — the source-registry baseline, the malformed-input guard, and the
temporal-currentness guard — map onto the evaluator's intake stage and temporal
review. The plan's expected figures are the ones the deterministic builder
produces: five through this analysis layer's helpers (the temporal-currentness
sweep, the currentness lattice, the signal inventory, the horizon bands, and the
batch reading overview) and eight straight from the registry, the evaluator, and
the status contracts. The protocol compares reproducible contract outcomes only.
None of these summaries is evidence that any aspiration is true, and none is a
score.
