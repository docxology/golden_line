# golden-line skill — AGENTS.md

Project-scoped skill bundle for the Golden Line instrument.

| File | Purpose |
| --- | --- |
| [`SKILL.md`](SKILL.md) | The skill itself: frontmatter (`name`, `description`) plus the operating body. |
| [`AGENTS.md`](AGENTS.md) | This file — folder contract. |
| [`README.md`](README.md) | Pointer for humans browsing the tree. |

## Audience

Agents that need to:

- Read aspirations and record markers or counter-signals through
  `progress_report(...)` without inventing a score.
- Check registry soundness with `all_invariants(...)` / `registry_sound(...)`.
- Rebuild the deterministic figures and re-run the source-to-artifact gate.

## Contract

- `SKILL.md` is a reader's interface to `src/golden_line/`, not a second
  specification. When the evaluator, registry, analysis layer, or figure set
  changes, update `SKILL.md` in the same patch; the package remains the source
  of truth.
- Keep the non-compliance boundary explicit here as well: the four readings
  describe a record, never a person, virtue, safety state, legality, or
  permission.
- Keep the standalone invariant: no prose, registry entries, or code copied
  from the Red, Black, or White Line projects.
- Code shown in `SKILL.md` must run against the current public API
  (`golden_line.__all__`).

## Validation

The skill claims no behaviour of its own. Its fenced Python examples are
executed by `tests/test_skill.py`, which runs the blocks in order against the
installed package, asserts that every name they import is in
`golden_line.__all__`, and re-derives the sweep example's documented outcome
from a real replay. That test runs as part of the first gate below; the other
three do not read `.agents/`.

- `uv run pytest tests/ --cov=src --cov-branch --cov-report=term-missing`
- `uv run python scripts/check_registry.py`
- `uv run python scripts/build_figures.py`
- `uv run python scripts/check_artifacts.py`

## Cross-refs

- Project contract: [`../../../AGENTS.md`](../../../AGENTS.md)
- Package contract: [`../../../src/golden_line/AGENTS.md`](../../../src/golden_line/AGENTS.md)
- Command surface: [`../../../docs/development.md`](../../../docs/development.md)
