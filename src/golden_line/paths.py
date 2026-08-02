"""Shared project-root resolution for the Golden Line source tree.

Marker-based resolution keeps the root correct no matter how deep a submodule
is nested. Modules should import :data:`PROJECT_ROOT` from here rather than
recomputing ``parents[N]`` locally.
"""

from __future__ import annotations

from pathlib import Path


def _resolve_project_root(module_file: str) -> Path:
    """Return the nearest ancestor with ``pyproject.toml``, or the src root."""
    resolved = Path(module_file).resolve()
    return next(
        (
            parent
            for parent in resolved.parents
            if (parent / "pyproject.toml").is_file()
        ),
        resolved.parents[2],
    )


PROJECT_ROOT = _resolve_project_root(__file__)
