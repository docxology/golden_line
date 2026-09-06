"""Derivation of ``data/formalism_claim_ledger.json`` from declared manuscript labels.

The external publication engine's evidence registry resolves ``[@def:...]``/
``[@prop:...]`` cross-references only when the project declares them, so this
module re-derives the whole declaration from the manuscript's formalism blocks
and writes ``data/formalism_claim_ledger.json``. Tests re-derive the same set,
so a block added, renamed, or removed without regenerating fails the suite.
"""

from __future__ import annotations

import json
import re

from golden_line.paths import PROJECT_ROOT

MS = PROJECT_ROOT / "docs" / "manuscript"

_LAB = re.compile(
    r"^::: \{[^}]*#((?:def|prop|thm|lem|cor|rem|ax|clm|ex):[a-zA-Z0-9_-]+)",
    re.MULTILINE,
)


def build_ledger() -> str:
    """Derive every citation row, write the ledger, and return the summary line."""

    claims = []
    for f in sorted(MS.glob("*.md")):
        for label in _LAB.findall(f.read_text(encoding="utf-8")):
            cid = label.replace(":", "_").replace("-", "_")
            kind_word = "definition" if label.startswith("def:") else "proposition"
            claims.append(
                {
                    "claim_id": cid,
                    "kind": "citation",
                    "value": label,
                    "source": (
                        f"docs/manuscript/{f.name}: {kind_word} block declared "
                        "with this label"
                    ),
                    "source_path": f"docs/manuscript/{f.name}",
                    "source_tier": "manuscript_formalism_block",
                    "freshness": "active",
                }
            )
    doc = {
        "claim_boundary": (
            "Grounds the manuscript's formalism cross-references in the evidence "
            "registry. Every `kind: citation` row re-derives from a formalism "
            "block label declared in docs/manuscript/, re-derived by "
            "tests/test_formalism_claim_ledger.py. These rows support "
            "reproducibility of the code description only; they do not establish "
            "that any proposition is universally valid."
        ),
        "schema_version": "1.0",
        "claims": claims,
    }
    out = PROJECT_ROOT / "data" / "formalism_claim_ledger.json"
    out.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    return f"wrote {out} with {len(claims)} citation rows"
