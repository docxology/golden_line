"""Bind the figures' in-print label size to the geometry the reader receives.

A figure is drawn in canvas units and then scaled by LaTeX to a printed width,
so the printed size of a label is a *derived* quantity: it depends on the PNG's
real pixel dimensions, the ``width=`` the manuscript declares on the embed, the
``rendering.figure_height_fraction`` cap in ``manuscript/config.yaml``, and the
page geometry. This module re-derives that number for every shipped figure and
fails below :data:`golden_line.figures.svg.MIN_POINT_SIZE`.

The accessibility convention the figures rely on — shape and text repeating
what colour shows — only works if the text can be read at print scale, so this
is a correctness gate rather than a style preference. Every check here is
proof-of-detection tested: a planted small label and a planted over-tall canvas
must both be reported.
"""

from __future__ import annotations

import re
import struct
from dataclasses import dataclass
from pathlib import Path

import pytest

from golden_line.figures import FIGURES, build_figures
from golden_line.figures.svg import (
    CANVAS_WIDTH,
    MAX_CANVAS_HEIGHT,
    MIN_POINT_SIZE,
    MIN_TEXT_UNITS,
    _text,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = PROJECT_ROOT / "manuscript"
CONFIG = MANUSCRIPT / "config.yaml"

#: US Letter, the paper the combined manuscript is rendered on. Cross-checked
#: against the rendered LaTeX log whenever one is present, so this constant
#: cannot quietly disagree with the artifact the reader actually gets.
PAGE_WIDTH_IN = 8.5
PAGE_HEIGHT_IN = 11.0

#: TeX's point, the unit LaTeX reports \textwidth and \textheight in.
TEX_PT_PER_INCH = 72.27

#: The typographic point that font sizes are quoted in.
POINTS_PER_INCH = 72.0

_FONT_SIZE = re.compile(r'font-size="([\d.]+)px"')
_SVG_HEAD = re.compile(r'<svg[^>]*width="(\d+)" height="(\d+)"')
_EMBED = re.compile(
    r"!\[[^\]]*\]\(\.\./output/figures/(?P<name>[\w]+)\.png\)"
    r"\{#(?P<label>fig:[\w:-]+)(?P<attrs>[^}]*)\}"
)


def _config_fraction(key: str) -> float:
    """Read one ``rendering:`` fraction without adding a YAML dependency."""
    match = re.search(
        rf"^\s+{re.escape(key)}:\s*([\d.]+)\s*$",
        CONFIG.read_text(encoding="utf-8"),
        flags=re.MULTILINE,
    )
    assert match is not None, f"{key} is not declared in {CONFIG}"
    return float(match.group(1))


def _page_margins_inches() -> tuple[float, float]:
    """Return ``(per-side horizontal, per-side vertical)`` margins in inches.

    The manuscript declares its compact geometry with four sides, e.g.
    ``metadata.geometry: "left=0.33in,right=0.33in,top=0.58in,bottom=0.58in"``.
    The horizontal pair (``left``/``right``) bounds the printed text width and
    the vertical pair (``top``/``bottom``) bounds its height, so the printed
    label size must be derived from both. Each per-side value is the average of
    its pair so the caller's ``2 * margin`` reduction reproduces the true
    four-sided text area.
    """
    match = re.search(r'geometry:\s*"([^"]+)"', CONFIG.read_text(encoding="utf-8"))
    assert match is not None, "manuscript geometry margin is not declared"
    values: dict[str, float] = {}
    for token in match.group(1).split(","):
        key, _, raw = token.partition("=")
        assert raw.endswith("in"), f"geometry token {token!r} is not in inches"
        values[key.strip()] = float(raw[:-2])
    for required in ("left", "right", "top", "bottom"):
        assert required in values, f"geometry is missing the {required} margin"
    horizontal = (values["left"] + values["right"]) / 2
    vertical = (values["top"] + values["bottom"]) / 2
    return horizontal, vertical


def _text_area_tex_pt() -> tuple[float, float]:
    """Return ``(textwidth, textheight)`` in TeX points for the shipped geometry."""
    horizontal, vertical = _page_margins_inches()
    width = (PAGE_WIDTH_IN - 2 * horizontal) * TEX_PT_PER_INCH
    height = (PAGE_HEIGHT_IN - 2 * vertical) * TEX_PT_PER_INCH
    return width, height


def _png_pixels(path: Path) -> tuple[int, int]:
    """Real pixel dimensions straight out of the PNG's IHDR chunk."""
    header = path.read_bytes()[:24]
    assert header[:8] == b"\x89PNG\r\n\x1a\n", path
    width, height = struct.unpack(">II", header[16:24])
    return width, height


def _manuscript_embed_widths() -> dict[str, float]:
    """Map each embedded figure name to the width fraction it declares."""
    widths: dict[str, float] = {}
    for path in sorted(MANUSCRIPT.glob("*.md")):
        for match in _EMBED.finditer(path.read_text(encoding="utf-8")):
            percent = re.search(r"width=(\d+)%", match.group("attrs"))
            assert percent is not None, f"{match.group('name')} declares no width"
            widths[match.group("name")] = int(percent.group(1)) / 100
    return widths


@dataclass(frozen=True)
class PlateMeasurement:
    """One figure's derived print geometry; every field is computed, not stated."""

    name: str
    pixel_width: int
    pixel_height: int
    smallest_label_units: float
    printed_width_inches: float
    units_per_inch: float
    smallest_label_points: float
    bound_by: str


def measure_plate(
    name: str,
    svg: str,
    png: Path,
    width_fraction: float,
    height_fraction: float,
) -> PlateMeasurement:
    """Re-derive the printed size of ``name``'s smallest label from artifacts."""
    pixel_width, pixel_height = _png_pixels(png)
    head = _SVG_HEAD.search(svg)
    assert head is not None, name
    assert (int(head.group(1)), int(head.group(2))) == (pixel_width, pixel_height), (
        f"{name}: the rasterized PNG is not 1:1 with its SVG canvas, so canvas "
        "units cannot be converted to printed points"
    )
    sizes = [float(value) for value in _FONT_SIZE.findall(svg)]
    assert sizes, f"{name} draws no text at all"

    text_width_pt, text_height_pt = _text_area_tex_pt()
    by_width = width_fraction * text_width_pt / pixel_width
    by_height = height_fraction * text_height_pt / pixel_height
    scale = min(by_width, by_height)
    printed_width_inches = pixel_width * scale / TEX_PT_PER_INCH
    units_per_inch = pixel_width / printed_width_inches
    smallest = min(sizes)
    return PlateMeasurement(
        name=name,
        pixel_width=pixel_width,
        pixel_height=pixel_height,
        smallest_label_units=smallest,
        printed_width_inches=printed_width_inches,
        units_per_inch=units_per_inch,
        smallest_label_points=smallest / units_per_inch * POINTS_PER_INCH,
        bound_by="width" if by_width <= by_height else "height",
    )


def legibility_violations(plates: list[PlateMeasurement]) -> list[str]:
    """Return every print-legibility violation; an empty list means the set passes."""
    issues: list[str] = []
    if not plates:
        issues.append("no figure plates were measured; the gate would be vacuous")
    for plate in plates:
        if plate.smallest_label_points < MIN_POINT_SIZE:
            issues.append(
                f"{plate.name}: smallest label prints at "
                f"{plate.smallest_label_points:.2f} pt, below the "
                f"{MIN_POINT_SIZE} pt floor"
            )
        if plate.bound_by != "width":
            issues.append(
                f"{plate.name}: the height cap binds before the width, shrinking "
                f"every label on the plate ({plate.pixel_height} canvas units tall)"
            )
    return issues


def _measured_plates(root: Path) -> list[PlateMeasurement]:
    """Build every figure into ``root`` and measure the rendered artifacts."""
    build_figures(root)
    widths = _manuscript_embed_widths()
    height_fraction = _config_fraction("figure_height_fraction")
    front_fraction = _config_fraction("front_matter_figure_height_fraction")
    plates: list[PlateMeasurement] = []
    for name, _label, builder, *_ in FIGURES:
        assert name in widths, f"{name} is built but never embedded in the manuscript"
        plates.append(
            measure_plate(
                name,
                builder(),
                root / "output" / "figures" / f"{name}.png",
                widths[name],
                # The first embedded figure is bounded by the front-matter
                # fraction, so the gate must clear the tighter of the two.
                min(height_fraction, front_fraction),
            )
        )
    return plates


def test_every_shipped_figure_clears_the_print_floor(tmp_path: Path) -> None:
    """Re-derive each plate's smallest printed label; none may fall under 6 pt."""
    plates = _measured_plates(tmp_path)
    assert len(plates) == len(FIGURES)
    assert plates, "the scan set is empty, so the gate would prove nothing"
    assert legibility_violations(plates) == []


def test_measured_floor_is_the_declared_floor(tmp_path: Path) -> None:
    """MIN_TEXT_UNITS is the real floor: some plate actually draws at it."""
    plates = _measured_plates(tmp_path)
    assert min(plate.smallest_label_units for plate in plates) == MIN_TEXT_UNITS
    assert all(plate.pixel_width == CANVAS_WIDTH for plate in plates)
    assert all(plate.pixel_height <= MAX_CANVAS_HEIGHT for plate in plates)


def test_gate_rejects_a_planted_small_label(tmp_path: Path) -> None:
    """Proof of detection: shrink one label and the gate must name that plate."""
    build_figures(tmp_path)
    widths = _manuscript_embed_widths()
    height_fraction = _config_fraction("figure_height_fraction")
    name, _label, builder, *_ = FIGURES[0]
    planted = builder().replace('font-size="20px"', 'font-size="12px"', 1)
    assert 'font-size="12px"' in planted, "the plant did not apply"
    plate = measure_plate(
        name,
        planted,
        tmp_path / "output" / "figures" / f"{name}.png",
        widths[name],
        height_fraction,
    )
    assert plate.smallest_label_points < MIN_POINT_SIZE
    issues = legibility_violations([plate])
    assert any("below the" in issue and name in issue for issue in issues), issues


def test_gate_rejects_a_plate_whose_height_cap_binds(tmp_path: Path) -> None:
    """Proof of detection: a tall canvas is caught even with legal font sizes."""
    build_figures(tmp_path)
    widths = _manuscript_embed_widths()
    height_fraction = _config_fraction("figure_height_fraction")
    name, _label, builder, *_ = FIGURES[0]
    svg = builder()
    head = _SVG_HEAD.search(svg)
    assert head is not None
    tall = int(head.group(2)) * 3
    planted_svg = svg.replace(f'height="{head.group(2)}"', f'height="{tall}"')
    png = tmp_path / "planted.png"
    original = (tmp_path / "output" / "figures" / f"{name}.png").read_bytes()
    # Rewrite only the IHDR height so the measurement sees the taller canvas.
    header = bytearray(original[:24])
    header[20:24] = struct.pack(">I", tall)
    png.write_bytes(bytes(header) + original[24:])
    plate = measure_plate(name, planted_svg, png, widths[name], height_fraction)
    assert plate.bound_by == "height"
    issues = legibility_violations([plate])
    assert any("height cap binds" in issue for issue in issues), issues


def test_empty_scan_set_is_itself_a_violation() -> None:
    """A gate over nothing must fail rather than pass silently."""
    assert legibility_violations([]) != []


def test_text_primitive_refuses_a_sub_floor_size() -> None:
    """The floor is structural: a builder cannot emit illegible text at all."""
    assert _text(0, 0, "legal", MIN_TEXT_UNITS)
    with pytest.raises(ValueError, match="legibility floor"):
        _text(0, 0, "too small", MIN_TEXT_UNITS - 1)


def test_standalone_config_example_carries_the_legibility_geometry() -> None:
    """The example config is what a standalone copy starts from; it must not

    drop the fractions this gate reads. An example missing them would export a
    copy whose figures are height-bound — every label shrunk below the floor —
    with no local check able to notice, because the gate reads the live config.
    """
    example = MANUSCRIPT / "config.yaml.example"
    assert example.is_file()
    live_text = CONFIG.read_text(encoding="utf-8")
    example_text = example.read_text(encoding="utf-8")
    keys = re.findall(r"^\s+(\w*height_fraction):\s*([\d.]+)\s*$", live_text, re.M)
    assert keys, "the live config declares no height fractions; gate is vacuous"
    for key, value in keys:
        pattern = rf"^\s+{re.escape(key)}:\s*{re.escape(value)}\s*$"
        assert re.search(pattern, example_text, re.M), key


def test_declared_page_geometry_matches_the_rendered_log() -> None:
    """Cross-check the assumed paper size against the last real LaTeX run.

    The rendered log is a build artifact and may be absent on a fresh clone;
    when it is present it is authoritative, so a paper-size change cannot leave
    this module quietly measuring the wrong page.
    """
    log = PROJECT_ROOT / "output" / "pdf" / "_combined_manuscript.log"
    if not log.is_file():
        pytest.skip("no rendered LaTeX log in this checkout")
    raw = log.read_text(encoding="utf-8", errors="replace")
    reported = {
        key: float(value)
        for key, value in re.findall(r"\*?\s*\\(textwidth|textheight)=([\d.]+)pt", raw)
    }
    if not reported:
        pytest.skip("the rendered log records no \\textwidth/\\textheight")
    expected_width, expected_height = _text_area_tex_pt()
    assert abs(reported["textwidth"] - expected_width) < 0.5
    assert abs(reported["textheight"] - expected_height) < 0.5


def _geometry_margins(config_text: str) -> dict[str, float]:
    """Parse the four-sided ``geometry`` value from a config's text."""
    match = re.search(r'geometry:\s*"([^"]+)"', config_text)
    assert match is not None, "no geometry declared"
    margins: dict[str, float] = {}
    for token in match.group(1).split(","):
        key, _, raw = token.partition("=")
        assert raw.endswith("in"), f"geometry token {token!r} is not in inches"
        margins[key.strip()] = float(raw[:-2])
    return margins


def test_geometry_is_four_sided_and_matches_its_own_example() -> None:
    """The page geometry is four-sided, and the example carries the same shape.

    The printed label size this module derives depends on the exact margin the
    reader receives, so the parser pins the contract: a ``margin=…in`` single-
    sided geometry is refused here, not silently averaged, and a standalone
    copy started from ``config.yaml.example`` must land on the same page. This
    guards against the drift where the live config moved to four-sided margins
    while the example (and the old parser) still said ``margin=0.58in``.
    """
    live = _geometry_margins(CONFIG.read_text(encoding="utf-8"))
    for key in ("left", "right", "top", "bottom"):
        assert key in live, f"live geometry is missing the {key} margin"
    example = MANUSCRIPT / "config.yaml.example"
    assert example.is_file()
    example_margins = _geometry_margins(example.read_text(encoding="utf-8"))
    assert example_margins == live, (
        "config.yaml.example geometry drifted from the live config; "
        "a standalone copy would render a different page than this gate measures"
    )
    assert _page_margins_inches()[0] == (live["left"] + live["right"]) / 2
    assert _page_margins_inches()[1] == (live["top"] + live["bottom"]) / 2
