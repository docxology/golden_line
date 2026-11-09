"""Check declared figure artifacts and profile validation consistency."""

from __future__ import annotations

import re
from pathlib import Path

from golden_line.figures import FIGURES

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PLAN = PROJECT_ROOT / "experiment_plan.yaml"
PROFILE = PROJECT_ROOT / "domain_profile.yaml"


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


def test_domain_profile_review_gates_are_a_subset_of_its_validation_gates() -> None:
    """A review gate the profile never declared as a validation gate is a typo."""
    validation = _yaml_list(PROFILE, "validation_gates")
    review = _yaml_list(PROFILE, "review_gates")
    assert validation, "no validation gates declared; the check would be vacuous"
    assert review, "no review gates declared; the check would be vacuous"
    assert set(review) <= set(validation)


def test_plan_artifact_expectations_name_the_generated_registries() -> None:
    """The profile's artifact expectations must include what the builder writes."""
    expectations = set(_yaml_list(PROFILE, "artifact_expectations"))
    assert "output/figures/figure_registry.json" in expectations
    assert "output/figures/golden_registry.json" in expectations
