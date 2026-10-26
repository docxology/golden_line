# Publication and citation

## How to cite

Cite this work via its minted DOI or repository:

> Friedman, D. A. (2026). *Golden Line: Toward What Matters* (version
> 0.5.0) [Software and manuscript]. GitHub.
> <https://github.com/docxology/golden_line/tree/v0.5.0>

BibTeX:

```bibtex
@software{friedman_golden_line_2026,
  author  = {Friedman, Daniel Ari},
  title   = {Golden Line: Toward What Matters},
  version = {0.5.0},
  year    = {2026},
  url     = {https://github.com/docxology/golden_line/tree/v0.5.0}
}
```

The last verified Zenodo edition is 0.4.1, DOI
`10.5281/zenodo.22833506`, verified against the Zenodo API on 2026-10-21.
That DOI is retained in publication metadata pending Daniel's reserve-first
new-version deposition. It does not identify a newly minted 0.5.0 deposit.

`CITATION.cff` carries the release metadata in machine-readable form, and
`.zenodo.json` carries the deposit metadata. The version authority is
`docs/manuscript/config.yaml`; `tests/test_publication_metadata.py` fails if they
disagree.

## Persistent Identifiers and Verification

This repository retains its last verified Zenodo DOI (`10.5281/zenodo.22833506`).
`tests/test_publication_metadata.py` refuses any unverified DOI-shaped string in
the citation metadata unless that exact DOI is listed as verified inside the test
itself. A placeholder DOI that renders like a real one is worse than no DOI: it
survives copy-and-paste into someone else's bibliography and points nowhere.

## Reserving and Minting DOIs (reserve-first order)

1. Create the Zenodo deposition **without publishing it**, and reserve its DOI.
2. Record the reserved DOI in this repository: add it under `identifiers:` in
   `CITATION.cff`, add it to `related_identifiers` in `.zenodo.json` if
   relevant, add `publication.doi` to `docs/manuscript/config.yaml`, and add the
   exact string to the verified list in `tests/test_publication_metadata.py`.
   The gate turns green only when a person has asserted the DOI is real.
3. Re-render the manuscript so the printed artifact carries its own DOI. A PDF
   deposited without its DOI on the cover cannot be cited from the paper alone.
4. Upload the re-rendered artifacts and publish the deposition.

## The other works

This work belongs to eight instruments, their reader, and a witness register.
The founding four are historical origin. Known verified DOI references below
are retained; the remaining instrument references use repository URLs rather
than invented identifiers. No work imports another, and the shared report-envelope schema
string is aligned by published convention rather than by dependency.

| Work | Role | Repository | DOI |
| --- | --- | --- | --- |
| `red_line` | line — what I refuse (personal security boundary) | <https://github.com/docxology/red_line> | `https://doi.org/10.5281/zenodo.21754240` |
| `black_line` | line — how I try to do strong work (declaration coverage) | <https://github.com/docxology/black_line> | `https://doi.org/10.5281/zenodo.22833503` |
| `white_line` | line — what is absent, withheld, or unknowable (absence ledger) | <https://github.com/docxology/white_line> | `https://doi.org/10.5281/zenodo.21754242` |
| `line_set` | the reader that declares the set and checks vocabulary separation | <https://github.com/docxology/line_set> | `https://doi.org/10.5281/zenodo.22833507` |
| `witness_register` | companion beside the set — co-registration without aggregation | <https://github.com/docxology/witness_register> | `https://doi.org/10.5281/zenodo.22833511` |
| `green_line` | developed capacity | <https://github.com/docxology/green_line> | not asserted here |
| `blue_line` | maintained commitment | <https://github.com/docxology/blue_line> | not asserted here |
| `violet_line` | affected-party consent | <https://github.com/docxology/violet_line> | not asserted here |
| `silver_line` | stewardship | <https://github.com/docxology/silver_line> | not asserted here |

## Before the repository goes public

- [ ] Every gate in `AGENTS.md` green on a clean checkout.
- [ ] `LICENSE` present and accurate.
- [ ] No absolute local paths, secrets, or private-project names in any tracked
      file (`tests/test_publication_metadata.py` checks the first of these).
- [ ] Git history contains nothing that should not be public — the published
      history is a fresh initial-release commit, not a monorepo extract.
- [ ] The rendered PDF regenerated at the release tree.
