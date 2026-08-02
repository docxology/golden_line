# Test folder contract

`tests/` exercises the public API, registry, evaluator, analysis, serialization,
deterministic figures, the skill and experiment-plan surfaces, and cross-cutting
contracts.

## Test modules

- `test_api.py` — imports, version markers, public surface
- `test_golden_line.py` — core package smoke and default call forms
- `test_registry.py` — aspiration registry, lookups, and digest
- `test_invariants.py` — structural checks and planted-bad cases
- `test_progress.py` — progress_report and temporal review
- `test_analysis.py` — horizon distribution, batch summary, currentness
- `test_serialization.py` — canonical JSON and registry digest
- `test_figures.py` — figure determinism and registry metadata
- `test_figure_guards.py` — figure guard invariants
- `test_figure_legibility.py` — printed text size constraints
- `test_artifacts.py` — artifact validation and digest agreement
- `test_formalism_bindings.py` — prose and formalism block bindings
- `test_formalism_syntax.py` — formalism syntax and error paths
- `test_publication_metadata.py` — publication metadata across config and package
- `test_experiment_plan.py` — experiment plan surface
- `test_skill.py` — Golden Line skill descriptor surface
- `test_report_envelope.py` — report envelope export contract
- `test_scripts_cli.py` — every read-only script passes on good input
- `test_standalone_contract.py` — the package works without sibling repos
- `test_no_mocks.py` — lexical ban on mocks, stand-in names, path hardcodes

## Invariants

- No mocks. Use real data, temporary output roots, and planted-bad registries.
- Keep project coverage at or above the `90` floor in `pyproject.toml`.
- Import figure builders from `golden_line.figures`, not from `scripts/`.

## Validation

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90 --cov-report=term-missing
```
