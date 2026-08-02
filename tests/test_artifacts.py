"""Artifact-chain checks cover both success and fail-closed branches."""

from __future__ import annotations

import json
from pathlib import Path

from golden_line.artifacts import check_artifacts
from golden_line.figures import (
    BUILD_PROVENANCE,
    FIGURES,
    GOLDEN_REGISTRY_SCHEMA,
    build_figures,
)


def _artifact_root(tmp_path: Path) -> Path:
    build_figures(tmp_path)
    manuscript_dir = tmp_path / "manuscript"
    manuscript_dir.mkdir()
    (manuscript_dir / "00_test.md").write_text(_stand_in_manuscript(), encoding="utf-8")
    return tmp_path


def _stand_in_manuscript() -> str:
    """A manuscript that satisfies both the embed and the cross-reference rule."""
    return " ".join(
        f"![caption](../output/figures/{name}.png){{#{label} width=95%}} see [@{label}]"
        for name, label, *_ in FIGURES
    )


def _figure_registry_path(root: Path) -> Path:
    return root / "output" / "figures" / "figure_registry.json"


def _golden_registry_path(root: Path) -> Path:
    return root / "output" / "figures" / "golden_registry.json"


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def test_missing_figure_registry_is_reported(tmp_path: Path) -> None:
    root = _artifact_root(tmp_path)
    _figure_registry_path(root).unlink()
    assert check_artifacts(root) == [
        f"missing {root / 'output' / 'figures' / 'figure_registry.json'}"
    ]


def test_missing_golden_registry_is_reported(tmp_path: Path) -> None:
    root = _artifact_root(tmp_path)
    _golden_registry_path(root).unlink()
    assert check_artifacts(root) == [
        f"missing {root / 'output' / 'figures' / 'golden_registry.json'}"
    ]


def test_corrupt_generated_registry_is_reported(tmp_path: Path) -> None:
    root = _artifact_root(tmp_path)
    _figure_registry_path(root).write_bytes(b"{not valid json\n")
    issues = check_artifacts(root)
    assert len(issues) == 1
    assert issues[0].startswith("generated registry is unreadable: ")


def test_golden_registry_mismatches_are_reported(tmp_path: Path) -> None:
    root = _artifact_root(tmp_path)
    payload = _load_json(_golden_registry_path(root))
    payload["registry_version"] = "broken"
    payload["digest"] = "not-the-real-digest"
    payload["aspirations"] = []
    _write_json(_golden_registry_path(root), payload)
    assert check_artifacts(root) == [
        "golden registry version does not match source",
        "golden registry digest does not match source",
        "golden registry payload does not match source",
    ]


def test_figure_registry_header_mismatches_are_reported(tmp_path: Path) -> None:
    root = _artifact_root(tmp_path)
    payload = _load_json(_figure_registry_path(root))
    payload["schema_version"] = "0.0"
    payload["registry_version"] = "broken"
    payload["registry_digest"] = "not-the-real-digest"
    payload["status_values"] = ["BROKEN"]
    _write_json(_figure_registry_path(root), payload)
    assert check_artifacts(root) == [
        "figure registry schema is not 1.2",
        "figure registry version does not match source",
        "figure registry digest does not match source",
        "figure registry status values do not match source",
    ]


def test_figure_registry_figures_field_must_be_a_list(tmp_path: Path) -> None:
    root = _artifact_root(tmp_path)
    payload = _load_json(_figure_registry_path(root))
    payload["figures"] = {"not": "a list"}
    _write_json(_figure_registry_path(root), payload)
    assert check_artifacts(root) == ["figure registry figures field is not a list"]


def test_figure_registry_filename_and_label_sets_must_match_builders(
    tmp_path: Path,
) -> None:
    root = _artifact_root(tmp_path)
    payload = _load_json(_figure_registry_path(root))
    records = payload["figures"]
    assert isinstance(records, list)
    records[0]["filename"] = "wrong.png"
    records[1]["label"] = "fig:not-the-real-label"
    _write_json(_figure_registry_path(root), payload)
    assert check_artifacts(root) == [
        "figure registry filenames do not match the figure builders",
        "figure registry labels do not match the figure builders",
        "missing generated PNG: wrong.png",
        "missing generated SVG: wrong.svg",
        "figure label is not embedded by the manuscript: fig:not-the-real-label",
        "figure label has no prose cross-reference: fig:not-the-real-label",
    ]


