---
name: student-report-guides
description: 中一至中六成績表入分、計分、出核對稿流程。Use when the user asks about 成績表、下學期入分、比重滿分、stpGenerateReport、核對稿、退學生 flgTerm2、或 student-report 操作步驟。
---

# 成績表操作指引（Skill）

**一律先讀專案內指引，勿憑記憶臆測步驟。**

## 入口

| 範圍 | 路徑 |
|------|------|
| 總覽（含可同步步驟） | `Administrative/CHW/student-report/guides/0_總覽_中一至中五下學期成績表流程.md` |
| 逐步指引 | `Administrative/CHW/student-report/guides/1_` … `9_`、`10_行政分工_下學期時序與聯絡.md`、`3b_內聯網開放入分與權限.md` |
| 中六 | `Administrative/CHW/student-report/guides/6S_中六下學期成績表重新生成指引.md` |
| 表關係 | `Administrative/CHW/student-report/reference/STUDENT_REPORT_SQL_TABLE_RELATIONSHIPS.md` |
| 中一至中六 中/英/數分組 ↔ `auxiliaryClass` | `Administrative/CHW/student-report/reference/CEM_GROUPING_EXCEL_TO_AUXILIARY_CLASS.md` |
| SQL 腳本 | `Administrative/CHW/student-report/sql/` |
| Python 工具 | `shared-tools/student-report/` |
| 歷年檔案／核對稿 | 校內 `T:\{學年}\ITAdmin_13_StudentReport\`（不入 git） |

## 骨幹順序（不可跳）

1. 學期旗標／退學（`flgTerm2`）→ 2. 比重滿分 → 3. 入分 → 5. 計分 → 6. `tblZStudentReport2` → 7. Word/PDF

## 常見要點

- **各科總分怎樣計**：見 `2_檢查_下學期比重與滿分.md` 內「計分方法」— `R`/`E`/`O` 由 `Calculate Score_special_edition.sql` 寫入 `tblZStudentRank2`，成績表讀 `section='O'`
- **內聯網開放入分**：`3b_內聯網開放入分與權限.md` — `tblFormInputControl.flgActiveSubject` + 群組 7 `Score Input Users` + `studentNet/report/`
- **NULL vs 0**：見 `3_入分_同事輸入與資料表.md`「NULL 與 0 點入」— 分數只有豁免／缺席用 NULL，其餘用 **0**；態度比唔到（如長缺）先 NULL
- 步驟 1 與步驟 2「比重／滿分」檢查可同步；學生缺分檢查要等退學旗標改好
- 改來源表後要重做 5→6（快照唔會自動更新）
- 中六用 `tblZStudentReport_S456`，唔係 `tblZStudentReport2`

## MCP

查改 legacy 庫時用 `mssql-mcp-legacy-execute` skill；寫入前確認學年與是否定稿。
