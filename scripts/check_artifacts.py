#!/usr/bin/env python3
"""Fail-closed validation for generated Golden Line publication artifacts."""

from __future__ import annotations

import argparse

from golden_line.artifacts import check_artifacts
from golden_line.figures import FIGURES
from golden_line.registry import GOLDEN_ASPIRATIONS
from golden_line.serialization import registry_digest
from golden_line.version import REGISTRY_VERSION


def main() -> None:
    """Report every artifact-chain issue and exit non-zero if there is one.

    The gate takes no options. It still parses its command line, because a gate
    that silently ignores an argument it was given cannot be told apart from
    one that honoured it: a mistyped flag would otherwise read as a clean run
    over something the gate never looked at.
    """
    argparse.ArgumentParser(description=__doc__).parse_args()
    problems = check_artifacts()
    if problems:
        for problem in problems:
            print(f"FAIL {problem}")
        raise SystemExit(1)
    print(
        f"PASS artifact chain: {len(FIGURES)} figures, registry_version={REGISTRY_VERSION}, "
        f"digest={registry_digest(GOLDEN_ASPIRATIONS)}"
    )


if __name__ == "__main__":
    main()
