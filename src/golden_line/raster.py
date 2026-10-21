import hashlib
import json
import shutil
import subprocess
from functools import lru_cache
from pathlib import Path


def renderer_provenance() -> tuple[str, dict[str, str]]:
    converter = shutil.which("rsvg-convert")
    if converter is None:
        raise RuntimeError(
            "rsvg-convert is required to build deterministic PNG figures"
        )
    version = subprocess.run(
        [converter, "--version"], check=True, capture_output=True, text=True
    ).stdout.strip()
    return converter, {
        "version": version,
        "executable_sha256": hashlib.sha256(Path(converter).read_bytes()).hexdigest(),
    }


@lru_cache(maxsize=128)
def rasterized_svg(svg: bytes, converter: str, provenance: str) -> bytes:
    return subprocess.run(
        [converter], input=svg, check=True, capture_output=True
    ).stdout


def raster_bytes(svg: bytes, converter: str, provenance: dict[str, str]) -> bytes:
    return rasterized_svg(svg, converter, json.dumps(provenance, sort_keys=True))