def test_missing_png_is_reported(tmp_path: Path) -> None:
    root = _artifact_root(tmp_path)
    (root / "output" / "figures" / "golden_horizon_thread.png").unlink()
    assert check_artifacts(root) == [
        "missing generated PNG: golden_horizon_thread.png",
        "output/figures contains stale or unexpected PNG files",
    ]


def test_missing_svg_is_reported(tmp_path: Path) -> None:
    root = _artifact_root(tmp_path)
    (root / "output" / "figures" / "golden_horizon_thread.svg").unlink()
    assert check_artifacts(root) == ["missing generated SVG: golden_horizon_thread.svg"]


def test_uncited_label_is_reported(tmp_path: Path) -> None:
    root = _artifact_root(tmp_path)
    (root / "manuscript" / "00_test.md").write_text("", encoding="utf-8")
    issues = check_artifacts(root)
    assert len(issues) == 2 * len(FIGURES)
    assert (
        "figure label is not embedded by the manuscript: fig:golden_horizon_thread"
        in issues
    )
    assert (
        "figure label has no prose cross-reference: fig:batch_reading_overview"
        in issues
    )


def test_anchor_without_a_prose_cross_reference_is_reported(tmp_path: Path) -> None:
    """A numbered float the text never points at is a real omission, not a pass.

    The gate used to accept any occurrence of the label, which the figure's own
    ``{#fig:...}`` anchor always satisfies — so an uncited float could never be
    detected. Embedding every figure but dropping one prose reference must now
    be reported, and only for that figure.
    """
    root = _artifact_root(tmp_path)
    dropped = FIGURES[0][1]
    body = " ".join(
        f"![caption](../output/figures/{name}.png){{#{label} width=95%}}"
        + ("" if label == dropped else f" see [@{label}]")
        for name, label, *_ in FIGURES
    )
    (root / "manuscript" / "00_test.md").write_text(body, encoding="utf-8")
    assert check_artifacts(root) == [
        f"figure label has no prose cross-reference: {dropped}"
    ]


def test_golden_registry_schema_mismatch_is_reported(tmp_path: Path) -> None:
    """The source-derived registry snapshot's schema marker is checked too."""
    root = _artifact_root(tmp_path)
    payload = _load_json(_golden_registry_path(root))
    payload["schema_version"] = "0.9"
    _write_json(_golden_registry_path(root), payload)
    assert check_artifacts(root) == [
        f"golden registry schema is not {GOLDEN_REGISTRY_SCHEMA}"
    ]


def test_hand_edited_caption_and_alt_are_reported(tmp_path: Path) -> None:
    """caption/alt are a description surface, so they are compared to source."""
    root = _artifact_root(tmp_path)
    payload = _load_json(_figure_registry_path(root))
    records = payload["figures"]
    assert isinstance(records, list)
    records[0]["caption"] = "a caption nobody generated"
    records[1]["alt"] = "alt text nobody generated"
    _write_json(_figure_registry_path(root), payload)
    assert check_artifacts(root) == [
        f"figure record caption does not match source: {FIGURES[0][1]}",
        f"figure record alt text does not match source: {FIGURES[1][1]}",
    ]


def test_unexpected_generated_by_is_reported(tmp_path: Path) -> None:
    root = _artifact_root(tmp_path)
    payload = _load_json(_figure_registry_path(root))
    records = payload["figures"]
    assert isinstance(records, list)
    records[0]["generated_by"] = "not-" + BUILD_PROVENANCE
    _write_json(_figure_registry_path(root), payload)
    assert check_artifacts(root) == [
        "figure record has unexpected generator: fig:golden_horizon_thread"
    ]


def test_stale_extra_png_is_reported(tmp_path: Path) -> None:
    root = _artifact_root(tmp_path)
    (root / "output" / "figures" / "stale.png").write_bytes(b"\x89PNG\r\n\x1a\nstale")
    assert check_artifacts(root) == [
        "output/figures contains stale or unexpected PNG files"
    ]
