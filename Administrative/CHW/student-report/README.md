## Student report（成績表）

對應原專案 `chw-student-report-old`（已併入本 repo）。

### 快速入口

| 用途 | 路徑 |
|------|------|
| 流程總覽 | [`guides/0_總覽_中一至中五下學期成績表流程.md`](guides/0_總覽_中一至中五下學期成績表流程.md) |
| 逐步指引 | [`guides/`](guides/) |
| 表關係 | [`reference/STUDENT_REPORT_SQL_TABLE_RELATIONSHIPS.md`](reference/STUDENT_REPORT_SQL_TABLE_RELATIONSHIPS.md) |
| SQL 腳本 | [`sql/`](sql/) |
| 中六郵件合併等 | [`export/`](export/) |
| Python 工具 | [`../../shared-tools/student-report/`](../../shared-tools/student-report/) |
| Agent skill | [`.cursor/skills/student-report-guides/`](../../../.cursor/skills/student-report-guides/) |

### 校內資料（不入 git）

歷年工作檔、核對稿 PDF、Datafile Excel 等存放於校內磁碟，例如：

```
T:\25-26\ITAdmin_13_StudentReport\
├── _Program\SQL Scripts\     ← 與 sql/ 目錄結構相同
├── Datafile\25_26_Term2\
├── _Program\Copies\          ← 核對稿
└── _Program\Summaries\connection.txt
```

Python 工具預設讀寫 `T:\25-26\...`；在家工作時需 VPN／遠端存取 T:，或將當年 Datafile 複製到本機再改 CLI 參數。

### 2525–26 一次性腳本

[`scripts/2025-2026/`](scripts/2025-2026/) — 體育女班科獎等；成績表完成後可刪。
