---
name: tidy-up
description: >-
  Audits and reorganizes school-agent-os folder structure: separates assessments
  working drafts from past-papers finals, fixes naming, relocates misplaced files,
  and updates path references in tools and docs. Use when the user asks to tidy
  up, reorganize folders, fix naming, clean past-papers, or align repo layout
  with NAV.md and Subjects/STORAGE.md.
---

# Tidy Up（Repo 結構整理）

## 目標

使 repo 符合「**工作區 vs 終稿庫**」分離原則，便於查找、跨年度沿用，以及與同事分享文件。

**索引：** [NAV.md](../../../NAV.md)  
**教學存放策略：** [Subjects/STORAGE.md](../../../Subjects/STORAGE.md)  
**Panel 對照：** [panel-storage-sync/mapping.md](../panel-storage-sync/mapping.md)

## 快速決策（檔案應放邊）

| 類型 | 目標路徑 | 可否發佈 S: |
|------|----------|-------------|
| 終稿試卷 `.pdf` / `.docx` | `past-papers/{YYYY-YYYY}/Term {01\|02}/WrittenExam\|Practical*` | 是（須批准） |
| `_generation/`、`*.spec.json`、blueprint | `assessments/.../_generation/` | 否 |
| `exam-input/`、答案腳本 `.py` | `assessments/` | 否 |
| 任務素材、樣本 `.txt/.json/.xml/.png` | `assessments/.../_assets/` | 否 |
| 參考卷、樣本卷 | `resources/reference/` | 視需要 |
| 學生提交、批改暫存 | `assessments/.../_student_submissions/` | **勿 bulk commit** |
| 工具暫存、逐字稿草稿 | `output/`（已在 `.gitignore`） | 否 |
| 校務專案 | `Administrative/CHW/{project}/` | 視需要 |
| 科組選書等 | `Subjects/TechEd/booklist-material-planning/` | 視需要 |
| DSE 官方卷、題庫 | `Subjects/DSE-ICT/` | 參考庫，結構不變 |

完整分類表見 [reference.md](reference.md)。

## 執行流程

```
進度：
- [ ] 1. 掃描：找出放錯位置或命名不一致的項目
- [ ] 2. 搬移：git mv（保留歷史）
- [ ] 3. 更新：工具／skills／README 內路徑引用
- [ ] 4. 驗證：past-papers 僅剩終稿類副檔名
- [ ] 5. 文件：書面語 README；必要時更新 NAV.md
```

### Step 1 — 掃描

在 `Subjects/` 下搜尋常見錯放：

```text
past-papers/**/_generation
past-papers/**/_reference
past-papers/**/_assets
past-papers/**/_student_submissions
past-papers/**/*.spec.json
past-papers/**/*.py
past-papers/**/Reference
exam-input/          # 應在 assessments/exam-input/
15_*                 # 舊式資料夾前綴
```

行政區：確認 CHW 專案在 `Administrative/CHW/`，勿與 `Subjects/TechEd/` 混放。

### Step 2 — 搬移

- 使用 **`git mv`**，鏡像原學期路徑：`past-papers/...` → `assessments/...`
- 建立目標父資料夾後再搬移
- `Reference/` → `resources/reference/`
- 資料夾命名：`booklist-material-planning`（kebab-case）；評核類別統一 `PracticalAssessment`（勿用 `Practical`）

### Step 3 — 更新路徑引用

搬移 `_generation` 後，搜尋並更新：

```text
past-papers/.../_generation  →  assessments/.../_generation
S3-CMP/exam-input             →  S3-CMP/assessments/exam-input
15_Booklist_materialPlanning  →  booklist-material-planning
```

重點檔案：

- `shared-tools/paper-generator/*.py`（預設 `_DEFAULT_GEN` 路徑）
- `.cursor/skills/generate-f5-ict-*/`
- `.cursor/rules/subjects-workspace.mdc`、`paper-generator.mdc`
- `Subjects/*/README.md`、`STORAGE.md`
- `.cursor/skills/panel-storage-sync/scripts/pull-from-panel.ps1`（`_assets` → `assessments/`）

### Step 4 — 驗證

`past-papers/` 內應 primarily 為 `.pdf`、`.docx`、`.doc`。若仍有 `.py`、`.spec.json`、`_generation`，繼續搬至 `assessments/`。

```powershell
Get-ChildItem Subjects -Recurse -File |
  Where-Object { $_.FullName -match 'past-papers' -and $_.Extension -notin '.pdf','.docx','.doc' }
```

例外：`DSE-ICT/past-papers/` 為官方參考庫，勿按校內試卷規則重構。

### Step 5 — 文件

- 新增或更新之 `README.md`、規範文件：**書面語**（可分享同事）
- 與用戶對話可用口語；**docs 用書面語**
- 新科目工作區補 `assessments/README.md` 簡述用途

## 命名規範

| 項目 | 規範 |
|------|------|
| 科目工作區 | `S{form}-{CMP\|ICT}`（例：`S3-CMP`） |
| 學年 | `{YYYY-YYYY}` |
| 學期資料夾 | `Term 01`、`Term 02`（空格 + 兩位數） |
| 評核類別 | `WrittenExam`、`PracticalAssessment`、`PracticalMock`、`PracticalExam` |
| 試卷檔名 | `{YY}_{YY}_S{form}_{SUBJ}_...` |
| 子專案資料夾 | kebab-case（例：`booklist-material-planning`） |

## 禁止事項

- 勿將成績表、具名學生作品 bulk commit
- 勿寫入 panel share `S:\...\08_Others`（除非用戶明確批准）
- 勿把 `_generation` 或 `*.spec.json` 發佈為「終稿」
- 勿在未更新工具路徑前只搬檔案

## 相關技能

- **panel-storage-sync** — 從 S: 拉入／發佈終稿
- **generate-f5-ict-exam** — S5 出卷（產物寫入 `assessments/.../_generation/`）

詳細對照與搬移範例見 [reference.md](reference.md).
