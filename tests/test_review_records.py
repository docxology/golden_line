import json
from dataclasses import replace

import pytest

import golden_line as gl


def test_self_report_and_contestation_remain_explicit_after_export():
    records = gl.worked_evidence_records()
    payload = json.loads(gl.canonical_evidence_records(*records))
    assert payload["observations"][0]["authorship"] == "self_report"
    assert payload["observations"][1]["contests"] == [
        payload["observations"][0]["observation_ref"]
    ]
    assert payload["source_content_verified"] is False
    assert payload["grants_permission"] is False
    assert len(payload["conflicts"]) == 3
    assert all(
        record["unresolved_alternatives"] and record["decision_owner"]
        for record in payload["conflicts"]
    )
    assert "score" not in payload


@pytest.mark.parametrize(
    "change",
    [
        {"source_refs": "snapshot"},
        {"authorship": "verified"},
        {"observer_role": ""},
        {"token_sources": (("undeclared", ("source",)),)},
    ],
)
def test_provenance_rejects_malformed_records(change):
    observations, conflicts = gl.worked_evidence_records()
    with pytest.raises(ValueError):
        gl.canonical_evidence_records((replace(observations[0], **change),), conflicts)


def test_conflict_requires_human_owner_and_retains_affected_perspectives():
    observations, conflicts = gl.worked_evidence_records()
    assert all(conflict.affected_perspectives for conflict in conflicts)
    with pytest.raises(ValueError, match="decision_owner"):
        gl.canonical_evidence_records(
            observations, (replace(conflicts[0], decision_owner=""),)
        )


@pytest.mark.parametrize(
    "case",
    [
        "outer-list",
        "nonrecord",
        "duplicate-observation",
        "unknown-id",
        "token-container",
        "token-shape",
        "token-ref",
        "conflict-type",
        "duplicate-conflict",
        "unknown-conflict-id",
    ],
)
def test_evidence_record_validation_rejects_structural_errors(case):
    observations, conflicts = gl.worked_evidence_records()
    if case == "outer-list":
        observations = list(observations)
    elif case == "nonrecord":
        observations = (None,)
    elif case == "duplicate-observation":
        observations = observations + (observations[0],)
    elif case == "unknown-id":
        observations = (replace(observations[0], aspiration_id="unknown"),)
    elif case == "token-container":
        observations = (replace(observations[0], token_sources="token"),)
    elif case == "token-shape":
        observations = (replace(observations[0], token_sources=(None,)),)
    elif case == "token-ref":
        observations = (
            replace(
                observations[0],
                token_sources=(("handoff used", ("undeclared-source",)),),
            ),
        )
    elif case == "conflict-type":
        conflicts = (None,)
    elif case == "duplicate-conflict":
        conflicts = conflicts + (conflicts[0],)
    else:
        conflicts = (replace(conflicts[0], aspiration_ids=("unknown",)),)
    with pytest.raises(ValueError):
        gl.canonical_evidence_records(observations, conflicts)


def test_documentation_uses_current_family_and_founding_history():
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    for name in (
        "README.md",
        "docs/architecture.md",
        "docs/manuscript/01b_line_set_relationship.md",
        ".agents/skills/golden-line/SKILL.md",
    ):
        text = (root / name).read_text()
        assert "founding four" in text, name
        assert "eight instruments" in text, name
    assert (
        "developed capacity"
        in (root / "docs/manuscript/01b_line_set_relationship.md").read_text()
    )
