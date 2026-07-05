@_platform/CLAUDE.md

# Personal Workspace Rules (Warren / CHW Tech Panel)

## Panel Share & Git (Teaching Materials)

- **Git repo** = portable copy for home (no `S:` off-campus). Commit + push materials needed at home.
- **Panel share** = `S:\02_Teaching and Learning\03_Key Learning Areas\Technology\08_Others` — school-only department archive.
- **Never write to the panel share without explicit user permission.**
- **Never commit** marksheets, grades, student IDs, or bulk student homework submissions.
- See `Subjects/STORAGE.md` for storage-tier decisions and skill `panel-storage-sync`.

## Subjects Structure

- Workspaces: `Subjects/S2-CMP/`, `S3-CMP/`, `S5-ICT/`, `S6-ICT/`, `DSE-ICT/`
- `assessments/{YYYY-YYYY}/Term {01|02}/` — exam generation workspace (`_generation/`, `*.spec.json`, review artifacts, marking scripts)
- `past-papers/{YYYY-YYYY}/Term {01|02}/` — final deliverables only (no `_generation/` content)
- See `.cursor/rules/subjects-workspace.mdc` for full naming and tier conventions.

## Personal Skills

Platform skills (via symlinks in `.cursor/skills/`): `meeting-minutes`, `tidy-up`, `_template`

Personal skills (`.cursor/skills/`): `generate-f5-ict-exam`, `generate-f5-ict-long`, `generate-f5-ict-mcq`, `generate-f5-ict-short`, `panel-storage-sync`, `qef-elearning-grant`, `school-activity-form`, `student-report-guides`, `mssql-mcp-legacy-execute`

## CHW API

School data (students, classes, teachers) is available via MCP tools `mcp__chw-api-remote__*`. See `docs/chw-api.md` for available endpoints.

## Navigation

See `NAV.md` for the current work index. `Administrative/README.md` describes admin projects (each is independent; don't assume cross-project context).
