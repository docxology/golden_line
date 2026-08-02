"""Guard the manuscript's auto-numbered formalism blocks and their references.

Numbering is the renderer's job. ``infrastructure/rendering/formalism.lua`` in
the publication engine counts every ``::: {.definition #def:x title="..."}``
block in document order and rewrites ``[@def:x]`` into the number it assigned,
so a result inserted in the middle renumbers the prose along with itself. That
only holds while the source contains no number of its own: a hand-written
"Definition 3" left in a sentence is invisible to the filter and goes stale
silently, and a reference to a label nobody declared is emitted as literal
``[@def:x]`` markup with pandoc still exiting 0.

This module is the local check for both failure modes, plus the structural
obligations the filter cannot enforce — every block labelled, every label
prefixed for its kind, every label distinct. It reads the manuscript files
themselves, so it works in a checkout that has no rendering toolchain.

Every check is proof-of-detection tested against planted text, and the scan
asserts it is non-empty before asserting any property.
"""

from __future__ import annotations

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = PROJECT_ROOT / "manuscript"

#: Class name to displayed title, matching ``DEFAULT_KINDS`` in the filter.
#: A kind the manuscript never uses still belongs here: the literal check has
#: to catch a hand-numbered "Lemma 2" that nobody has declared a block for.
KIND_TITLES: dict[str, str] = {
    "definition": "Definition",
    "proposition": "Proposition",
    "theorem": "Theorem",
    "lemma": "Lemma",
    "corollary": "Corollary",
    "remark": "Remark",
    "axiom": "Axiom",
    "claim": "Claim",
    "example": "Example",
}

#: The label prefix each kind must use. Only the kinds this manuscript
#: declares need one; an undeclared kind is refused by name.
KIND_PREFIXES: dict[str, str] = {
    "definition": "def",
    "proposition": "prop",
}

_BLOCK_OPEN = re.compile(r"^:{3,}\s*\{(?P<attrs>[^}]*)\}\s*$", re.MULTILINE)
_CLASS = re.compile(r"\.([A-Za-z][\w-]*)")
_IDENTIFIER = re.compile(r"#([A-Za-z][\w:-]*)")
_TITLE = re.compile(r'title="([^"]*)"')
_REFERENCE = re.compile(r"@((?:" + "|".join(KIND_PREFIXES.values()) + r"):[\w-]+)")
_FENCED_CODE = re.compile(r"^(```|~~~).*?^\1", re.MULTILINE | re.DOTALL)
_HAND_NUMBER = re.compile(
    r"\b(" + "|".join(KIND_TITLES.values()) + r")s?\s+\d+",
)


def _manuscript_sources() -> dict[str, str]:
    """Every manuscript markdown file, keyed by name in render order."""
    sources = {
        path.name: path.read_text(encoding="utf-8")
        for path in sorted(MANUSCRIPT.glob("*.md"))
    }
    assert sources, "the manuscript scan found no markdown files"
    return sources


def _strip_code(text: str) -> str:
    """Blank out fenced code blocks, preserving line count for reporting."""
    return _FENCED_CODE.sub(lambda match: "\n" * match.group(0).count("\n"), text)


def declared_blocks(sources: dict[str, str]) -> list[tuple[str, str, str, str]]:
    """Return ``(file, kind, label, title)`` for every formalism Div, in order.

    A Div whose classes name no formalism kind is not ours and is skipped; a
    Div carrying the ``theorem-box`` class is skipped for the same reason the
    filter skips it.
    """
    blocks: list[tuple[str, str, str, str]] = []
    for name, text in sources.items():
        for match in _BLOCK_OPEN.finditer(text):
            attrs = match.group("attrs")
            classes = _CLASS.findall(attrs)
            if "theorem-box" in classes:
                continue
            kind = next((cls for cls in classes if cls in KIND_TITLES), None)
            if kind is None:
                continue
            identifier = _IDENTIFIER.search(attrs)
            title = _TITLE.search(attrs)
            blocks.append(
                (
                    name,
                    kind,
                    identifier.group(1) if identifier else "",
                    title.group(1) if title else "",
                )
            )
    return blocks


def rendered_numbers(
    blocks: list[tuple[str, str, str, str]],
) -> dict[str, tuple[str, int]]:
    """Map each label to the ``(displayed title, number)`` the filter assigns.

    Counters run per kind in document order, which is what the filter does; the
    result is what a reader of the rendered PDF sees next to each block.
    """
    counters: dict[str, int] = {}
    numbered: dict[str, tuple[str, int]] = {}
    for _name, kind, label, _title in blocks:
        counters[kind] = counters.get(kind, 0) + 1
        if label:
            numbered[label] = (KIND_TITLES[kind], counters[kind])
    return numbered


