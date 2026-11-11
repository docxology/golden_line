# Publication and citation

## How to cite

For source version 0.7.0, use the repository citation until an archive for that
exact edition is independently verified:

> Friedman, D. A. (2026). *Golden Line: Toward What Matters* (version
> 0.7.0) [Software source]. GitHub.
> <https://github.com/docxology/golden_line>

BibTeX:

```bibtex
@software{friedman_golden_line_2026,
  author  = {Friedman, Daniel Ari},
  title   = {Golden Line: Toward What Matters},
  version = {0.7.0},
  year    = {2026},
  url     = {https://github.com/docxology/golden_line}
}
```

Previously verified source archive: version 0.6.2,
<https://doi.org/10.5281/zenodo.24069424>. It identifies that source ZIP only,
not version 0.7.0 or a standalone rendered manuscript. Historical edition 0.4.1,
DOI `10.5281/zenodo.22833506`, was verified against the Zenodo API on
2026-10-21 and remains a separate prior-edition reference.

`CITATION.cff` carries the release metadata in machine-readable form, and
`.zenodo.json` carries the deposit metadata. The version authority is
`docs/manuscript/config.yaml`; `tests/test_publication_metadata.py` fails if they
disagree.

## Persistent Identifiers and Verification

Verify the actual archive record's repository, tag, version, and contents before
assigning its identifier to that edition/object. Current metadata uses the
repository until the exact edition/object is independently verified.
A local metadata assertion is not external publication evidence. Keep historical
title/DOI pairs unchanged; never invent identifiers or rewrite issued bytes.

## Authorized automatic publication

On November 8, 2026, the owner authorized this GitHub Release campaign with the
existing public repositories' Zenodo hooks left active. Future use requires
actual owner authority for that release and object. Inspect the authenticated
hook state immediately before publication and verify the resulting archive's
repository, tag, version, and contents. Never prefill a DOI or amend an immutable
tag to add one learned afterward. PyPI, private-source disclosure, and new
private-sibling deposit automation remain unauthorized. The manual procedure
below is an alternative, not a universal prerequisite.

## Manual reserve-first DOI publication

1. With owner authority for the specific object, create an unpublished Zenodo
   deposition and reserve its DOI. A reservation is not a published deposit.
2. Identify the exact software source or standalone manuscript being deposited.
   If rendering a manuscript with its reserved DOI, label the reservation
   accurately; a source ZIP DOI does not identify a separate PDF.
3. Publish only the authorized bytes, then independently verify the actual
   record's repository, tag, version, and contents.
4. Record the verified identifier for that exact edition/object. If source has
   advanced, retain it as a versioned historical reference, not a current DOI.
   Never amend an immutable tag or archive to insert a DOI learned afterward.

## The other works

Current membership belongs to the [Line Set declaration](https://github.com/docxology/line_set).
The founding four are historical origin. DOI references below retain earlier
editions; they are not a current publication inventory. Other references use
repository URLs rather than invented identifiers. Native instruments do not
import siblings. Main deliberately imports published namespace bindings only;
Witness receives report envelopes by value. The shared report-envelope schema
is aligned by convention, not a shared runtime dependency.

| Work | Role | Repository | DOI |
| --- | --- | --- | --- |
| `red_line` | line — what I refuse (personal security boundary) | <https://github.com/docxology/red_line> | `https://doi.org/10.5281/zenodo.21754240` |
| `black_line` | line — how I try to do strong work (declaration coverage) | <https://github.com/docxology/black_line> | `https://doi.org/10.5281/zenodo.22833503` |
| `white_line` | line — what is absent, withheld, or unknowable (absence ledger) | <https://github.com/docxology/white_line> | `https://doi.org/10.5281/zenodo.21754242` |
| `line_set` | the reader that declares the set and checks vocabulary separation | <https://github.com/docxology/line_set> | `https://doi.org/10.5281/zenodo.22833507` |
| `witness_register` | companion beside the set — co-registration without aggregation | <https://github.com/docxology/witness_register> | `https://doi.org/10.5281/zenodo.22833511` |
| `green_line` | capacity under development; declared marker coverage, not demonstrated skill | <https://github.com/docxology/green_line> | not asserted here |
| `blue_line` | maintained commitment | <https://github.com/docxology/blue_line> | not asserted here |
| `violet_line` | affected-party consent; access-controlled source | <https://github.com/docxology/line_set> (membership reference) | not asserted here |
| `silver_line` | memory, custody, and succession | <https://github.com/docxology/silver_line> | not asserted here |
| `copper_line` | dimensioned finite resource use, outstanding commitments, and attributed burdens; access-controlled source | <https://github.com/docxology/line_set> (membership reference) | not asserted here |
| `iron_line` | recorded recovery exercises compared with scenario-specific targets; access-controlled source | <https://github.com/docxology/line_set> (membership reference) | not asserted here |

Copper's quantities are not aspiration priorities or evidence of fairness;
Iron's comparisons do not promise future recovery. Membership is not source access.

## Publication-readiness audit

The repository is public; this list stands as the audit to re-run before each
release, not as a step still pending.

- [ ] Every gate in `AGENTS.md` green on a clean checkout.
- [ ] `LICENSE` present and accurate.
- [ ] No absolute local paths, secrets, or private-project names in any tracked
      file (`tests/test_publication_metadata.py` checks the first of these).
- [ ] Review newly published Git history for disclosure. The fresh initial-release
      history was a first-publication decision, not an instruction to reset it.
- [ ] The rendered PDF regenerated at the release tree.
