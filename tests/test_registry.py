"""Shape tests for the aspiration registry."""

from golden_line import GOLDEN_ASPIRATIONS, Aspiration, aspiration_ids, find_aspiration


def test_registry_shape() -> None:
    assert len(GOLDEN_ASPIRATIONS) == 9
    assert aspiration_ids() == tuple(item.id for item in GOLDEN_ASPIRATIONS)
    assert all(isinstance(item, Aspiration) for item in GOLDEN_ASPIRATIONS)


def test_every_aspiration_declares_both_signal_kinds() -> None:
    for item in GOLDEN_ASPIRATIONS:
        assert item.markers and all(
            isinstance(marker, str) and marker for marker in item.markers
        )
        assert item.counter_signals and all(
            isinstance(signal, str) and signal for signal in item.counter_signals
        )


def test_find_aspiration_hit_and_miss() -> None:
    hit = find_aspiration("repairable-systems")
    assert hit is not None and hit.title == "Prefer systems that can be repaired"
    assert find_aspiration("no-such-aspiration") is None


def test_canonical_dict_matches_fields() -> None:
    item = GOLDEN_ASPIRATIONS[0]
    canonical = item.canonical()
    assert canonical["id"] == item.id
    assert canonical["markers"] == list(item.markers)
    assert canonical["counter_signals"] == list(item.counter_signals)
