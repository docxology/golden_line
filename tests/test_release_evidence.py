import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

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


def _working_copy(tmp_path):
    root = Path(__file__).resolve().parents[1]
    clone = tmp_path / "golden_line"
    clone.mkdir()
    paths = subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "ls-files",
            "--cached",
            "--others",
            "--exclude-standard",
            "-z",
        ],
        check=True,
        capture_output=True,
    ).stdout.split(b"\0")
    for name in paths:
        if not name:
            continue
        relative = Path(os.fsdecode(name))
        source = root / relative
        if source.is_file():
            destination = clone / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
    subprocess.run(["git", "init", "--quiet", "--template=", str(clone)], check=True)
    subprocess.run(["git", "-C", str(clone), "add", "--all"], check=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(clone),
            "-c",
            "user.name=Golden Line test",
            "-c",
            "user.email=golden-line-test@example.invalid",
            "-c",
            "commit.gpgsign=false",
            "-c",
            "core.hooksPath=" + str(tmp_path / "no-hooks"),
            "commit",
            "--quiet",
            "-m",
            "Snapshot current source for release-evidence control",
        ],
        check=True,
    )
    return clone


def test_source_observation_preserves_git_index(tmp_path):
    clone = _working_copy(tmp_path)
    source = clone / "src" / "golden_line" / "version.py"
    stat = source.stat()
    os.utime(source, ns=(stat.st_atime_ns, stat.st_mtime_ns + 2_000_000_000))
    index = clone / ".git" / "index"
    index_before = index.read_bytes()
    manifest = evidence.collect_evidence(clone, tmp_path / "receipt", commands=())
    assert manifest["tracked_source_dirty"] is False
    assert manifest["source_unchanged"] is True
    assert manifest["passed"] is False
    assert index.read_bytes() == index_before


def test_failed_canonical_gate_alone_blocks_success(tmp_path, monkeypatch):
    clone = _working_copy(tmp_path)
    monkeypatch.setenv("VIRTUAL_ENV", str(clone / ".venv"))
    monkeypatch.setenv("UV_PYTHON", sys.executable)
    monkeypatch.setenv("PYTHONPATH", os.pathsep.join((str(clone / "src"), str(clone))))
    monkeypatch.setenv("PYTEST_ADDOPTS", "--golden-line-intentional-unknown-option")
    manifest = evidence.collect_evidence(clone, tmp_path / "receipt")
    assert manifest["complete_gate_surface"] is True
    assert manifest["tracked_source_dirty"] is False
    assert manifest["source_unchanged"] is True
    assert manifest["renderer_issue"] is None
    assert manifest["commands"][0]["exit_status"] == 4
    assert all(record["exit_status"] == 0 for record in manifest["commands"][1:])
    assert manifest["passed"] is False


def test_dirty_working_source_is_bound_but_cannot_pass(tmp_path):
    clone = _working_copy(tmp_path)
    source = clone / "src" / "golden_line" / "version.py"
    source.write_text(source.read_text() + "\n# Uncommitted working-source change\n")
    manifest = evidence.collect_evidence(
        clone,
        tmp_path / "receipt",
        commands=((sys.executable, "-c", "print('working-source gate')"),),
    )
    assert manifest["tracked_source_dirty"] is True
    assert manifest["source_unchanged"] is True
    assert manifest["passed"] is False
    assert manifest["working_source_files"]["src/golden_line/version.py"] == (
        evidence.hashlib.sha256(source.read_bytes()).hexdigest()
    )
    assert manifest["working_source_sha256"] == evidence._snapshot_digest(
        manifest["working_source_files"]
    )


@pytest.mark.parametrize("mutation", ["content", "mode"])
def test_gate_source_mutation_cannot_reuse_starting_source_binding(tmp_path, mutation):
    clone = _working_copy(tmp_path)
    manifest = evidence.collect_evidence(
        clone,
        tmp_path / "receipt",
        commands=(
            (
                sys.executable,
                "-c",
                (
                    "from pathlib import Path; "
                    "p=Path('src/golden_line/version.py'); "
                    + (
                        "p.write_text(p.read_text() + '\\n# Changed during gate\\n')"
                        if mutation == "content"
                        else "p.chmod(p.stat().st_mode ^ 0o111)"
                    )
                ),
            ),
        ),
    )
    assert manifest["tracked_source_dirty"] is False
    assert manifest["source_unchanged"] is False
    assert manifest["passed"] is False
    assert (
        manifest["working_source_sha256"]
        != evidence._snapshot_digest(evidence._source_snapshot(clone))
    ) is (mutation == "content")
