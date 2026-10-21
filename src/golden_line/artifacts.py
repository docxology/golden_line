"""Fail-closed validation for the generated Golden Line artifact chain."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

from golden_line.figures import (
    BUILD_PROVENANCE,
    FIGURE_REGISTRY_SCHEMA,
    FIGURES,
    GOLDEN_REGISTRY_SCHEMA,
)
from golden_line.models import HorizonStatus
from golden_line.paths import PROJECT_ROOT
from golden_line.raster import raster_bytes, renderer_provenance
from golden_line.registry import GOLDEN_ASPIRATIONS
from golden_line.serialization import canonical_registry, registry_digest
from golden_line.version import REGISTRY_VERSION

ROOT = PROJECT_ROOT


def check_artifacts(project_root: Path | None = None) -> list[str]:
    """Return every artifact-chain issue; an empty list means the chain is sound."""
    root = project_root or ROOT
    figure_dir = root / "output" / "figures"
    issues: list[str] = []
    expected_names = {name for name, *_ in FIGURES}
    expected_labels = {label for _, label, *_ in FIGURES}

    figure_registry_path = figure_dir / "figure_registry.json"
    golden_registry_path = figure_dir / "golden_registry.json"
    if not figure_registry_path.is_file():
        issues.append(f"missing {figure_registry_path}")
        return issues
    if not golden_registry_path.is_file():
        issues.append(f"missing {golden_registry_path}")
        return issues

    try:
        figure_payload = json.loads(figure_registry_path.read_text(encoding="utf-8"))
        golden_payload = json.loads(golden_registry_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return [f"generated registry is unreadable: {exc}"]

    if type(figure_payload) is not dict or type(golden_payload) is not dict:
        return ["generated registries must be JSON objects"]

    expected_digest = registry_digest(GOLDEN_ASPIRATIONS)
    expected_registry = json.loads(canonical_registry(GOLDEN_ASPIRATIONS))
    if golden_payload.get("schema_version") != GOLDEN_REGISTRY_SCHEMA:
        issues.append(f"golden registry schema is not {GOLDEN_REGISTRY_SCHEMA}")
    if golden_payload.get("registry_version") != REGISTRY_VERSION:
        issues.append("golden registry version does not match source")
    if golden_payload.get("digest") != expected_digest:
        issues.append("golden registry digest does not match source")
    if golden_payload.get("aspirations") != expected_registry:
        issues.append("golden registry payload does not match source")

    if figure_payload.get("schema_version") != FIGURE_REGISTRY_SCHEMA:
        issues.append(f"figure registry schema is not {FIGURE_REGISTRY_SCHEMA}")
    if figure_payload.get("registry_version") != REGISTRY_VERSION:
        issues.append("figure registry version does not match source")
    if figure_payload.get("registry_digest") != expected_digest:
        issues.append("figure registry digest does not match source")
    if figure_payload.get("status_values") != [
        status.value for status in HorizonStatus
    ]:
        issues.append("figure registry status values do not match source")

    records = figure_payload.get("figures")
    if not isinstance(records, list):
        return issues + ["figure registry figures field is not a list"]
    if any(
        type(record) is not dict
        or type(record.get("filename")) is not str
        or type(record.get("label")) is not str
        for record in records
    ):
        return issues + ["figure records must be objects with text filename and label"]
    record_names = {Path(record["filename"]).stem for record in records}
    record_labels = {record.get("label") for record in records}
    if record_names != expected_names:
        issues.append("figure registry filenames do not match the figure builders")
    if record_labels != expected_labels:
        issues.append("figure registry labels do not match the figure builders")
    if len(records) != len(FIGURES) or len(
        {record["filename"] for record in records}
    ) != len(records):
        issues.append("figure registry requires exactly one record per builder")

    try:
        converter, renderer = renderer_provenance()
    except (RuntimeError, OSError, subprocess.SubprocessError) as exc:
        return issues + [f"toolchain prerequisite failed: {exc}"]
    if figure_payload.get("renderer") != renderer:
        issues.append(
            "renderer provenance differs from the current toolchain; rebuild required"
        )

    try:
        manuscript_text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted(
                (
                    root / "docs" / "manuscript"
                    if (root / "docs" / "manuscript").is_dir()
                    else root / "manuscript"
                ).glob("*.md")
            )
        )
    except (OSError, UnicodeError) as exc:
        return issues + [f"manuscript is unreadable: {exc}"]
    described = {label: (caption, alt) for _, label, _, caption, alt in FIGURES}
    builders = {f"{name}.png": (label, builder) for name, label, builder, *_ in FIGURES}
    for record in records:
        filename = record.get("filename", "")
        label = record.get("label", "")
        if filename not in builders or builders[filename][0] != label:
            issues.append(
                f"figure filename/label pair does not match source: {filename!r}, {label!r}"
            )
            continue
        if any(
            (figure_dir / f"{Path(filename).stem}.{suffix}").resolve().parent
            != figure_dir.resolve()
            for suffix in ("png", "svg")
        ):
            issues.append(f"figure path escapes output directory: {filename}")
            continue
        if not (figure_dir / filename).is_file():
            issues.append(f"missing generated PNG: {filename}")
        if (
            filename.endswith(".png")
            and not (figure_dir / f"{filename[:-4]}.svg").is_file()
        ):
            issues.append(f"missing generated SVG: {filename[:-4]}.svg")
        # An anchor and a prose cross-reference are separate obligations. The
        # anchor alone satisfies a bare substring test, so a numbered float the
        # text never points at would otherwise pass unnoticed.
        if f"{{#{label}" not in manuscript_text:
            issues.append(f"figure label is not embedded by the manuscript: {label}")
        if f"@{label}" not in manuscript_text:
            issues.append(f"figure label has no prose cross-reference: {label}")
        if record.get("generated_by") != BUILD_PROVENANCE:
            issues.append(f"figure record has unexpected generator: {label}")
        if label in described:
            caption, alt = described[label]
            if record.get("caption") != caption:
                issues.append(f"figure record caption does not match source: {label}")
            if record.get("alt") != alt:
                issues.append(f"figure record alt text does not match source: {label}")
        svg = builders[filename][1]().encode("utf-8")
        try:
            png = raster_bytes(svg, converter, renderer)
        except (OSError, subprocess.SubprocessError) as exc:
            issues.append(f"toolchain source replay failed for {filename}: {exc}")
            continue
        for suffix, expected in (("svg", svg), ("png", png)):
            path = figure_dir / f"{Path(filename).stem}.{suffix}"
            if not path.is_file():
                continue
            try:
                actual = path.read_bytes()
            except OSError as exc:
                issues.append(f"unreadable {suffix.upper()}: {path.name}: {exc}")
                continue
            if actual != expected:
                issues.append(
                    f"{suffix.upper()} bytes do not match source replay: {path.name}"
                )
            if record.get(f"{suffix}_sha256") != hashlib.sha256(actual).hexdigest():
                issues.append(
                    f"{suffix.upper()} checksum differs from manifest: {path.name}"
                )

    actual_pngs = {path.stem for path in figure_dir.glob("*.png")}
    if actual_pngs != expected_names:
        issues.append("output/figures contains stale or unexpected PNG files")
    if {path.stem for path in figure_dir.glob("*.svg")} != expected_names:
        issues.append("output/figures contains stale or unexpected SVG files")
    return issues
