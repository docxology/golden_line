"""Source-driven structural schematics that read registry and evaluator state."""

from __future__ import annotations

from datetime import date, timedelta

from golden_line.models import Aspiration, HorizonEntry, HorizonStatus
from golden_line.progress import EVALUATOR_STAGES, progress_report
from golden_line.registry import (
    GOLDEN_ASPIRATIONS,
    founding_aspirations,
    further_aspirations,
)

from .svg import (
    CARD,
    CARD_LINE,
    GOLD,
    GOLD_DARK,
    GOLD_HALO,
    GOLD_LIGHT,
    INK,
    MUTED,
    PAPER,
    RED,
    STATUS_COLOURS,
    TEAL,
    _canvas,
    _entries,
    _plural,
    _text,
    _wrap,
)


#: Interpretive icon and colour for each founding aspiration, keyed by
#: identifier. Keying by id rather than by registry position means a registry
#: reorder can never hand one aspiration another's symbol; a founding entry
#: with no entry here raises instead of drawing a silently wrong icon.
FOUNDING_SYMBOLS: dict[str, tuple[str, str]] = {
    "attention-before-output": (GOLD, "attention"),
    "useful-to-others": (TEAL, "usefulness"),
    "repairable-systems": (GOLD_DARK, "repair"),
    "wide-human-flourishing": (RED, "flourishing"),
}

#: Where each founding card sits. Positions are layout, not rank.
_THREAD_SLOTS = ((300, 340), (1300, 340), (300, 720), (1300, 720))


def thread_nodes(
    founding: tuple[Aspiration, ...],
    symbols: dict[str, tuple[str, str]] = FOUNDING_SYMBOLS,
    slots: tuple[tuple[int, int], ...] = _THREAD_SLOTS,
) -> tuple[tuple[Aspiration, int, int, str, str], ...]:
    """Pair each founding aspiration with its slot, colour, and icon.

    Both failure modes are refused rather than drawn around: an aspiration with
    no declared symbol, and a founding set the layout has no room for.
    """
    missing = [item.id for item in founding if item.id not in symbols]
    if missing:
        raise ValueError(f"founding aspirations without a declared symbol: {missing}")
    if len(founding) != len(slots):
        raise ValueError(
            f"the thread figure lays out {len(slots)} founding cards but the "
            f"registry declares {len(founding)} founding aspirations"
        )
    return tuple(
        (item, slot[0], slot[1], *symbols[item.id])
        for item, slot in zip(founding, slots)
    )


