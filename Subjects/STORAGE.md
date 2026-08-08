# Teaching Material Storage

教學素材存放策略 — 配合 **家中無 S: 網絡** 及 **科組共用資料夾** 兩個環境。

## 兩層存放

| 層級 | 位置 | 用途 |
|------|------|------|
| **A — 可攜工作區** | 本 repo（GitHub） | 家中、學校皆可；Agent 與工具主要在此工作 |
| **B — 科組共用** | `S:\02_Teaching and Learning\03_Key Learning Areas\Technology\08_Others` | 僅學校網絡；給同科老師查閱；歷史檔案庫 |

```
                    ┌─────────────────┐
  家中（無 S:）      │  git pull/push  │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  school-agent-os │
                    │  Subjects/ …     │
                    └────────┬────────┘
                             │ 在校時可選
                    ┌────────▼────────┐
                    │  S: 08_Others    │  ← 發佈終稿予科組（須批准）
                    └─────────────────┘
```

## 甚麼放 Git、甚麼留 S:

### 應 commit 入 repo（家中要用）

- 近 1–2 年 `past-papers/`（**教師定稿**校內試卷、實作評估 — 人手修改後版本）
- 本學期正在用的 `notes/`
- `DSE-ICT/` 官方卷、EDB 文件、題庫 JSON
- 出卷工作區 `assessments/`（含 `exam-input/`、`source/`、`_generation/`、`**/*.spec.json` — **只留 git，不發佈去 S:**）

**重要：** `paper-generator` / `paper-formatter` 產出嘅 DOCX 係 **generated draft**，預設放 `assessments/…/_generation/`。**唔好**當作 `past-papers/` 終稿；只有教師人手定稿後先移至 `past-papers/`。

### 只留 S:（不要 bulk 入 git）

- `03_Marksheets/` — **成績表（私隱，禁止入 git）**
- `_2_Past_PanelFolderBackup_2003-2019` — 五萬多個舊檔
- `_6_SBA/`、整個 `_5_Resources/` — 除非個別檔案需要在家用
- 大型媒體 — 已在 `.gitignore`（`*.mp4`, `*.zip`, `*.apk`, `*.aia`）

### 學生作業／提交

- 批改用可暫存 workspace，**避免**把大量具名學生作品 commit 入 git
- 科組分享用副本可放 S:（用戶批准後）

## 路徑對照（精簡）

Panel 根目錄：`S:\02_Teaching and Learning\03_Key Learning Areas\Technology\08_Others`

| Panel | Repo |
|-------|------|
| `{year}/05_Test_and_Exam_Paper/S2CMP/` | `Subjects/S2-CMP/past-papers/{year}/` |
| `{year}/06_NotesLibrary/S3_CMP/` | `Subjects/S3-CMP/notes/` |
| `_4_HKEAA_Paper/ICT/` | `Subjects/DSE-ICT/past-papers/` |
| `_1_EDB_Documents/` | `Subjects/DSE-ICT/edb/` |

完整對照表：`.qoder/skills/panel-storage-sync/mapping.md`

## 科目工作區結構

```
Subjects/
├── S2-CMP/          assessments/, past-papers/, notes/, resources/
├── S3-CMP/
├── S5-ICT/
├── S6-ICT/
├── TechEd/          booklist-material-planning/ 等科組行政
└── DSE-ICT/         past-papers/, edb/, question-bank/  ← F4–F6 共用
```

`assessments/`（工作區，只留 git）：

```
{YYYY-YYYY}/Term {01|02}/_generation|_reference|_assets|WrittenExam|PracticalAssessment|…
exam-input/
```

`past-papers/`（終稿庫，可發佈至 S:）：

```
{YYYY-YYYY}/Term {01|02}/WrittenExam|PracticalAssessment|PracticalMock/
```

檔名：`{YY}_{YY}_S3_CMP_Term01_...`（方便工具辨識）

## 日常工作流

### 在校 — 拉入 repo（為家中準備）

1. 從 S: 複製**需要的**檔案 → 對應 `Subjects/…` 路徑
2. `git add` → commit → push
3. **不要**刪除或移動 S: 上的原檔

### 在家

1. `git pull` 後只在 repo 內工作
2. 完成後 commit + push
3. 若缺 S: 獨有檔案 — 回校後再拉入 repo

### 在校 — 發佈予科組

1. **必須先經用戶批准** 才可複製去 S:
2. 只發佈**終稿**（`.docx` / `.pdf` / 教師筆記）
3. 目標例：`{year}/05_Test_and_Exam_Paper/S5ICT/` 或 `06_NotesLibrary/…`

## Agent 規則摘要

- 未經批准 **不得** 寫入 S:
- **不得** 將成績、學生個資 commit 入 git
- `_generation/`、`*.spec.json` 只留 git
- 詳見 Cursor skill：`panel-storage-sync`

## 離校前 checklist

- [ ] 本週需要的 S: 參考已拉入 `Subjects/…`
- [ ] 已 `git push`
- [ ] 若有科組共用終稿 — 已獲批准並複製至 S:
