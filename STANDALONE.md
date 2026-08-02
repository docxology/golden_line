# Golden Line standalone guide

Golden Line is its own repository. This file states what a separated copy is,
what it can do alone, and what it cannot.

## What a separated copy is

A copy of this repository is the whole instrument: the `golden_line` Python
package, its tests, its documentation, its manuscript sources, its references,
and its deterministic figure builders. The package declares no third-party
Python dependencies and imports no sibling line project — `red_line`,
`black_line`, `white_line`, and `line_set` are separate works with separate
repositories, and none of them is installed, imported, or consulted at runtime.
Links to them are orientation, not dependency.

## What it can do alone

All four canonical gates in [`docs/development.md`](docs/development.md) run
from the copy alone, offline:

- the test suite with its coverage floor,
- the registry structural battery,
- the deterministic figure build,
- the source-to-artifact gate.

The only thing outside Python that the figure build needs is `rsvg-convert`
from librsvg (`brew install librsvg`, `apt-get install librsvg2-bin`). It is a
hard requirement of the PNG step and fails loudly when absent.

## What it cannot do alone

It cannot produce the typeset PDF/HTML manuscript. Rendering, rendered-output
validation, and the strict publication audit belong to the separate publication
engine at [`docxology/template`](https://github.com/docxology/template), which
you clone wherever you like — see `docs/development.md` for the
path-independent invocation. The generated publishing-status block in
`README.md` is produced by that same toolchain and cannot be regenerated from
this repository; `manuscript/config.yaml` is the source of truth it renders.

That is a declared external dependency. It is not evidence that the evaluator
or manuscript is unsound, and the absence of a rendered PDF is not a failing
gate — it is an unrun one.

## Purpose

This project records long-horizon aspirations and bounded directional readings.
It is not a compliance score, safety service, accreditation, moral authority,
or permission mechanism. See `README.md`, `AGENTS.md`, and
`docs/evidence-protocol.md` before changing the evaluator.

## Making a copy

Copy or clone the repository whole; there is no extraction step and no helper
from another checkout to run. Do not copy a rendering engine into this tree.
After copying, update `manuscript/config.yaml` and the publication metadata
before release, and check that every cross-work reference still names a
repository rather than a relative path out of this one.

## Validation

Use the canonical local validation commands in
[`docs/development.md`](docs/development.md). Generated figures must be rebuilt
before the artifact gate; `output/` is ignored and disposable.

The local artifact gate is necessary but not sufficient. Rendered PDF/HTML
outputs must also pass the template engine's validation before publication.
