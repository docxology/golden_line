# Data

`data/claim_ledger.yaml` records the implementation facts that the manuscript
and binding tests rely on: counts, registry metadata, currentness constants,
digest length, and figure ids with their generated artifact paths.

If a source-derived number or figure reference changes, update the ledger and
rerun `uv run pytest tests/test_formalism_bindings.py -q`. That module derives
every numeric row from the source the row names, checks that the set of numeric
rows matches the set of derivations, and verifies that each `source:` path
still exists — so a number cannot drift and a row cannot be added unbound.

See [AGENTS.md](AGENTS.md) for the working contract.