def formalism_violations(sources: dict[str, str]) -> list[str]:
    """Return every formalism-syntax violation; an empty list means the set passes."""
    issues: list[str] = []
    if not sources:
        issues.append("no manuscript files were scanned; the gate would be vacuous")
        return issues

    blocks = declared_blocks(sources)
    if not blocks:
        issues.append("no formalism blocks were declared; the gate would be vacuous")

    seen: set[str] = set()
    for name, kind, label, title in blocks:
        if not label:
            issues.append(f"{name}: a .{kind} block carries no label")
            continue
        if not title:
            issues.append(f"{name}: {label} carries no title attribute")
        expected = KIND_PREFIXES.get(kind)
        if expected is None:
            issues.append(f"{name}: .{kind} has no declared label prefix")
        elif not label.startswith(f"{expected}:"):
            issues.append(f"{name}: {label} does not use the '{expected}:' prefix")
        if label in seen:
            issues.append(f"{name}: duplicate formalism label {label}")
        seen.add(label)

    for name, text in sources.items():
        body = _strip_code(text)
        for match in _REFERENCE.finditer(body):
            if match.group(1) not in seen:
                issues.append(
                    f"{name}: reference to undeclared formalism {match.group(1)}"
                )
        for match in _HAND_NUMBER.finditer(body):
            line = body.count("\n", 0, match.start()) + 1
            issues.append(
                f"{name}:{line}: hand-written formalism number "
                f"{match.group(0)!r}; write a [@label] reference instead"
            )
    return issues


def test_the_manuscript_carries_no_formalism_syntax_violation() -> None:
    """The shipped manuscript passes every structural and reference check."""
    sources = _manuscript_sources()
    assert formalism_violations(sources) == []


def test_every_declared_block_is_labelled_titled_and_numbered() -> None:
    """The scan is non-empty and every declared block reaches the number map."""
    blocks = declared_blocks(_manuscript_sources())
    assert blocks, "no formalism blocks parsed, so the gate would be vacuous"
    numbers = rendered_numbers(blocks)
    assert len(numbers) == len(blocks)
    kinds = {kind for _name, kind, _label, _title in blocks}
    assert kinds == {"definition", "proposition"}
    for kind in sorted(kinds):
        drawn = [
            numbers[label][1]
            for _n, block_kind, label, _t in blocks
            if block_kind == kind
        ]
        assert drawn == list(range(1, len(drawn) + 1)), kind


def test_no_source_file_states_a_formalism_number() -> None:
    """The whole point: the number lives in the renderer, never in the source."""
    sources = _manuscript_sources()
    for name, text in sources.items():
        assert not _HAND_NUMBER.search(_strip_code(text)), name


def test_guard_rejects_a_hand_written_number() -> None:
    """Proof of detection: a hand-numbered reference in prose is reported."""
    planted = dict(_manuscript_sources())
    planted["02a_formalism.md"] += "\n\nBy Definition 3, the registry is sound.\n"
    issues = formalism_violations(planted)
    assert any("hand-written formalism number" in issue for issue in issues), issues


def test_guard_rejects_a_reference_to_an_undeclared_label() -> None:
    """Proof of detection: a typo'd label would ship as literal markup."""
    planted = dict(_manuscript_sources())
    planted["05_limits.md"] += "\n\nSee [@prop:no_such_result].\n"
    issues = formalism_violations(planted)
    assert any("undeclared formalism prop:no_such_result" in i for i in issues), issues


def test_guard_rejects_an_unlabelled_block() -> None:
    """Proof of detection: an unlabelled block can never be referenced."""
    planted = {"x.md": '::: {.definition title="Nameless"}\nBody.\n:::\n'}
    issues = formalism_violations(planted)
    assert any("carries no label" in issue for issue in issues), issues


def test_guard_rejects_a_mismatched_label_prefix() -> None:
    """Proof of detection: a proposition labelled ``def:`` is reported."""
    planted = {"x.md": '::: {.proposition #def:wrong title="Wrong"}\nBody.\n:::\n'}
    issues = formalism_violations(planted)
    assert any("does not use the 'prop:' prefix" in issue for issue in issues), issues


def test_guard_rejects_a_duplicate_label() -> None:
    """Proof of detection: two blocks sharing a label make a reference ambiguous."""
    planted = {
        "x.md": (
            '::: {.definition #def:one title="One"}\nA.\n:::\n\n'
            '::: {.definition #def:one title="Two"}\nB.\n:::\n'
        )
    }
    issues = formalism_violations(planted)
    assert any("duplicate formalism label def:one" in issue for issue in issues), issues


def test_guard_rejects_a_block_with_no_title() -> None:
    """Proof of detection: a titleless block renders as a bare number."""
    planted = {"x.md": "::: {.definition #def:bare}\nBody.\n:::\n"}
    issues = formalism_violations(planted)
    assert any("carries no title attribute" in issue for issue in issues), issues


def test_guard_is_not_vacuous_on_an_empty_scan() -> None:
    """A gate over nothing must fail rather than pass silently."""
    assert formalism_violations({}) != []
    assert formalism_violations({"x.md": "no formalism here\n"}) != []


def test_a_fenced_code_block_may_still_spell_a_number() -> None:
    """Code samples are quoted text, not prose the renderer would renumber."""
    planted = {
        "x.md": '::: {.definition #def:a title="A"}\nBody.\n:::\n\n```\nDefinition 3\n```\n'
    }
    assert formalism_violations(planted) == []
