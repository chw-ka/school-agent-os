USE [db25_26];
GO

/*
S6 report mail-merge data generation, 2025-2026 Term 2.

Word master found:
T:\25-26\ITAdmin_13_StudentReport\_Program\Copies\2026_03_24_S6_??????\MasterCopies\25_26_S6ReportDraft.doc

SQL source scripts:
T:\25-26\ITAdmin_13_StudentReport\_Program\SQL Scripts\06 Make Reports\_Report_2014_S456.sql
T:\25-26\ITAdmin_13_StudentReport\_Program\SQL Scripts\06 Make Reports\Report_S6_special_edition.sql

The mail-merge data table is dbo.tblZStudentReport_S456.
*/

-- 1. Regenerate S6 Term 2 report rows.
EXEC dbo.stpGenerateReport_S456_2014 6, 2;
GO

-- 2. S6 special post-processing copied from Report_S6_special_edition.sql.
--    If all component papers are absent, show absent at the subject aggregate row.
UPDATE dbo.tblZStudentReport_S456
SET Sbj01_2 = N'???'
WHERE form = 6
  AND Term_EName = 2
  AND Sbj02_2 = N'????'
  AND Sbj03_2 = N'????'
  AND Sbj04_2 = N'????'
  AND Sbj05_2 = N'????';
GO

UPDATE dbo.tblZStudentReport_S456
SET Sbj07_2 = N'???'
WHERE form = 6
  AND Term_EName = 2
  AND Sbj08_2 = N'????'
  AND Sbj09_2 = N'????';
GO

-- 3. Student not issued report draft: clear score/attendance/rank display fields.
UPDATE dbo.tblZStudentReport_S456
SET ave3 = '--', CRank3 = '--', FRank3 = '--',
    Sbj01_3 = '', Sbj02_3 = '', Sbj03_3 = '', Sbj04_3 = '', Sbj05_3 = '',
    Sbj06_3 = '', Sbj07_3 = '', Sbj08_3 = '', Sbj09_3 = '', Sbj10_3 = '',
    Sbj11_3 = '', Sbj12_3 = '', Sbj13_3 = '', Sbj14_3 = '', Sbj15_3 = '',
    Sbj16_3 = '', Sbj17_3 = '', Sbj18_3 = '', Sbj19_3 = '', Sbj20_3 = '',
    Sbj21_3 = '', Sbj22_3 = '', Sbj23_3 = '', Sbj24_3 = '', Sbj25_3 = '',
    Sbj26_3 = '', Sbj27_3 = '',
    Lsn_01 = '', Asm_01 = '', Lsn_02 = '', Asm_02 = '', Lsn_03 = '', Asm_03 = '',
    Lsn_04 = '', Asm_04 = '', Lsn_05 = '', Asm_05 = '', Lsn_06 = '', Asm_06 = '',
    Lsn_07 = '', Asm_07 = '', Lsn_08 = '', Asm_08 = '', Lsn_09 = '', Asm_09 = '',
    Lsn_10 = '', Asm_10 = '', Lsn_11 = '', Asm_11 = '', Lsn_12 = '', Asm_12 = '',
    Lsn_13 = '', Asm_13 = '', Lsn_14 = '', Asm_14 = '', Lsn_15 = '', Asm_15 = '',
    Lsn_16 = '', Asm_16 = '', Lsn_17 = '', Asm_17 = '', Lsn_18 = '', Asm_18 = '',
    Lsn_19 = '', Asm_19 = '', Lsn_20 = '', Asm_20 = ''
WHERE form = 6
  AND Term_EName = 2
  AND idStudent IN (20078);
GO

-- 4. Mail-merge record source for Word.
SELECT *
FROM dbo.tblZStudentReport_S456
WHERE form = 6
  AND term = 2
ORDER BY Class, Num;
