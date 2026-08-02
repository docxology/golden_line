"""Figures derived from analysis helpers and the worked batch replay."""

from __future__ import annotations

from dataclasses import dataclass

from golden_line.analysis import (
    horizon_distribution,
    report_overview,
    signal_inventory,
    temporal_currentness_sweep,
)
from golden_line.models import HorizonEntry, HorizonStatus
from golden_line.progress import (
    IntakeSetAsideReason,
    classify_intake_entries,
    progress_report,
)
from golden_line.registry import GOLDEN_ASPIRATIONS, find_aspiration
from golden_line.version import REGISTRY_VERSION

from .svg import (
    CARD,
    CARD_LINE,
    GOLD,
    GOLD_DARK,
    INK,
    MUTED,
    PAPER,
    RED,
    STATUS_COLOURS,
    TEAL,
    _canvas,
    _plural,
    _text,
    _wrap,
)


# The sweep review context is derived from the registry version date so the
# figure is deterministic and re-derivable, never tied to the build day.
SWEEP_AS_OF = REGISTRY_VERSION.replace(".", "-")
SWEEP_STALE_AFTER_DAYS = 90
SWEEP_AGES = (-7, 0, 15, 30, 45, 60, 75, 89, 90, 91, 105, 120, 150, 180)

#: How many sweep cells sit in one drawn row. The sweep is one timeline read
#: left to right and then top to bottom; the wrap exists so each cell is wide
#: enough for its own labels to print legibly.
SWEEP_COLUMNS = 7


