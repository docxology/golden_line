"""Shared SVG constants and text primitives for deterministic figures.

The typography constants here are a *rendered-print* contract, not a taste
preference. A figure is drawn in canvas units and then scaled by LaTeX to a
fixed printed width, so the printed size of a label is fixed by the ratio of
its font size to :data:`CANVAS_WIDTH`. :data:`MIN_TEXT_UNITS` is the smallest
font size that still clears the project's printed floor at that ratio, and
:func:`_text` refuses to draw below it. ``tests/test_figure_legibility.py``
re-derives the printed point size from the shipped PNG dimensions, the
manuscript's declared embed width, and the page geometry, so the constants
below cannot drift away from what the reader actually receives.
"""

from __future__ import annotations

from golden_line.models import HorizonStatus


PAPER = "#f5f0e7"
INK = "#282421"
MUTED = "#6d645a"
GOLD = "#b47a16"
GOLD_DARK = "#714a0a"
GOLD_LIGHT = "#e4c272"
GOLD_HALO = "#f2d58c"
TEAL = "#176d6b"
RED = "#a9342a"
CARD = "#efe7d8"
CARD_LINE = "#d8cbb4"

#: One hue per directional reading, shared by every figure that draws a
#: status. Colour is never the only channel: each drawn status also carries its
#: own name, or a fill-versus-outline distinction that survives greyscale.
STATUS_COLOURS = {
    HorizonStatus.TOWARD: TEAL,
    HorizonStatus.INQUIRY: GOLD_DARK,
    HorizonStatus.DRIFTING: RED,
    HorizonStatus.NOT_OBSERVED: MUTED,
}

#: The design width, in canvas units, shared by every Golden Line figure.
#: Every manuscript embed declares the same ``width=95%``, so this single
#: number fixes the canvas-unit-to-printed-point scale for the whole set.
CANVAS_WIDTH = 1600

#: The smallest printed size, in typographic points, any in-figure label may
#: reach at the shipped page geometry. Below roughly this size the shape and
#: text redundancy the figures rely on stops functioning in print.
MIN_POINT_SIZE = 6.0

#: The smallest font size, in canvas units, a figure may draw. Derived from
#: :data:`MIN_POINT_SIZE` and the shipped geometry by the legibility gate;
#: pinned here so a builder cannot silently fall below it.
MIN_TEXT_UNITS = 20

#: The tallest canvas that still lets the embed's ``width`` bind before the
#: configured ``rendering.figure_height_fraction`` cap. A taller canvas would
#: be scaled down by its height instead, shrinking every label on the plate.
MAX_CANVAS_HEIGHT = 1900


def _esc(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _text(
    x: int, y: int, value: str, size: int, fill: str = INK, weight: str = "400"
) -> str:
    """Draw one text run, refusing any size below the printed legibility floor.

    Raising rather than silently clamping keeps the floor structural: a new
    label cannot be added at an illegible size and then pass the gate because
    the primitive quietly rewrote it.
    """
    if size < MIN_TEXT_UNITS:
        raise ValueError(
            f"figure text size {size} is below the legibility floor "
            f"MIN_TEXT_UNITS={MIN_TEXT_UNITS} (value: {value!r})"
        )
    return f'<text x="{x}" y="{y}" font-family="Arial, sans-serif" font-size="{size}px" font-weight="{weight}" fill="{fill}">{_esc(value)}</text>'


def _canvas(
    width: int,
    height: int,
    title: str | None = None,
    desc: str | None = None,
) -> list[str]:
    """Open a figure canvas, refusing a plate too tall to render width-bound.

    When *title* and *desc* are supplied the SVG carries accessibility markup
    (``role=\"img\"``, ``aria-labelledby``, ``<title>``, ``<desc>``) so the
    figure supports screen readers without altering its visual layout.
    """
    if width != CANVAS_WIDTH:
        raise ValueError(f"figure width {width} is not the shared {CANVAS_WIDTH}")
    if height > MAX_CANVAS_HEIGHT:
        raise ValueError(
            f"figure height {height} exceeds MAX_CANVAS_HEIGHT={MAX_CANVAS_HEIGHT}; "
            "the height cap would bind before the width and shrink every label"
        )
    a11y_parts: list[str] = []
    if title is not None or desc is not None:
        a11y_parts = [
            '<svg xmlns="http://www.w3.org/2000/svg"'
            f' role="img" aria-labelledby="fig-title fig-desc"'
            f' width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        ]
        if title is not None:
            a11y_parts.append(f'<title id="fig-title">{_esc(title)}</title>')
        if desc is not None:
            a11y_parts.append(f'<desc id="fig-desc">{_esc(desc)}</desc>')
    else:
        a11y_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        ]
    a11y_parts.append(
        f'<rect width="{width}" height="{height}" fill="{PAPER}"/>',
    )
    return a11y_parts


def _wrap(value: str, width: int) -> list[str]:
    words = value.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if current and len(candidate) > width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def _plural(count: int, noun: str) -> str:
    """Grammatical count phrase derived from the live count, never hardcoded."""
    return f"{count} {noun}{'' if count == 1 else 's'}"


def _entries(count: int) -> str:
    """Registry-entry count phrase; the plural form is irregular, so it is here."""
    return f"{count} {'entry' if count == 1 else 'entries'}"
