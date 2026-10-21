import json
import sys
from pathlib import Path

import golden_line.release_evidence as evidence


def test_failed_command_is_recorded_and_blocks_success(tmp_path):
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


def test_successful_command_does_not_override_dirty_source(tmp_path):
    root = Path(__file__).resolve().parents[1]
    manifest = evidence.collect_evidence(
        root, tmp_path, commands=((sys.executable, "-c", "print('real subprocess')"),)
    )
    assert manifest["commands"][0]["exit_status"] == 0
    assert manifest["passed"] is False
    assert manifest["complete_gate_surface"] is False
    assert manifest["lock_sha256"]
    assert manifest["renderer"]["version"]
