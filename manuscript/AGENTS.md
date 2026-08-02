# Manuscript contract

`manuscript/` contains the prose source, render configuration, bibliography,
and cover-asset reference surface for this project.

## Files

- `00_abstract.md` through `06_conclusion.md` hold the ordered manuscript sections: `00_abstract.md`, `01_introduction.md`, `01b_line_set_relationship.md`, `02_method.md`, `02a_formalism.md`, `02b_scholarship.md`, `02c_evidence_protocol.md`, `03_aspirations.md`, `04_examples.md`, `04a_batch_reading.md`, `05_limits.md`, `06_conclusion.md`, and `99_references.md`.
- `config.yaml` is the live manuscript/render configuration.
- `config.yaml.example` is the standalone shape example for that configuration.
- `preamble.md` carries the shared preamble text.
- `references.bib` is the bibliography file.
- `assets/` holds the checked-in cover image and its local folder docs.

## Invariants

- Do not hand-edit generated files under `output/`; cite figures here as `../output/figures/<name>.png` and rebuild them from source.
- Figure labels cited in these section files are checked by `check_artifacts()`. If a `fig:` label or figure filename changes, rebuild and rerun the artifact gate in the same patch.
- Keep claims and terminology aligned with the non-compliance boundary used by the evaluator code and project root guidance.

## Validation

- `uv run python scripts/build_figures.py`
- `uv run python scripts/check_artifacts.py`
