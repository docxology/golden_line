# Fixture custody

`cff-1.2.0.schema.json` is the official Citation File Format 1.2.0 schema,
retrieved on 2026-10-21 from
<https://citation-file-format.github.io/1.2.0/schema.json> for offline metadata
validation. Its SHA-256 is
`0b8d22140da702d766df318dcff3a91af2f39521298dcf36d76315fd99cc169b`.
The missing-reference-author control confirms that the validator rejects the
metadata defect found by the independent release audit.

`native_report_v040.json` preserves the native canonical bytes and digest
produced at the pre-review baseline; the archive tests check that compatibility
without rewriting this fixture.
