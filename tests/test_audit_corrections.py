import copy
import json
from dataclasses import replace
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft7Validator, FormatChecker

from golden_line import (
    GOLDEN_ASPIRATIONS,
    HorizonEntry,
    envelope_matches_report,
    progress_report,
    report_envelope,
    validate_instrument_envelope,
)

ROOT = Path(__file__).resolve().parents[1]


def _cff_validator():
    schema = json.loads((ROOT / "tests/fixtures/cff-1.2.0.schema.json").read_text())
    Draft7Validator.check_schema(schema)
    return Draft7Validator(schema, format_checker=FormatChecker())


def test_citation_conforms_to_official_cff_schema():
    metadata = yaml.safe_load((ROOT / "CITATION.cff").read_text())
    errors = list(_cff_validator().iter_errors(metadata))
    assert not errors, [(list(error.path), error.message) for error in errors]


def test_cff_schema_rejects_reference_without_authors():
    metadata = copy.deepcopy(yaml.safe_load((ROOT / "CITATION.cff").read_text()))
    metadata["references"][0].pop("authors", None)
    assert any(
        list(error.path) == ["references", 0] and "authors" in error.message
        for error in _cff_validator().iter_errors(metadata)
    )


def test_outer_batch_failure_is_outside_passive_data_boundary():
    def batch():
        yield HorizonEntry(GOLDEN_ASPIRATIONS[0].id)
        raise RuntimeError("batch producer failed")

    with pytest.raises(RuntimeError, match="batch producer failed"):
        progress_report(batch(), as_of="2026-10-20")
    method = (ROOT / "docs/manuscript/02_method.md").read_text()
    assert "never\n   raised" not in method
    assert "outer batch iterator" in method


def test_caller_metadata_is_not_a_report_binding():
    report = progress_report([], as_of="2026-10-20")
    envelope = replace(
        report_envelope(report),
        subject_id="another subject",
        source_snapshot_refs=("b",),
    )
    assert envelope_matches_report(envelope, report)
    assert validate_instrument_envelope(envelope) == ()
    formalism = (ROOT / "docs/manuscript/02a_formalism.md").read_text()
    assert "any post-export edit is visible" not in formalism