def _svg_thread() -> str:
    """A source-derived loop for the founding four, not a progress ladder."""
    nodes = thread_nodes(founding_aspirations())
    parts = _canvas(
        1600,
        1000,
        title="The Golden Line",
        desc="Four founding aspirations held in a revisable loop. Direction is not a score.",
    )
    parts.extend(
        [
            f'<circle cx="800" cy="530" r="300" fill="none" stroke="{GOLD_LIGHT}" stroke-width="2" stroke-dasharray="2 18" opacity="0.7"/>',
            f'<circle cx="800" cy="530" r="238" fill="none" stroke="{CARD_LINE}" stroke-width="1.5"/>',
            f'<path d="M800 262 C 1080 262, 1235 392, 1135 632 C 1050 837, 690 857, 485 662 C 315 502, 505 262, 800 262" fill="none" stroke="{GOLD}" stroke-width="12" stroke-linecap="round"/>',
            f'<path d="M800 262 C 1080 262, 1235 392, 1135 632 C 1050 837, 690 857, 485 662 C 315 502, 505 262, 800 262" fill="none" stroke="{GOLD_HALO}" stroke-width="3" stroke-dasharray="3 18" stroke-linecap="round"/>',
            _text(70, 90, "THE GOLDEN LINE", 24, GOLD_DARK, "700"),
            _text(
                70, 140, "Four aspirations, held in a revisable loop", 42, INK, "700"
            ),
            _text(
                70,
                180,
                "The founding four correct one another; they are not steps on a ladder or a scorecard.",
                20,
                MUTED,
            ),
            _text(
                70,
                232,
                "SOURCE-DRIVEN SCHEMATIC · NOT A COMPLIANCE VERDICT",
                20,
                TEAL,
                "700",
            ),
            _text(690, 512, "DIRECTION", 20, GOLD_DARK, "700"),
            _text(674, 552, "not a score", 26, INK, "700"),
            _text(636, 588, "look · transfer · repair · serve", 20, MUTED),
            _text(70, 934, "READING RULE", 20, GOLD_DARK, "700"),
            _text(
                272,
                934,
                "a marker makes direction discussable; a missing marker keeps the question open",
                20,
                INK,
            ),
            _text(
                70,
                968,
                "The Golden Line does not replace refusal, evidence, or attention to what is absent.",
                20,
                MUTED,
            ),
        ]
    )
    for item, x, y, colour, icon in nodes:
        card_x = x - 268
        card_y = y - 90
        parts.extend(
            [
                f'<rect x="{card_x}" y="{card_y}" width="536" height="180" rx="18" fill="{CARD}" stroke="{colour}" stroke-width="2.5"/>',
                f'<circle cx="{card_x + 44}" cy="{card_y + 46}" r="26" fill="{PAPER}" stroke="{colour}" stroke-width="3"/>',
            ]
        )
        if icon == "attention":
            parts.extend(
                [
                    f'<ellipse cx="{card_x + 44}" cy="{card_y + 46}" rx="14" ry="9" fill="none" stroke="{colour}" stroke-width="3"/>',
                    f'<circle cx="{card_x + 44}" cy="{card_y + 46}" r="4" fill="{colour}"/>',
                ]
            )
        elif icon == "usefulness":
            parts.extend(
                [
                    f'<path d="M{card_x + 30} {card_y + 56} L{card_x + 44} {card_y + 33} L{card_x + 58} {card_y + 56}" fill="none" stroke="{colour}" stroke-width="3" stroke-linecap="round"/>',
                    f'<path d="M{card_x + 31} {card_y + 46} L{card_x + 57} {card_y + 46}" stroke="{colour}" stroke-width="3"/>',
                ]
            )
        elif icon == "repair":
            parts.extend(
                [
                    f'<path d="M{card_x + 32} {card_y + 34} L{card_x + 57} {card_y + 59}" stroke="{colour}" stroke-width="5" stroke-linecap="round"/>',
                    f'<path d="M{card_x + 34} {card_y + 36} L{card_x + 40} {card_y + 30} M{card_x + 51} {card_y + 53} L{card_x + 59} {card_y + 61}" stroke="{colour}" stroke-width="3" stroke-linecap="round"/>',
                ]
            )
        else:
            parts.extend(
                [
                    f'<path d="M{card_x + 44} {card_y + 60} L{card_x + 44} {card_y + 41} M{card_x + 44} {card_y + 47} L{card_x + 32} {card_y + 37} M{card_x + 44} {card_y + 49} L{card_x + 56} {card_y + 38}" stroke="{colour}" stroke-width="3" stroke-linecap="round"/>',
                    f'<circle cx="{card_x + 44}" cy="{card_y + 30}" r="10" fill="none" stroke="{colour}" stroke-width="3"/>',
                ]
            )
        title_lines = _wrap(item.title, 29)[:3]
        for line_index, line in enumerate(title_lines):
            parts.append(
                _text(card_x + 88, card_y + 42 + line_index * 27, line, 22, INK, "700")
            )
        title_bottom = card_y + 42 + len(title_lines) * 27
        parts.extend(
            [
                _text(
                    card_x + 88,
                    title_bottom + 8,
                    f"horizon · {item.horizon}",
                    20,
                    MUTED,
                ),
                _text(
                    card_x + 88,
                    title_bottom + 42,
                    f"{_plural(len(item.markers), 'marker')}  ·  "
                    f"{_plural(len(item.counter_signals), 'counter-signal')}",
                    20,
                    colour,
                    "700",
                ),
            ]
        )
    parts.extend(
        [
            f'<path d="M1090 186 C 1150 166, 1210 166, 1260 190" fill="none" stroke="{RED}" stroke-width="4" stroke-linecap="round"/>',
            _text(1090, 152, "counter-signals keep the loop honest", 20, RED, "700"),
            "</svg>",
        ]
    )
    return "".join(parts)


