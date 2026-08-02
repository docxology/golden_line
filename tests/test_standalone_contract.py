"""Guards that this repository stays readable and runnable on its own.

Golden Line is one work of five, each now in its own repository. The set's
standalone rule is explicit: "Each project has its own source of truth, Python
package, tests, documentation, manuscript, references, figures, and rendered
artifacts. A separated copy must still explain its own purpose and limits.
Cross-references are orientation links, not hidden dependencies."

A fresh-clone audit found that the prose had drifted from that rule while the
code never had. Four markdown links resolved above the repository root, the
grounding citation for the project's own name was deferred to a document that
does not ship here, the one non-Python prerequisite of the figure build was
recorded only in a deep maintainer note, and the render instructions assumed a
particular directory layout. None of those defects can be caught by a test that
imports the package, so they are caught here, from the files themselves.

Every guard asserts its scan is non-empty before asserting the property, so a
rename or a moved directory shows up as a failure rather than as a silent pass.
"""

from __future__ import annotations

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FIGURES_INIT = PROJECT_ROOT / "src" / "golden_line" / "figures" / "__init__.py"
MANUSCRIPT = PROJECT_ROOT / "manuscript"
BIBLIOGRAPHY = MANUSCRIPT / "references.bib"

#: Generated, vendored, and tooling trees are not authored documentation.
SKIP_DIRS = frozenset(
    {
        ".git",
        ".venv",
        ".pytest_cache",
        ".ruff_cache",
        ".mypy_cache",
        "__pycache__",
        "htmlcov",
        "output",
        "build",
    }
)

#: ``[text](target)`` with an optional pandoc title; angle-bracket autolinks and
#: bare URLs are handled by the scheme test in :func:`_relative_links`.
_LINK = re.compile(r"\[(?P<text>[^\]\n]*)\]\((?P<target>[^)\s]+)(?:\s+\"[^\"]*\")?\)")
_SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")

#: Cross-reference anchors share the citation syntax but are not bibliography
#: keys; they are resolved by the renderer against the manuscript itself.
#: ``fig:`` and friends belong to pandoc-crossref; ``def:`` and ``prop:``
#: belong to the formalism filter, which consumes them before the citation
#: machinery runs. Excluding them here is not a hole: that they all resolve to
#: a declared block is exactly what ``tests/test_formalism_syntax.py`` checks,
#: from the manuscript files rather than from the bibliography.
_CROSSREF_PREFIXES = ("fig:", "tbl:", "eq:", "sec:", "lst:", "def:", "prop:")
_CITATION = re.compile(r"\[@(?P<key>[A-Za-z][A-Za-z0-9_:.-]*)")
_BIB_ENTRY = re.compile(r"^@\w+\{(?P<key>[^,\s]+),", re.MULTILINE)


def _markdown_files() -> tuple[Path, ...]:
    """Every authored markdown file in the repository."""

    files = [
        path
        for path in sorted(PROJECT_ROOT.rglob("*.md"))
        if SKIP_DIRS.isdisjoint(path.relative_to(PROJECT_ROOT).parts)
    ]
    assert files, "the documentation scan found zero markdown files"
    return tuple(files)


def _relative_links() -> tuple[tuple[Path, int, str], ...]:
    """Return ``(file, line, target)`` for every non-URL markdown link."""

    found: list[tuple[Path, int, str]] = []
    for path in _markdown_files():
        text = path.read_text(encoding="utf-8")
        for match in _LINK.finditer(text):
            target = match.group("target")
            if _SCHEME.match(target) or target.startswith(("#", "//")):
                continue
            line = text.count("\n", 0, match.start()) + 1
            found.append((path, line, target))
    assert found, "no relative markdown links were scanned; the guard is vacuous"
    return tuple(found)


def _located(path: Path, line: int, target: str) -> str:
    """Format one finding so a failure names the file, line, and link."""

    return f"{path.relative_to(PROJECT_ROOT)}:{line} -> {target}"


def test_no_relative_link_escapes_the_repository_root() -> None:
    """A link out of the repository is a dependency on a checkout we do not ship.

    This is the guard that would have caught the audited defect: four links to
    ``docs/line-set.md`` sitting above the project root, two of them inside the
    manuscript and therefore inside the rendered publication. Companion works
    are named by repository URL instead, which resolves for a reader holding
    only this repository.
    """

    escaping = [
        _located(path, line, target)
        for path, line, target in _relative_links()
        if not str((path.parent / target.split("#")[0]).resolve()).startswith(
            str(PROJECT_ROOT) + "/"
        )
    ]
    assert not escaping, (
        "relative links resolve above the repository root: " + ", ".join(escaping)
    )


def test_every_relative_link_resolves_to_a_file_that_ships() -> None:
    """Links that stay inside the repository must also point at something real."""

    broken = [
        _located(path, line, target)
        for path, line, target in _relative_links()
        if target.split("#")[0] and not (path.parent / target.split("#")[0]).exists()
    ]
    assert not broken, "relative links point at absent files: " + ", ".join(broken)


