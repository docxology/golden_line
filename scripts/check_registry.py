#!/usr/bin/env python3
"""Print the registry digest and fail if any structural invariant is unsound."""

from __future__ import annotations

import argparse
import sys

from golden_line import (
    GOLDEN_ASPIRATIONS,
    REGISTRY_VERSION,
    all_invariants,
    registry_digest,
)


def main() -> None:
    """Run the battery, print each result, and exit non-zero on any failure.

    The gate takes no options. It still parses its command line, because a gate
    that silently ignores an argument it was given cannot be told apart from
    one that honoured it: a mistyped flag would otherwise read as a clean run
    over something the gate never looked at.
    """
    argparse.ArgumentParser(description=__doc__).parse_args()
    results = all_invariants(GOLDEN_ASPIRATIONS)
    for result in results:
        print(f"{'PASS' if result.passed else 'FAIL'} {result.name}: {result.detail}")
    print(
        f"registry_version={REGISTRY_VERSION} aspirations={len(GOLDEN_ASPIRATIONS)} "
        f"digest={registry_digest(GOLDEN_ASPIRATIONS)}"
    )
    if not all(result.passed for result in results):
        sys.exit(1)


if __name__ == "__main__":
    main()
