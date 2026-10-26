# `golden_line` package

The aspirational thread: a directional instrument for recording aspirations and
movement toward them without turning aspiration into compliance.

## Module map

| Module | Role |
| --- | --- |
| `__init__.py` | Public surface and version re-exports |
| `models.py` | Dataclasses: `Aspiration`, `HorizonEntry`, `HorizonStatus`, etc |
| `registry.py` | `GOLDEN_ASPIRATIONS` tuple and registry digests |
| `analysis.py` | Horizon distribution, batch summary, currentness sweeps |
| `progress.py` | `progress_report` — the core evaluation |
| `invariants.py` | Structural checks over the registry |
| `serialization.py` | Canonical JSON serialization |
| `paths.py` | Project-root resolution |
| `version.py` | Single source of truth for the package version |
| `envelope.py` | Report envelope export for cross-instrument transport |
| `archive.py` | Versioned intake sidecar: `canonical_archive`, `decode_archive` |
| `evidence_records.py` | Optional provenance and conflict side records |
| `validation.py` | Bounded collection/input validation helpers |
| `artifacts.py` | Figure and registry artifact validation |
| `raster.py` | `rsvg-convert` PNG rasterization and renderer provenance |
| `formalism_ledger.py` | Derives `data/formalism_claim_ledger.json` from manuscript labels |
| `release_evidence.py` | Runs the local gate surface and records exact-revision evidence |
| `figures/` | Deterministic SVG/PNG builders (5 modules) |
