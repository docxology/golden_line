# `golden_line` package

The aspirational thread: a directional instrument for recording aspirations and
movement toward them without turning aspiration into compliance.

## Module map

| Module | Role |
| --- | --- |
| `__init__.py` | Public surface and version re-exports |
| `models.py` | Dataclasses: `Aspiration`, `Marker`, `HorizonStatus`, etc |
| `registry.py` | `GOLDEN_ASPIRATIONS` tuple and registry digests |
| `analysis.py` | Horizon distribution, batch summary, currentness sweeps |
| `progress.py` | `progress_report` — the core evaluation |
| `invariants.py` | Structural checks over the registry |
| `serialization.py` | Canonical JSON serialization |
| `paths.py` | Project-root resolution |
| `version.py` | Single source of truth for the package version |
| `envelope.py` | Report envelope export for cross-instrument transport |
| `artifacts.py` | Figure and registry artifact validation |
| `figures/` | Deterministic SVG/PNG builders (16 modules) |
