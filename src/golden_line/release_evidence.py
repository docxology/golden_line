import argparse
import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from .paths import PROJECT_ROOT
from .raster import renderer_provenance
from .registry import GOLDEN_ASPIRATIONS
from .serialization import registry_digest

LOCAL_GATES = (
    (
        "uv",
        "run",
        "pytest",
        "tests/",
        "--cov=src",
        "--cov-branch",
        "--cov-report=term-missing",
        "--cov-report=json:output/evidence/coverage.json",
    ),
    ("uv", "run", "ruff", "check", "src", "tests", "scripts"),
    ("uv", "run", "ruff", "format", "--check", "src", "tests", "scripts"),
    ("uv", "run", "mypy", "src/golden_line"),
    ("uv", "run", "python", "scripts/check_registry.py"),
    ("uv", "run", "python", "scripts/build_figures.py"),
    ("uv", "run", "python", "scripts/check_artifacts.py"),
    ("uv", "run", "python", "scripts/gen_formalism_ledger.py", "--check"),
)


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args], check=True, capture_output=True, text=True
    ).stdout.strip()


def _untracked(root: Path) -> list[str]:
    return [
        name
        for name in _git(
            root, "ls-files", "--others", "--exclude-standard"
        ).splitlines()
        if not name.startswith("graft/")
    ]


def collect_evidence(
    root: Path,
    destination: Path,
    *,
    commands: tuple[tuple[str, ...], ...] = LOCAL_GATES,
) -> dict:
    """Run real commands and record exact-revision evidence, even on failure.

    Success requires clean tracked source and zero exit status for every gate.
    External manuscript rendering is a separate receipt, never inferred here.
    """
    destination.mkdir(parents=True, exist_ok=True)
    commit = _git(root, "rev-parse", "HEAD")
    untracked = _untracked(root)
    dirty = bool(_git(root, "status", "--porcelain", "--untracked-files=no")) or bool(
        untracked
    )
    outputs = []
    for index, command in enumerate(commands, start=1):
        try:
            result = subprocess.run(
                command, cwd=root, capture_output=True, text=True, check=False
            )
            status, output = result.returncode, result.stdout + result.stderr
        except OSError as exc:
            status, output = 127, str(exc)
        filename = f"gate-{index:02d}.log"
        (destination / filename).write_text(output, encoding="utf-8")
        outputs.append(
            {
                "argv": list(command),
                "exit_status": status,
                "output_file": filename,
                "output_sha256": hashlib.sha256(output.encode("utf-8")).hexdigest(),
            }
        )
    renderer_issue = None
    try:
        _, renderer = renderer_provenance()
    except (OSError, RuntimeError, subprocess.SubprocessError) as exc:
        renderer = {}
        renderer_issue = str(exc)
    unchanged = (
        _git(root, "rev-parse", "HEAD") == commit
        and not _untracked(root)
        and not _git(root, "status", "--porcelain", "--untracked-files=no")
    )
    artifacts = {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for folder in ("figures", "pdf", "web", "html", "epub")
        for path in sorted((root / "output" / folder).rglob("*"))
        if path.is_file()
    }
    manifest = {
        "schema_version": "golden-line.release-evidence/1.0",
        "source_commit": commit,
        "tracked_source_dirty": dirty,
        "untracked_source_paths": untracked,
        "complete_gate_surface": commands == LOCAL_GATES,
        "source_unchanged": unchanged,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(),
        "python_prefix": str(Path(sys.prefix).resolve()),
        "python_base_prefix": str(Path(sys.base_prefix).resolve()),
        "lock_sha256": hashlib.sha256((root / "uv.lock").read_bytes()).hexdigest(),
        "renderer": renderer,
        "renderer_issue": renderer_issue,
        "registry_digest": registry_digest(GOLDEN_ASPIRATIONS),
        "commands": outputs,
        "artifact_sha256": artifacts,
        "external_render": {
            "status": "not_run",
            "reason": "separate external toolchain receipt required",
        },
        "passed": commands == LOCAL_GATES
        and not dirty
        and unchanged
        and renderer_issue is None
        and all(record["exit_status"] == 0 for record in outputs),
    }
    (destination / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output", type=Path, default=PROJECT_ROOT / "output" / "evidence"
    )
    args = parser.parse_args()
    manifest = collect_evidence(PROJECT_ROOT, args.output)
    print(json.dumps(manifest, indent=2))
    return 0 if manifest["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
