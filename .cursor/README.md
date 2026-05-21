# Cursor project config

Agent rules and skills for this repo.

## Rules (`.cursor/rules/`)

| Rule | Scope | Purpose |
|------|-------|---------|
| `panel-storage-sync.mdc` | Always | S: vs git; no panel writes without permission; privacy |
| `subjects-workspace.mdc` | `Subjects/**` | Folder layout and naming |

## Skills (`.cursor/skills/`)

| Skill | Purpose |
|-------|---------|
| `panel-storage-sync` | Pull/publish teaching files between repo and panel share |

## Related docs

- [Subjects/STORAGE.md](../Subjects/STORAGE.md) — full storage policy
- [.cursorrules](../.cursorrules) — project constitution