def _svg_registry_map() -> str:
    """Taxonomy of the whole registry, drawn from the live source tuple."""
    width, height = 1600, 1380
    founding = founding_aspirations()
    further = further_aspirations()
    parts = _canvas(
        width,
        height,
        title="The Aspiration Registry",
        desc="A taxonomy of all versioned aspirations with their horizons, markers, and counter-signals.",
    )
    parts.extend(
        [
            _text(70, 84, "THE ASPIRATION REGISTRY", 24, GOLD_DARK, "700"),
            _text(
                70,
                132,
                f"{len(GOLDEN_ASPIRATIONS)} versioned aspirations, drawn from source",
                40,
                INK,
                "700",
            ),
            _text(
                70,
                172,
                "Each row shows a horizon and the declared markers and counter-signals",
                20,
                MUTED,
            ),
            _text(
                70,
                200,
                "that make its readings reachable. No cell is a grade.",
                20,
                MUTED,
            ),
        ]
    )
    row_step = 104
    groups = (
        (f"FOUNDING · {_entries(len(founding))}", founding, 288),
        (
            f"FURTHER · {_entries(len(further))}",
            further,
            288 + len(founding) * row_step + 100,
        ),
    )

    for label, items, top in groups:
        parts.append(_text(70, top - 20, label, 20, TEAL, "700"))
        parts.append(
            f'<line x1="70" y1="{top - 6}" x2="1530" y2="{top - 6}" stroke="{CARD_LINE}" stroke-width="2"/>'
        )
        for index, item in enumerate(items):
            y = top + index * row_step
            parts.append(
                f'<rect x="70" y="{y}" width="1460" height="90" rx="10" fill="{CARD}" stroke="{CARD_LINE}" stroke-width="1.5"/>'
            )
            parts.append(
                f'<rect x="70" y="{y}" width="8" height="90" rx="4" fill="{GOLD}"/>'
            )
            parts.append(_text(100, y + 38, item.title, 22, INK, "700"))
            parts.append(_text(100, y + 70, f"horizon: {item.horizon}", 20, MUTED))
            parts.append(
                f'<rect x="1078" y="{y + 24}" width="204" height="44" rx="8" fill="{PAPER}" stroke="{TEAL}" stroke-width="1.5"/>'
            )
            parts.append(
                _text(
                    1098,
                    y + 53,
                    _plural(len(item.markers), "marker"),
                    20,
                    TEAL,
                    "700",
                )
            )
            parts.append(
                f'<rect x="1298" y="{y + 24}" width="232" height="44" rx="8" fill="{PAPER}" stroke="{RED}" stroke-width="1.5"/>'
            )
            parts.append(
                _text(
                    1318,
                    y + 53,
                    _plural(len(item.counter_signals), "counter-signal"),
                    20,
                    RED,
                    "700",
                )
            )
    parts.append(
        _text(
            70,
            height - 34,
            "SOURCE-DRIVEN SCHEMATIC · marker and counter-signal counts describe reachability, not performance",
            20,
            GOLD_DARK,
            "700",
        )
    )
    parts.append("</svg>")
    return "".join(parts)


