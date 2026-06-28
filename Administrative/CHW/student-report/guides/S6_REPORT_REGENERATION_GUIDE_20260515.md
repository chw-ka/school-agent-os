# S6 Report Regeneration Guide

> **中文指引（建議優先閱讀）**：[`6S_中六下學期成績表重新生成指引.md`](./6S_中六下學期成績表重新生成指引.md)  
> **中六郵件合併 SQL**：[`../export/6S_中六郵件合併_2526下學期.sql`](../export/6S_中六郵件合併_2526下學期.sql)  
> **中一至中五流程**：[`0_總覽_中一至中五下學期成績表流程.md`](./0_總覽_中一至中五下學期成績表流程.md)

Date: 2026-05-15

## Purpose

This note documents how to regenerate the S6 report mail-merge data for future use.
It was written after investigating why 6C02 still showed 上課表現 / 功課考勤 in the generated report data even though `tblStudentAttitude` had already been cleared.

## Key Files

Word mail-merge master:

```text
T:\25-26\ITAdmin_13_StudentReport\_Program\Copies\2026_03_24_S6_成績表核對稿\MasterCopies\25_26_S6ReportDraft.doc
```

Main SQL file to use:

```text
T:\25-26\ITAdmin_13_StudentReport\_Program\SQL Scripts\06 Make Reports\Report_S6_special_edition.sql
```

Stored procedure source:

```text
T:\25-26\ITAdmin_13_StudentReport\_Program\SQL Scripts\06 Make Reports\_Report_2014_S456.sql
```

Mail-merge data table:

```sql
dbo.tblZStudentReport_S456
```

## Important Finding

`tblZStudentReport_S456` is a generated snapshot table.

Changing source tables such as `tblStudentAttitude` does not automatically update the Word mail-merge data. The S6 report rows must be regenerated.

For 6C02:

- Student: 6C02 蔡凱玥
- `idStudent`: `20061`
- Source table `dbo.tblStudentAttitude` had already been cleared:
  - `lesson_2 = NULL`
  - `assessment_2 = NULL`
- But `dbo.tblZStudentReport_S456` still had old generated values in `Lsn_*` / `Asm_*`.

This happened because the report snapshot was generated before the attitude values were cleared.

## Why Regeneration Clears 6C02

The stored procedure `stpGenerateReport_S456_2014 6, 2` deletes and rebuilds the S6 term 2 rows:

```sql
DELETE
FROM tblZStudentReport_S456
WHERE form = @form AND term = @term
```

Then it recalculates `Lsn_*` and `Asm_*` from `tblStudentAttitude`.

In `_Report_2014_S456.sql`, the relevant logic is:

```sql
CASE WHEN sa.lesson_2 is null
     THEN ''
     ELSE sa.lesson_2 + N'　' + a3.nameChinese
END

CASE WHEN sa.assessment_2 is null
     THEN ''
     ELSE sa.assessment_2 + N'　' + a4.nameChinese
END
```

Therefore, after the source table has `NULL`, regenerating the report should make the corresponding `Lsn_*` / `Asm_*` fields blank.

## SQL Range To Run

Open:

```text
T:\25-26\ITAdmin_13_StudentReport\_Program\SQL Scripts\06 Make Reports\Report_S6_special_edition.sql
```

Run only from:

```sql
-- Sub Program Call

stpGenerateReport_S456_2014 6, 2
Go
```

Through the end of the existing 6D15 special-case update:

```sql
where idStudent in (20078) and Term_EName = 2 and form = 6
```

Do not run the older commented-out special cases below:

```sql
-- 處理分卷全數缺席時，考試分總分轉為缺席
-- CHI
```

Those lines are historical notes / commented special cases and are not needed for normal regeneration.

## Why Not Run Only The Bottom UPDATEs

Do not run only the `UPDATE tblZStudentReport_S456 ...` special-case statements.

Those statements only patch specific cases after generation. They do not rebuild the `Lsn_*` / `Asm_*` fields from `tblStudentAttitude`.

The critical line is:

```sql
stpGenerateReport_S456_2014 6, 2
```

Without this line, `tblZStudentReport_S456` remains the old snapshot.

## Post-Regeneration Checks

Check all S6 report rows:

```sql
SELECT *
FROM dbo.tblZStudentReport_S456
WHERE form = 6
  AND term = 2
ORDER BY Class, Num;
```

Check 6C02 specifically:

```sql
SELECT Class, Num, CName,
       Lsn_01, Asm_01,
       Lsn_07, Asm_07,
       Lsn_16, Asm_16,
       Lsn_18, Asm_18
FROM dbo.tblZStudentReport_S456
WHERE form = 6
  AND term = 2
  AND idStudent = 20061;
```

Expected result for 6C02 after regeneration:

- The relevant 上課表現 (`Lsn_*`) fields should be blank.
- The relevant 功課考勤 (`Asm_*`) fields should be blank.

## Existing Special Case

The current S6 special-edition SQL contains one active student-level cleanup:

```sql
where idStudent in (20078) and Term_EName = 2 and form = 6
```

This is for:

- `idStudent`: `20078`
- Class/number: 6D15

It clears total score, average, class rank, form rank, and lesson/assessment attitude fields for that student.

6C02 is not included in that special-case cleanup because 6C02 should be handled by regenerating from `tblStudentAttitude`, where the source fields have already been set to `NULL`.

## Encoding Warning

Use the original T-drive SQL file when running Chinese string updates.

Avoid using copied/exported SQL if Chinese literals appear as `???`, because that indicates an encoding loss and may corrupt Chinese matching/update values.

