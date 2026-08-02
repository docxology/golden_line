# Golden Line documentation guidance

This directory explains the executable package and its evidence boundaries.
The project-level `AGENTS.md` remains authoritative; these rules only add
documentation-specific constraints.

- Keep module paths, command names, figure counts, and gate descriptions aligned
  with the source and `docs/development.md`.
- Use relative links only for documents inside this repository. A relative link
  that resolves above the repository root is a defect: refer to the companion
  works by repository URL instead, and keep the reference an orientation link,
  not a code dependency.
- Describe statuses as readings of records, never as claims about people,
  safety, legality, permission, or universal truth.
- Do not duplicate evaluator logic in documentation; explain the source module
  and bind numerical claims to the claim ledger or generated artifacts.
