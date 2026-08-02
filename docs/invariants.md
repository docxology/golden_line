# Registry invariants and proof-of-detection

`src/golden_line/invariants.py` holds seven pure-compute checks over the shape
of the aspiration registry. Each returns a frozen
`SoundnessResult(name, passed, detail)`; `all_invariants()` runs the battery
and `registry_sound()` collapses it to a boolean.

## The checks

| Check | What breakage it detects |
| --- | --- |
| `distinct_aspiration_ids` | Duplicate ids, which would make findings ambiguous. |
| `fields_populated` | Blank `id`, `title`, `thread`, or `horizon` text. |
| `reachable_statuses` | An aspiration with no markers (can never read `TOWARD`) or no counter-signals (can never read `DRIFTING`) — a status silently unreachable while the registry still looks populated. |
| `signal_disjointness` | A token listed as both marker and counter-signal, which would read as movement toward and away at once. |
| `signal_text` | Blank or non-string signal tokens planted through `dataclasses.replace`, which dataclasses do not type-check. |
| `signal_uniqueness` | Repeated marker or counter-signal declarations that would overstate one token's reachability. |
| `digest_stability` | A canonical form that no longer serializes, or a digest that depends on registry order. |

## Proof-of-detection

A green check that never saw a bad input is not evidence. For every check the
test suite (`tests/test_invariants.py`) asserts both directions:

- the check **passes** on the real `GOLDEN_ASPIRATIONS`, and
- the check **fails** on a planted-bad registry built with
  `dataclasses.replace` (duplicate id, blank thread, empty marker tuple,
  overlapping signals, non-string token, repeated token, malformed registry
  entry, unserializable token, twin ids that make the sort order-unstable).

| Check | Proof-of-detection tests |
| --- | --- |
| `distinct_aspiration_ids` | `test_distinct_ids_detects_duplicate` |
| `fields_populated` | `test_fields_populated_detects_blank` |
| `reachable_statuses` | `test_reachable_statuses_detects_markerless`, `test_reachable_statuses_detects_counter_signalless` |
| `signal_disjointness` | `test_signal_disjointness_detects_overlap` |
| `signal_text` | `test_signal_text_detects_blank_token`, `test_signal_text_detects_non_string_token` |
| `signal_uniqueness` | `test_signal_uniqueness_detects_repeated_token` |
| `digest_stability` | `test_digest_stability_detects_unserializable`, `test_digest_stability_detects_order_dependence` |

`scripts/check_registry.py` runs the same battery from the command line and
exits non-zero on any failure, so drift in the registry is caught outside the
test suite as well. The digest it prints is a review instrument for comparing
revisions; it makes no safety claim.
