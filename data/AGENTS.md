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
