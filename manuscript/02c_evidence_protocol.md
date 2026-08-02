# Evidence boundary and artifact chain {#sec:evidence-protocol}

Golden Line does not begin with a score. It begins with a separation of things
that are easy to conflate: what the registry declares, what an observer records,
what the evaluator can derive, and what a generated artifact can prove about its
own provenance (formalized in [@def:temporal_review] and [@prop:boundary_exclusive]).

## Hard constraints and soft choices

The hard constraints are epistemic and semantic. An observation cannot create a
signal that the registry did not declare. Missing evidence cannot become
evidence of absence. A status must be reproducible from its inputs. Malformed
temporal metadata cannot establish currentness. An aspiration cannot authorize
what the Red Line refuses or resolve what the White Line leaves absent.

The soft choices are the nine-entry registry, exact token matching, the
first-valid-entry rule for duplicates, the optional staleness window, and the
names of the four statuses. They are versioned design decisions, not universal
truths. A future registry may revise them, but it must revise the digest,
figures, tests, and manuscript together.

![The four HorizonStatus readings mapped to bounded evidence conditions: no admitted entry; incomplete, stale, or unauditable evidence; a declared counter-signal; and complete current/auditable evidence. The matrix is not a ranking.](../output/figures/evidence_state_matrix.png){#fig:evidence_state_matrix width=95%}

## Statuses as bounded claims

`NOT_OBSERVED` means that no valid entry was admitted. `INQUIRY` means that an
entry exists but does not support a complete current positive reading. `DRIFTING`
means that a declared counter-signal was recorded and takes precedence over
markers. `TOWARD` means that every declared marker was observed, no declared
counter-signal was recorded, and the observation was current when temporal
review was enabled. None of these readings is a grade, a diagnosis, a safety
claim, or a permission mechanism. [@fig:evidence_state_matrix]

The full reasons trail remains useful to a human reader, but structured fields
(`observed`, `unmet`, `countered`, ignored tokens, note, date, and temporal flags)
make the derivation directly inspectable. A consumer need not turn explanatory
prose back into data before checking what happened.

Every reading returns the same record; which of its fields carry content is
decided by what the matching stage found. [@fig:finding_field_matrix] runs one
entry per evidence condition and reports, field by field, what came back. Three
fields are carried under every condition — the aspiration id, the status, and
the reasons trail — so no reading arrives unexplained, and the remaining nine
are carried exactly when the record supplied something for them. An empty field
is an absent observation and nothing more.

![The twelve structured fields of a finding against six evidence conditions, one executed progress_report call per column. Filled cells are fields the returned record carries and outlined cells are empty, and every cell prints which it is. A carried temporal flag records a currentness problem, not a good result; an empty field records an absent observation and never asserts that what it names is false.](../output/figures/finding_field_matrix.png){#fig:finding_field_matrix width=95%}

## Source to publication

The local release chain is:

```text
registry + status enum
        ↓
progress_report + invariant battery
        ↓
deterministic SVG, PNG, and JSON registries
        ↓
check_artifacts.py
        ↓
template PDF/HTML render and release audit
```

`check_artifacts.py` verifies the registry version and digest, the expected
figure inventory, SVG/PNG pairs, generator identity, and figure-label citations
in the manuscript. It is a consistency gate, not independent truth
verification. A rendered artifact still needs visual and publication validation
in the sibling template checkout.
