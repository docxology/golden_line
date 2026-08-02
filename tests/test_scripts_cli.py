"""Every script in ``scripts/`` must fail closed on a command line it cannot honour.

A gate that accepts an argument it does not understand and then exits ``0``
reports success for a run it never performed: the operator believes a flag was
honoured, and the exit code agrees with them. These tests execute the real
scripts as subprocesses — no patching tooling and no import-time shortcut — and
assert both directions, so the check cannot pass by rejecting everything.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

#: Every executable entry point in ``scripts/``. Discovered rather than listed,
#: so a new script joins this gate by existing instead of by being remembered.
SCRIPTS = tuple(
    sorted(path.name for path in SCRIPTS_DIR.glob("*.py") if path.name != "__init__.py")
)

#: The read-only gates, safe to execute for real in a test. ``build_figures.py``
#: is excluded because its positive control writes into ``output/``;
#: ``tests/test_figures.py`` exercises that builder against ``tmp_path``.
READ_ONLY_SCRIPTS = ("check_artifacts.py", "check_registry.py")

BAD_ARGUMENTS = ("--definitely-not-a-real-flag", "garbage-positional-argument")


def _run(script: str, *arguments: str) -> subprocess.CompletedProcess[str]:
    """Execute one script as the operator would, from the project root."""
    return subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / script), *arguments],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_the_script_scan_set_is_not_empty() -> None:
    """A parametrized gate over zero scripts would prove nothing at all."""
    assert SCRIPTS, "no scripts were discovered, so the gate below is vacuous"
    assert set(READ_ONLY_SCRIPTS) <= set(SCRIPTS)


@pytest.mark.parametrize("script", SCRIPTS)
@pytest.mark.parametrize("argument", BAD_ARGUMENTS)
def test_script_rejects_an_argument_it_cannot_honour(
    script: str, argument: str
) -> None:
    """An unknown flag or stray positional must exit non-zero, never silently."""
    result = _run(script, argument)
    assert result.returncode != 0, (
        f"{script} exited 0 on {argument!r}; an ignored argument is "
        "indistinguishable from an honoured one"
    )
    assert "usage:" in result.stderr


@pytest.mark.parametrize("script", READ_ONLY_SCRIPTS)
def test_script_still_succeeds_on_its_real_input(script: str) -> None:
    """The positive control: rejecting everything would be its own defect."""
    result = _run(script)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS" in result.stdout
    assert "FAIL" not in result.stdout


@pytest.mark.parametrize("script", SCRIPTS)
def test_script_documents_itself_without_doing_any_work(script: str) -> None:
    """``--help`` is honoured, so the parser is real rather than a bare reject."""
    result = _run(script, "--help")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "usage:" in result.stdout
