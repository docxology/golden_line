# .agents/skills — AGENTS.md

Project-local skill catalog. One folder per skill.

| Skill | Purpose |
| --- | --- |
| [`golden-line/`](golden-line/AGENTS.md) | Operate the Golden Line instrument end-to-end. |

## Skill contract

Every folder under `.agents/skills/<name>/` ships three files:

- `SKILL.md` — YAML frontmatter (`name`, `description`) plus a body covering
  when to use the skill, the quick reference, the pitfalls, and cross-refs.
- `AGENTS.md` — the folder's technical contract.
- `README.md` — purpose and pointer.

Skill names are lowercase and hyphenated, and must not collide with a skill
name in a sibling project.
