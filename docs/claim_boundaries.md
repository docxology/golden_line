# Claim boundaries

Statuses describe records, never people, safety, legality, virtue, or permission.
Counter-signal precedence applies within the admitted record. First valid wins
is order sensitive; rejected contradictory duplicates remain in `intake_archive`.
No voting, merge, compensation, or cross-line override occurs.

| Surface | Executable boundary | Limit |
| --- | --- | --- |
| Registry | `validate_registry` accepts nonempty tuple/list registries of `Aspiration`, copies tuple/list signals to immutable tuples, checks nonblank fields, unique IDs, populated unique disjoint signals | Structural validity is not empirical validation; custom vocabulary is labelled `custom:` and identified by digest |
| Intake | Built-in tuple/list/set/frozenset text-token collections, bounded by `MAX_COLLECTION_SIZE`; malformed passive records are set aside | Arbitrary token iterators are rejected without executing them; exceptions from the outer batch iterator remain caller/environment failures; raw malformed bytes require separate custody |
| Time | Calendar `date` or ISO date string; timestamps rejected; sweep ages exact integers without bool/coercion | `currentness_evaluated=False` when no window is set; stale flags then do not certify freshness |
| Envelope | Strict schema/identity/non-claim/shape validation is separate from native correspondence | Subject/source references are unverified caller metadata; reference tuple/list order and duplicates are retained |
| Archive | Existing native bytes and digest contract unchanged; versioned intake sidecar and envelope-driven ID bijection reconstruction | A consistent rewrite and rehash passes; SHA-256 does not authenticate history or source truth |
| Human evidence | Optional provenance and conflict records preserve self-report, source pointers, contestation, and human ownership | Source content is unverified; no automatic consensus, benefit claim, permission, or override |
| Figures | Source SVG replay, converter identity, raster replay, checksums, exact manifest inventory, manuscript citations | Source consistency and byte integrity are separate from visual quality and substantive truth |
| Release | Exact source revision, lock hash, converter identity, command output/status and artifact hashes | Coverage is coverage evidence; local package gates do not imply an external render ran |

See [evidence protocol](evidence-protocol.md), [evidence records](evidence-records.md),
and the [review disposition](reviews/2026-10-20.md).
