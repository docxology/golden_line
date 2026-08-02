# Evidence protocol

Golden Line is made of four distinct things: a declared aspiration registry, an
admitted observation, a deterministic derivation, and a generated artifact
chain. No later layer can add truth that was absent from an earlier one.

## First-principles contract

The hard constraints are narrow:

| Constraint | Type | Consequence |
| --- | --- | --- |
| An observation can only name declared signals | hard semantic boundary | Undeclared tokens are ignored and exposed. |
| A status must be reproducible from its inputs | hard audit requirement | Reports carry structured derivation and review metadata. |
| Missing evidence is not evidence of absence | hard epistemic limit | Missing entries produce `NOT_OBSERVED`, not failure. |
| Currentness cannot be inferred from incomplete time data | hard data-quality boundary | A missing or malformed observation date cannot produce `TOWARD` during temporal review. |
| Aspiration is not authorization | hard scope boundary | No Golden Line status overrides Red Line, Black Line, or White Line. |

The soft choices are the nine-entry registry, first-wins duplicate handling,
exact token matching, the optional staleness window, and the four names in the
status vocabulary. Those choices are versioned and revisable; they are not laws
of human flourishing.

## Status decision

For one admitted entry, the evaluator computes declared observations, unmet
markers, declared counter-signals, ignored tokens, and temporal quality before
selecting a status:

1. no admitted entry → `NOT_OBSERVED`;
2. a declared counter-signal → `DRIFTING`;
3. no declared marker → `INQUIRY`;
4. an unmet marker → `INQUIRY`;
5. stale, missing, or currentness-un-auditable positive evidence → `INQUIRY`;
6. otherwise → `TOWARD`.

The ordering is a conservative precedence rule, not a severity ranking.
`DRIFTING` describes a declared counter-signal in one record; it does not
diagnose a person or project. `TOWARD` describes a complete current marker
record; it does not certify safety, legality, virtue, quality, or permission.

## Artifact gate

The source-to-publication chain is:

```text
registry + status enum
        ↓
progress_report / invariants
        ↓
deterministic SVG + PNG + JSON registries
        ↓
check_artifacts.py
        ↓
template PDF/HTML rendering and release audit
```

Run `uv run python scripts/build_figures.py` and then
`uv run python scripts/check_artifacts.py`. The gate checks registry version and
digest, expected figure inventory, SVG/PNG presence, generator identity, and
manuscript figure-label citations. A passing local gate still does not prove
the prose claims are true or that a rendered document is visually perfect;
the sibling template's rendered-artifact audit remains necessary.
