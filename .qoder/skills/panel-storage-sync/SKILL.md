---
name: panel-storage-sync
description: >-
  Syncs teaching materials between the git repo (portable, home-safe) and the
  school panel share S:\...\08_Others. Use when pulling past papers or notes
  from the department drive, publishing finals for colleagues, working at home
  without S: access, or deciding what belongs in git vs on the network share.
---

# Panel Storage Sync

## Core model

| Location | Role |
|----------|------|
| **Git repo** (`Subjects/`, GitHub) | Portable working copy — **required for home** (no S: access) |
| **Panel share** (`S:\...\08_Others`) | Department archive + publish target — **school network only** |

```
Home:     git pull → work → git commit/push
School:   optional pull S: → repo → push  |  optional publish repo → S: (with permission)
```

## Hard rules

1. **Never copy or write to `S:\...\08_Others` without explicit user permission.**
2. **Never commit** marksheets, student grades, class lists with IDs, or bulk student submissions.
3. **At home**, assume S: is unavailable — if a file is not in git, it cannot be used.
4. **Agent artifacts** (`_generation/`, `*.spec.json`, drafts) stay in git only; do not publish to S:.
5. **Final deliverables only** when publishing to S: (`.docx`, `.pdf`, teacher notes — not specs or scratch files).

## What goes in git

Pin in repo (commit + push) when you need access at home:

- Current + recent past papers (`past-papers/{YYYY-YYYY}/`)
- Active teaching notes (`notes/`)
- DSE / EDB references (`DSE-ICT/`)
- Exam specs and tool inputs (`assessments/exam-input/`, `assessments/.../_generation/`, `source/`)

Keep **S: only** (do not bulk-import):

- `03_Marksheets/` and any grade data
- `_2_Past_PanelFolderBackup_2003-2019` (~55k legacy files)
- Large media already in `.gitignore` (`*.mp4`, `*.zip`, `*.apk`, `*.aia`)
- Whole `_5_Resources` or `_6_SBA` unless a specific file is needed

## Path mapping

Full table: [mapping.md](mapping.md)

Quick examples (2024-2025+ year folders):

| Panel (S:) | Repo |
|------------|------|
| `{year}/05_Test_and_Exam_Paper/S2CMP/` | `Subjects/S2-CMP/past-papers/{year}/` |
| `{year}/06_NotesLibrary/S2_CMP/` | `Subjects/S2-CMP/notes/` |
| `_4_HKEAA_Paper/ICT/` | `Subjects/DSE-ICT/past-papers/` |
| `_1_EDB_Documents/` | `Subjects/DSE-ICT/edb/` |

Use workspace naming inside repo: `{YY}_{YY}_S3_CMP_Term01_...`, `Term {01|02}/WrittenExam|PracticalAssessment|PracticalMock`.

## Workflows

### A — Pull from panel (at school, into repo)

Use when user needs S: files at home.

1. Confirm S: path is reachable (`Test-Path` on panel root).
2. Copy **only requested files** to the matching `Subjects/…` path (do not mirror whole year folders).
3. Tell user to `git add`, commit, and push — or do so if they asked.
4. Do **not** delete or move files on S:.

Optional helper (dry-run default):

```powershell
.qoder/skills/panel-storage-sync/scripts/pull-from-panel.ps1 `
  -Subject S2-CMP -Year 2024-2025 -WhatIf
```

### B — Publish to panel (at school, from repo)

**Stop and ask the user first.** Only proceed after explicit approval.

1. Confirm final artifact path in repo (not `_generation/` or draft).
2. Map to panel destination (see [mapping.md](mapping.md)).
3. Copy final file(s) only; preserve existing panel filenames if colleagues expect them.
4. Report source → destination paths to the user.

### C — Work at home

1. Use repo contents only.
2. Commit finished work and push.
3. Remind user: to share with department or pull legacy S: files, sync at school (workflow A or B).

## School sync checklist (for user)

Before leaving school:

- [ ] Pull any S: references needed this week into `Subjects/…`
- [ ] `git commit` + `git push`
- [ ] At home: `git pull`

After creating shareable finals at school:

- [ ] User approves panel publish
- [ ] Copy finals to `{year}/05_Test_and_Exam_Paper/…` or `06_NotesLibrary/…`

## Related docs

- [Subjects/STORAGE.md](../../../Subjects/STORAGE.md) — full storage policy
- [mapping.md](mapping.md) — S: ↔ repo paths
