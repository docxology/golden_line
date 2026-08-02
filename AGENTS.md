# Golden Line project guidance

Golden Line is a standalone project in its own repository. Its source of truth is
`src/golden_line/`, its executable contract is tested under `tests/`, and its
manuscript and generated figures must remain synchronized.

## Working contract

- Keep evaluator logic in `src/golden_line/`; scripts are thin orchestrators.
- Preserve the non-compliance boundary: statuses describe records, never
  people, virtue, safety, legality, or permission.
- Any registry, status, or method change must update tests, docs, manuscript,
  figures, `output/figures/`, and the artifact gate together.
- Use `uv`; do not add copied template-engine payloads or companion registries.
- Do not import, vendor, or depend on `red_line`, `black_line`, `white_line`, or
  `line_set`; refer to them by repository, never by a relative path that leaves
  this one.
- Run the local gates documented in [`docs/development.md`](docs/development.md)
  before asking the rendering toolchain to render. That command surface is the
  single source of truth for local and rendered validation.

Rendering happens in a separate checkout of the publication engine at
<https://github.com/docxology/template>, cloned anywhere; this repository is
linked into it and rendered under a qualified project name. The exact
path-independent commands are in [`docs/development.md`](docs/development.md).
Generated PDF/HTML output is evidence of rendering success, not independent
validation of the manuscript's substantive claims.
