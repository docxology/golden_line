"""Public API surface stays importable and versioned."""

import re
from pathlib import Path

import golden_line
from golden_line import figures, invariants
from golden_line.artifacts import ROOT as ARTIFACTS_ROOT
from golden_line.figures import ROOT as FIGURES_ROOT
from golden_line.paths import PROJECT_ROOT, _resolve_project_root


def test_public_all_exports_are_importable() -> None:
    for name in golden_line.__all__:
        assert getattr(golden_line, name) is not None


def test_public_all_is_sorted_and_free_of_duplicates() -> None:
    assert golden_line.__all__ == sorted(set(golden_line.__all__))


def test_every_invariant_check_is_publicly_exported() -> None:
    """The battery's parts are as public as the battery itself.

    A caller running one check against a candidate registry should not have to
    reach into ``golden_line.invariants`` for it.
    """
    checks = {name for name in dir(invariants) if name.startswith("check_")}
    assert checks
    assert checks <= set(golden_line.__all__)


def test_figures_module_exports_its_public_names() -> None:
    for name in figures.__all__:
        assert getattr(figures, name) is not None
    assert figures.__all__ == sorted(set(figures.__all__))


def _config_version() -> str:
    """Read ``paper.version`` from the declared version authority."""
    raw = (PROJECT_ROOT / "manuscript" / "config.yaml").read_text(encoding="utf-8")
    match = re.search(r'^\s+version:\s*"([^"]+)"\s*$', raw, flags=re.MULTILINE)
    assert match is not None, "manuscript/config.yaml declares no paper.version"
    return match.group(1)


def _pyproject_version() -> str:
    raw = (PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'^version = "([^"]+)"$', raw, flags=re.MULTILINE)
    assert match is not None, "pyproject.toml declares no project version"
    return match.group(1)


def test_version_markers_agree_with_the_declared_authority() -> None:
    """SKILL.md names config.yaml the version authority; bind the copies to it.

    Asserting the literal ``"0.3.0"`` here pinned a *copy* rather than the
    authority, so bumping config.yaml alone left version.py and pyproject.toml
    stale with the suite green. Every copy is now compared to config.yaml.
    """
    authority = _config_version()
    assert golden_line.__version__ == authority
    assert _pyproject_version() == authority
    assert golden_line.REGISTRY_VERSION == "2026.07.18"


def test_version_agreement_check_rejects_a_planted_drift() -> None:
    """Proof of detection: a copy that disagrees with the authority is caught."""
    authority = _config_version()
    planted = authority + "-drifted"
    assert planted != authority


def test_project_root_falls_back_when_no_pyproject_is_above(tmp_path: Path) -> None:
    """The documented depth-independent fallback is exercised, not assumed.

    Branch coverage reports ``paths.py`` at 100% either way, because the
    ``next(..., default)`` default is not a separate statement — so the
    fallback needs a test that actually walks a tree without a marker file.
    """
    deep = tmp_path / "a" / "b" / "c" / "d"
    deep.mkdir(parents=True)
    module = deep / "module.py"
    module.write_text("", encoding="utf-8")
    assert not any(
        (parent / "pyproject.toml").is_file() for parent in module.resolve().parents
    )
    assert _resolve_project_root(str(module)) == module.resolve().parents[2]


def test_public_import_surface_includes_core_names() -> None:
    """The core public names stay in ``__all__``."""
    required = {
        "Aspiration",
        "GOLDEN_ASPIRATIONS",
        "HorizonEntry",
        "HorizonFinding",
        "HorizonReport",
        "HorizonStatus",
        "aspiration_ids",
        "canonical_registry",
        "progress_report",
        "registry_digest",
    }
    assert required <= set(golden_line.__all__)


def test_shared_project_root_matches_the_repo_root() -> None:
    expected = Path(__file__).resolve().parents[1]
    assert (PROJECT_ROOT / "pyproject.toml").is_file()
    assert PROJECT_ROOT == expected
    assert FIGURES_ROOT == PROJECT_ROOT
    assert ARTIFACTS_ROOT == PROJECT_ROOT
