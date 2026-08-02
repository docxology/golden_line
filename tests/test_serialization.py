"""Determinism and digest stability for registry and report serialization."""

import json

from golden_line import (
    GOLDEN_ASPIRATIONS,
    HorizonEntry,
    canonical_registry,
    canonical_report,
    progress_report,
    registry_digest,
    report_digest,
)


def test_canonical_registry_is_deterministic_json() -> None:
    first = canonical_registry(GOLDEN_ASPIRATIONS)
    second = canonical_registry(tuple(reversed(GOLDEN_ASPIRATIONS)))
    assert first == second
    payload = json.loads(first)
    assert [item["id"] for item in payload] == sorted(
        item.id for item in GOLDEN_ASPIRATIONS
    )


def test_registry_digest_is_sha256_hex() -> None:
    digest = registry_digest(GOLDEN_ASPIRATIONS)
    assert len(digest) == 64
    assert set(digest) <= set("0123456789abcdef")


def test_canonical_report_is_deterministic() -> None:
    entries = [
        HorizonEntry(GOLDEN_ASPIRATIONS[0].id, frozenset(GOLDEN_ASPIRATIONS[0].markers))
    ]
    report_a = progress_report(entries, as_of="2026-07-17")
    report_b = progress_report(entries, as_of="2026-07-17")
    assert canonical_report(report_a) == canonical_report(report_b)
    assert report_digest(report_a) == report_digest(report_b)
    payload = json.loads(canonical_report(report_a))
    assert set(payload) == {
        "findings",
        "intake_notes",
        "counts",
        "registry_version",
        "registry_digest",
        "as_of",
        "stale_after_days",
    }
    assert payload["registry_version"] == "2026.07.18"
    assert payload["registry_digest"] == registry_digest(GOLDEN_ASPIRATIONS)


def test_report_digest_changes_with_content() -> None:
    base = progress_report([], as_of="2026-07-17")
    moved = progress_report(
        [
            HorizonEntry(
                GOLDEN_ASPIRATIONS[0].id, frozenset(GOLDEN_ASPIRATIONS[0].markers)
            )
        ],
        as_of="2026-07-17",
    )
    assert report_digest(base) != report_digest(moved)
