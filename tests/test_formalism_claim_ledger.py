"""Bind ``data/formalism_claim_ledger.json`` to the manuscript.

The render engine's evidence registry knows ``fig:``/``sec:``/``tbl:``/``eq:``/
``lst:`` label prefixes and treats every other ``[@x]`` as a bibliography key,
so a formalism reference is reported as an unsupported citation unless the
project declares it. ``data/formalism_claim_ledger.json`` is that declaration;
this module re-derives the whole set from the manuscript, so a block added,
renamed, or removed without the ledger following fails here rather than
surfacing as a red output-validation report after a render. Negative controls
prove each gate can fail.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_ms = ROOT / "docs" / "manuscript"
MANUSCRIPT = _ms
LEDGER = ROOT / "data" / "formalism_claim_ledger.json"

_BLOCK = re.compile(r"^::: \{(?P<attrs>[^}]*)\}\s*$", re.MULTILINE)
_LABEL = re.compile(r"#([a-z]+:[a-zA-Z0-9_-]+)")
_REFERENCE = re.compile(r"\[@((?:def|prop|thm|lem|cor|rem|ax|clm|ex):[a-z0-9-]+)\]")


def _body_files() -> list[Path]:
    return [
        path
        for path in sorted(MANUSCRIPT.glob("*.md"))
        if path.name not in ("preamble.md", "reading_record.json")
    ]


def _declared_labels() -> set[str]:
    labels: set[str] = set()
    for path in _body_files():
        for match in _BLOCK.finditer(path.read_text(encoding="utf-8")):
            label = _LABEL.search(match.group("attrs"))
            if label:
                labels.add(label.group(1))
    return labels


def _referenced_labels() -> set[str]:
    refs: set[str] = set()
    for path in _body_files():
        refs.update(_REFERENCE.findall(path.read_text(encoding="utf-8")))
    return refs


def _ledger() -> dict:
    return json.loads(LEDGER.read_text(encoding="utf-8"))


def _ledger_citations() -> set[str]:
    return {row["value"] for row in _ledger()["claims"] if row["kind"] == "citation"}


# -------------------------------------------------------------------- gates


def test_every_declared_label_is_in_the_ledger() -> None:
    declared = _declared_labels()
    assert declared, "no labels declared; this gate would be vacuous"
    assert _ledger_citations() == declared, sorted(_ledger_citations() ^ declared)


def test_every_ledger_citation_is_a_declared_block() -> None:
    assert _ledger_citations() <= _declared_labels(), sorted(
        _ledger_citations() - _declared_labels()
    )


def test_every_referenced_label_is_both_declared_and_ledgered() -> None:
    declared = _declared_labels()
    referenced = _referenced_labels()
    assert referenced, "no formalism references found; this gate would be vacuous"
    assert referenced <= declared, sorted(referenced - declared)
    assert referenced <= _ledger_citations(), sorted(referenced - _ledger_citations())


def test_every_ledger_source_path_exists() -> None:
    for row in _ledger()["claims"]:
        assert (ROOT / row["source_path"]).is_file(), row["claim_id"]
        assert row["freshness"] == "active", row["claim_id"]


def test_ledger_claim_ids_are_unique() -> None:
    rows = _ledger()["claims"]
    assert len({row["claim_id"] for row in rows}) == len(rows)


# ------------------------------------------------------- negative controls


def test_negative_control_label_gap_fails() -> None:
    ledger = _ledger()
    kept = [row for row in ledger["claims"] if row["value"] != min(_declared_labels())]
    citations = {row["value"] for row in kept if row["kind"] == "citation"}
    assert citations != _declared_labels()
