# Tidy Up — Reference

## 科目工作區標準結構

```
Subjects/S3-CMP/
├── assessments/                    # git only — 工作區
│   ├── exam-input/
│   └── {YYYY-YYYY}/Term {01|02}/
│       ├── _generation/
│       ├── _reference/
│       ├── _assets/
│       ├── WrittenExam/
│       ├── PracticalAssessment/
│       │   └── _student_submissions/
│       └── PracticalMock/
├── past-papers/                    # 終稿 — 可發佈 S:
│   └── {YYYY-YYYY}/Term {01|02}/
│       ├── WrittenExam/
│       ├── PracticalAssessment/
│       └── PracticalMock/
├── resources/
│   └── reference/
└── notes/
```

## 行政區標準結構

```
Administrative/CHW/
├── migration/
├── homework-diligence-award/
├── conduct-mark/
├── websams-management/
├── slp/
├── student-report/
├── sportsday/
└── digital-education/

Subjects/TechEd/
└── booklist-material-planning/
```

## past-papers 內常見錯放 → 目標

| 錯放於 `past-papers/` | 搬至 |
|----------------------|------|
| `_generation/` | `assessments/{同學年學期}/_generation/` |
| `_reference/` | `assessments/{同學年學期}/_reference/` |
| `_assets/`、`*.png`、`*.xml` | `assessments/.../_assets/` |
| `*.spec.json` | `assessments/.../_generation/` 或 `WrittenExam/` |
| `*.py`（答案／模板） | `assessments/.../Practical*/` |
| `*.txt`、`*.json`（樣本資料） | `assessments/.../` |
| `vibe_spec.md`、草稿 `.md` | `assessments/.../` |
| `Reference/` | `resources/reference/` |
| `_student_submissions/` | `assessments/.../PracticalAssessment/` |

## 路徑替換清單（搬移後）

```
Subjects/S5-ICT/past-papers/2025-2026/Term 02/_generation
  → Subjects/S5-ICT/assessments/2025-2026/Term 02/_generation

Subjects/S5-ICT/past-papers/2024-2025/Term 02/_generation
  → Subjects/S5-ICT/assessments/2024-2025/Term 02/_generation

Subjects/S5-ICT/past-papers/2024-2025/Term 02/_reference
  → Subjects/S5-ICT/assessments/2024-2025/Term 02/_reference

Subjects/S3-CMP/exam-input
  → Subjects/S3-CMP/assessments/exam-input

Subjects/TechEd/15_Booklist_materialPlanning
  → Subjects/TechEd/booklist-material-planning

Subjects/S3-CMP/past-papers/Reference
  → Subjects/S3-CMP/resources/reference
```

## S5 ICT 出卷預設路徑

```
Subjects/S5-ICT/assessments/{YYYY-YYYY}/Term 02/_generation/
  exam_blueprint.json
  25_26_S5_ICT_Exam02.spec.json
  regenerate_exam02.py

Subjects/S5-ICT/past-papers/{YYYY-YYYY}/Term 02/WrittenExam/
  *.docx / *.pdf   ← 交付終稿
```

入口：`shared-tools/paper-generator/build_f5_exam02.py`

## Panel pull 規則

`pull-from-panel.ps1`：

- 試卷終稿 → `past-papers/{year}/Term {NN}/{category}/`
- 未分類素材（`_assets`）→ `assessments/{year}/Term {NN}/_assets/`

## 掃描指令（PowerShell）

```powershell
# 錯放於 past-papers 的非終稿檔
Get-ChildItem Subjects -Recurse -File |
  Where-Object {
    $_.FullName -match '\\past-papers\\' -and
    $_.FullName -notmatch '\\DSE-ICT\\' -and
    $_.Extension -notin '.pdf','.docx','.doc'
  } | Select-Object FullName

# 底線工作資料夾仍在 past-papers 內
Get-ChildItem Subjects -Recurse -Directory |
  Where-Object {
    $_.FullName -match '\\past-papers\\' -and
    $_.Name -match '^_|^exam-input$|^Reference$'
  } | Select-Object FullName
```

## 完成後檢查

- [ ] `NAV.md` 反映新專案／科目路徑
- [ ] `Subjects/README.md`、`STORAGE.md` 與實際結構一致
- [ ] `shared-tools` 預設路徑可執行（抽查 `build_f5_exam02.py --help`）
- [ ] `.gitignore` 含 `output/`
- [ ] 無具名學生大量提交被新增至 commit
