"""Every fail-closed guard in the figure layer must be shown to fire.

A guard that has never rejected anything is a comment with a raise attached.
Each test here calls the guard directly with the exact bad state it exists for
and asserts that it reports the problem, in the same proof-of-detection style
the invariant battery uses on the registry. Every input is a real object built
from the public API — no patching tooling anywhere.
"""

from __future__ import annotations

import dataclasses

import pytest

from golden_line import Aspiration, HorizonEntry, horizon_distribution
from golden_line.figures import analysis_figures, core_schematics, svg
from golden_line.progress import EVALUATOR_STAGES
from golden_line.registry import GOLDEN_ASPIRATIONS, founding_aspirations


def test_canvas_rejects_a_non_standard_width() -> None:
    """One shared design width is what makes the point-size contract computable."""
    assert svg._canvas(svg.CANVAS_WIDTH, 800)
    with pytest.raises(ValueError, match="is not the shared"):
        svg._canvas(svg.CANVAS_WIDTH + 100, 800)


def test_canvas_rejects_a_plate_taller_than_the_height_budget() -> None:
    """Past MAX_CANVAS_HEIGHT the height cap binds and every label shrinks."""
    assert svg._canvas(svg.CANVAS_WIDTH, svg.MAX_CANVAS_HEIGHT)
    with pytest.raises(ValueError, match="exceeds MAX_CANVAS_HEIGHT"):
        svg._canvas(svg.CANVAS_WIDTH, svg.MAX_CANVAS_HEIGHT + 1)


def test_thread_nodes_accept_the_shipped_founding_set() -> None:
    """The positive control: the real registry maps cleanly onto the layout."""
    nodes = core_schematics.thread_nodes(founding_aspirations())
    assert len(nodes) == len(core_schematics._THREAD_SLOTS)
    assert [item.id for item, *_ in nodes] == [
        item.id for item in founding_aspirations()
    ]


def test_thread_nodes_reject_a_founding_entry_with_no_symbol() -> None:
    """Icons are keyed by id; an unmapped founding entry must not draw silently."""
    reduced = {
        key: value
        for key, value in core_schematics.FOUNDING_SYMBOLS.items()
        if key != "repairable-systems"
    }
    assert len(reduced) == len(core_schematics.FOUNDING_SYMBOLS) - 1
    with pytest.raises(ValueError, match="without a declared symbol"):
        core_schematics.thread_nodes(founding_aspirations(), reduced)


def test_thread_nodes_reject_a_founding_set_the_layout_cannot_hold() -> None:
    """A fifth founding aspiration must fail loudly, not overwrite a card."""
    with pytest.raises(ValueError, match="founding cards"):
        core_schematics.thread_nodes(
            founding_aspirations(),
            core_schematics.FOUNDING_SYMBOLS,
            core_schematics._THREAD_SLOTS[:3],
        )


def test_pipeline_stages_bind_to_the_evaluator_stage_names() -> None:
    """The positive control, and then a figure that describes one stage fewer."""
    bodies = tuple("body" for _ in EVALUATOR_STAGES)
    colours = tuple("#000000" for _ in EVALUATOR_STAGES)
    stages = core_schematics.pipeline_stages(EVALUATOR_STAGES, bodies, colours)
    assert [title for title, *_ in stages] == [
        f"{index + 1} · {name.upper()}" for index, name in enumerate(EVALUATOR_STAGES)
    ]
    with pytest.raises(ValueError, match="different number of stages"):
        core_schematics.pipeline_stages(EVALUATOR_STAGES, bodies[:-1], colours[:-1])


def test_precedence_heading_lines_reject_a_heading_that_would_be_truncated() -> None:
    """A heading longer than its column is reported rather than silently clipped."""
    for heading, _markers, _counter, age in core_schematics._PRECEDENCE_COLUMNS:
        assert core_schematics.precedence_heading_lines(heading, age)
    overlong = (
        "a column heading far too long to fit inside the space this panel "
        "reserves for headings above the grid at {age} days"
    )
    with pytest.raises(ValueError, match="heading does not fit"):
        core_schematics.precedence_heading_lines(overlong, 400)


def test_precedence_heading_fills_in_the_age_the_column_uses() -> None:
    """The heading's age is the column's own age, not a second hand-kept copy."""
    heading, _markers, _counter, age = core_schematics._PRECEDENCE_COLUMNS[3]
    lines = core_schematics.precedence_heading_lines(heading, age)
    assert str(age) in " ".join(lines)
    assert "{age}" not in " ".join(lines)


def test_lattice_label_lines_reject_a_title_that_would_be_truncated() -> None:
    """A long aspiration title must fail rather than lose its last words.

    Slicing the wrapped title to two lines instead would drop its tail, which
    is how a figure comes to disagree with the registry it claims to draw.
    """
    for item in GOLDEN_ASPIRATIONS:
        assert 1 <= len(analysis_figures.lattice_label_lines(item.title)) <= 2
    long_title = " ".join(["extremely"] * 12) + " long aspiration title"
    stretched = dataclasses.replace(GOLDEN_ASPIRATIONS[0], title=long_title)
    with pytest.raises(ValueError, match="does not fit in two lines"):
        analysis_figures.lattice_label_lines(stretched.title)


def test_lattice_deviations_of_an_empty_replay_is_empty() -> None:
    """The deviation count is defined for an empty registry, not undefined."""
    assert analysis_figures.lattice_deviations(()) == ()


def test_worked_batch_fates_reject_an_unmappable_set_aside() -> None:
    """A malformed record has no display string in this figure; say so."""
    assert len(analysis_figures.worked_batch_fates()) == len(
        analysis_figures.WORKED_BATCH_ENTRIES
    )
    with pytest.raises(ValueError, match="non-displayable set-aside"):
        analysis_figures.worked_batch_fates(
            analysis_figures.WORKED_BATCH_ENTRIES + ("not a HorizonEntry record",)
        )


def test_set_aside_accounting_rejects_a_count_mismatch() -> None:
    """The figure's own set-aside tally must equal the report's intake notes."""
    fates = analysis_figures.worked_batch_fates()
    set_aside = sum(fate != "admitted" for fate in fates)
    analysis_figures.check_set_aside_accounting(fates, set_aside)
    with pytest.raises(ValueError, match="intake classification count mismatch"):
        analysis_figures.check_set_aside_accounting(fates, set_aside + 1)


def test_horizon_distribution_still_refuses_an_unclassified_horizon() -> None:
    """The band map's brittleness is deliberate; confirm it is still brittle."""
    stranger = Aspiration("odd", "Odd", "t", "no such horizon", ("m",), ("c",))
    with pytest.raises(ValueError, match="no such horizon"):
        horizon_distribution((stranger,))


def test_precedence_cells_are_built_from_ordinary_horizon_entries() -> None:
    """The panel's inputs go through the public API, not a private shortcut."""
    rows = core_schematics.precedence_cells()
    assert len(rows) == len(GOLDEN_ASPIRATIONS)
    first = GOLDEN_ASPIRATIONS[0]
    sample = HorizonEntry(
        first.id,
        observed_markers=frozenset(first.markers),
        counter_signals=frozenset(first.counter_signals),
        observed_on=core_schematics.PRECEDENCE_AS_OF,
    )
    assert isinstance(sample, HorizonEntry)
    assert sample.aspiration_id == rows[0][0]
