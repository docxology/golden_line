#!/usr/bin/env python3
"""Thin CLI wrapper for the source-owned deterministic figure builder."""

from __future__ import annotations

import argparse

from golden_line.figures import build_figures


def main() -> None:
    """Rebuild every figure and print how many PNGs were written, and where.

    The builder takes no options. It still parses its command line, because a
    build that silently ignores an argument it was given cannot be told apart
    from one that honoured it: a mistyped flag would otherwise look like a
    successful build of something other than what was asked for.
    """
    argparse.ArgumentParser(description=__doc__).parse_args()
    paths = build_figures()
    print(f"generated {len(paths)} Golden Line figure PNGs under {paths[0].parent}")


if __name__ == "__main__":
    main()
