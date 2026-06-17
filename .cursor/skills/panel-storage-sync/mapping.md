# Panel Share ↔ Repo Mapping

Panel root:

```
S:\02_Teaching and Learning\03_Key Learning Areas\Technology\08_Others
```

## Cross-year folders (archive / reference)

| Panel folder | Repo path | Notes |
|--------------|-----------|-------|
| `_1_EDB_Documents/` | `Subjects/DSE-ICT/edb/` | EDB / HKEAA curriculum docs |
| `_4_HKEAA_Paper/ICT/` | `Subjects/DSE-ICT/past-papers/` | Official DSE papers |
| `_5_Resources/` | Pull selectively → relevant `Subjects/*/notes/` | Textbooks, worksheets; do not bulk-import |
| `_6_SBA/` | S: only unless building SBA tooling | |
| `_2_Past_PanelFolderBackup_2003-2019/` | S: only | Legacy archive; browse on demand |
| `_3_Official_Forms/` | `Administrative/` (future) | |
| `_7_*` | S: only | DSE analysis reports |

## Per-year folders (`2019-2020` … `2025-2026`)

Recent years (≈2024-2025+) use numbered prefixes:

| Panel subfolder | Repo | Git? |
|-----------------|------|------|
| `05_Test_and_Exam_Paper/S1CMP` … `S6ICT` | `Subjects/S{1-6}-{CMP\|ICT}/past-papers/{year}/` | Yes (selective) |
| `06_NotesLibrary/S*_CMP`, `S*_ICT` | `Subjects/S*-*/notes/` | Yes (active units) |
| `02_Course_Outline/` | `Administrative/` or S: only | Usually S: |
| `03_Marksheets/` | **Never in git** | S: only |
| `00_Activities/`, agendas, DH reports | `Administrative/` | S: unless needed |

Older years (≈2019-2023) may use names like `5_Test_and_Exam_Paper`, `6_Notes_Library` — same logical mapping.

### Panel exam layout vs repo

Panel often stores files **flat** under term folders:

```
{year}/05_Test_and_Exam_Paper/S2CMP/Term1/*.docx
{year}/05_Test_and_Exam_Paper/S2CMP/Term2/*.pdf
```

Repo uses category subfolders (match by filename when pulling):

| Filename pattern | Repo folder |
|------------------|-------------|
| `*Exam*`, `*Written*` | `Term {01\|02}/WrittenExam/` |
| `*Practical_Assessment*`, `*PracticalAssessment*` | `Term {01\|02}/PracticalAssessment/` |
| `*Practical_Mock*`, `*PracticalMock*` | `Term {01\|02}/PracticalMock/` |
| Images, task data, misc | `assessments/{year}/Term {01\|02}/_assets/`（工作檔；不入 past-papers） |

Use `scripts/pull-from-panel.ps1` for this mapping.

## Form / subject name conversion

| Panel exam folder | Repo workspace |
|-------------------|----------------|
| `S1CMP` | `S1-CMP` (create if needed) |
| `S2CMP` | `S2-CMP` |
| `S3CMP` | `S3-CMP` |
| `S4ICT` | `S4-ICT` (create if needed) |
| `S5ICT` | `S5-ICT` |
| `S6ICT` | `S6-ICT` |

## Repo layout (`assessments` + `past-papers`)

```
Subjects/S3-CMP/
├── assessments/                    # working drafts — git only, never publish to S:
│   ├── exam-input/
│   └── {YYYY-YYYY}/Term {01|02}/
│       ├── _generation/            # specs, agent output
│       ├── _reference/
│       ├── _assets/
│       └── …                       # answer scripts, student submissions workspace
└── past-papers/                    # finals only — may publish to S:
    └── {YYYY-YYYY}/Term {01|02}/
        ├── WrittenExam/
        ├── PracticalAssessment/
        ├── PracticalMock/
        └── PracticalExam/          # if used
```

## Publish targets (finals only, with user permission)

| Artifact type | Panel destination |
|---------------|-------------------|
| Written / practical exam (final) | `{year}/05_Test_and_Exam_Paper/S{form}{CMP\|ICT}/` |
| Teaching notes / worksheets | `{year}/06_NotesLibrary/S{form}_{CMP\|ICT}/` |
| Panel-wide resource | `_5_Resources/` or year `4_Resources/` |

Current school year for publish: use the active `{YYYY-YYYY}` folder on panel (e.g. `2025-2026`).
