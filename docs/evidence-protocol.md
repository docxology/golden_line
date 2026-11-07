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

For each aspiration, intake first determines whether a valid entry was admitted.
For an admitted entry, the evaluator computes declared observations, unmet
markers, declared counter-signals, ignored tokens, and optional temporal quality:

1. no admitted entry → `NOT_OBSERVED`;
2. a declared counter-signal in the admitted entry → `DRIFTING`;
3. no declared marker → `INQUIRY`;
4. an unmet marker → `INQUIRY`;
5. with temporal review enabled, stale or currentness-un-auditable positive
   evidence (including missing or malformed dates) → `INQUIRY`;
6. otherwise → `TOWARD`.

Thus no entry or only rejected malformed material means `NOT_OBSERVED`; an
admitted empty entry means `INQUIRY`; complete admitted markers with no declared
counter-signal mean `TOWARD`, subject to enabled temporal review. Without a
window, currentness is unevaluated and an undated entry can be `TOWARD`. With a
window, age exactly at the threshold is current; a future date or greater age is
stale.

The ordering is a conservative precedence rule within the admitted record, not
a severity ranking across submitted records. A duplicate requires a prior valid
admitted same-ID entry; it is retained but not evaluated. `DRIFTING` does not
diagnose a person or project, and `TOWARD` does not certify safety, legality,
virtue, quality, permission, or freshness when temporal review is disabled.

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
digest, exact filename/label inventory, SVG source bytes, replayed PNG bytes,
manifest checksums, converter version/binary identity, generator identity, and
manuscript figure-label citations. A passing local gate still does not prove
the prose claims are true or that a rendered document is visually perfect;
the sibling template's rendered-artifact audit remains necessary.

Counter-signal precedence is local to the admitted record. First-wins preserves
order sensitivity; normalized rejected duplicates remain in a separately hashed
intake sidecar. Source metadata, including subject and snapshot references, is
unverified. A consistent rewrite and rehash can pass correspondence, so hashes
do not authenticate archive history. The supported data domain is documented in
[claim boundaries](claim_boundaries.md); optional authorship and conflict records
are specified in [evidence records](evidence-records.md).