def _required_system_tool() -> str:
    """Read the external binary name out of the figure builder's own source."""

    source = FIGURES_INIT.read_text(encoding="utf-8")
    match = re.search(r"shutil\.which\(\s*\"(?P<tool>[^\"]+)\"", source)
    assert match is not None, f"{FIGURES_INIT.name} names no external tool to require"
    return match.group("tool")


def test_the_figure_builds_system_prerequisite_is_documented_where_readers_look() -> (
    None
):
    """The one non-Python prerequisite must appear in the reader-facing docs.

    The name is read from the builder rather than restated here, so renaming the
    tool in the source fails this test instead of quietly stranding the docs.
    Before the audit it appeared only in ``src/golden_line/figures/AGENTS.md``,
    a maintainer note a first-time cloner has no reason to open, while
    ``docs/development.md`` told that reader to run the figure build.
    """

    tool = _required_system_tool()
    for relative in ("README.md", "STANDALONE.md", "docs/development.md"):
        text = (PROJECT_ROOT / relative).read_text(encoding="utf-8")
        assert tool in text, (
            f"{relative} does not name the required {tool} prerequisite"
        )


def test_render_instructions_do_not_assume_a_surrounding_directory_layout() -> None:
    """Rendering is an external dependency, so it must be addressed as one.

    ``cd ../../../template`` only resolves for a reader who happens to hold the
    engine at one particular relative position. Naming the repository works from
    anywhere; the guard also requires that the repository actually be named, so
    removing the bad path by deleting the instructions fails too.
    """

    monorepo_hop = re.compile(r"(\.\./){2,}[A-Za-z0-9_.-]*template")
    offenders = [
        f"{path.relative_to(PROJECT_ROOT)}:{text.count(chr(10), 0, match.start()) + 1}"
        for path in _markdown_files()
        for text in (path.read_text(encoding="utf-8"),)
        for match in monorepo_hop.finditer(text)
    ]
    assert not offenders, "layout-dependent template paths remain at: " + ", ".join(
        offenders
    )

    development = (PROJECT_ROOT / "docs" / "development.md").read_text(encoding="utf-8")
    assert "github.com/docxology/template" in development


def test_the_project_does_not_describe_itself_as_part_of_a_larger_checkout() -> None:
    """Self-description has to match what a separated copy actually is.

    The stale phrasings below all told a reader of this repository that it was a
    fragment of something else — a private, symlinked sidecar rendered by a
    sibling directory. It is its own repository now, and the documents that
    explain it must say so.
    """

    stale = (
        "private sidecar",
        "symlinked sidecar",
        "sidecar project",
        "sidecar checkout",
    )
    offenders = [
        f"{path.relative_to(PROJECT_ROOT)}: {phrase}"
        for path in _markdown_files()
        for text in (path.read_text(encoding="utf-8").lower(),)
        for phrase in stale
        if phrase in text
    ]
    assert not offenders, "stale self-description remains at: " + ", ".join(offenders)


def _bibliography_keys() -> frozenset[str]:
    """Every key defined in the manuscript's own bibliography."""

    keys = frozenset(
        match.group("key")
        for match in _BIB_ENTRY.finditer(BIBLIOGRAPHY.read_text(encoding="utf-8"))
    )
    assert keys, "the bibliography defines no entries; citation guards are vacuous"
    return keys


def _cited_keys(path: Path) -> frozenset[str]:
    """Bibliography keys cited by one manuscript file, crossref anchors removed."""

    return frozenset(
        match.group("key")
        for match in _CITATION.finditer(path.read_text(encoding="utf-8"))
        if not match.group("key").startswith(_CROSSREF_PREFIXES)
    )


def test_every_manuscript_citation_resolves_in_this_repositorys_bibliography() -> None:
    """The manuscript's references must ship with the manuscript."""

    defined = _bibliography_keys()
    cited: set[str] = set()
    for path in sorted(MANUSCRIPT.glob("*.md")):
        cited |= _cited_keys(path)
    assert cited, "no manuscript citations were scanned; the guard is vacuous"
    assert not (cited - defined), (
        f"citations without a bibliography entry: {cited - defined}"
    )


def test_the_citrinitas_framing_carries_its_own_grounding_citation() -> None:
    """The paper must ground its own name without sending the reader elsewhere.

    The audited defect was a content dependency, not an orientation link: the
    relationship chapter said the Jung citation "lives once in the shared
    line-set map", a document that does not ship in this repository. A reader
    holding only this repository could not reach it.
    """

    chapter = MANUSCRIPT / "01b_line_set_relationship.md"
    text = chapter.read_text(encoding="utf-8")
    assert "citrinitas" in text.lower(), "the framing this guard covers has moved"

    grounding = {
        key
        for key in _cited_keys(chapter) & _bibliography_keys()
        if "jung" in key.lower()
    }
    assert grounding, "the citrinitas framing cites no Jung reference of its own"

    bibliography = BIBLIOGRAPHY.read_text(encoding="utf-8")
    for key in grounding:
        entry_start = bibliography.index(f"{{{key},")
        entry = bibliography[entry_start : bibliography.index("\n}", entry_start)]
        assert "Alchemy" in entry, f"{key} is not the Psychology and Alchemy reference"
