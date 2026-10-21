import shutil
from pathlib import Path

import pytest

from golden_line.formalism_ledger import build_ledger


def test_ledger_source_check_rejects_mutation_on_a_copy(tmp_path):
    root = Path(__file__).resolve().parents[1]
    shutil.copytree(root / "docs" / "manuscript", tmp_path / "docs" / "manuscript")
    (tmp_path / "data").mkdir()
    assert "citation rows" in build_ledger(project_root=tmp_path)
    assert "verified" in build_ledger(check=True, project_root=tmp_path)
    (tmp_path / "data" / "formalism_claim_ledger.json").write_text("{}")
    with pytest.raises(ValueError, match="differs from source"):
        build_ledger(check=True, project_root=tmp_path)
