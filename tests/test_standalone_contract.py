"""Repository-local documentation links and bibliography closure."""

from __future__ import annotations

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = PROJECT_ROOT / "docs" / "manuscript"
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

    broken = []
    for path, line, target in _relative_links():
        without_anchor = target.split("#")[0]
        if not without_anchor:
            continue
        if (path.parent / without_anchor).exists():
            continue
        if re.search(r"^(?:\.\./)+output/", without_anchor):
            # The manuscript embeds its plates with an ``../output/`` prefix
            # that crosses the docs-first layout boundary; ``output/`` is
            # disposable and is gated by the figure-build tests, not here.
            continue
        broken.append(_located(path, line, target))
    assert not broken, "relative links point at absent files: " + ", ".join(broken)


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
