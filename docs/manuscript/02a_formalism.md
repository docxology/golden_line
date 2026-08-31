# Formalism: the evaluator and its invariants {#sec:formalism}

The formalism restates the evaluator the method section describes; every result
below tracks the code that implements it. This section states the implemented
semantics. Every result below describes
what the code in `golden_line` actually does, and the reasons and transitions
named here are the ones the evaluator produces. The formalism *describes* the
instrument; it does not extend or idealize it. Numbering is assigned by the
renderer in document order, so no number is written in the source and none can
go stale.

## Domain objects

::: {.definition #def:aspiration title="Aspiration"}
An aspiration $a$ is the six-tuple
$$a = (\mathrm{id},\ \mathrm{title},\ \mathrm{thread},\ \mathrm{horizon},\ M,\ C),$$
where $\mathrm{id}, \mathrm{title}, \mathrm{thread}, \mathrm{horizon}$ are text
fields and $M$ (Markers) and $C$ (Counter-signals) are finite sequences of
observable tokens. Markers are signs of movement *toward* the aspiration;
Counter-signals are signs of movement *away* from it.
:::

::: {.definition #def:registry title="Registry"}
The registry $R = \langle a_1, \dots, a_n \rangle$ is an ordered tuple of
aspirations with $n = 9$: four founding aspirations (attention before output,
usefulness beyond the author, repairable systems, answerability to human
flourishing) followed by five further ones (durable understanding, teachable
craft, honest uncertainty, unhurried questions, improvements returned to the
commons). Write $\mathrm{ids}(R)$ for the set of identifiers appearing in $R$.
:::

::: {.definition #def:horizon_entry title="Horizon entry"}
A horizon entry is
$e = (\mathrm{aid},\ O,\ K,\ \mathrm{note},\ \mathrm{d_{obs}})$, where
$\mathrm{aid}$ names an aspiration, $O$ is the set of observed markers, $K$ is
the set of observed counter-signals, $\mathrm{note}$ is free text, and
$\mathrm{d_{obs}}$ is an optional ISO date.
:::

::: {.definition #def:status_codomain title="Status codomain"}
The directional readings form the four-element set
$$\Sigma = \{\texttt{TOWARD},\ \texttt{INQUIRY},\ \texttt{DRIFTING},\ \texttt{NOT\_OBSERVED}\},$$
copied verbatim from the `HorizonStatus` enumeration. These are the *only*
statuses the evaluator can emit.
:::

::: {.definition #def:finding title="Finding"}
A finding is
$$f = (\mathrm{aid},\ \sigma,\ \mathrm{reasons},\ \mathrm{observed},\ \mathrm{unmet},\ \mathrm{countered},\ \mathrm{ign}_M,\ \mathrm{ign}_C,\ \mathrm{note},\ \mathrm{d_{obs}},\ \mathrm{stale},\ \mathrm{date\_issue})$$
with $\sigma \in \Sigma$ ([@def:status_codomain]). The structured fields list the declared markers
observed and unmet, the declared counter-signals, the undeclared marker tokens
$\mathrm{ign}_M$ and counter-signal tokens $\mathrm{ign}_C$ that were ignored,
the original note and date, and two temporal quality flags. Ignored markers and
ignored counter-signals are kept apart rather than pooled, because a reader
checking why a token did nothing needs to know which vocabulary it failed to
match. Human-readable `reasons` remain a parallel explanation, not the only
source of derivation.
:::

## The staged evaluator

::: {.definition #def:report_function title="Report function"}
The evaluator has signature
$$\texttt{progress\_report} : (E,\ R,\ \mathrm{as\_of},\ \tau) \longrightarrow \mathrm{HorizonReport},$$
where $E$ is a batch of horizon entries, $R$ defaults to the registry of
[@def:registry], $\mathrm{as\_of}$ is an optional review date, and $\tau$
(`stale_after_days`) is an optional non-negative integer staleness threshold;
$\mathrm{as\_of}$ and $\tau$ are keyword-only. It runs three stages: intake
screening, matching, and decision. The returned report also identifies the
registry version/digest and the review context.
:::

::: {.definition #def:intake title="Intake screening"}
Screening builds an accepted map $A : \mathrm{ids}(R) \rightharpoonup E$ by a
first-wins rule. Iterating $E$, a record with the wrong type or malformed
fields is set aside with an intake note; an entry whose
$\mathrm{aid} \notin \mathrm{ids}(R)$ is set aside with an unknown-id note; an
entry whose $\mathrm{aid}$ is already in $A$ is set aside with a duplicate note
and the first valid entry stands; otherwise the entry is admitted. Iterable
text-token fields are normalized to sets. Screening never raises on malformed
or unexpected input. It is a pure function of the pair $(E, \mathrm{ids}(R))$:
records are tested in a fixed order — shape, then registry membership, then
prior admission — and iteration follows the order of $E$ with indices counted
from 1 in the intake notes.
:::

::: {.definition #def:matching title="Matching"}
For aspiration $a$ ([@def:aspiration]) with admitted entry $e = A(a.\mathrm{id})$ ([@def:horizon_entry]), define
$$\mathrm{observed}(a,e) = O \cap M,\quad \mathrm{unmet}(a,e) = M \setminus O,\quad \mathrm{countered}(a,e) = K \cap C.$$
Undeclared tokens $O \setminus M$ and $K \setminus C$ are ignored and recorded in
the reasons; they can never determine a status.
:::

::: {.definition #def:temporal_review title="Temporal review"}
Given review date $d$ and threshold $\tau$, temporal review is enabled exactly
when $\tau$ is set. If $\tau$ is unset, temporal metadata does not affect the
status. If $\tau$ is set, a missing or unparseable $\mathrm{d_{obs}}$ sets
`date_issue` to true: the record is not fatal, but it cannot support a
currentness claim. With a parseable date, $\mathrm{stale}(e, d, \tau)$ holds iff
$\mathrm{d_{obs}} > d$ (a future observation) or $d - \mathrm{d_{obs}} > \tau$
days.
:::

::: {.definition #def:decision_rule title="Decision rule"}
The status $\sigma(a, e)$ is determined by the first matching clause, in order:

1. if $e = \bot$ (no admitted entry): $\texttt{NOT\_OBSERVED}$;
2. else if $\mathrm{countered}(a,e) \neq \varnothing$: $\texttt{DRIFTING}$;
3. else if $\mathrm{observed}(a,e) = \varnothing$: $\texttt{INQUIRY}$;
4. else if $\mathrm{unmet}(a,e) \neq \varnothing$: $\texttt{INQUIRY}$;
5. else if $\mathrm{stale}(e,d,\tau)$ or `date_issue`: $\texttt{INQUIRY}$;
6. otherwise: $\texttt{TOWARD}$.
:::

## Propositions about the evaluator

Each proposition below follows from [@def:intake] through [@def:decision_rule]
and is exercised by the package's test suite; the binding table at the end of
this section names the verifying test for every result. Each proposition is a
statement about code behavior — never about the world, safety, or persons.

::: {.proposition #prop:totality title="Totality"}
For every aspiration $a \in R$ the evaluator emits exactly one finding ([@def:finding]), so a
report contains $n = 9$ findings, one per registry entry, whether or not any
entry was filed. The report's `counts` therefore partition the findings across
$\Sigma$.
:::

::: {.proposition #prop:precedence title="Counter-signal precedence"}
If a declared counter-signal is recorded, meaning
$\mathrm{countered}(a,e) \neq \varnothing$ ([@def:matching]), the status is $\texttt{DRIFTING}$,
regardless of how many markers were observed and regardless of staleness.
Clause 2 precedes clauses 3–6, so a positive signal can never launder a
recorded drift.
:::

::: {.proposition #prop:toward_exact title="Exactness and currency of TOWARD"}
$\sigma(a,e) = \texttt{TOWARD}$ iff $\mathrm{observed}(a,e) = M$ (every declared
marker seen), $\mathrm{countered}(a,e) = \varnothing$ ([@def:matching]), and neither
$\mathrm{stale}(e,d,\tau)$ nor `date_issue` holds. Any missing marker, any
counter-signal, stale observation, or unparseable reviewed date reverts the
reading to $\texttt{INQUIRY}$ or $\texttt{DRIFTING}$. Counter-signal precedence is as stated in [@prop:precedence]. There is no partial
credit: an entry recording every marker but one reads exactly as an entry
recording none.
:::

::: {.proposition #prop:temporal_inquiry title="Temporal uncertainty reopens, never condemns"}
A fully-marked but stale or date-un-auditable observation with no
counter-signal yields $\texttt{INQUIRY}$ (clause 5), not $\texttt{DRIFTING}$.
Age or malformed temporal metadata reopens a question; it does not manufacture
drift.
:::

::: {.proposition #prop:absence title="Absence is not negation"}
$\texttt{NOT\_OBSERVED}$ arises solely from the absence of an admitted entry
(clause 1). The admission rule of [@prop:first_wins] determines which entries are admitted; when none is,
the reading is $\texttt{NOT\_OBSERVED}$ regardless of what records may have been
submitted. It asserts nothing about whether the aspiration is being served; it
reports only that no valid record was available to this report. The intake
notes preserve why submitted records were set aside when that distinction
matters.
:::

::: {.proposition #prop:first_wins title="First valid entry stands; the reading is deterministic"}
For each identifier, screening admits the first valid entry bearing it in the
order of $E$: the first valid entry bearing an identifier stands, and every
later entry with that identifier is set aside with a duplicate note. For an
identifier with no valid entry, the reading is $\texttt{NOT\_OBSERVED}$
([@prop:absence]). Exchanging
the positions of two entries that share an identifier can therefore change the
finding, but nothing else about the call can: replaying an identical batch with
identical $\mathrm{as\_of}$ and $\tau$ reproduces the identical report, digest
for digest. Determinism is a property of the code path; it does not make the
underlying records true.
:::

::: {.proposition #prop:intake-screening-determinism title="Intake screening determinism"}
The intake screening function ([@def:intake]) is a pure function of the pair
$(E, \mathrm{ids}(R))$: records are tested in a fixed order — shape, then
registry membership, then prior admission — and iteration follows the order
of $E$ with indices counted from 1 in the intake notes. For the identical
batch $E$ and the identical known ids $\mathrm{ids}(R)$, screening produces
the identical accepted map $A$ and the identical intake notes every time.
Malformed input is set aside deterministically: a record with the wrong type
or malformed fields always gets a malformed note, an entry whose
$\mathrm{aid} \notin \mathrm{ids}(R)$ always gets an unknown-id note, and
an entry whose $\mathrm{aid}$ is already in $A$ always gets a duplicate note.
Screening never raises on malformed or unexpected input — it is a pure
computation, and its determinism is separate from the first-wins semantics
of [@prop:first_wins], which covers which entry stands when multiple valid
entries share an identifier. Intake screening determinism covers the
screening function's behavior on all input, including malformed records.
:::

::: {.proposition #prop:boundary_exclusive title="The currentness boundary is exclusive"}
Staleness uses the strict comparison $d - \mathrm{d_{obs}} > \tau$ of
[@def:temporal_review], so a fully-marked, counter-signal-free entry with
$\tau = 90$ reads $\texttt{TOWARD}$ at age exactly 90 days and reverts from age
91 days: age $\tau$ is the last current age and $\tau + 1$ the first stale one.
The threshold is the caller's review-cadence choice; nothing in the evaluator
endorses any particular number of days as a natural constant.
:::

![The evaluator's ordered decision rule. Counter-signal precedence is explicit; TOWARD requires complete markers and auditable currentness when temporal review is enabled. The path reads a record; it is not a compliance verdict.](../output/figures/horizon_decision_path.png){#fig:horizon_decision_path width=95%}

The ordered clauses and the four readings they terminate in are drawn from the
`HorizonStatus` enumeration — the decision rule's codomain, not the registry —
in [@fig:horizon_decision_path].

### The completeness half of the rule

The exactness clause of [@prop:toward_exact] is the one a reader is most likely
to soften into "mostly there". [@fig:marker_completeness] refuses that reading
by running it: every subset of every aspiration's declared markers is filed as
an entry and evaluated, and the panel prints the status the evaluator returned
alongside the number of markers left unmet. Only the complete subset reads
$\texttt{TOWARD}$; a single missing marker holds the direction open at
$\texttt{INQUIRY}$, exactly as an empty entry does. The panel characterizes the
clause order, not any observed practice.

![Every observed-marker subset for every aspiration, filed as an entry and evaluated. Each cell prints the status progress_report returned and the count of markers still unmet, so the grid reads without colour; only the complete subset reaches TOWARD, and one missing marker reads exactly as none. Marker completeness is a property of the record, never a measure of the work.](../output/figures/marker_completeness.png){#fig:marker_completeness width=95%}

### The temporal half of the rule

[@prop:temporal_inquiry] has a picture. The `temporal_currentness_sweep`
analysis helper replays one fully-marked, counter-signal-free entry through the
real evaluator at a range of observation ages with $\tau = 90$: the reading
holds $\texttt{TOWARD}$ through age 90 exactly (the boundary is exclusive),
reverts to $\texttt{INQUIRY}$ from age 91, and a future-dated observation
likewise reads $\texttt{INQUIRY}$. Every cell in
[@fig:temporal_currentness_sweep] is an actual `progress_report` result, not an
illustration of one; the sweep observes the evaluator and never re-implements
it.

![A fully-marked entry replayed through the real evaluator at 14 observation ages with stale_after_days = 90. Every cell names the status progress_report actually returned, so nothing here is carried by colour alone: TOWARD through age 90, INQUIRY from age 91 and for future-dated observations. Age reopens the question; it never manufactures drift.](../output/figures/temporal_currentness_sweep.png){#fig:temporal_currentness_sweep width=95%}

::: {.proposition #prop:sweep_codomain title="Sweep delegation and codomain"}
The sweep computes no status of its own: its only status-producing call is
`progress_report` ([@def:report_function]), and each `SweepPoint` copies that call's finding. This is an
architectural property, not an empirical one — comparing a sweep point against a
second `progress_report` call would compare the same code path with itself, so
the verifying test instead asserts that `analysis.py` constructs no
`HorizonStatus` anywhere. Because sweep entries are fully marked,
counter-signal-free, and bear a known identifier, only clauses 5 and 6 of
[@def:decision_rule] can fire: $\texttt{DRIFTING}$ and $\texttt{NOT\_OBSERVED}$
are unreachable in a sweep; that half *is* falsifiable and is tested by
enumeration. The sweep characterizes the instrument's temporal behavior; it does
not describe any observed practice.
:::

[@prop:boundary_exclusive] states the boundary and the sweep shows it for one
registry entry. Whether the boundary belongs to the *evaluator* rather than to
that one entry is a separate question, and one that a single row cannot answer.

::: {.proposition #prop:boundary_uniform title="The currentness boundary is uniform across the registry"}
Replaying the sweep ([@prop:sweep_codomain]) for every $a \in R$ at the same review date and threshold
yields the same $\texttt{TOWARD} \to \texttt{INQUIRY}$ transition age for every
aspiration, because [@def:temporal_review] reads only $\mathrm{d_{obs}}$, $d$,
and $\tau$ — no field of $a$ enters the staleness comparison. The sweep
confirms that the temporal-inquiry behaviour stated in
[@prop:temporal_inquiry] and the exclusive boundary stated in
[@prop:boundary_exclusive] are properties of the evaluator's code path, not
of any particular aspiration. The lattice in
[@fig:currentness_lattice] is that replay: $9 \times 14 = 126$ executed
`progress_report` calls, with each row's own transition age printed beside it
and a count of rows that differ. Uniformity here is a fact about the code path;
it says nothing about how any aspiration is actually served.
:::

![The same currentness replay run across the whole registry: 9 aspiration rows by 14 observation ages, 126 executed progress_report calls at stale_after_days = 90. Filled cells are TOWARD and outlined cells are INQUIRY, so the grid reads without colour; the FLIPS AT column gives each row's own transition age and the footer counts rows that differ. Uniform ageing is a fact about the evaluator's code path, not evidence that any aspiration is being served.](../output/figures/currentness_lattice.png){#fig:currentness_lattice width=95%}

## Structural invariants

The evaluator reads a registry; a malformed registry would make its readings
meaningless. Seven pure-compute structural checks validate the *shape* of the
registry, independent of any horizon entry. Let $I_1, \dots, I_7$ be their
predicates; `registry_sound(R)` returns $\bigwedge_{k=1}^{7} I_k(R)$.

- $I_1$ **distinct identifiers**: no two aspirations share an id, so findings are
  unambiguous.
- $I_2$ **fields populated**: id, title, thread, and horizon all carry content.
- $I_3$ **reachable statuses**: each aspiration has at least one marker and at
  least one counter-signal, so both $\texttt{TOWARD}$ and $\texttt{DRIFTING}$ are
  reachable for it.
- $I_4$ **signal text**: every marker and counter-signal is a non-blank string.
- $I_5$ **signal uniqueness**: no marker or counter-signal repeats within one
  declaration.
- $I_6$ **signal disjointness**: $M \cap C = \varnothing$ within each aspiration,
  so no token reads as movement toward and away at once.
- $I_7$ **digest stability**: the canonical registry serializes, and its SHA-256
  digest is independent of registry order.

::: {.proposition #prop:digest_order title="Digest order-independence"}
`canonical_registry` serializes aspirations sorted by identifier, so
$\mathrm{registry\_digest}(R) = \mathrm{registry\_digest}(\pi(R))$ for every
permutation $\pi$ of $R$, and the digest is exactly 64 lowercase hexadecimal
characters (SHA-256). Two readers comparing digests are comparing registry
content, never the order in which they happened to list it — and a matching
digest attests only sameness of content, not soundness or merit.
:::

::: {.proposition #prop:detection title="Proof of detection"}
For each invariant $I_k$, the test suite asserts both that $I_k$ *passes* on the
real registry and that $I_k$ *fails* on a deliberately planted-bad registry
constructed to violate exactly that check. A green check that had never seen a
bad input would not count as evidence, so each invariant is paired with the
counter-example that gives it meaning.
:::

These digests and checks are review and drift-detection instruments for humans
comparing registry revisions. They carry no safety, warranty, or attestation
semantics of any kind. The detection proof of [@prop:detection] establishes
that the structural invariants can fail — each has a planted counter-example
— and therefore a green check is a positive result, not a silent absence.
[@prop:digest_order] gives the digest its order-independence; detection gives
the invariants their falsifiability.

## The report envelope

A reader holding reports from several independent instruments needs one
uniform way to say "this instrument, about this subject, at this review
moment, said this — and here is the pointer to its complete native report."
The envelope is that data contract and nothing more. For this instrument the
usual worry — that a selected status becomes a safe projection mistaken for
the whole state — takes a specific form: Golden Line has *no* single overall
verdict, so the only honest transportable status is the complete ordered
vector of per-aspiration readings. The envelope carries exactly that vector,
in report order, and invents no summary above it; compressing nine
directional readings into one word would manufacture precisely the aggregate
virtue score this instrument refuses everywhere else.

::: {.definition #def:report_envelope title="Report envelope"}
The report envelope is the frozen record
$v = (\mathrm{schema\_version},\ \mathrm{line\_id},\ \mathrm{subject\_id},\ \mathrm{review\_date},\ \mathrm{registry\_version},\ \mathrm{registry\_digest},\ \mathrm{native\_status},\ \mathrm{report\_ref},\ \mathrm{source\_snapshot\_refs},\ \mathrm{scope\_and\_nonclaims})$
with exactly those ten fields, in order, exported under the schema string
`line.report-envelope/1.0`. $\mathrm{native\_status}$ is the complete ordered
sequence of $(\mathrm{aspiration\_id}, \mathrm{status})$ pairs from the
report's findings — this line's own vocabulary, one pair per registry
aspiration ([@prop:totality]), never a summary. $\mathrm{report\_ref}$ is the SHA-256 of the
complete canonical report, so the envelope points at the full derivation —
reasons trails, matched and ignored tokens, temporal flags, intake notes —
rather than copying or restating any of it.
$\mathrm{scope\_and\_nonclaims}$ carries the instrument's transportable
non-claims inside the record itself, so a stored envelope cannot quietly
outgrow what the instrument was allowed to say. Sibling instruments export
the same shape by publishing the same schema string, never by importing one
another, and envelopes from different lines must not be compared, ranked,
averaged, or merged on $\mathrm{native\_status}$.
:::

::: {.proposition #prop:envelope_pointer title="The envelope points, never reinterprets"}
For every report $r$, `report_envelope(r)` satisfies
`envelope_matches_report(envelope, r)`: the digest pointer, the review date,
the registry version and digest ([@prop:digest_order]), and the per-aspiration readings all agree
with the report they were exported from, and editing any of them afterwards
makes the check return false. The envelope ([@def:report_envelope]) adds no field the report does not
determine except the caller-supplied $\mathrm{subject\_id}$ and
$\mathrm{source\_snapshot\_refs}$, which the evaluator stores and does not
verify. A matching envelope attests that the pair was archived unedited; it
says nothing about the truth of the report or the merit of anything the
report read.
:::

## Formalism-to-test bindings

Every definition and proposition above is verified by named tests in the
package's suite; the tables below bind each result to the test that would fail
if the code stopped satisfying it. Each row is keyed on the block's *label*, not
on its number, and the label renders as the number the reader sees, so inserting
a result renumbers the prose and the table together and can never split them.

Two binding tests police the tables.
`tests/test_formalism_bindings.py::test_binding_tables_bind_every_declared_block`
fails if the set of row labels stops matching the set of labels declared in this
section, and
`tests/test_formalism_bindings.py::test_every_binding_row_names_an_existing_test`
fails per row if any row's verifying-test cell names no test or names one that
does not exist. Neither checks that a named test is a *good* test, only that
every declared block is bound to one that exists. The boundary column restates
what each result does *not* claim.

| Definition | Statement essence | Verifying test | Boundary |
| --- | --- | --- | --- |
| [@def:aspiration] | six fields, two of them token sequences | `tests/test_formalism_bindings.py::test_aspiration_tuple_matches_the_dataclass` | names the fields, not what a marker is worth |
| [@def:registry] | nine entries, four founding then five further | `tests/test_formalism_bindings.py::test_registry_definition_matches_the_source_tuple` | a versioned design choice, not a canon |
| [@def:horizon_entry] | five fields, the observation date optional | `tests/test_formalism_bindings.py::test_horizon_entry_tuple_matches_the_dataclass` | records an observation, not a person |
| [@def:status_codomain] | exactly the four `HorizonStatus` values, in enum order | `tests/test_formalism_bindings.py::test_status_codomain_matches_the_enumeration` | four readings, not a scale from bad to good |
| [@def:finding] | twelve fields, ignored markers kept apart from ignored counter-signals | `tests/test_formalism_bindings.py::test_finding_tuple_matches_the_dataclass` | exposes a derivation, not a justification |
| [@def:report_function] | four parameters, two keyword-only; three named stages | `tests/test_formalism_bindings.py::test_report_function_signature_matches_manuscript` | a call shape, not a guarantee about inputs |
| [@def:intake] | shape, then membership, then prior admission; notes indexed from 1; never raises | `tests/test_formalism_bindings.py::test_intake_screening_tests_records_in_the_stated_order`, `tests/test_formalism_bindings.py::test_intake_screening_never_raises_on_hostile_input`, `tests/test_formalism_bindings.py::test_intake_first_wins_and_replay_determinism_match_manuscript` | screening judges records, never their authors |
| [@def:matching] | the three set operations, and undeclared tokens discarded | `tests/test_formalism_bindings.py::test_matching_set_operations_match_manuscript` | set membership, not sufficiency of evidence |
| [@def:temporal_review] | enabled iff $\tau$ is set; missing or unparseable dates flag rather than fail | `tests/test_formalism_bindings.py::test_temporal_review_rule_matches_manuscript` | a data-quality window, not a decay law |
| [@def:decision_rule] | six clauses, first match wins | `tests/test_formalism_bindings.py::test_decision_clauses_fire_in_the_stated_order` | clause order, not moral order |

| Proposition | Statement essence | Verifying test | Boundary |
| --- | --- | --- | --- |
| [@prop:totality] | one finding per registry aspiration; counts partition $n = 9$ | `tests/test_progress.py::test_counts_summary`, `tests/test_formalism_bindings.py::test_totality_count_matches_manuscript` | report shape, not coverage of a life |
| [@prop:precedence] | a declared counter-signal forces `DRIFTING` over every later clause | `tests/test_progress.py::test_drifting_survives_staleness` | flags a recorded signal, not a failing person |
| [@prop:toward_exact] | `TOWARD` iff all markers observed, none countered, currentness auditable | `tests/test_progress.py::test_observed_and_unmet_fields_are_populated`, `tests/test_progress.py::test_fresh_observation_stays_toward`, `tests/test_figures.py::test_completeness_panel_gives_no_partial_credit` | a reading of one record, not an accreditation |
| [@prop:temporal_inquiry] | temporal uncertainty yields `INQUIRY`, never `DRIFTING` | `tests/test_progress.py::test_stale_observation_reverts_toward_to_inquiry`, `tests/test_progress.py::test_undated_entry_cannot_certify_currentness` | age reopens a question, never condemns |
| [@prop:absence] | `NOT_OBSERVED` arises solely from no admitted entry | `tests/test_progress.py::test_unknown_aspiration_id_is_noted_not_fatal`, `tests/test_progress.py::test_empty_entries_yield_all_not_observed` | absence of signal is not evidence of drift |
| [@prop:first_wins] | first valid entry per id stands; identical calls reproduce identical reports | `tests/test_progress.py::test_duplicate_entries_first_wins_and_is_noted`, `tests/test_formalism_bindings.py::test_intake_first_wins_and_replay_determinism_match_manuscript` | determinism of the reading, not truth of the records |
| [@prop:intake-screening-determinism] | screening is a pure function of (E, ids(R)); malformed input is set aside deterministically; never raises | `tests/test_formalism_bindings.py::test_intake_screening_never_raises_on_hostile_input`, `tests/test_formalism_bindings.py::test_intake_screening_is_deterministic_on_all_input` | determinism of the screening function, not truth of records |
| [@prop:boundary_exclusive] | staleness is strict: `TOWARD` at age $\tau$, stale from $\tau + 1$ | `tests/test_progress.py::test_observation_exactly_at_staleness_boundary_stays_fresh`, `tests/test_progress.py::test_observation_one_day_past_staleness_boundary_is_stale`, `tests/test_formalism_bindings.py::test_currentness_boundary_constants_match_manuscript` | the threshold is a review-cadence choice, not a decay law |
| [@prop:sweep_codomain] | sweep delegates to `progress_report` and computes no status; codomain is `TOWARD`/`INQUIRY` only | `tests/test_analysis.py::test_sweep_module_constructs_no_status_of_its_own`, `tests/test_analysis.py::test_sweep_never_produces_drifting_or_not_observed`, `tests/test_formalism_bindings.py::test_sweep_codomain_matches_manuscript` | characterizes the instrument, not any observed practice |
| [@prop:boundary_uniform] | every aspiration's reading flips at the same observation age | `tests/test_figures.py::test_lattice_cells_are_executed_evaluator_readings`, `tests/test_figures.py::test_lattice_reports_a_uniform_flip_age`, `tests/test_figures.py::test_lattice_deviation_count_detects_a_planted_outlier` | uniformity of the code path, not of any practice |
| [@prop:digest_order] | registry digest is permutation-invariant, 64 lowercase hex characters | `tests/test_serialization.py::test_canonical_registry_is_deterministic_json`, `tests/test_golden_line.py::test_registry_is_unique_and_order_independent`, `tests/test_formalism_bindings.py::test_digest_order_independence_matches_manuscript` | a drift-review handle, no attestation semantics |
| [@prop:detection] | every invariant passes on the real registry and rejects a planted-bad one | `tests/test_invariants.py::test_battery_passes_on_real_registry`, `tests/test_invariants.py::test_registry_sound_false_on_any_planted_bad` | detection proof concerns the checks, not registry merit |

The envelope section declares its blocks after the propositions above, so its
rows sit in their own table, in the same document order:

| Envelope block | Statement essence | Verifying test | Boundary |
| --- | --- | --- | --- |
| [@def:report_envelope] | ten fields, `native_status` the complete ordered per-aspiration pairs | `tests/test_formalism_bindings.py::test_report_envelope_tuple_matches_the_dataclass` | a data contract, not a summary and not a score |
| [@prop:envelope_pointer] | the envelope agrees with its report field for field; any post-export edit is visible | `tests/test_formalism_bindings.py::test_envelope_pointer_matches_manuscript`, `tests/test_report_envelope.py::test_envelope_matches_report_verifies_an_archived_pair` | archival agreement, not truth of the report |

The bindings are themselves code behavior: they show which claims the suite
would catch, not that the registry's aspirations are wise or well served.
