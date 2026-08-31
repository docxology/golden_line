"""Generate data/formalism_claim_ledger.json from declared manuscript labels.

The external publication engine's evidence registry resolves ``[@def:...]``/
``[@prop:...]`` cross-references only when the project declares them, so this
script re-derives the whole declaration from the manuscript's formalism blocks
and writes ``data/formalism_claim_ledger.json``. Tests re-derive the same set,
so a block added, renamed, or removed without regenerating fails the suite.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MS = ROOT / "docs" / "manuscript"

_LAB = re.compile(
    r"^::: \{[^}]*#((?:def|prop|thm|lem|cor|rem|ax|clm|ex):[a-zA-Z0-9_-]+)", re.M
)


def build_parser() -> argparse.ArgumentParser:
    """The CLI: no arguments are honoured besides ``--help``."""

    return argparse.ArgumentParser(
        prog="gen_formalism_ledger.py",
        description="Regenerate data/formalism_claim_ledger.json.",
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

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
    out = ROOT / "data" / "formalism_claim_ledger.json"
    out.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {out} with {len(claims)} citation rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