def _svg_decision_path() -> str:
    """The evaluator's decision rule, terminating in the status enum values."""
    width, height = 1600, 1030
    statuses = {status.name: status.value for status in HorizonStatus}
    parts = _canvas(
        width,
        height,
        title="The Horizon Decision Path",
        desc="The evaluator's ordered decision rule terminating in four directional readings.",
    )
    parts.extend(
        [
            _text(70, 84, "THE HORIZON DECISION PATH", 24, GOLD_DARK, "700"),
            _text(
                70, 132, "How one entry becomes one directional reading", 40, INK, "700"
            ),
            _text(
                70,
                172,
                "Clauses are tested in order; the first that matches decides.",
                20,
                MUTED,
            ),
            _text(
                70,
                200,
                "A counter-signal outranks every marker.",
                20,
                MUTED,
            ),
        ]
    )

    def decision(x: int, y: int, text: str) -> None:
        parts.append(
            f'<rect x="{x}" y="{y}" width="800" height="78" rx="10" fill="{CARD}" stroke="{GOLD_DARK}" stroke-width="2"/>'
        )
        parts.append(_text(x + 26, y + 48, text, 22, INK, "700"))

    def terminal(x: int, y: int, status_value: str, colour: str) -> None:
        parts.append(
            f'<rect x="{x}" y="{y}" width="350" height="66" rx="33" fill="{PAPER}" stroke="{colour}" stroke-width="3"/>'
        )
        parts.append(_text(x + 30, y + 44, status_value, 24, colour, "700"))

    steps = [
        (
            "Any admitted entry for this aspiration?",
            statuses["NOT_OBSERVED"],
            RED,
            "no",
        ),
        ("A declared counter-signal recorded?", statuses["DRIFTING"], RED, "yes"),
        ("No declared marker observed?", statuses["INQUIRY"], GOLD_DARK, "yes"),
        ("Some declared markers still unmet?", statuses["INQUIRY"], GOLD_DARK, "yes"),
        (
            "Stale, future, or unauditable date (review on)?",
            statuses["INQUIRY"],
            GOLD_DARK,
            "yes",
        ),
    ]
    top = 248
    gap = 128
    for index, (question, status_value, colour, branch) in enumerate(steps):
        y = top + index * gap
        decision(70, y, question)
        parts.append(
            f'<line x1="870" y1="{y + 39}" x2="1190" y2="{y + 39}" stroke="{colour}" stroke-width="2.5"/>'
        )
        parts.append(_text(896, y + 28, branch, 20, colour, "700"))
        terminal(1190, y + 6, status_value, colour)
        if index < len(steps) - 1:
            parts.append(
                f'<line x1="470" y1="{y + 78}" x2="470" y2="{y + gap}" stroke="{TEAL}" stroke-width="2.5"/>'
            )
            parts.append(_text(486, y + 106, "otherwise", 20, TEAL, "700"))
    final_y = top + len(steps) * gap
    parts.append(
        f'<line x1="470" y1="{top + (len(steps) - 1) * gap + 78}" x2="470" y2="{final_y + 6}" stroke="{TEAL}" stroke-width="2.5"/>'
    )
    terminal(300, final_y, statuses["TOWARD"], TEAL)
    parts.append(
        _text(
            688,
            final_y + 44,
            "every declared marker observed, no counter-signal, currentness auditable",
            20,
            MUTED,
        )
    )
    parts.append(
        _text(
            70,
            height - 34,
            "SOURCE-DRIVEN SCHEMATIC · statuses quoted from the HorizonStatus enumeration · NOT A COMPLIANCE VERDICT",
            20,
            GOLD_DARK,
            "700",
        )
    )
    parts.append("</svg>")
    return "".join(parts)


#: The four evidence conditions the precedence panel replays, in reading order.
#: Each is a (column heading, whether markers are filed, whether a
#: counter-signal is filed, observation age in days) tuple; the age is only
#: consulted when temporal review is enabled for that column.
_PRECEDENCE_COLUMNS: tuple[tuple[str, bool, bool, int], ...] = (
    ("complete markers, no counter-signal", True, False, 0),
    ("complete markers, one counter-signal", True, True, 0),
    ("no markers, one counter-signal", False, True, 0),
    ("complete markers, one counter-signal, {age} d old", True, True, 400),
)


