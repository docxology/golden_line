"""Session setup for the Golden Line suite.

``output/`` is ignored and disposable, so a clean checkout — or a render host
that wipes generated output before running the tests — arrives with no
``output/figures``. Two gates in this suite read that directory: the formalism
ledger's source-path binding and the ``check_artifacts.py`` CLI check. Without
this fixture they fail for a reason that has nothing to do with the property
under test. ``docs/development.md`` already states the requirement in prose —
"rebuild the ignored generated outputs before running ``check_artifacts.py``";
this fixture makes the suite enforce it instead of relying on the reader.

The rebuild uses this project's own deterministic builder and nothing else. It
is a rebuild of an ignored artifact, not a stand-in: the same bytes the
committed registry already pins. If the builder cannot run — a missing
``rsvg-convert``, say — the error surfaces here rather than being swallowed,
because a broken figure build is a real defect and must not be masked.
"""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "output" / "figures" / "figure_registry.json"


@pytest.fixture(scope="session", autouse=True)
def _ensure_generated_figures() -> None:
    """Rebuild ``output/figures`` when the ignored directory is absent."""

    if REGISTRY.exists():
        return

    from golden_line.figures import build_figures

    build_figures(ROOT)
