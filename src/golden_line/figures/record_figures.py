"""Figures that replay the evaluator to draw its record, not its description.

Two properties of the decision rule are stated in the formalism and drawn
nowhere else in the figure set:

* marker *completeness* — ``TOWARD`` requires the whole declared marker set, so
  an entry recording every marker but one reads exactly as an entry recording
  none. :func:`completeness_rows` files every subset of every aspiration's
  markers and reports what the evaluator returned;
* the *shape of a finding* — every reading comes back as the same record, and
  which of its structured fields carry content is decided by the matching stage.
  :func:`field_matrix_rows` runs one witness per evidence condition and reports,
  field by field, what the returned finding actually carries.

Both helpers call the public :func:`~golden_line.progress.progress_report` and
copy its results. Neither computes a status, and neither ranks anything: a cell
describes one synthetic record under one evidence condition.
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from datetime import date, timedelta
from itertools import combinations

from golden_line.models import (
    Aspiration,
    HorizonEntry,
    HorizonFinding,
    HorizonStatus,
)
from golden_line.progress import progress_report
from golden_line.registry import GOLDEN_ASPIRATIONS
from golden_line.version import REGISTRY_VERSION

from .svg import (
    CARD,
    CARD_LINE,
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

#: Review context for both replays, derived from the registry version so the
#: figures are reproducible and never tied to the build day.
RECORD_AS_OF = REGISTRY_VERSION.replace(".", "-")
RECORD_STALE_AFTER_DAYS = 90


def _dated(offset_days: int) -> str:
    """An ISO observation date ``offset_days`` before the fixed review date."""
    return (date.fromisoformat(RECORD_AS_OF) - timedelta(days=offset_days)).isoformat()


# ---------------------------------------------------------------------------
# Marker completeness
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CompletenessCell:
    """One executed reading for one observed-marker subset."""

    observed_count: int
    status: HorizonStatus
    unmet_count: int


@dataclass(frozen=True)
class CompletenessRow:
    """One aspiration's readings across every subset of its declared markers."""

    aspiration_id: str
    title: str
    cells: tuple[CompletenessCell, ...]


def marker_subsets(marker_count: int) -> tuple[tuple[int, ...], ...]:
    """Every subset of ``marker_count`` marker positions, smallest first."""
    return tuple(
        indices
        for size in range(marker_count + 1)
        for indices in combinations(range(marker_count), size)
    )


def completeness_rows(
    aspirations: tuple[Aspiration, ...] = GOLDEN_ASPIRATIONS,
) -> tuple[CompletenessRow, ...]:
    """File every observed-marker subset for every aspiration and read the result.

    The panel is a grid, so every row must have the same columns. A registry
    whose aspirations declare different numbers of markers has no such grid;
    that is refused here rather than drawn around, because a row silently
    shorter than its heading is how a figure comes to disagree with the
    registry it claims to draw.
    """
    counts = {len(item.markers) for item in aspirations}
    if len(counts) != 1:
        raise ValueError(
            "the completeness panel needs one column per marker subset, but the "
            f"registry declares differing marker counts: {sorted(counts)}"
        )
    marker_count = counts.pop()
    subsets = marker_subsets(marker_count)
    review = date.fromisoformat(RECORD_AS_OF)

    rows: list[CompletenessRow] = []
    for item in aspirations:
        cells: list[CompletenessCell] = []
        for indices in subsets:
            entry = HorizonEntry(
                aspiration_id=item.id,
                observed_markers=frozenset(item.markers[index] for index in indices),
                observed_on=review.isoformat(),
            )
            finding = progress_report(
                [entry],
                (item,),
                as_of=review,
                stale_after_days=RECORD_STALE_AFTER_DAYS,
            ).findings[0]
            cells.append(
                CompletenessCell(
                    observed_count=len(indices),
                    status=finding.status,
                    unmet_count=len(finding.unmet),
                )
            )
        rows.append(CompletenessRow(item.id, item.title, tuple(cells)))
    return tuple(rows)


