from dataclasses import replace
from datetime import date, datetime, timezone

import pytest

from golden_line import (
    GOLDEN_ASPIRATIONS,
    HorizonEntry,
    progress_report,
    registry_sound,
    report_envelope,
    temporal_currentness_sweep,
)

A = GOLDEN_ASPIRATIONS[0]


@pytest.mark.parametrize(
    "registry",
    [
        (A, A),
        (object(),),
        None,
        "registry",
        {A.id: A},
        (),
        (replace(A, id=" "),),
        (replace(A, markers="ab"),),
        (replace(A, markers=b"ab"),),
        (replace(A, markers={"a": 1}),),
        (replace(A, markers=iter(("a",))),),
        (replace(A, markers=()),),
        (replace(A, title=None),),
    ],
)
def test_invalid_registry_rejected_before_entries_are_read(registry):
    with pytest.raises(ValueError, match="registry") as caught:
        progress_report([], registry, as_of="2026-10-20")
    assert caught.value.issues


def test_battery_does_not_consume_one_shot_signal_fields():
    tokens = iter(("a", "b"))
    assert not registry_sound((replace(A, markers=tokens),))
    assert next(tokens) == "a"


def test_subset_identity_and_immutable_replay():
    report = progress_report([], (A,), as_of="2026-10-20")
    assert report.registry_version.startswith("custom:")
    assert report == progress_report([], (A,), as_of="2026-10-20")


@pytest.mark.parametrize("window", [None, 30])
def test_date_only_rejects_timestamp_in_both_modes(window):
    with pytest.raises(TypeError, match="date"):
        progress_report(
            [HorizonEntry(A.id, observed_on="2026-10-20")],
            as_of=datetime(2026, 10, 20, 12, tzinfo=timezone.utc),
            stale_after_days=window,
        )


@pytest.mark.parametrize("age", [True, False, 1.5, "2"])
def test_sweep_ages_are_exact_integers(age):
    with pytest.raises(ValueError, match="integer"):
        temporal_currentness_sweep(A.id, [age], as_of="2026-10-20", stale_after_days=30)


def test_sweep_rejects_datetime():
    with pytest.raises(TypeError, match="date"):
        temporal_currentness_sweep(
            A.id,
            [0],
            as_of=datetime(2026, 10, 20, tzinfo=timezone.utc),
            stale_after_days=30,
        )


def _raising_tokens():
    raise RuntimeError("must not execute token iterators")
    yield "unreachable"


@pytest.mark.parametrize("tokens", [{"a": 1}, iter(()), _raising_tokens()])
def test_unsupported_token_containers_are_set_aside_without_iteration(tokens):
    report = progress_report([HorizonEntry(A.id, tokens)], as_of="2026-10-20")
    assert report.findings[0].status.value == "NOT_OBSERVED"
    assert report.intake_notes


def test_currentness_is_explicitly_not_evaluated():
    report = progress_report([], as_of=date(2026, 10, 20))
    assert report.currentness_evaluated is False


@pytest.mark.parametrize(
    "refs", ["snapshot-1", b"snap", {"snap": 1}, None, (1,), (" ",)]
)
def test_envelope_rejects_invalid_reference_containers(refs):
    with pytest.raises((TypeError, ValueError), match="source_snapshot_refs"):
        report_envelope(
            progress_report([], as_of="2026-10-20"), source_snapshot_refs=refs
        )


def test_reference_order_and_duplicates_are_preserved():
    refs = ["b", "a", "b"]
    envelope = report_envelope(
        progress_report([], as_of="2026-10-20"), source_snapshot_refs=refs
    )
    assert envelope.source_snapshot_refs == tuple(refs)
