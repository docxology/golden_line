"""Execute the project skill's code examples instead of trusting them.

The fenced Python blocks run in order against the shipped package, including
archive/envelope read-back with rejected contrary intake. Assertions exercise
the native behavior rather than pinning prose or comments.
"""

from __future__ import annotations

import re
from pathlib import Path

import golden_line

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SKILL = PROJECT_ROOT / ".agents" / "skills" / "golden-line" / "SKILL.md"

_PYTHON_BLOCK = re.compile(r"```python\n(.*?)```", re.DOTALL)


def _blocks() -> list[str]:
    return _PYTHON_BLOCK.findall(SKILL.read_text(encoding="utf-8"))


def test_skill_examples_execute_against_the_shipped_package() -> None:
    """Run every example block in order; a stale example now fails the suite."""
    namespace: dict[str, object] = {}
    blocks = _blocks()
    assert blocks, "no executable skill examples"
    for index, block in enumerate(blocks):
        compiled = compile(block, f"{SKILL.name}#block{index}", "exec")
        exec(compiled, namespace)  # noqa: S102 - the source is this repository's own
    assert isinstance(namespace["report"], golden_line.HorizonReport)