def precedence_heading_lines(
    heading: str, age: int, wrap_width: int = 20, max_lines: int = 4
) -> list[str]:
    """Wrap a column heading, refusing one the column has no room to show.

    The age is filled in from the column that uses it, so the heading cannot
    describe a different observation age than the cells beneath it.
    """
    lines = _wrap(heading.format(age=age), wrap_width)
    if len(lines) > max_lines:
        raise ValueError(f"precedence column heading does not fit: {heading!r}")
    return lines


#: Review context for the precedence replay. Fixed so the figure is
#: reproducible and never tied to the build day.
PRECEDENCE_AS_OF = "2026-07-18"
PRECEDENCE_STALE_AFTER_DAYS = 90


def precedence_cells() -> tuple[tuple[str, tuple[HorizonStatus, ...]], ...]:
    """Replay the four evidence conditions against every registry aspiration.

    The decision path draws counter-signal precedence as a clause in a list.
    This runs it: for each aspiration the public :func:`progress_report` is
    called once per column and the returned status is what the figure prints,
    so the rule is read off executed output rather than asserted by a box.
    """
    review = date.fromisoformat(PRECEDENCE_AS_OF)
    rows: list[tuple[str, tuple[HorizonStatus, ...]]] = []
    for item in GOLDEN_ASPIRATIONS:
        statuses: list[HorizonStatus] = []
        for _heading, with_markers, with_counter, age in _PRECEDENCE_COLUMNS:
            observed_on = (review - timedelta(days=age)).isoformat()
            entry = HorizonEntry(
                aspiration_id=item.id,
                observed_markers=frozenset(item.markers)
                if with_markers
                else frozenset(),
                counter_signals=(
                    frozenset(item.counter_signals) if with_counter else frozenset()
                ),
                observed_on=observed_on,
            )
            report = progress_report(
                [entry],
                (item,),
                as_of=review,
                stale_after_days=PRECEDENCE_STALE_AFTER_DAYS,
            )
            statuses.append(report.findings[0].status)
        rows.append((item.id, tuple(statuses)))
    return tuple(rows)


def _svg_counter_signal_dominance() -> str:
    """Counter-signal precedence, replayed for every aspiration rather than drawn."""
    rows = precedence_cells()
    dominated = sum(1 for _, statuses in rows if statuses[1] is HorizonStatus.DRIFTING)
    stale_dominated = sum(
        1 for _, statuses in rows if statuses[3] is HorizonStatus.DRIFTING
    )
    width, height = 1600, 1360
    parts = _canvas(
        width,
        height,
        title="Counter-Signal Precedence",
        desc="Counter-signal precedence replayed for every aspiration rather than drawn.",
    )
    parts.extend(
        [
            _text(70, 84, "COUNTER-SIGNAL PRECEDENCE", 24, GOLD_DARK, "700"),
            _text(
                70,
                132,
                f"{dominated} of {len(rows)} aspirations still read DRIFTING",
                40,
                INK,
                "700",
            ),
            _text(
                70,
                172,
                "Each cell is one real progress_report call on a synthetic entry for that aspiration",
                20,
                MUTED,
            ),
            _text(
                70,
                200,
                f"(review date {PRECEDENCE_AS_OF}, stale_after_days = {PRECEDENCE_STALE_AFTER_DAYS}).",
                20,
                MUTED,
            ),
            _text(
                70,
                244,
                "SOURCE-DRIVEN SCHEMATIC · a replayed clause ordering, never a judgement of the work or its author",
                20,
                TEAL,
                "700",
            ),
        ]
    )

    label_x, grid_x, col_pitch, col_w = 90, 590, 235, 220
    header_y, top, row_pitch, cell_h = 296, 424, 84, 66
    for index, (heading, _markers, _counter, age) in enumerate(_PRECEDENCE_COLUMNS):
        x = grid_x + index * col_pitch
        lines = precedence_heading_lines(heading, age)
        for line_index, line in enumerate(lines):
            parts.append(_text(x, header_y + line_index * 28, line, 20, TEAL, "700"))
    parts.append(_text(label_x, top - 22, "ASPIRATION", 20, TEAL, "700"))

    for row_index, (aspiration_id, statuses) in enumerate(rows):
        y = top + row_index * row_pitch
        parts.append(
            f'<rect x="70" y="{y}" width="1460" height="{cell_h}" rx="10" fill="{CARD}" stroke="{CARD_LINE}" stroke-width="1.5"/>'
        )
        parts.append(_text(label_x, y + 42, aspiration_id, 20, INK, "700"))
        for column, status in enumerate(statuses):
            x = grid_x + column * col_pitch
            colour = STATUS_COLOURS[status]
            filled = status is HorizonStatus.DRIFTING
            parts.append(
                f'<rect x="{x - 16}" y="{y + 12}" width="{col_w}" height="42" rx="8" '
                f'fill="{colour if filled else PAPER}" stroke="{colour}" stroke-width="2.5"/>'
            )
            parts.append(
                _text(x, y + 40, status.value, 20, PAPER if filled else colour, "700")
            )

    summary_y = top + len(rows) * row_pitch + 34
    parts.append(
        _text(
            70,
            summary_y,
            f"Complete markers plus one declared counter-signal returns DRIFTING for "
            f"{dominated} of {len(rows)} aspirations; at an observation "
            f"{_PRECEDENCE_COLUMNS[3][3]} days old it still does, for {stale_dominated}.",
            20,
            GOLD_DARK,
            "700",
        )
    )
    parts.append(
        _text(
            70,
            summary_y + 34,
            "Staleness reopens a positive reading; it never erases a recorded drift, and drift never becomes a verdict on a person.",
            20,
            MUTED,
        )
    )
    parts.append(
        _text(
            70,
            height - 34,
            "SOURCE-DRIVEN SCHEMATIC · filled cells are DRIFTING, outlined cells are not · NOT A COMPLIANCE VERDICT",
            20,
            GOLD_DARK,
            "700",
        )
    )
    parts.append("</svg>")
    return "".join(parts)


