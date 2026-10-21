import json
import subprocess
import sys
from pathlib import Path

import golden_line.release_evidence as evidence


def test_failed_custom_command_is_recorded(tmp_path):
    root = Path(__file__).resolve().parents[1]
    manifest = evidence.collect_evidence(
        root,
        tmp_path,
        commands=(
            (sys.executable, "-c", "print('intentional failure'); raise SystemExit(7)"),
        ),
    )
    assert manifest["passed"] is False
    assert manifest["commands"][0]["exit_status"] == 7
    assert (
        "intentional failure"
        in (tmp_path / manifest["commands"][0]["output_file"]).read_text()
    )
    assert manifest["external_render"]["status"] == "not_run"
    assert (
        json.loads((tmp_path / "manifest.json").read_text())["source_commit"]
        == manifest["source_commit"]
    )


def test_incomplete_gate_surface_cannot_pass(tmp_path):
    root = Path(__file__).resolve().parents[1]
    manifest = evidence.collect_evidence(
        root, tmp_path, commands=((sys.executable, "-c", "print('real subprocess')"),)
    )
    assert manifest["commands"][0]["exit_status"] == 0
    assert manifest["passed"] is False
    assert manifest["complete_gate_surface"] is False
    assert manifest["lock_sha256"]
    assert manifest["renderer"]["version"]


def test_failed_canonical_gate_alone_blocks_success(tmp_path, monkeypatch):
    root = Path(__file__).resolve().parents[1]
    clone = tmp_path / "golden_line"
    subprocess.run(["git", "clone", "--quiet", str(root), str(clone)], check=True)
    monkeypatch.setenv("UV_PROJECT_ENVIRONMENT", str(tmp_path / "environment"))
    monkeypatch.setenv("PYTEST_ADDOPTS", "--golden-line-intentional-unknown-option")
    manifest = evidence.collect_evidence(clone, tmp_path / "receipt")
    assert manifest["complete_gate_surface"] is True
    assert manifest["tracked_source_dirty"] is False
    assert manifest["source_unchanged"] is True
    assert manifest["renderer_issue"] is None
    assert manifest["commands"][0]["exit_status"] == 4
    assert all(record["exit_status"] == 0 for record in manifest["commands"][1:])
    assert manifest["passed"] is False
