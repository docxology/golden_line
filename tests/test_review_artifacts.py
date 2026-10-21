import hashlib
import json
import shutil

import pytest

from golden_line.artifacts import check_artifacts
from golden_line.figures import FIGURES, build_figures


@pytest.fixture(scope="module")
def built_artifacts(tmp_path_factory):
    root = tmp_path_factory.mktemp("artifact-source")
    build_figures(root)
    (root / "manuscript").mkdir()
    (root / "manuscript" / "figures.md").write_text(
        " ".join(
            f"![figure]({name}.png){{#{label}}} [@{label}]"
            for name, label, *_ in FIGURES
        )
    )
    return root


@pytest.mark.parametrize(
    "mutation",
    [
        "list",
        "null",
        "record-null",
        "integer-filename",
        "duplicate",
        "swapped-labels",
        "suffix",
        "escape",
        "utf8",
        "svg-bytes",
        "png-bytes",
        "rehash-png",
        "renderer",
        "golden-list",
        "golden-null",
    ],
)
def test_artifact_gate_rejects_mutated_data_without_crashing(
    tmp_path, built_artifacts, mutation
):
    root = tmp_path / "edition"
    shutil.copytree(built_artifacts, root)
    directory = root / "output" / "figures"
    path = directory / "figure_registry.json"
    payload = json.loads(path.read_text())
    if mutation == "list":
        payload = []
    elif mutation == "null":
        payload = None
    elif mutation == "record-null":
        payload["figures"] = [None]
    elif mutation == "integer-filename":
        payload["figures"][0]["filename"] = 123
    elif mutation == "duplicate":
        payload["figures"].append(payload["figures"][0])
    elif mutation == "swapped-labels":
        payload["figures"][0]["label"], payload["figures"][1]["label"] = (
            payload["figures"][1]["label"],
            payload["figures"][0]["label"],
        )
    elif mutation == "suffix":
        payload["figures"][0]["filename"] = FIGURES[0][0] + ".svg"
    elif mutation == "escape":
        payload["figures"][0]["filename"] = "../" + payload["figures"][0]["filename"]
    elif mutation == "utf8":
        path.write_bytes(b"\xff")
    elif mutation in ("svg-bytes", "png-bytes", "rehash-png"):
        extension = "svg" if mutation == "svg-bytes" else "png"
        (directory / f"{FIGURES[0][0]}.{extension}").write_bytes(b"not an image")
        if mutation == "rehash-png":
            payload["figures"][0]["png_sha256"] = hashlib.sha256(
                b"not an image"
            ).hexdigest()
    elif mutation == "renderer":
        payload["renderer"] = {"version": "different toolchain"}
    else:
        (directory / "golden_registry.json").write_text(
            json.dumps([] if mutation == "golden-list" else None)
        )
    if mutation != "utf8":
        path.write_text(json.dumps(payload))
    assert check_artifacts(root), mutation


def test_unchanged_source_build_passes(built_artifacts):
    assert check_artifacts(built_artifacts) == []
