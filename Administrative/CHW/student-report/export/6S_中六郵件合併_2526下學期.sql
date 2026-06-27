USE [db25_26];
GO

/*
中六成績表郵件合併資料 — 2025-2026 下學期

Word 主檔（校內 T 碟）：
T:\25-26\ITAdmin_13_StudentReport\_Program\Copies\2026_03_24_S6_成績表核對稿\MasterCopies\25_26_S6ReportDraft.doc

程序與特殊個案來源（請以 T 碟原始檔為準，避免中文亂碼）：
...\SQL Scripts\06 Make Reports\_Report_2014_S456.sql
...\SQL Scripts\06 Make Reports\Report_S6_special_edition.sql

郵件合併資料表：dbo.tblZStudentReport_S456

操作說明：guides/6S_中六下學期成績表重新生成指引.md
*/

-- 1. 重新生成中六下學期成績表列
EXEC dbo.stpGenerateReport_S456_2014 6, 2;
GO

-- 2. 特殊後處理：分卷全數缺席時，科目總分欄顯示缺席（摘自 Report_S6_special_edition.sql）
UPDATE dbo.tblZStudentReport_S456
SET Sbj01_2 = N'　缺席'
WHERE form = 6
  AND Term_EName = 2
  AND Sbj02_2 = N'　　缺席'
  AND Sbj03_2 = N'　　缺席'
  AND Sbj04_2 = N'　　缺席'
  AND Sbj05_2 = N'　　缺席';
GO

UPDATE dbo.tblZStudentReport_S456
SET Sbj07_2 = N'　缺席'
WHERE form = 6
  AND Term_EName = 2
  AND Sbj08_2 = N'　　缺席'
  AND Sbj09_2 = N'　　缺席';
GO

-- 3. 不獲發成績表核對稿：清空總分、名次、態度等顯示欄（idStudent 20078 / 6D15）
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

-- 4. 供 Word 郵件合併使用的查詢結果
SELECT *
FROM dbo.tblZStudentReport_S456
WHERE form = 6
  AND term = 2
ORDER BY Class, Num;