def _svg_currentness_sweep() -> str:
    """Proposition 4 drawn from the live evaluator, not from a description.

    A fully-marked, counter-signal-free entry for the first registry
    aspiration is replayed through ``progress_report`` at each sampled
    observation age; every cell colour below is the status the real evaluator
    returned for that age.
    """
    aspiration = GOLDEN_ASPIRATIONS[0]
    points = temporal_currentness_sweep(
        aspiration.id,
        SWEEP_AGES,
        as_of=SWEEP_AS_OF,
        stale_after_days=SWEEP_STALE_AFTER_DAYS,
    )
    width, height = 1600, 960
    parts = _canvas(
        width,
        height,
        title="The Temporal Currentness Sweep",
        desc="How one reading ages under temporal review across multiple observation ages.",
    )
    parts.extend(
        [
            _text(70, 84, "THE TEMPORAL CURRENTNESS SWEEP", 24, GOLD_DARK, "700"),
            _text(
                70, 132, "How one reading ages under temporal review", 40, INK, "700"
            ),
            _text(
                70,
                172,
                f"A fully-marked entry for '{aspiration.id}' replayed through the real evaluator",
                20,
                MUTED,
            ),
            _text(
                70,
                200,
                f"at each observation age (review date {SWEEP_AS_OF}, stale_after_days = {SWEEP_STALE_AFTER_DAYS}).",
                20,
                MUTED,
            ),
            _text(
                70,
                244,
                "SOURCE-DRIVEN SCHEMATIC · every cell is an actual progress_report result · NOT A COMPLIANCE VERDICT",
                20,
                TEAL,
                "700",
            ),
        ]
    )
    cell_w, cell_h, gap = 202, 168, 8
    left, top, row_gap = 70, 300, 64
    boundary: tuple[int, int, int] | None = None
    for index, point in enumerate(points):
        row, column = divmod(index, SWEEP_COLUMNS)
        x = left + column * (cell_w + gap)
        y = top + row * (cell_h + row_gap)
        colour = STATUS_COLOURS[point.status]
        parts.append(
            f'<rect x="{x}" y="{y}" width="{cell_w}" height="{cell_h}" rx="10" fill="{CARD}" stroke="{colour}" stroke-width="2.5"/>'
        )
        parts.append(
            f'<rect x="{x}" y="{y}" width="{cell_w}" height="42" rx="10" fill="{colour}"/>'
        )
        parts.append(_text(x + 16, y + 30, point.status.value, 20, PAPER, "700"))
        age_label = (
            f"{point.age_days} d"
            if point.age_days >= 0
            else f"{point.age_days} d (future)"
        )
        parts.append(_text(x + 16, y + 80, age_label, 22, INK, "700"))
        parts.append(_text(x + 16, y + 114, point.observed_on, 20, MUTED))
        flag = (
            "stale" if point.stale else ("no audit" if point.date_issue else "current")
        )
        parts.append(_text(x + 16, y + 148, flag, 20, colour, "700"))
        if (
            boundary is None
            and index > 0
            and point.age_days > SWEEP_STALE_AFTER_DAYS
            and points[index - 1].age_days <= SWEEP_STALE_AFTER_DAYS
        ):
            boundary = (x - gap // 2 - 1, y, column)
    if boundary is not None:
        boundary_x, boundary_y, boundary_column = boundary
        parts.append(
            f'<line x1="{boundary_x}" y1="{boundary_y - 26}" x2="{boundary_x}" y2="{boundary_y + cell_h + 20}" stroke="{RED}" stroke-width="3" stroke-dasharray="8 6"/>'
        )
        label_x = boundary_x + 16 if boundary_column <= 2 else boundary_x - 620
        parts.append(
            _text(
                label_x,
                boundary_y - 34,
                f"exclusive boundary: age {SWEEP_STALE_AFTER_DAYS} is current, age {SWEEP_STALE_AFTER_DAYS + 1} is stale",
                20,
                RED,
                "700",
            )
        )
    rows_drawn = -(-len(points) // SWEEP_COLUMNS)
    legend_y = top + rows_drawn * (cell_h + row_gap) + 44
    legend_x = 70
    for status in (HorizonStatus.TOWARD, HorizonStatus.INQUIRY):
        colour = STATUS_COLOURS[status]
        parts.append(
            f'<rect x="{legend_x}" y="{legend_y - 20}" width="26" height="26" rx="6" fill="{colour}"/>'
        )
        parts.append(_text(legend_x + 38, legend_y, status.value, 20, INK, "700"))
        legend_x += 220
    parts.extend(
        [
            _text(70, legend_y + 46, "READING RULE", 20, GOLD_DARK, "700"),
            _text(
                272,
                legend_y + 46,
                "age or a future date reopens the question (INQUIRY); it never manufactures drift",
                20,
                INK,
            ),
            _text(
                70,
                legend_y + 80,
                "A stale reading is an invitation to look again, not evidence of failure.",
                20,
                MUTED,
            ),
        ]
    )
    parts.append("</svg>")
    return "".join(parts)


@dataclass(frozen=True)
class _LatticeRow:
    """One aspiration's replayed sweep, plus the age its reading first flips."""

    aspiration_id: str
    title: str
    statuses: tuple[HorizonStatus, ...]
    flip_age: int | None


def lattice_rows() -> tuple[_LatticeRow, ...]:
    """Replay :data:`SWEEP_AGES` through the evaluator for every aspiration.

    The shipped single-row sweep shows where *one* reading loses currency. This
    runs the same replay across the whole registry, so the claim that the
    staleness boundary is a property of the evaluator rather than of one entry
    becomes something the figure can be read off rather than asserted. Every
    cell is a real :func:`temporal_currentness_sweep` result.
    """
    rows: list[_LatticeRow] = []
    for item in GOLDEN_ASPIRATIONS:
        points = temporal_currentness_sweep(
            item.id,
            SWEEP_AGES,
            as_of=SWEEP_AS_OF,
            stale_after_days=SWEEP_STALE_AFTER_DAYS,
        )
        statuses = tuple(point.status for point in points)
        flip_age: int | None = None
        for index, point in enumerate(points):
            if (
                index > 0
                and point.status is HorizonStatus.INQUIRY
                and points[index - 1].status is HorizonStatus.TOWARD
            ):
                flip_age = point.age_days
                break
        rows.append(_LatticeRow(item.id, item.title, statuses, flip_age))
    return tuple(rows)


def lattice_deviations(rows: tuple[_LatticeRow, ...]) -> tuple[str, ...]:
    """Aspiration ids whose flip age differs from the first row's, in order."""
    if not rows:
        return ()
    reference = rows[0].flip_age
    return tuple(row.aspiration_id for row in rows if row.flip_age != reference)


def lattice_label_lines(
    title: str, wrap_width: int = 32, max_lines: int = 2
) -> list[str]:
    """Wrap one lattice row label, refusing a title the row cannot show whole.

    Slicing the wrapped lines instead would drop a title's tail silently, which
    is how a figure comes to disagree with the registry it claims to draw.
    """
    lines = _wrap(title, wrap_width)
    if len(lines) > max_lines:
        raise ValueError(f"lattice row label does not fit in two lines: {title!r}")
    return lines


def _svg_currentness_lattice() -> str:
    """The whole registry swept at once, so uniformity is shown, not claimed."""
    rows = lattice_rows()
    deviations = lattice_deviations(rows)
    reference_age = rows[0].flip_age
    width, height = 1600, 1290
    parts = _canvas(
        width,
        height,
        title="The Currentness Lattice",
        desc="The whole registry swept across all observation ages showing uniformity.",
    )
    parts.extend(
        [
            _text(70, 84, "THE CURRENTNESS LATTICE", 24, GOLD_DARK, "700"),
            _text(
                70,
                132,
                f"{len(rows)} aspirations × {len(SWEEP_AGES)} observation ages",
                40,
                INK,
                "700",
            ),
            _text(
                70,
                172,
                "Every cell is one real progress_report reading for a fully-marked, counter-signal-free entry",
                20,
                MUTED,
            ),
            _text(
                70,
                200,
                f"(review date {SWEEP_AS_OF}, stale_after_days = {SWEEP_STALE_AFTER_DAYS}) — "
                f"{len(rows) * len(SWEEP_AGES)} executed evaluator calls.",
                20,
                MUTED,
            ),
            _text(
                70,
                244,
                "SOURCE-DRIVEN SCHEMATIC · the lattice shows the evaluator's temporal rule, not any observed practice",
                20,
                TEAL,
                "700",
            ),
        ]
    )

    label_x = 90
    grid_x, cell_w, cell_pitch = 490, 60, 62
    flip_x = grid_x + len(SWEEP_AGES) * cell_pitch + 22
    top, row_pitch, cell_h = 386, 78, 62

    parts.append(_text(label_x, top - 20, "ASPIRATION", 20, TEAL, "700"))
    parts.append(_text(grid_x, top - 54, "OBSERVATION AGE IN DAYS", 20, TEAL, "700"))
    for index, age in enumerate(SWEEP_AGES):
        parts.append(
            _text(grid_x + index * cell_pitch + 6, top - 20, str(age), 20, MUTED)
        )
    parts.append(_text(flip_x, top - 20, "FLIPS AT", 20, TEAL, "700"))

    for row_index, row in enumerate(rows):
        y = top + row_index * row_pitch
        parts.append(
            f'<rect x="70" y="{y}" width="1460" height="{cell_h}" rx="10" fill="{CARD}" stroke="{CARD_LINE}" stroke-width="1.5"/>'
        )
        title_lines = lattice_label_lines(row.title)
        for line_index, line in enumerate(title_lines):
            parts.append(_text(label_x, y + 28 + line_index * 26, line, 20, INK, "700"))
        for column, status in enumerate(row.statuses):
            colour = STATUS_COLOURS[status]
            cx = grid_x + column * cell_pitch
            if status is HorizonStatus.TOWARD:
                parts.append(
                    f'<rect x="{cx}" y="{y + 16}" width="{cell_w - 16}" height="30" rx="6" fill="{colour}"/>'
                )
            else:
                parts.append(
                    f'<rect x="{cx}" y="{y + 16}" width="{cell_w - 16}" height="30" rx="6" fill="none" stroke="{colour}" stroke-width="3"/>'
                )
        flip_label = "—" if row.flip_age is None else f"{row.flip_age} d"
        parts.append(
            _text(
                flip_x,
                y + 40,
                flip_label,
                20,
                RED if row.aspiration_id in deviations else TEAL,
                "700",
            )
        )

    legend_y = top + len(rows) * row_pitch + 40
    parts.append(
        f'<rect x="70" y="{legend_y - 22}" width="44" height="30" rx="6" fill="{STATUS_COLOURS[HorizonStatus.TOWARD]}"/>'
    )
    parts.append(_text(128, legend_y, "TOWARD (filled)", 20, INK, "700"))
    parts.append(
        f'<rect x="440" y="{legend_y - 22}" width="44" height="30" rx="6" fill="none" stroke="{STATUS_COLOURS[HorizonStatus.INQUIRY]}" stroke-width="3"/>'
    )
    parts.append(_text(498, legend_y, "INQUIRY (outlined)", 20, INK, "700"))
    parts.append(
        _text(
            70,
            legend_y + 42,
            f"{_plural(len(deviations), 'row')} of {len(rows)} flip at an age other than "
            f"{reference_age} d — the boundary is a property of the evaluator, not of one entry.",
            20,
            RED if deviations else GOLD_DARK,
            "700",
        )
    )
    parts.append(
        _text(
            70,
            height - 34,
            "SOURCE-DRIVEN SCHEMATIC · uniform ageing is a fact about the code path, never evidence that any aspiration is served",
            20,
            GOLD_DARK,
            "700",
        )
    )
    parts.append("</svg>")
    return "".join(parts)


def _svg_signal_inventory() -> str:
    """The aggregate declared-signal vocabulary, one unit block per token."""
    inventory = signal_inventory()
    width, height = 1600, 1400
    parts = _canvas(
        width,
        height,
        title="The Signal Inventory",
        desc="The aggregate declared-signal vocabulary with one unit block per token.",
    )
    parts.extend(
        [
            _text(70, 84, "THE SIGNAL INVENTORY", 24, GOLD_DARK, "700"),
            _text(
                70,
                132,
                f"{inventory.total_markers} declared markers, {inventory.total_counter_signals} counter-signals",
                40,
                INK,
                "700",
            ),
            _text(
                70,
                172,
                "One block per declared token, aggregated from the versioned registry.",
                20,
                MUTED,
            ),
            _text(
                70,
                200,
                "The blocks are vocabulary the evaluator can match, not observations and not points.",
                20,
                MUTED,
            ),
            _text(
                70,
                244,
                f"UNIQUENESS · {inventory.unique_markers} of {inventory.total_markers} marker tokens distinct · "
                f"{inventory.unique_counter_signals} of {inventory.total_counter_signals} counter-signal tokens distinct",
                20,
                TEAL,
                "700",
            ),
        ]
    )
    top = 296
    row_h = 104
    block = 30
    for index, row in enumerate(inventory.rows):
        item = find_aspiration(row.aspiration_id)
        assert item is not None  # rows come from the registry itself
        y = top + index * row_h
        parts.append(
            f'<rect x="70" y="{y}" width="1460" height="90" rx="10" fill="{CARD}" stroke="{CARD_LINE}" stroke-width="1.5"/>'
        )
        parts.append(_text(100, y + 38, item.title, 22, INK, "700"))
        parts.append(_text(100, y + 70, f"horizon: {row.horizon}", 20, MUTED))
        block_x = 1080
        for _ in range(row.marker_count):
            parts.append(
                f'<rect x="{block_x}" y="{y + 30}" width="{block}" height="{block}" rx="6" fill="{TEAL}"/>'
            )
            block_x += block + 10
        block_x = 1380
        for _ in range(row.counter_signal_count):
            parts.append(
                f'<rect x="{block_x}" y="{y + 30}" width="{block}" height="{block}" rx="6" fill="none" stroke="{RED}" stroke-width="3"/>'
            )
            block_x += block + 10
    legend_y = top + len(inventory.rows) * row_h + 46
    parts.extend(
        [
            f'<rect x="70" y="{legend_y - 22}" width="{block}" height="{block}" rx="6" fill="{TEAL}"/>',
            _text(
                114, legend_y, "declared marker (a sign of movement toward)", 20, INK
            ),
            f'<rect x="640" y="{legend_y - 22}" width="{block}" height="{block}" rx="6" fill="none" stroke="{RED}" stroke-width="3"/>',
            _text(684, legend_y, "declared counter-signal (a sign of drift)", 20, INK),
            _text(
                70,
                height - 34,
                "SOURCE-DRIVEN SCHEMATIC · counts describe the declared vocabulary, never fulfilment or performance",
                20,
                GOLD_DARK,
                "700",
            ),
        ]
    )
    parts.append("</svg>")
    return "".join(parts)


def _svg_horizon_bands() -> str:
    """The nine horizons grouped by temporal reach; a reading aid, not a ladder."""
    bands = horizon_distribution()
    width, height = 1600, 1370
    parts = _canvas(
        width,
        height,
        title="The Horizon-Band Distribution",
        desc="Horizons grouped by temporal reach as an interpretive reading aid.",
    )
    parts.extend(
        [
            _text(70, 84, "THE HORIZON-BAND DISTRIBUTION", 24, GOLD_DARK, "700"),
            _text(
                70,
                132,
                f"{sum(len(band.aspiration_ids) for band in bands)} horizons, "
                f"{len(bands)} reaches of visibility",
                40,
                INK,
                "700",
            ),
            _text(
                70,
                172,
                "An interpretive grouping declared in the analysis layer: each aspiration is",
                20,
                MUTED,
            ),
            _text(
                70,
                200,
                "placed by when its direction becomes visible. Band order widens reach; it does not rank importance.",
                20,
                MUTED,
            ),
            _text(
                70,
                244,
                "SOURCE-DRIVEN SCHEMATIC · the bands are a reading aid, not registry contract and not a maturity ladder",
                20,
                TEAL,
                "700",
            ),
        ]
    )
    band_colours = (GOLD, TEAL, GOLD_DARK, RED)
    top = 292
    band_h = 232
    for index, band in enumerate(bands):
        colour = band_colours[index % len(band_colours)]
        y = top + index * (band_h + 24)
        parts.append(
            f'<rect x="70" y="{y}" width="1460" height="{band_h}" rx="12" fill="{CARD}" stroke="{colour}" stroke-width="2.5"/>'
        )
        parts.append(
            f'<rect x="70" y="{y}" width="12" height="{band_h}" rx="6" fill="{colour}"/>'
        )
        parts.append(_text(112, y + 48, band.band.upper(), 22, colour, "700"))
        parts.append(
            _text(
                112,
                y + 82,
                _plural(len(band.aspiration_ids), "aspiration"),
                20,
                MUTED,
            )
        )
        chip_x = 396
        for aspiration_id in band.aspiration_ids:
            item = find_aspiration(aspiration_id)
            assert item is not None  # band members come from the registry itself
            parts.append(
                f'<rect x="{chip_x}" y="{y + 24}" width="264" height="{band_h - 48}" rx="10" fill="{PAPER}" stroke="{CARD_LINE}" stroke-width="1.5"/>'
            )
            title_lines = _wrap(item.title, 20)[:3]
            for line_index, line in enumerate(title_lines):
                parts.append(
                    _text(chip_x + 18, y + 58 + line_index * 28, line, 20, INK, "700")
                )
            horizon_lines = _wrap(f"“{item.horizon}”", 22)[:2]
            horizon_top = y + band_h - 44 - (len(horizon_lines) - 1) * 28
            for line_index, line in enumerate(horizon_lines):
                parts.append(
                    _text(chip_x + 18, horizon_top + line_index * 28, line, 20, MUTED)
                )
            chip_x += 280
    parts.append(
        _text(
            70,
            height - 34,
            "SOURCE-DRIVEN SCHEMATIC · a wider horizon is not a higher rank; every band is revisited in its own time",
            20,
            GOLD_DARK,
            "700",
        )
    )
    parts.append("</svg>")
    return "".join(parts)


WORKED_BATCH_ENTRIES: tuple[HorizonEntry, ...] = (
    HorizonEntry(
        "attention-before-output",
        observed_markers=frozenset({"question revisited", "context named"}),
    ),
    HorizonEntry(
        "repairable-systems",
        observed_markers=frozenset({"failure named", "revision attempted"}),
        counter_signals=frozenset({"defect hidden to preserve appearance"}),
    ),
    HorizonEntry(
        "useful-to-others",
        observed_markers=frozenset({"handoff used"}),
    ),
    HorizonEntry(
        "honest-uncertainty",
        observed_markers=frozenset(
            {
                "limit stated beside claim",
                "confidence qualified in print",
                "extra token that is undeclared",
            }
        ),
    ),
    HorizonEntry(
        "not-a-real-id",
        observed_markers=frozenset({"whatever"}),
    ),
    HorizonEntry(
        "attention-before-output",
        observed_markers=frozenset({"question revisited"}),
    ),
)


def check_set_aside_accounting(fates: tuple[str, ...], intake_note_count: int) -> None:
    """The figure's own set-aside tally must equal the report's intake notes."""
    set_aside_count = sum(fate != "admitted" for fate in fates)
    if set_aside_count != intake_note_count:
        raise ValueError(
            "worked batch intake classification count mismatch: "
            f"{set_aside_count} figure set-asides != {intake_note_count} report intake notes"
        )


_WORKED_BATCH_REPORT = progress_report(list(WORKED_BATCH_ENTRIES))
_WORKED_BATCH_OVERVIEW = report_overview(_WORKED_BATCH_REPORT)
_WORKED_BATCH_COUNTS = _WORKED_BATCH_REPORT.counts()


def worked_batch_fates(
    entries: tuple[object, ...] = WORKED_BATCH_ENTRIES,
) -> tuple[str, ...]:
    """Map the single intake-classification source to figure display strings.

    Only the set-aside reasons the worked batch is built to show have a display
    string; any other outcome is refused rather than drawn as a blank chip.
    """
    fates: list[str] = []
    for classification in classify_intake_entries(entries):
        if classification.admitted:
            fates.append("admitted")
            continue
        if classification.set_aside_reason is IntakeSetAsideReason.UNKNOWN_ID:
            fates.append("set aside · unknown id")
            continue
        if classification.set_aside_reason is IntakeSetAsideReason.DUPLICATE:
            fates.append("set aside · duplicate")
            continue
        raise ValueError(
            "worked batch intake classification produced a non-displayable set-aside: "
            f"{classification.set_aside_reason}"
        )
    return tuple(fates)


def _svg_batch_overview() -> str:
    """The 04a worked batch fanning from submitted entries to real findings."""
    report = _WORKED_BATCH_REPORT
    overview = _WORKED_BATCH_OVERVIEW
    counts = _WORKED_BATCH_COUNTS
    width, height = 1600, 1330
    parts = _canvas(
        width,
        height,
        title="The Batch Reading Overview",
        desc="The worked batch fanning from submitted entries to real findings.",
    )
    parts.extend(
        [
            _text(70, 84, "THE BATCH READING OVERVIEW", 24, GOLD_DARK, "700"),
            _text(
                70,
                132,
                f"{len(WORKED_BATCH_ENTRIES)} entries in, {len(report.findings)} findings out",
                40,
                INK,
                "700",
            ),
            _text(
                70,
                172,
                "The worked batch of the batch-reading section replayed through progress_report",
                20,
                MUTED,
            ),
            _text(
                70,
                200,
                "and report_overview; every count is the actual result.",
                20,
                MUTED,
            ),
            _text(
                70,
                244,
                "SOURCE-DRIVEN SCHEMATIC · every grouping is an actual report_overview result · NOT A COMPLIANCE VERDICT",
                20,
                TEAL,
                "700",
            ),
        ]
    )

    fates = worked_batch_fates()
    check_set_aside_accounting(fates, overview.intake_note_count)

    col_top = 320
    parts.append(_text(70, col_top - 18, "SUBMITTED", 20, TEAL, "700"))
    chip_h, chip_gap = 112, 12
    for index, (entry, fate) in enumerate(zip(WORKED_BATCH_ENTRIES, fates)):
        y = col_top + index * (chip_h + chip_gap)
        aside = fate != "admitted"
        edge = RED if aside else CARD_LINE
        parts.append(
            f'<rect x="70" y="{y}" width="640" height="{chip_h}" rx="10" fill="{CARD}" stroke="{edge}" stroke-width="2"/>'
        )
        parts.append(_text(96, y + 36, entry.aspiration_id, 20, INK, "700"))
        detail = _plural(len(entry.observed_markers), "token") + " observed"
        if entry.counter_signals:
            detail += f" · {_plural(len(entry.counter_signals), 'counter-signal')}"
        parts.append(_text(96, y + 66, detail, 20, MUTED))
        parts.append(_text(96, y + 96, fate, 20, RED if aside else TEAL, "700"))

    fan_y = col_top + 3 * (chip_h + chip_gap) - chip_gap // 2
    parts.append(
        f'<path d="M720 {fan_y} L800 {fan_y}" stroke="{MUTED}" stroke-width="3"/>'
    )
    parts.append(
        f'<path d="M786 {fan_y - 12} L800 {fan_y} L786 {fan_y + 12}" fill="none" stroke="{MUTED}" stroke-width="3"/>'
    )

    group_x, group_w = 820, 710
    parts.append(
        _text(
            group_x,
            col_top - 18,
            "FINDINGS BY STATUS · from progress_report",
            20,
            TEAL,
            "700",
        )
    )
    y = col_top
    for status in HorizonStatus:
        ids = overview.by_status[status.value]
        colour = STATUS_COLOURS[status]
        id_lines = _wrap(", ".join(ids) if ids else "—", 52)[:3]
        box_h = 60 + len(id_lines) * 28 + 14
        parts.append(
            f'<rect x="{group_x}" y="{y}" width="{group_w}" height="{box_h}" rx="12" fill="{CARD}" stroke="{colour}" stroke-width="2.5"/>'
        )
        parts.append(
            f'<rect x="{group_x}" y="{y}" width="12" height="{box_h}" rx="6" fill="{colour}"/>'
        )
        parts.append(
            _text(
                group_x + 34,
                y + 42,
                f"{status.value} · {counts[status.value]}",
                22,
                colour,
                "700",
            )
        )
        for line_index, line in enumerate(id_lines):
            parts.append(_text(group_x + 34, y + 74 + line_index * 28, line, 20, INK))
        y += box_h + 16

    strip_y = 1080
    parts.append(
        f'<rect x="70" y="{strip_y}" width="1460" height="192" rx="12" fill="{PAPER}" stroke="{RED}" stroke-width="2.5"/>'
    )
    parts.append(
        _text(
            96,
            strip_y + 42,
            f"INTAKE ACCOUNTING · {_plural(overview.intake_note_count, 'record')} set aside · "
            f"{_plural(overview.ignored_marker_total, 'undeclared token')} ignored · "
            f"{_plural(overview.stale_count, 'stale flag')} · "
            f"{_plural(overview.date_issue_count, 'date issue')}",
            20,
            RED,
            "700",
        )
    )
    for note_index, note in enumerate(report.intake_notes):
        parts.append(_text(96, strip_y + 82 + note_index * 32, f"“{note}”", 20, INK))
    parts.append(
        _text(
            96,
            strip_y + 82 + len(report.intake_notes) * 32 + 8,
            "the whole delta between what was submitted and what was read is visible above",
            20,
            MUTED,
        )
    )
    parts.append(
        _text(
            70,
            height - 34,
            "SOURCE-DRIVEN SCHEMATIC · the groupings count readings in this record; a small record is not a poor one",
            20,
            GOLD_DARK,
            "700",
        )
    )
    parts.append("</svg>")
    return "".join(parts)
