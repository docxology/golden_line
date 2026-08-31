# Limits and safeguards {#sec:limits}

Aspiration language can become sentimental, coercive, or falsely universal, and
a directional instrument can be misread as a verdict. Golden Line therefore
carries six hard limits. Three of them have a mechanical core the code
enforces, and the proposition that pins each one is named inline; the other
three are commitments the code cannot hold for us, and saying so is part of
keeping them.

- *Commitment.* A registry entry is a design choice, not a discovery of
  humanity's single highest good. The nine aspirations are a starting set,
  versioned and revisable, not a closed canon.
- *Enforced ([@prop:toward_exact]).* A `TOWARD` result says only that declared markers
  were observed, no counter-signal was recorded, and (when temporal review is
  enabled) currentness was auditable from a present, parseable, in-window date.
  Those conditions are necessary and sufficient in the code. That the result
  does not prove the work good, safe, lawful, or beneficial is a reading rule,
  not a check.
- *Enforced ([@prop:absence]).* A `NOT_OBSERVED` result arises solely from the
  absence of an admitted entry. It is not evidence that the aspiration is
  absent; submitted records may have been malformed, unknown, or duplicate, and
  the intake notes say which.
- *Commitment.* Counter-signals are local warnings about a record, not
  psychological diagnoses or public labels for a person or project. Nothing in
  the evaluator can stop a reader from using one that way.
- *Enforced ([@def:intake; @prop:temporal_inquiry]).* A malformed entry is visible as an
  intake set-aside, and a missing or malformed date in an enabled temporal
  review prevents a positive record from being read as current. These are
  data-quality safeguards, not proof that the underlying work failed.
- *Commitment.* The instrument cannot resolve conflicts among affected people;
  it can only make the chosen direction and its tradeoffs easier to discuss.
  This is an absence rather than a check, and no test can confirm it.

The sharpest risk is the one the scholarship section names: that a published
aspiration hardens into a target and is gamed rather than served
[@strathern1997audit], or that stating the direction as a scorecard evokes the
very behavior it was meant to describe [@merton1948prophecy]. The design pushes
against this at every stage: no numeric score, no aggregate grade,
counter-signals surfaced first, absence read as inquiry, and no positive
currentness claim from malformed temporal data. What it does not touch is the
adversarial case [@manheim2018goodhart]: the evaluator matches the tokens an
observer filed against the registry, so an observer who wants a `TOWARD` can
file the tokens that produce one, and no clause ordering prevents it. The honest
safeguard is to keep the readings directional and the responsibility human, in
the spirit of Jonas's long-horizon duty rather than a compliance ritual
[@jonas1984responsibility].

## Limits of the descriptive analysis layer

The descriptive helpers — `signal_inventory`, `horizon_distribution`,
`temporal_currentness_sweep`, and `report_overview` — introduce their own,
smaller risks of over-reading, and each is deliberately constrained so it cannot
outrun the evaluator it sits beside.

- The inventory counts declared *vocabulary*, never fulfilment. That the registry
  declares eighteen markers and nine counter-signals says nothing about how many
  have ever been observed; a larger marker count is not a higher standard, only a
  longer list of things one could look for. Reading the inventory as a scoreboard
  would invert its purpose.
- The horizon bands are an interpretive reading aid declared in the analysis
  layer, not part of the registry contract. Their order widens temporal reach; it
  does not rank merit, and an "open-ended" horizon is not superior to an
  "immediate" one. The band map is intentionally brittle: an aspiration whose
  horizon it does not classify raises an error rather than being dropped, so a
  future registry change forces the map to be revisited by a human instead of
  silently mis-grouping an entry.
- The currentness sweep replays **one** fully-marked, counter-signal-free
  synthetic entry to expose where a reading loses currency. It is a probe of the
  evaluator's temporal rule under a chosen `stale_after_days`, not a claim about
  any real observation, and the staleness boundary it draws is a data-quality
  threshold — a `stale` cell is an invitation to look again, never evidence that
  the underlying work failed. The lattice widens the probe to every registry
  entry, which rules out the boundary being an artifact of the one entry
  chosen; it does not make the entries any less synthetic.
- `report_overview` regroups and counts findings that already exist; it adds no
  claim the report did not carry and derives nothing from outside the report's own
  structured fields. Its per-status tallies are a summary, and a batch that reads
  mostly `NOT_OBSERVED` is a small record, not a poor one.

Because all four helpers are pure, deterministic, and read-only, they cannot
change what a reading means — but a reader can still misuse a number. The
safeguard is the same one the whole instrument relies on: keep the summaries
descriptive and the judgement human.

For security boundaries, use Red Line. For how the work was performed, use Black
Line. For what is missing, withheld, unobserved, or ethically left unclaimed, use
White Line. A horizon report must never be used to bypass those scopes, and a
`TOWARD` on any Golden Line aspiration can never authorize what Red Line refuses.
