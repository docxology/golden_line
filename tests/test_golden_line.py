from golden_line import (
    GOLDEN_ASPIRATIONS,
    HorizonEntry,
    HorizonStatus,
    aspiration_ids,
    progress_report,
    registry_digest,
)


def test_registry_is_unique_and_order_independent() -> None:
    assert len(aspiration_ids()) == len(set(aspiration_ids())) == 9
    assert registry_digest(GOLDEN_ASPIRATIONS) == registry_digest(
        tuple(reversed(GOLDEN_ASPIRATIONS))
    )


def test_missing_and_empty_notes_remain_open() -> None:
    report = progress_report([HorizonEntry("attention-before-output")])
    statuses = {item.aspiration_id: item.status for item in report.findings}
    assert statuses["attention-before-output"] is HorizonStatus.INQUIRY
    assert statuses["useful-to-others"] is HorizonStatus.NOT_OBSERVED


def test_directional_states_are_not_compliance_verdicts() -> None:
    aspiration = GOLDEN_ASPIRATIONS[0]
    toward = progress_report(
        [HorizonEntry(aspiration.id, frozenset(aspiration.markers))]
    )
    assert toward.findings[0].status is HorizonStatus.TOWARD

    drifting = progress_report(
        [
            HorizonEntry(
                aspiration.id, counter_signals=frozenset(aspiration.counter_signals)
            )
        ]
    )
    assert drifting.findings[0].status is HorizonStatus.DRIFTING


def test_partial_markers_remain_inquiry() -> None:
    aspiration = GOLDEN_ASPIRATIONS[1]
    report = progress_report(
        [HorizonEntry(aspiration.id, frozenset({aspiration.markers[0]}))]
    )
    assert report.findings[1].status is HorizonStatus.INQUIRY
