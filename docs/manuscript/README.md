# Golden Line manuscript

The 13 numbered Markdown sections are the source of *Golden Line: Toward What
Matters*. Start with the [method](02_method.md), [aspiration
registry](03_aspirations.md), [worked examples](04_examples.md), and [claim
limits](05_limits.md).

- [Config](config.yaml) carries paper metadata and enables PDF, HTML, and EPUB.
  [The example](config.yaml.example) shows the standalone configuration shape.
- [Preamble](preamble.md) supplies shared typesetting commands.
- [Bibliography](references.bib) supplies the works cited in the numbered
  sections. The [references section](99_references.md) anchors the list.
- [Cover assets](assets/README.md) describe the checked-in illustration.
  Body figures are rebuilt into `output/figures/` from the repository root
  and referenced here as `../../output/figures/<name>.png`.

Rebuild figures with `uv run python scripts/build_figures.py`, then run
`uv run python scripts/check_artifacts.py`. Use the [pinned render
recipe](../development.md#rendering-the-manuscript-external-toolchain) for the
combined outputs. [Repository guidance](AGENTS.md) covers source maintenance.
