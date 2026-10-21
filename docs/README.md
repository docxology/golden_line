# Golden Line documentation

Golden Line is a small, inspectable directional instrument. The registry is in
`src/golden_line/registry.py`; the staged progress logic is in
`src/golden_line/progress.py`; the structural check battery is in
`src/golden_line/invariants.py`; the pure descriptive-analysis helpers are in
`src/golden_line/analysis.py`; and the reproducible figure builders are in the
`src/golden_line/figures/` package (invoked through `scripts/build_figures.py`).

- [architecture.md](architecture.md) — module map, the staged reporting flow,
  the descriptive-analysis layer, and digest semantics.
- [invariants.md](invariants.md) — the seven structural checks and their
  proof-of-detection tests.
- [development.md](development.md) — commands for tests, registry check, and
  figures.
- [evidence-protocol.md](evidence-protocol.md) — the first-principles evidence
  contract, status semantics, and publication artifact gate.
- [correspondence.md](correspondence.md) — design reviews received and what
  this repository adopted, deferred, or declined in response.
- [publication.md](publication.md) — citation instructions, DOI policy, and
  pre-publication checklist.
- [releases/v0.4.0.md](releases/v0.4.0.md) — release packet for version 0.4.0.

The founding four describe the origin of the current family of eight
instruments, a reader, and a register. Their relationships are declared in
[`line_set`](https://github.com/docxology/line_set). The original companions
are [`docxology/red_line`](https://github.com/docxology/red_line),
[`docxology/black_line`](https://github.com/docxology/black_line), and
[`docxology/white_line`](https://github.com/docxology/white_line). Each is a
separate repository, and none of them is required to run anything here.

See [AGENTS.md](AGENTS.md) for the working contract.
