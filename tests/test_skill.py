"""Execute the project skill's code examples instead of trusting them.

`.agents/skills/golden-line/AGENTS.md` promises that the skill's examples are
checked by the project gates and that the code shown must run against the
current public API. Neither was true: no gate read `.agents/`, so an API rename
would leave four green gates and a broken skill. This module makes the promise
literal — it runs the fenced Python blocks, in order, in one namespace, and
re-derives the outcomes their comments assert.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import golden_line
from golden_line import HorizonStatus, temporal_currentness_sweep

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SKILL = PROJECT_ROOT / ".agents" / "skills" / "golden-line" / "SKILL.md"

_PYTHON_BLOCK = re.compile(r"```python\n(.*?)```", re.S)


def _blocks() -> list[str]:
    return _PYTHON_BLOCK.findall(SKILL.read_text(encoding="utf-8"))


def test_skill_declares_python_examples() -> None:
    """Without at least one block every check below would be vacuous."""
    assert len(_blocks()) >= 2


def test_skill_examples_execute_against_the_shipped_package() -> None:
    """Run every example block in order; a stale example now fails the suite."""
    namespace: dict[str, object] = {}
    for index, block in enumerate(_blocks()):
        compiled = compile(block, f"{SKILL.name}#block{index}", "exec")
        exec(compiled, namespace)  # noqa: S102 - the source is this repository's own
    assert isinstance(namespace["report"], golden_line.HorizonReport)


def test_skill_examples_only_import_from_the_public_api() -> None:
    """The AGENTS.md contract: skill code runs against ``golden_line.__all__``."""
    exported = set(golden_line.__all__)
    imported: set[str] = set()
    for block in _blocks():
        for node in ast.walk(ast.parse(block)):
            if isinstance(node, ast.ImportFrom) and node.module == "golden_line":
                imported.update(alias.name for alias in node.names)
    assert imported, "no golden_line imports found in the skill examples"
    assert imported <= exported, sorted(imported - exported)


def test_skill_sweep_example_outcome_is_re_derived() -> None:
    """The sweep example's asserted ages/statuses come from a real replay.

    The block's own call arguments are parsed out of the file, so the
    documented outcome cannot drift away from the call that produces it.
    """
    text = " ".join(SKILL.read_text(encoding="utf-8").split())
    call = re.search(
        r'temporal_currentness_sweep\( # [^"]*?"([\w-]+)", \[([\d, ]+)\], '
        r'as_of="([\d-]+)", stale_after_days=(\d+),',
        text,
    )
    assert call is not None, "the SKILL.md sweep example call could not be parsed"
    aspiration_id = call.group(1)
    ages = [int(value) for value in call.group(2).split(",")]
    as_of = call.group(3)
    threshold = int(call.group(4))

    points = temporal_currentness_sweep(
        aspiration_id, ages, as_of=as_of, stale_after_days=threshold
    )
    toward = [p.age_days for p in points if p.status is HorizonStatus.TOWARD]
    inquiry = [p.age_days for p in points if p.status is HorizonStatus.INQUIRY]
    assert toward and inquiry, "the example must show both sides of the boundary"

    stated = (
        f"TOWARD at ages {'/'.join(str(age) for age in toward)}, "
        f"flips to INQUIRY (stale) at {inquiry[0]}."
    )
    assert stated in text, stated


def test_skill_sweep_outcome_guard_rejects_a_stale_sentence() -> None:
    """Proof of detection: an outcome sentence for other ages must not match."""
    text = " ".join(SKILL.read_text(encoding="utf-8").split())
    assert "TOWARD at ages 0/15/30/45, flips to INQUIRY (stale) at 60." not in text
