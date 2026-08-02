# Worked records {#sec:examples}

The model is intentionally small enough to inspect at the command line. A single
horizon entry against one aspiration produces a full report over the whole
registry:

```python
from golden_line import HorizonEntry, progress_report

report = progress_report([
    HorizonEntry(
        aspiration_id="repairable-systems",
        observed_markers=frozenset({"failure named", "revision attempted"}),
        note="The failure was recorded before the release note was written.",
    )
])
```

That entry yields `TOWARD` for `repairable-systems` and `NOT_OBSERVED` for the
other eight registry items, because no horizon note was recorded for them. The
readings move exactly as the decision rule prescribes:

- If the same entry also records the counter-signal `defect hidden to preserve
  appearance`, the finding becomes `DRIFTING`. Counter-signal precedence
  ([@prop:precedence]) means this holds even if both markers are still present;
  a positive signal cannot launder a recorded drift.
- If only one of the two declared markers is present, the finding becomes
  `INQUIRY` with an `unmet` list naming the marker still outstanding, so the
  direction is recorded as open rather than reached — no partial credit
  ([@prop:toward_exact]).
- If both markers are present but the observation carries an old, future, or
  missing/unparseable `observed_on` date and the caller passes
  `stale_after_days`, the finding reverts to `INQUIRY`: temporal uncertainty
  reopens the question without inventing drift ([@prop:temporal_inquiry]).
- An entry naming an aspiration that is not in the registry is set aside during
  intake ([@def:intake]) and reported in the intake notes; it never crashes the
  report and never silently disappears.
- A malformed record, such as one whose marker field is `None`, is also set
  aside and named in the intake notes ([@def:intake]). If a dated positive
  record is supplied with temporal review enabled but its date is not
  ISO-parseable, the finding is `INQUIRY` with `date_issue=True`
  ([@prop:temporal_inquiry]): malformed time metadata cannot certify
  currentness.

![A batch of horizon entries passes through intake screening, signal matching, and decision. Records that fail intake — malformed, unknown-id, or duplicate — are set aside into visible intake notes (quoted verbatim from a real progress_report replay), undeclared tokens are ignored and noted, and the output is one bounded finding per registry aspiration. Findings are directional readings, never grades.](../output/figures/staged_evaluation_pipeline.png){#fig:staged_evaluation_pipeline width=95%}

The first of those bullets is the one most worth distrusting, because it is the
rule a reader is most likely to assume has an exception. It does not. Running
all nine aspirations through four evidence conditions — complete markers alone,
complete markers with one declared counter-signal, a counter-signal with no
markers, and a counter-signal on an observation four hundred days old — returns
`DRIFTING` in every cell where a counter-signal is present, including all nine
cells where every declared marker is also present. [@fig:counter_signal_dominance]
is that run: each cell in it is a `progress_report` return value rather than a
box drawn to illustrate one.

![Counter-signal precedence replayed rather than drawn: for each of the nine aspirations, four progress_report calls at review date 2026-07-18 with stale_after_days = 90. Complete markers with no counter-signal read TOWARD; adding one declared counter-signal returns DRIFTING even though every marker is still present, and it still returns DRIFTING when the same observation is stale. Filled cells are DRIFTING and outlined cells are not, so the panel reads without colour. The panel characterizes clause order; it does not grade any work or person.](../output/figures/counter_signal_dominance.png){#fig:counter_signal_dominance width=95%}

These distinctions keep a positive signal from laundering a counter-signal
([@prop:precedence]), and keep the absence of evidence from masquerading as
either success or failure ([@prop:absence]). The
path from an entry to its reading is shown in [@fig:horizon_decision_path], and
the three evaluator stages an entry passes through — including the set-aside
branch that carries malformed, unknown-id, and duplicate records into the
intake notes — are shown in [@fig:staged_evaluation_pipeline], while the
bounded meaning of all four readings is summarized in
[@fig:evidence_state_matrix].

A single entry shows the decision rule in isolation. The next section runs a
whole batch — positive, drifting, partial, malformed, and duplicate entries at
once — through the same evaluator and the descriptive analysis layer, so the
gap between what was submitted and what was read becomes fully accountable.
