---
name: mssql-mcp-legacy-execute
description: >-
  Runs read-only or write T-SQL via the project MCP mssql-legacy (execute_sql) against CHW legacy SQL Server. Documents reliable query patterns so result grids return consistently (single-statement batches, no fragile multi-batch). Use when the agent uses MCP to query or update dbo tables, troubleshoot "rows affected -1", or the user asks to fix MCP SQL output behavior.
---

# MSSQL legacy MCP (`execute_sql`) — reliable usage

## When this applies

- Project **`.cursor/mcp.json`** starts `python -m mssql_mcp_server.server` (mssql-legacy).
- Target database is **legacy SQL Server** (e.g. **2005-style**): see `Administrative/CHW/student-report/reference/STUDENT_REPORT_SQL_TABLE_RELATIONSHIPS.md`.

## Relationship to other rules

- **AGENTS.md** still requires **full T-SQL in chat** for the user to run in **SSMS** on important work—MCP is a **helper**, not a substitute for copy-paste scripts when the user expects them.
- This skill only governs **how to call `execute_sql`** so previews and post-checks **actually show up** in the agent UI.

## What `Rows affected: -1` means

- It is **not** an error by itself. It often appears for **SELECT** or when row counts are not reported.
- If you see **only** `Rows affected: -1` **and no column/row output**, the usual causes are:
  1. **Empty result set** (0 rows)—some clients show almost nothing for empty grids.
  2. **Multiple statements in one `query` string**—the MCP/client may not surface all result sets reliably.

## Golden rules (follow these every time)

### 1) Use **exactly one SQL statement** per `execute_sql` call

- **Project rule:** every MCP `execute_sql` call must contain only **one** SQL statement. Do not combine preview, backup, update, and verify in one call.
- **Bad (fragile):** `DECLARE @id …; SELECT …;` as two batches in one string.
- **Good:** one `SELECT` that joins `tblStudent` / filters by `class` + `numberClass` instead of variables.
- For data changes, split work into separate calls: one backup/read statement, one update statement, one verify statement.

Example (resolve class inline):

```sql
SELECT s.idStudent, COUNT(*) AS matches
FROM dbo.tblStudent s
JOIN dbo.tblYSLPAchievement ach ON ach.idStudent = s.idStudent
JOIN dbo.tblYSLPActivity act ON act.idActivity = ach.idActivity
WHERE s.class = N'6A' AND s.numberClass = 6
  AND ISNULL(ach.flgActive, 1) = 1
  AND ISNULL(act.flgActive, 1) = 1
GROUP BY s.idStudent;
```

### 2) If you must preview **and** update in MCP

- Do not combine preview and update in one MCP call.
- Use separate calls: (a) preview or backup `SELECT`, (b) one `UPDATE`, (c) post-check `SELECT`.

### 3) Avoid features that confuse old servers or drivers

- **SQL Server 2005:** no `OFFSET/FETCH`; no `DECLARE @x int = 1` inline initialization—use `DECLARE` then `SET` in SSMS scripts; in **single-statement MCP calls**, avoid `DECLARE` entirely.
- Keep Unicode literals as **`N'…'`** where needed.

### 4) Always surface “empty or not” explicitly

- If a filter might return 0 rows, run a **`SELECT COUNT(*) AS c …`** (single statement) so the user always sees a number.

### 5) After killing the MCP Python process

- Cursor must **reload** (or restart MCP) so `execute_sql` reconnects; expect **`Not connected`** until then.

## Quick checklist before sending `execute_sql`

| Check | Reason |
|--------|--------|
| Exactly one `SELECT` or one `UPDATE` per call | Matches project rule and maximizes chance the grid appears |
| No unnecessary `SET NOCOUNT ON` in tiny probes | Easier to see default row messages when debugging |
| `ISNULL(flgActive,1)=1` when user asked for active-only | Matches YSLP conventions |
| Join path: **achievement → activity** for student-linked rows | Matches student-report table docs |

## Optional: restart stuck MCP (Windows)

From PowerShell (find then kill `python.exe` whose command line contains `mssql_mcp_server`), then **reload Cursor window**. Only do this when the tool repeatedly returns no result sets despite valid single-statement `SELECT 1`.

## Reference

- Student report table semantics: `Administrative/CHW/student-report/reference/STUDENT_REPORT_SQL_TABLE_RELATIONSHIPS.md`
