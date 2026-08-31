# Reading a batch: the descriptive layer at work {#sec:batch-reading}

A single horizon entry is easy to read by eye. A real review is rarely a single
entry: it is a batch of observations filed against several aspirations at once,
some positive, some drifting, some partial, and a few malformed. The descriptive
analysis layer exists to characterize such a batch without adding any claim the
evaluator did not already make. This section runs one batch end to end so the
helpers can be seen doing exactly — and only — what the formalism permits.

## A worked batch

Consider six submitted horizon entries evaluated against the shipped nine-entry
registry with `progress_report`:

```python
from golden_line import HorizonEntry, progress_report, report_overview

entries = [
    HorizonEntry("attention-before-output",
        observed_markers=frozenset({"question revisited", "context named"})),
    HorizonEntry("repairable-systems",
        observed_markers=frozenset({"failure named", "revision attempted"}),
        counter_signals=frozenset({"defect hidden to preserve appearance"})),
    HorizonEntry("useful-to-others",
        observed_markers=frozenset({"handoff used"})),
    HorizonEntry("honest-uncertainty",
        observed_markers=frozenset({"limit stated beside claim",
                                    "confidence qualified in print",
                                    "extra token that is undeclared"})),
    HorizonEntry("not-a-real-id",
        observed_markers=frozenset({"whatever"})),
    HorizonEntry("attention-before-output",
        observed_markers=frozenset({"question revisited"})),
]
report = progress_report(entries)
overview = report_overview(report)
```

Six entries were submitted, but the report still contains exactly nine findings —
one per registry aspiration — because totality ([@prop:totality]) does not depend on
what was filed. `report.counts()` partitions those nine findings as **two
`TOWARD`, one `INQUIRY`, one `DRIFTING`, and five `NOT_OBSERVED`**. The
`report_overview` helper regroups the same findings by status and totals the
intake so the batch can be described without re-parsing prose:

| Reading | Count | Aspirations |
| --- | --- | --- |
| `TOWARD` | 2 | `attention-before-output`, `honest-uncertainty` |
| `INQUIRY` | 1 | `useful-to-others` |
| `DRIFTING` | 1 | `repairable-systems` |
| `NOT_OBSERVED` | 5 | `wide-human-flourishing`, `durable-understanding`, `teachable-craft`, `unhurried-questions`, `commons-returned` |

Each reading follows the decision rule of the formalism, and each illustrates one
of its guarantees:

- `attention-before-output` recorded both of its declared markers and no
  counter-signal, so it reads `TOWARD`.
- `repairable-systems` recorded **both** declared markers *and* a declared
  counter-signal. Counter-signal precedence ([@prop:precedence]) surfaces the drift
  first: the reading is `DRIFTING`, and the two present markers cannot launder it.
- `useful-to-others` recorded only one of its two declared markers, so the
  direction is held open as `INQUIRY` with the second marker still unmet — not
  rounded up and not condemned ([@prop:toward_exact]).
- `honest-uncertainty` recorded both declared markers plus one token,
  `"extra token that is undeclared"`, that the registry never declares. The
  undeclared token is ignored, counted once in the overview's
  `ignored_marker_total`, and changes nothing: because both declared markers were
  present and no counter-signal was recorded, the reading is `TOWARD`. An
  observer-supplied token can never smuggle in a status ([@def:matching]).
- The five aspirations with no admitted entry read `NOT_OBSERVED`. This is not
  evidence that those directions are absent or failing; it reports only that no
  valid record reached this report ([@prop:absence]).

## What intake set aside

Two of the six submitted entries never became findings, and the overview makes
the reason legible without any narrative: `intake_note_count` is **2**. The
`report.intake_notes` are, verbatim:

- `"entry for unknown aspiration 'not-a-real-id' was set aside"`
- `"duplicate entry for 'attention-before-output' was set aside; the first entry stands"`

The unknown identifier was screened out during intake rather than crashing the
report; the duplicate `attention-before-output` entry — a weaker record with only
one marker — was set aside by the first-valid-entry rule, and the first, complete
entry stands. Neither disappeared silently: both are named in the intake notes so
the gap between six submissions and four incorporated readings is fully
accounted for. For this batch the overview's `ignored_marker_total` is **1**, its
`ignored_counter_signal_total`, `stale_count`, and `date_issue_count` are all
**0** (temporal review was left disabled here), so the entire delta between raw
input and final readings is visible in five small integers.

The whole batch is drawn in [@fig:batch_reading_overview]: the figure builder
replays exactly this batch through `progress_report` and `report_overview`, so
every count, grouping, and quoted intake note in the picture is the evaluator's
actual output for the code block above, not an illustration of it.

![The 6-entry worked batch of this section replayed through the real evaluator: 2 TOWARD, 1 INQUIRY, 1 DRIFTING, and 5 NOT_OBSERVED across 9 findings — one per registry aspiration whether or not an entry was filed — with 2 intake set-asides and 1 ignored undeclared token quoted verbatim from the report. The groupings count readings in this record; they do not grade the work or the people behind it.](../output/figures/batch_reading_overview.png){#fig:batch_reading_overview width=95%}

## Vocabulary and reach as reading context

The overview describes what *this batch* produced; the signal inventory and
horizon-band distribution describe the fixed vocabulary and temporal reach that
any batch is read against. Because every one of the registry's eighteen markers
and nine counter-signals is a distinct token ([@fig:signal_inventory]), the
`ignored_marker_total` above is unambiguous: the ignored token matched no
declared marker of any aspiration, not merely the one it was filed under. And
because the four aspirations that drew readings here — attention, repair,
usefulness, honest uncertainty — sit in three different temporal-reach bands
([@fig:horizon_bands]), a single review batch routinely mixes an
immediate-horizon reading with an at-handoff one. The bands are a reminder that
these readings become visible on different clocks, not a schedule on which they
should be expected to agree.

None of these summaries is a grade. `report_overview` adds no claim the findings
did not already carry; it only counts them. A batch that reads two `TOWARD` and
five `NOT_OBSERVED` is not "worse" than one that reads nine `TOWARD`. It is a
smaller record.