def _pipeline_setaside_demo() -> tuple[tuple[str, str], ...]:
    """Replay the three intake set-aside categories through the real evaluator.

    A malformed record, an unknown-id entry, and a duplicate entry are run
    through the public :func:`progress_report`; the note text drawn in the
    figure is the evaluator's own verbatim intake note, never a paraphrase.
    """
    first = GOLDEN_ASPIRATIONS[0]
    demo_batch = [
        "not a record",
        HorizonEntry("not-a-real-id"),
        HorizonEntry(first.id),
        HorizonEntry(first.id),
    ]
    report = progress_report(demo_batch)
    labels = ("malformed record", "unknown id", "duplicate entry")
    assert len(report.intake_notes) == len(labels)  # one note per set-aside kind
    return tuple(zip(labels, report.intake_notes))


def pipeline_stages(
    names: tuple[str, ...],
    bodies: tuple[str, ...],
    colours: tuple[str, ...],
) -> list[tuple[str, str, str]]:
    """Zip the evaluator's declared stage names with the figure's copy and colour.

    The figure may not describe more or fewer stages than
    :data:`golden_line.progress.EVALUATOR_STAGES` declares.
    """
    if not len(names) == len(bodies) == len(colours):
        raise ValueError(
            "the pipeline figure describes a different number of stages than "
            f"progress.EVALUATOR_STAGES declares ({len(names)})"
        )
    return [
        (f"{index + 1} · {name.upper()}", body, colour)
        for index, (name, body, colour) in enumerate(zip(names, bodies, colours))
    ]


