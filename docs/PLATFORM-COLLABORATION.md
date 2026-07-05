# Platform + Personal：同事共建 school-agent-os

> **狀態：** Phase 2 進行中 — `_platform/` submodule 已接入（2026-07-05）；platform repo 待 push 至 GitHub。  
> **目的：** 記錄如何與教不同科目、做不同行政工作的同事共建，而唔需要所有人共用同一個 monolithic repo。

## 問題

同事之間：

- 教的科目、級別不同（`Subjects/` 內容完全唔同）
- 行政專案不同（`Administrative/` 內容完全唔同）
- 但希望 **共建** 可重用基建：tools、skills、部分 rules

**結論：** 唔應逼所有人 share 同一個 repo 嘅全部內容；應拆成 **平台層（共建）** 同 **個人／科組層（自用）**。

## 目標架構（將來）

```
┌─────────────────────────────────────┐
│  school-agent-os-platform (共建)     │
│  shared-tools/  templates/          │
│  .cursor/skills/ (通用)             │
│  .cursor/rules/ (通用)              │
│  .cursorrules (憲法)                │
└──────────────┬──────────────────────┘
               │ submodule / subtree / sync
     ┌─────────┼─────────┐
     ▼         ▼         ▼
  同事 A      同事 B      你 (Tech)
  personal    personal    personal
  repo        repo        repo
  Subjects/   Subjects/   Subjects/
  Admin/…     Admin/…     Admin/CHW
  本地 skills 本地 skills 本地 skills
```

現有 repo 已隱含此分野（例如 `Administrative/CHW/` vs `Administrative/ART/`），將來只是把「平台 vs 個人」推到 **git repo 層面**。

## 平台 repo（大家共建、定期 pull）

| 內容 | 例子 |
|------|------|
| `shared-tools/` | `paper-formatter`、`data-processor`、`pdf-engine` |
| `templates/` | 學校格式 DOCX 範本 |
| 通用 skills | `meeting-minutes`、`_template`、`tidy-up`（通用版） |
| 通用 rules | 私隱、Tool First、文件格式（新細明體 12pt） |
| `.cursorrules` | 「憲法」— 唔涉及具體科目路徑或個人 S: 路徑 |

**入 platform 門檻：**

- 工具有 CLI + README；輸入輸出明確（JSON／檔案路徑）
- Skill 跟 `.cursor/skills/_template/` 結構
- 唔好放學生資料、成績、或綁死單一科組路徑
- 用 tag 版本（如 `v0.2.0`），方便個人 repo pin 版本

## 個人／科組 repo（每人自己管）

| 內容 | 例子 |
|------|------|
| `Subjects/` | 自己教的科、級別 |
| `Administrative/` | 自己負責的行政專案 |
| 專用 skills | `generate-f5-ict-exam`、`qef-elearning-grant` |
| 專用 rules | `subjects-workspace.mdc`（科目命名、資料夾慣例） |
| `NAV.md` | 自己的工作索引 |
| 本地設定 | S: panel 路徑、`.env`、學校 API（見 `.env.example`） |

**唔 share：** 成績表、具名學生作業、bulk 提交、科組專用行政草稿（除非同事主動提煉成通用 skill）。

## Skills 分類（現有 repo 對照）

| 適合將來放 platform | 留喺個人 repo |
|----------------------|---------------|
| `meeting-minutes` | `generate-f5-ict-exam` |
| `_template` | `qef-elearning-grant` |
| `tidy-up`（通用版） | `panel-storage-sync`（需參數化後才可上 platform） |

`panel-storage-sync` 現綁死 Tech 科 `S:\...\08_Others`。要上 platform，需改為讀每人 repo 內的本地 config（例如 `STORAGE.local.md`）。

## Rules 分類

| Platform（always apply） | Personal（globs 限定） |
|--------------------------|-------------------------|
| 私隱：唔 commit 成績、學生資料 | 科目 workspace 命名（如 `subjects-workspace.mdc`） |
| Tool First、Infrastructure > Prompt | Panel share 路徑（每科唔同） |
| 學校文件格式標準 | 行政專案子資料夾結構 |
| 唔寫 S: 除非用戶明確批准 | |

## 個人 repo 點樣「接」platform（將來揀一種）

### 1. Git submodule（已採用）

```
school-agent-os/              ← personal repo（你而家嘅 repo）
├── _platform/                ← submodule → school-agent-os-platform
├── shared-tools/             ← symlink → _platform/shared-tools
├── templates/                ← symlink → _platform/templates
├── .cursor/skills/           ← 個人 skills + platform skills（symlink）
├── Subjects/
└── Administrative/
```

設定步驟：[PLATFORM-SETUP.md](PLATFORM-SETUP.md)

### 2. Git subtree

定期 `git subtree pull`；可附 `sync-platform.ps1` 俾唔熟 git 的同事。

### 3. Cursor multi-root workspace（最易試用）

同時開 `school-agent-os-platform` 同 `school-agent-os-{name}` 兩個 folder；唔使即刻搞 submodule。

### 4. pip package（工具成熟後）

`shared-tools` 變可安裝套件；個人 repo 只留 spec、素材、skills。非第一步。

## 共建治理

1. **Platform 要有人 merge**（maintainer）；個人 repo 各自擁有。
2. **通用改動** → PR 去 platform；**科目 workflow** → 自己 repo，成熟後先提煉。
3. **版本 pin**：個人 repo 記低用緊 platform 邊個 tag，避免 breaking change。
4. **私隱底線**（全 repo 通用）：學生個人資料、成績只本地處理，唔入 platform，唔入 git。

## 實施路線（僅規劃，未開始）

| 階段 | 做咩 | 現狀 |
|------|------|------|
| **Phase 1** | 單 repo 內分清「平台區」vs「個人區」 | **完成** |
| **Phase 2** | 抽出 `school-agent-os-platform` repo；本 repo 以 `_platform/` submodule + symlink 接入 | **進行中**（本機 platform repo 已建；待 push GitHub） |
| **Phase 3** | GitHub org + template personal repo；`CONTRIBUTING.md` | 未做 |

## 例子：藝術科同事

可能只需要：

- **Platform：** `meeting-minutes` skill；通用文件排版工具（如有需要）
- **Personal：** `Administrative/ART/`、`Subjects/…`（如有）；自己 S: 路徑與 rules
- **唔需要：** `qef-elearning-grant`、`generate-f5-ict-exam`、DSE ICT 題庫鏈

現有 `Administrative/ART/` 已是個人／科組層嘅雛形。

## 相關文件

- [.cursorrules](../.cursorrules) — Infrastructure > Prompt、Tool First
- [.cursor/README.md](../.cursor/README.md) — rules / skills 索引
- [shared-tools/README.md](../shared-tools/README.md) — 可共用 CLI
- [Subjects/STORAGE.md](../Subjects/STORAGE.md) — git vs panel share（現為 Tech 科路徑）
- [Administrative/README.md](../Administrative/README.md) — 行政區「專案互相獨立」原則
