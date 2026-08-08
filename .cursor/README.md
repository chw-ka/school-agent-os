# Cursor project config (legacy — migrated to Qoder)

> **注意：** 本 repo 已遷移至 Qoder。主要配置現在位於 `.qoder/` 和 `AGENTS.md`。
> 此 `.cursor/` 目錄保留以兼容 Claude Code、Kimi Code CLI 等其他工具。

Agent rules and skills for this **personal** repo. Shared platform skills/tools live in `_platform/` (submodule).

## Platform vs personal

| | Location |
|---|----------|
| Tools, templates | `_platform/` (symlinked as `shared-tools/`, `templates/`) |
| Generic skills | `_platform/.cursor/skills/` — symlinked into `.cursor/skills/` |
| Personal skills | `.cursor/skills/` (non-symlink folders) |
| Personal rules | `.cursor/rules/` |

## Migration to Qoder

| Item | Old (Cursor) | New (Qoder) |
|------|-------------|------------|
| Rules | `.cursor/rules/*.mdc` | `.qoder/rules/*.md` |
| Skills | `.cursor/skills/` | `.qoder/skills/` |
| Project instructions | `CLAUDE.md` | `AGENTS.md` |
| Constitution | `.cursorrules` | `AGENTS.md` |

See [docs/PLATFORM-SETUP.md](../docs/PLATFORM-SETUP.md#qoder-遷移) for details.

## Rules (`.cursor/rules/`)

| Rule | Scope | Purpose |
|------|-------|---------|
| `panel-storage-sync.mdc` | Always | S: vs git; no panel writes without permission; privacy |
| `subjects-workspace.mdc` | `Subjects/**` | Folder layout and naming |
| `paper-generator.mdc` | Paper generation | S5 ICT pipeline hints |

## Skills (`.cursor/skills/`)

| Skill | Layer | Purpose |
|-------|-------|---------|
| `meeting-minutes` | platform | Transcript → structured Chinese minutes |
| `tidy-up` | platform | Repo layout audit |
| `_template` | platform | New skill template |
| `panel-storage-sync` | personal | Panel share ↔ repo |
| `generate-f5-ict-exam` (+ mcq/short/long) | personal | S5 ICT exam workflow |
| `qef-elearning-grant` | personal | QEF e-learning grant cycle |
| `school-activity-form` | personal | 校內外活動申請表 |
| `student-report-guides` | personal | 成績表流程 |
| `mssql-mcp-legacy-execute` | personal | CHW SQL MCP patterns |

## Related docs

- [Subjects/STORAGE.md](../Subjects/STORAGE.md)
- [.cursorrules](../.cursorrules)
- [docs/PLATFORM-COLLABORATION.md](../docs/PLATFORM-COLLABORATION.md)