def _svg_pipeline() -> str:
    """The three evaluator stages, with the intake set-aside branch visible."""
    width, height = 1600, 1020
    setasides = _pipeline_setaside_demo()
    parts = _canvas(
        width,
        height,
        title="The Staged Evaluation Pipeline",
        desc="Three evaluator stages with the intake set-aside branch visible.",
    )
    parts.extend(
        [
            _text(70, 84, "THE STAGED EVALUATION PIPELINE", 24, GOLD_DARK, "700"),
            _text(70, 132, "progress_report runs three stages", 40, INK, "700"),
            _text(
                70,
                172,
                "Malformed or unexpected input is recorded, never raised;",
                20,
                MUTED,
            ),
            _text(
                70,
                200,
                "every finding carries a full reasons trail.",
                20,
                MUTED,
            ),
        ]
    )
    stage_bodies = (
        "One entry per known id (first wins). Malformed records, unknown ids, and duplicates are set aside into intake notes.",
        "Observed markers and counter-signals are intersected with the declared sets. Undeclared tokens are ignored and noted.",
        "The matched sets, with optional temporal review, select one of the four directional readings.",
    )
    stage_colours = (TEAL, GOLD_DARK, RED)
    stages = pipeline_stages(EVALUATOR_STAGES, stage_bodies, stage_colours)
    top = 248
    box_h = 168
    box_w = 900
    for index, (title, body, colour) in enumerate(stages):
        y = top + index * (box_h + 36)
        parts.append(
            f'<rect x="70" y="{y}" width="{box_w}" height="{box_h}" rx="12" fill="{CARD}" stroke="{colour}" stroke-width="2.5"/>'
        )
        parts.append(
            f'<rect x="70" y="{y}" width="12" height="{box_h}" rx="6" fill="{colour}"/>'
        )
        parts.append(_text(112, y + 48, title, 24, colour, "700"))
        for line_index, line in enumerate(_wrap(body, 60)[:3]):
            parts.append(_text(112, y + 88 + line_index * 30, line, 20, INK))
        if index < len(stages) - 1:
            arrow_y = y + box_h
            parts.append(
                f'<path d="M520 {arrow_y} L520 {arrow_y + 36}" stroke="{MUTED}" stroke-width="3"/>'
            )
            parts.append(
                f'<path d="M508 {arrow_y + 24} L520 {arrow_y + 36} L532 {arrow_y + 24}" fill="none" stroke="{MUTED}" stroke-width="3"/>'
            )

    chan_x, chan_y, chan_w, chan_h = 1010, 248, 520, 480
    parts.append(
        f'<path d="M{70 + box_w} {top + 78} L{chan_x} {top + 78}" stroke="{RED}" stroke-width="3" stroke-dasharray="8 6"/>'
    )
    parts.append(
        f'<path d="M{chan_x - 14} {top + 66} L{chan_x} {top + 78} L{chan_x - 14} {top + 90}" fill="none" stroke="{RED}" stroke-width="3"/>'
    )
    parts.append(
        f'<rect x="{chan_x}" y="{chan_y}" width="{chan_w}" height="{chan_h}" rx="12" fill="{PAPER}" stroke="{RED}" stroke-width="2.5"/>'
    )
    parts.append(
        _text(
            chan_x + 22,
            chan_y + 44,
            f"SET ASIDE · {_plural(len(setasides), 'kind')} → intake_notes",
            20,
            RED,
            "700",
        )
    )
    parts.append(
        _text(
            chan_x + 22,
            chan_y + 76,
            "notes quoted verbatim from the evaluator",
            20,
            MUTED,
        )
    )
    chip_y = chan_y + 98
    for label, note in setasides:
        note_lines = _wrap(note, 40)[:3]
        chip_h = 42 + len(note_lines) * 26
        parts.append(
            f'<rect x="{chan_x + 18}" y="{chip_y}" width="{chan_w - 36}" height="{chip_h}" rx="8" fill="{CARD}" stroke="{CARD_LINE}" stroke-width="1.5"/>'
        )
        parts.append(_text(chan_x + 36, chip_y + 30, label.upper(), 20, RED, "700"))
        for line_index, line in enumerate(note_lines):
            parts.append(
                _text(chan_x + 36, chip_y + 58 + line_index * 26, line, 20, INK)
            )
        chip_y += chip_h + 12
    parts.append(
        _text(
            chan_x + 22,
            chan_y + chan_h - 22,
            "set aside, named, and counted — never silent",
            20,
            MUTED,
        )
    )

    note_y = chan_y + chan_h + 28
    parts.append(
        f'<path d="M{70 + box_w} {top + box_h + 36 + 78} L{chan_x} {note_y + 40}" stroke="{GOLD_DARK}" stroke-width="2.5" stroke-dasharray="8 6"/>'
    )
    parts.append(
        f'<rect x="{chan_x}" y="{note_y}" width="{chan_w}" height="120" rx="12" fill="{PAPER}" stroke="{GOLD_DARK}" stroke-width="2.5"/>'
    )
    parts.append(
        _text(chan_x + 22, note_y + 42, "UNDECLARED TOKENS", 20, GOLD_DARK, "700")
    )
    for line_index, line in enumerate(
        _wrap("ignored and noted; they can never determine a status", 34)
    ):
        parts.append(_text(chan_x + 22, note_y + 76 + line_index * 28, line, 20, INK))

    outcome_y = top + len(stages) * (box_h + 36) + 32
    parts.append(
        _text(
            70,
            outcome_y,
            f"OUTCOME: {_plural(len(GOLDEN_ASPIRATIONS), 'finding')} — one per aspiration, each a direction, never a grade.",
            20,
            GOLD_DARK,
            "700",
        )
    )
    parts.append(
        _text(
            70,
            height - 34,
            "SOURCE-DRIVEN SCHEMATIC · set-aside notes are actual progress_report intake notes · NOT A COMPLIANCE VERDICT",
            20,
            TEAL,
            "700",
        )
    )
    parts.append("</svg>")
    return "".join(parts)


