# Administrative

行政區（依功能／專案建立子資料夾）。主要原則：**專案互相獨立**、**流程可重用**、**敏感資料不入 git**。

這裡放：
- 資料流程定義（輸入/輸出 schema）
- 自動化工具的工作流（runbook）
- 範本與產出（按私隱規範處理）

## 導航

- 校內（CHW）常用專案集中：`Administrative/CHW/`（見 `Administrative/CHW/README.md`）
- 科組教學行政（選書等）：`Subjects/TechEd/`
- 藝術科會議紀錄：`Administrative/ART/`（generated → `_generation/`）

## 與科組 S: 的關係

Panel 共用資料夾 `S:\...\08_Others` 內的行政類內容（例：`1_Agenda_Minutes/`、`0_Plan_and_Report/`、`_3_Official_Forms/`）可對應到此區，但：

- **成績表**（`03_Marksheets/`）— 只留 S:，**禁止 commit 入 git**
- 其他行政檔 — 按需要拉入 repo；詳見 [Subjects/STORAGE.md](../Subjects/STORAGE.md)

## Administrative

Administrative workspace organized by domain (e.g., `Student-Records`, `Procurement`).

- Use structured inputs and shared-tools to generate consistent documents and reports.
- Store sensitive data locally and avoid unnecessary duplication.
- Panel share sync rules: see [Subjects/STORAGE.md](../Subjects/STORAGE.md).
