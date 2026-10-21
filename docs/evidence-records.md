# Optional evidence and conflict records

Design decision for G9 (2026-10-21): add separate, versioned side records through
`canonical_evidence_records`, leaving `HorizonEntry`, directional selection, and
the existing native report serialization unchanged. The release audit reviews
this boundary together with the full packet. This is a design of record custody,
not a new claim about the effects of work.

`ObservationProvenance` identifies an observation, aspiration, authorship
(`self_report`, `independent_observation`, or `unspecified`), source references,
observer role, collection method, review scope, token-to-source pointers,
contestation and supersession references. A reference identifies a source; it
does not verify its contents. Competing observations coexist without voting.

`AspirationConflict` retains the aspirations in tension, affected perspectives,
unresolved alternatives, review note, and human decision owner. A tension with
confidentiality or locally adverse effects can name a single Golden aspiration
and preserve the external concern in the perspectives and alternatives.
Consent, absence, and stewardship remain separate questions in
[Violet Line](https://github.com/docxology/violet_line),
[White Line](https://github.com/docxology/white_line), and
[Silver Line](https://github.com/docxology/silver_line).

`worked_evidence_records()` supplies illustrative records, exported by
`canonical_evidence_records(*worked_evidence_records())`:

| Record | Preserved tension | Human-owned alternatives |
| --- | --- | --- |
| `example:commons-confidentiality` | commons return versus collaborator confidentiality | release a redacted method; withhold sensitive material |
| `example:useful-unhurried` | usefulness versus protected inquiry time | publish a bounded interim handoff; continue inquiry before transfer |
| `example:flourishing-local-effects` | anticipated broad benefit versus reported local adverse effects | revise with affected participants; pause the proposed application |

The self-report handoff example and the recipient's contestation remain separate
records after export. They are synthetic worked records, not collected evidence.
Neither record type grants permission, overrides another line, or resolves a
human disagreement automatically.