def subset_heading(indices: tuple[int, ...], marker_count: int) -> tuple[str, str]:
    """A ``(size line, description line)`` heading for one subset column."""
    size = f"{len(indices)} of {marker_count}"
    if not indices:
        return size, "no marker observed"
    if len(indices) == marker_count:
        return size, "every marker observed"
    positions = ", ".join(str(index + 1) for index in indices)
    return size, f"marker {positions} only"


def completeness_toward_total(rows: tuple[CompletenessRow, ...]) -> int:
    """How many of the executed readings across the whole panel are ``TOWARD``."""
    return sum(
        1 for row in rows for cell in row.cells if cell.status is HorizonStatus.TOWARD
    )


def _svg_marker_completeness() -> str:
    """Exactness replayed: only the complete marker set reaches TOWARD."""
    rows = completeness_rows()
    marker_count = max(cell.observed_count for cell in rows[0].cells)
    subsets = marker_subsets(marker_count)
    toward_total = completeness_toward_total(rows)
    total_calls = len(rows) * len(subsets)

    width, height = 1600, 1310
    parts = _canvas(
        width,
        height,
        title="The Marker-Completeness Panel",
        desc="Every marker subset evaluated showing only the complete set reaches TOWARD.",
    )
    parts.extend(
        [
            _text(70, 84, "THE MARKER-COMPLETENESS PANEL", 24, GOLD_DARK, "700"),
            _text(
                70,
                132,
                f"{toward_total} of {total_calls} readings reach TOWARD",
                40,
                INK,
                "700",
            ),
            _text(
                70,
                172,
                "Every subset of every aspiration's declared markers, filed as an entry and evaluated",
                20,
                MUTED,
            ),
            _text(
                70,
                200,
                f"(review date {RECORD_AS_OF}, stale_after_days = {RECORD_STALE_AFTER_DAYS}, every observation current).",
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

    label_x, grid_x, col_pitch, col_w = 90, 500, 252, 236
    header_y, top, row_pitch, cell_h = 300, 424, 84, 64
    for index, indices in enumerate(subsets):
        x = grid_x + index * col_pitch
        size_line, description = subset_heading(indices, marker_count)
        parts.append(_text(x, header_y, size_line, 22, TEAL, "700"))
        for line_index, line in enumerate(_wrap(description, 18)):
            parts.append(_text(x, header_y + 30 + line_index * 26, line, 20, MUTED))
    parts.append(_text(label_x, top - 22, "ASPIRATION", 20, TEAL, "700"))

    for row_index, row in enumerate(rows):
        y = top + row_index * row_pitch
        parts.append(
            f'<rect x="70" y="{y}" width="1460" height="{cell_h}" rx="10" fill="{CARD}" stroke="{CARD_LINE}" stroke-width="1.5"/>'
        )
        parts.append(_text(label_x, y + 40, row.aspiration_id, 20, INK, "700"))
        for column, cell in enumerate(row.cells):
            x = grid_x + column * col_pitch
            colour = STATUS_COLOURS[cell.status]
            filled = cell.status is HorizonStatus.TOWARD
            parts.append(
                f'<rect x="{x - 16}" y="{y + 10}" width="{col_w}" height="44" rx="8" '
                f'fill="{colour if filled else PAPER}" stroke="{colour}" stroke-width="2.5"/>'
            )
            parts.append(
                _text(
                    x,
                    y + 30,
                    cell.status.value,
                    20,
                    PAPER if filled else colour,
                    "700",
                )
            )
            parts.append(
                _text(
                    x,
                    y + 50,
                    f"{_plural(cell.unmet_count, 'marker')} unmet",
                    20,
                    PAPER if filled else MUTED,
                )
            )

    summary_y = top + len(rows) * row_pitch + 34
    parts.append(
        _text(
            70,
            summary_y,
            f"Only the complete subset reads TOWARD: {toward_total} cells, one per aspiration. "
            f"One missing marker reads exactly as none — there is no partial credit.",
            20,
            GOLD_DARK,
            "700",
        )
    )
    parts.append(
        _text(
            70,
            summary_y + 34,
            "Filled cells are TOWARD and outlined cells are not, and every cell prints its own status and unmet count.",
            20,
            MUTED,
        )
    )
    parts.append(
        _text(
            70,
            height - 34,
            "SOURCE-DRIVEN SCHEMATIC · completeness is a property of the record, never a measure of the work or its author",
            20,
            GOLD_DARK,
            "700",
        )
    )
    parts.append("</svg>")
    return "".join(parts)


# ---------------------------------------------------------------------------
# The shape of a finding
# ---------------------------------------------------------------------------


#: One evidence condition per column of the field matrix, in decision-rule
#: order: ``(heading, observed marker count or None for no entry at all,
#: whether a counter-signal is filed, whether an undeclared token of each kind
#: is filed, observation age in days or None for an absent date)``.
#:
#: The set is chosen so that every field of a finding is carried by at least one
#: column. A field left empty in every column would draw a dead row, which reads
#: as though the evaluator never populates it.
FIELD_MATRIX_CONDITIONS: tuple[tuple[str, int | None, bool, bool, int | None], ...] = (
    ("no admitted entry", None, False, False, 0),
    ("counter-signal, one undeclared", 2, True, True, 0),
    ("markers incomplete, one undeclared", 1, False, True, 0),
    ("complete but stale", 2, False, False, RECORD_STALE_AFTER_DAYS + 1),
    ("complete but undated", 2, False, False, None),
    ("complete and current", 2, False, False, 0),
)

#: Tokens no aspiration declares, filed to exercise the ignored-token fields.
UNDECLARED_MARKER = "a marker the registry never declared"
UNDECLARED_COUNTER_SIGNAL = "a counter-signal the registry never declared"


def _condition_finding(
    marker_count: int | None,
    with_counter: bool,
    with_undeclared: bool,
    age_days: int | None,
) -> HorizonFinding:
    """Run one evidence condition against the first aspiration and return its finding."""
    item = GOLDEN_ASPIRATIONS[0]
    review = date.fromisoformat(RECORD_AS_OF)
    entries: list[HorizonEntry] = []
    if marker_count is not None:
        markers = set(item.markers[:marker_count])
        counters = set(item.counter_signals) if with_counter else set()
        if with_undeclared:
            markers.add(UNDECLARED_MARKER)
            counters.add(UNDECLARED_COUNTER_SIGNAL)
        entries.append(
            HorizonEntry(
                aspiration_id=item.id,
                observed_markers=frozenset(markers),
                counter_signals=frozenset(counters),
                note="filed during a review",
                observed_on="" if age_days is None else _dated(age_days),
            )
        )
    return progress_report(
        entries,
        (item,),
        as_of=review,
        stale_after_days=RECORD_STALE_AFTER_DAYS,
    ).findings[0]


def field_matrix_rows() -> tuple[tuple[str, tuple[bool, ...]], ...]:
    """Return ``(field name, carried-per-condition)`` for every finding field.

    ``carried`` means the returned finding's field holds content: a non-empty
    sequence or string, or a true flag. Nothing here inspects the evaluator's
    internals — each column is one public ``progress_report`` return value.
    """
    findings = field_matrix_findings()
    return tuple(
        (
            field.name,
            tuple(bool(getattr(finding, field.name)) for finding in findings),
        )
        for field in dataclasses.fields(HorizonFinding)
    )


def field_matrix_findings() -> tuple[HorizonFinding, ...]:
    """The finding each evidence condition returned, in column order."""
    return tuple(
        _condition_finding(markers, counter, undeclared, age)
        for _heading, markers, counter, undeclared, age in FIELD_MATRIX_CONDITIONS
    )


def field_matrix_statuses() -> tuple[HorizonStatus, ...]:
    """The status each evidence condition actually returned, in column order."""
    return tuple(finding.status for finding in field_matrix_findings())


def always_carried_fields(
    rows: tuple[tuple[str, tuple[bool, ...]], ...],
) -> tuple[str, ...]:
    """Field names carried under every evidence condition, in declaration order."""
    return tuple(name for name, carried in rows if all(carried))


def flag_fields() -> tuple[str, ...]:
    """The boolean quality flags of a finding, read off the dataclass annotations.

    They are named apart from the rest because a carried flag reports a problem
    with the record rather than a positive result, and the figure must not let
    a filled cell be read as a good outcome.
    """
    return tuple(
        field.name
        for field in dataclasses.fields(HorizonFinding)
        if field.type in {"bool", bool}
    )


def _svg_finding_field_matrix() -> str:
    """Which fields of the returned record carry content, condition by condition."""
    rows = field_matrix_rows()
    statuses = field_matrix_statuses()
    always = always_carried_fields(rows)
    flags = flag_fields()

    width, height = 1600, 1560
    parts = _canvas(
        width,
        height,
        title="The Shape of a Finding",
        desc="Which fields of a finding record carry content under each evidence condition.",
    )
    parts.extend(
        [
            _text(70, 84, "THE SHAPE OF A FINDING", 24, GOLD_DARK, "700"),
            _text(
                70,
                132,
                f"{len(rows)} fields × {len(statuses)} evidence conditions",
                40,
                INK,
                "700",
            ),
            _text(
                70,
                172,
                "Every reading returns the same record; the matching stage decides which fields carry content.",
                20,
                MUTED,
            ),
            _text(
                70,
                200,
                f"One executed progress_report call per column (review date {RECORD_AS_OF}, "
                f"stale_after_days = {RECORD_STALE_AFTER_DAYS}).",
                20,
                MUTED,
            ),
            _text(
                70,
                244,
                "SOURCE-DRIVEN SCHEMATIC · a derivation trail, never a justification of what was recorded",
                20,
                TEAL,
                "700",
            ),
        ]
    )

    label_x, grid_x, col_pitch, col_w = 90, 380, 191, 178
    header_y, top, row_pitch = 300, 448, 74
    for index, (heading, *_rest) in enumerate(FIELD_MATRIX_CONDITIONS):
        x = grid_x + index * col_pitch
        parts.append(_text(x, header_y, statuses[index].value, 20, TEAL, "700"))
        for line_index, line in enumerate(_wrap(heading, 16)[:3]):
            parts.append(_text(x, header_y + 30 + line_index * 26, line, 20, MUTED))
    parts.append(_text(label_x, top - 22, "FINDING FIELD", 20, TEAL, "700"))

    for row_index, (name, carried) in enumerate(rows):
        y = top + row_index * row_pitch
        parts.append(
            f'<rect x="70" y="{y}" width="1460" height="56" rx="10" fill="{CARD}" stroke="{CARD_LINE}" stroke-width="1.5"/>'
        )
        parts.append(_text(label_x, y + 36, name, 20, INK, "700"))
        for column, is_carried in enumerate(carried):
            x = grid_x + column * col_pitch
            colour = TEAL if is_carried else MUTED
            parts.append(
                f'<rect x="{x - 12}" y="{y + 10}" width="{col_w}" height="36" rx="8" '
                f'fill="{colour if is_carried else PAPER}" stroke="{colour}" stroke-width="2.5"/>'
            )
            parts.append(
                _text(
                    x,
                    y + 34,
                    "carried" if is_carried else "empty",
                    20,
                    PAPER if is_carried else colour,
                    "700",
                )
            )

    summary_y = top + len(rows) * row_pitch + 32
    parts.append(
        _text(
            70,
            summary_y,
            f"{_plural(len(always), 'field')} carried under every condition: "
            + ", ".join(always)
            + " — no reading arrives unexplained.",
            20,
            GOLD_DARK,
            "700",
        )
    )
    parts.append(
        _text(
            70,
            summary_y + 34,
            "Filled cells are carried and outlined cells are empty, and every cell prints which it is.",
            20,
            MUTED,
        )
    )
    parts.append(
        _text(
            70,
            summary_y + 74,
            "A carried flag is a recorded condition, not a good result: "
            + " and ".join(flags)
            + " are carried exactly when currentness could not be established.",
            20,
            RED,
        )
    )
    parts.append(
        _text(
            70,
            summary_y + 108,
            "An empty field is an absent observation: the record says what was seen, never what is true.",
            20,
            RED,
        )
    )
    parts.append(
        _text(
            70,
            height - 34,
            "SOURCE-DRIVEN SCHEMATIC · field contents describe one synthetic record, never a person or a project",
            20,
            GOLD_DARK,
            "700",
        )
    )
    parts.append("</svg>")
    return "".join(parts)
