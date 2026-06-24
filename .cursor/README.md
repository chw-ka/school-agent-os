# Cursor project config

Agent rules and skills for this repo.

## Rules (`.cursor/rules/`)

| Rule | Scope | Purpose |
|------|-------|---------|
| `panel-storage-sync.mdc` | Always | S: vs git; no panel writes without permission; privacy |
| `subjects-workspace.mdc` | `Subjects/**` | Folder layout and naming |

## Skills (`.cursor/skills/`)

See also [skills/README.md](skills/README.md) for how to add workflow skills.

| Skill | Purpose |
|-------|---------|
| `panel-storage-sync` | Pull/publish teaching files between repo and panel share |
| `qef-elearning-grant` | Annual QEF e-Learning Grant workflow (devices, router/SIM, loan records, claim) |
| `meeting-minutes` | Transcript → structured Chinese meeting minutes |
| `generate-f5-ict-exam` | F5 ICT exam generation workflow |
| `tidy-up` | Repo/workspace tidy-up checklist |

## Related docs

- [Subjects/STORAGE.md](../Subjects/STORAGE.md) — full storage policy
- [.cursorrules](../.cursorrules) — project constitution
- [docs/PLATFORM-COLLABORATION.md](../docs/PLATFORM-COLLABORATION.md) — platform + personal repo 共建構想（設計備忘，未實施）
