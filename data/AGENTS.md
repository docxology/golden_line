# Data contract

`data/` currently contains one handwritten file: `claim_ledger.yaml`.

## File shape

- `claim_ledger.yaml` is a top-level mapping with a `claims:` list.
- Each claim record has `id`, `kind`, `value`, `source`, and `source_tier`.
- Figure claims also carry `artifact_path` for the generated PNG they point to.

## Invariants

- Keep the ledger limited to reproducible implementation facts and figure bindings. It does not certify that an aspiration is true or universally valid.
- When a source-derived number, figure id, or artifact filename changes, update this ledger and the matching tests together.
- Every `kind: number` row is re-derived from executed code by `tests/test_formalism_bindings.py::test_claim_ledger_numbers_and_figures_match_executed_sources`, and `test_every_numeric_ledger_claim_is_re_derived` asserts that the *set* of numeric rows equals the set of derivations — a new row with no derivation fails the suite rather than sitting unchecked.
- `test_ledger_source_paths_point_at_files_that_exist` checks each row's `source:` path, so a provenance pointer cannot survive a module being split or renamed.
- Keep field names aligned with those parsers.


## Formalism cross-reference rows (witness_register pattern)

Beyond numbers and figures, the ledger carries `kind: citation` rows for every
`def:` / `prop:` label the manuscript prose cites with `[@...]`. The stage-04
evidence-registry gate otherwise reports those references as unsupported
citations, because the registry only knows labels that some ledger declares.

Invariants for citation rows:

- One row per used label; `value` is the bare label (`def:intake`), the same
  token the prose writes inside `[@...]`.
- `source` names the manuscript file where the referenced block is declared.
- `tests/test_formalism_bindings.py::test_every_citation_ledger_claim_is_bound_to_a_declared_block`
  refuses any row whose label no formalism block declares (negative-control
  tested in `test_citation_ledger_rows_are_exactly_the_used_label_set`).
- `test_every_manuscript_formalism_reference_has_a_citation_ledger_row` closes
  drift in both directions: a new `[@def:x]`/`[@prop:x]` in the prose without a
  ledger row fails, and a ledger row for a label the prose never cites fails.
- The numeric row `currentness_replay_call_count` (126 = 9 aspirations x 14
  sweep ages) grounds the replay figure claim in 02a and the abstract.
