# Claim boundaries

Statuses describe records, never people, safety, legality, virtue, or permission.
Counter-signal precedence applies within the admitted record. First valid wins
is order sensitive; rejected contradictory duplicates remain in `intake_archive`.
No voting, merge, compensation, or cross-line override occurs.

| Surface | Executable boundary | Limit |
| --- | --- | --- |
| Registry | `validate_registry` accepts nonempty tuple/list registries of `Aspiration`, copies tuple/list signals to immutable tuples, checks nonblank Unicode scalar text, unique IDs, populated unique disjoint signals | Structural validity is not empirical validation; custom vocabulary is labeled `custom:` and identified by digest |
| Intake | Built-in tuple/list/set/frozenset text-token collections, bounded by `MAX_COLLECTION_SIZE`; all IDs, notes, date text, and tokens must be Unicode scalar text; malformed passive records are set aside before membership or duplicates | Arbitrary token iterators are rejected without executing them; exceptions from the outer batch iterator remain caller/environment failures; raw malformed bytes require separate custody |
| Time | Calendar `date` or exact ASCII `YYYY-MM-DD` calendar-date string; timestamps, basic/week ISO forms, and non-ASCII digits rejected as review dates; sweep ages exact integers without bool/coercion | Malformed observation dates are retained but cannot establish currentness with a window; `currentness_evaluated=False` without a window, when date text is not interpreted |
| Envelope | Strict schema/identity/non-claim/shape validation is separate from native correspondence; caller text must contain only Unicode scalar values | Subject/source references are unverified caller metadata; reference tuple/list order and duplicates are retained |
| Archive | Existing valid native bytes and digest contract unchanged; versioned intake sidecar, first-valid admission, rejection notes, admitted-ID presence, and intrinsic retained-field correspondence checked during envelope-driven reconstruction | Not custom-registry or temporal replay; a consistent rewrite and rehash passes. Native-only reads have `intake_archive=None`, distinct from evaluated `()`; complete archive export and intake hashing refuse unavailable custody |
| Human evidence | Optional provenance and conflict records preserve self-report, source pointers, contestation, and human ownership; Unicode scalar text and bundled `GOLDEN_ASPIRATIONS` IDs/tokens only | Not a custom-registry exporter, including reused default IDs; retain custom evidence separately. Source content is unverified; no automatic consensus, benefit claim, permission, or override |
| Figures | Source SVG replay, converter identity, raster replay, checksums, exact manifest inventory, manuscript citations | Source consistency and byte integrity are separate from visual quality and substantive truth |
| Release | Exact source revision, lock hash, converter identity, command output/status and artifact hashes | Coverage is coverage evidence; local package gates do not imply an external render ran |

Unicode scalar text excludes code points U+D800–U+DFFF, which cannot be
serialized by the strict UTF-8 canonical transport. Ordinary non-ASCII and
supplementary characters remain unchanged; canonical JSON still uses
`ensure_ascii=False`, not surrogate escaping as a substitute for admission.

See [evidence protocol](evidence-protocol.md), [evidence records](evidence-records.md),
and the [review disposition](reviews/2026-10-20.md).