def _svg_evidence_state_matrix() -> str:
    """Show the four states as evidence conditions, never as a ranking."""
    width, height = 1600, 820
    rows = (
        (
            HorizonStatus.NOT_OBSERVED.value,
            "No admitted entry",
            "No observation is not evidence of absence.",
            RED,
        ),
        (
            HorizonStatus.INQUIRY.value,
            "Entry exists, but evidence is incomplete or not current",
            "The direction stays open; do not round uncertainty up or down.",
            GOLD_DARK,
        ),
        (
            HorizonStatus.DRIFTING.value,
            "A declared counter-signal is present",
            "This record-level warning takes precedence over positive markers.",
            RED,
        ),
        (
            HorizonStatus.TOWARD.value,
            "All declared markers, no counter-signal, currentness auditable",
            "This is directional evidence only; it is not safety, virtue, or permission.",
            TEAL,
        ),
    )
    parts = _canvas(
        width,
        height,
        title="The Evidence-State Matrix",
        desc="Four horizon status readings mapped to bounded evidence conditions.",
    )
    parts.extend(
        [
            _text(70, 84, "THE EVIDENCE-STATE MATRIX", 24, GOLD_DARK, "700"),
            _text(70, 132, "Four readings, four bounded claims", 40, INK, "700"),
            _text(
                70,
                172,
                "The statuses describe the admitted record and its limits;",
                20,
                MUTED,
            ),
            _text(70, 200, "they are not a scale from bad to good.", 20, MUTED),
        ]
    )
    top = 244
    for index, (status, condition, limit, colour) in enumerate(rows):
        y = top + index * 128
        parts.append(
            f'<rect x="70" y="{y}" width="1460" height="104" rx="12" fill="{CARD}" stroke="{colour}" stroke-width="2.5"/>'
        )
        parts.append(
            f'<rect x="70" y="{y}" width="316" height="104" rx="12" fill="{colour}"/>'
        )
        parts.append(_text(102, y + 62, status, 26, PAPER, "700"))
        parts.append(_text(422, y + 44, condition, 22, INK, "700"))
        parts.append(_text(422, y + 78, limit, 20, MUTED))
    parts.append(
        _text(
            70,
            height - 34,
            "SOURCE-DRIVEN SCHEMATIC · bounded evidence is not a verdict",
            20,
            GOLD_DARK,
            "700",
        )
    )
    parts.append("</svg>")
    return "".join(parts)
