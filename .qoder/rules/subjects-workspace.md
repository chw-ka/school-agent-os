---
trigger: glob
glob: Subjects/**
---

# Subjects workspace

## Folder layout

- One workspace per form + subject: `S2-CMP/`, `S3-CMP/`, `S5-ICT/`, `S6-ICT/`
- Cross-form DSE refs: `DSE-ICT/` only (not duplicated per form)
- `assessments/{YYYY-YYYY}/Term {01|02}/` — 出卷工作區（`_generation/`、`exam-input/`、答案腳本、批改暫存）
- `past-papers/{YYYY-YYYY}/Term {01|02}/WrittenExam|PracticalAssessment|PracticalMock/` — 終稿庫（僅可派發版本）
- `resources/` — 參考卷、樣本卷等教學資源
- Agent 產物：`_generation/`、`*.spec.json` — 只留 git，不發佈至 S:

## Naming

- Exam files: `{YY}_{YY}_S{form}_{CMP|ICT}_...` (e.g. `24_25_S3_CMP_Term1_WrittenExam.docx`)

## Storage tiers

- Commit active teaching materials needed at home (see `Subjects/STORAGE.md`)
- Do not commit marksheets, grades, or bulk named student submissions
- Never write to panel share `S:\...\08_Others` without user permission
