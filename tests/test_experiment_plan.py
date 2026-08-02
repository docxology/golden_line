"""Bind the shipped plan and domain profile to the code the manuscript cites.

``manuscript/02_method.md`` tells the reader that ``experiment_plan.yaml``'s
expected figures are the ones the deterministic builder produces, and that
``domain_profile.yaml`` names the validation gates. Both were previously
hand-kept: the plan listed nine of the eleven shipped figures for as long as
the lattice and the precedence panel existed, and no test looked. A claim about
a file's contents is only as good as the check that re-derives it, so these
tests derive each list from the source it describes and assert the file agrees.
"""

from __future__ import annotations

import re
from pathlib import Path

from golden_line.figures import FIGURES

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PLAN = PROJECT_ROOT / "experiment_plan.yaml"
PROFILE = PROJECT_ROOT / "domain_profile.yaml"
METHOD = PROJECT_ROOT / "manuscript" / "02_method.md"


def _yaml_list(path: Path, key: str) -> list[str]:
    """Read one flat ``key:`` list without adding a YAML runtime dependency."""
    lines = path.read_text(encoding="utf-8").splitlines()
    values: list[str] = []
    collecting = False
    for line in lines:
        if line.startswith(f"{key}:"):
            collecting = True
            continue
        if collecting:
            match = re.match(r"^\s+- (\S.*)$", line)
            if match is None:
                break
            values.append(match.group(1).strip())
    return values


def test_plan_expected_figures_are_the_built_figures() -> None:
    """The plan's figure list is the builder's, in the builder's order."""
    expected = [label for _name, label, *_ in FIGURES]
    assert expected, "FIGURES is empty, so this gate would be vacuous"
    assert _yaml_list(PLAN, "expected_figures") == expected


def test_plan_figure_guard_rejects_a_dropped_figure() -> None:
    """Proof of detection: the nine-figure list this test was written for fails."""
    expected = [label for _name, label, *_ in FIGURES]
    stale = [label for label in expected if label != "fig:currentness_lattice"]
    assert stale != expected
    assert len(stale) == len(expected) - 1


def test_method_section_figure_split_matches_the_modules() -> None:
    """02_method's analysis-drawn / schematic split is counted, not asserted.

    The split is which module draws each plate, so it is re-derived from the
    builders' own modules rather than from a remembered number.
    """
    from golden_line.figures import analysis_figures

    analysis_backed = [
        label
        for _name, label, builder, *_ in FIGURES
        if builder.__module__ == analysis_figures.__name__
    ]
    schematics = [
        label
        for _name, label, builder, *_ in FIGURES
        if builder.__module__ != analysis_figures.__name__
    ]
    assert len(analysis_backed) + len(schematics) == len(FIGURES)
    assert analysis_backed and schematics, "an empty side would make this vacuous"

    words = {5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine"}
    text = " ".join(METHOD.read_text(encoding="utf-8").split())
    assert (
        f"{words[len(analysis_backed)]} through this analysis layer's helpers" in text
    )
    assert f"and {words[len(schematics)]} straight from the registry" in text


def test_domain_profile_review_gates_are_a_subset_of_its_validation_gates() -> None:
    """A review gate the profile never declared as a validation gate is a typo."""
    validation = _yaml_list(PROFILE, "validation_gates")
    review = _yaml_list(PROFILE, "review_gates")
    assert validation, "no validation gates declared; the check would be vacuous"
    assert review, "no review gates declared; the check would be vacuous"
    assert set(review) <= set(validation)


def test_domain_profile_gates_are_the_ones_the_method_section_names() -> None:
    """02_method quotes the gate names; they must still be the declared ones."""
    validation = _yaml_list(PROFILE, "validation_gates")
    text = " ".join(METHOD.read_text(encoding="utf-8").split())
    for gate in validation:
        assert gate.replace("_", " ") in text, gate


def test_plan_artifact_expectations_name_the_generated_registries() -> None:
    """The profile's artifact expectations must include what the builder writes."""
    expectations = set(_yaml_list(PROFILE, "artifact_expectations"))
    assert "output/figures/figure_registry.json" in expectations
    assert "output/figures/golden_registry.json" in expectations
