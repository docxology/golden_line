import re
from pathlib import Path


def test_source_manuscript_image_references_resolve_to_generated_figures():
    root = Path(__file__).resolve().parents[1]
    references = [
        (path, ref)
        for path in (root / "docs" / "manuscript").glob("*.md")
        for ref in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", path.read_text())
    ]
    assert references
    for source, reference in references:
        target = (source.parent / reference).resolve()
        assert target.is_file(), (source.name, reference)
        assert target.parent == (root / "output" / "figures").resolve()
