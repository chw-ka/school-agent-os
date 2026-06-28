------------------------------------------------------------------------------------------------
-- stpInitializeTestReport
------------------------------------------------------------------------------------------------

if exists (select * from dbo.sysobjects where id = object_id(N'[dbo].[stpInitializeTestReport]') and OBJECTPROPERTY(id, N'IsProcedure') = 1)
drop procedure [dbo].[stpInitializeTestReport]
GO

CREATE PROCEDURE dbo.stpInitializeTestReport
@form tinyint, @test tinyint
AS

if exists (select * from tempdb..sysobjects where name = '##tblResultRow')
drop table [tempdb].[dbo].[##tblResultRow]

CREATE TABLE [dbo].[##tblResultRow] (
	[idRow] [smallint] IDENTITY (1, 1) NOT NULL,
	[idStudent] [int] NOT NULL,
	[row] [smallint] NOT NULL,
	[idSubject] [char] (3) NOT NULL,
	[flgScore] [char] (3) NOT NULL,
	[Sbj_EName] [nvarchar] (50) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	[Sbj_CName] [nvarchar] (50) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	[Sbj_1] [nvarchar] (10) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	[Sbj_2] [nvarchar] (10) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	[Sbj_3] [nvarchar] (10) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	[Lsn] [nvarchar] (10) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
	[Asm] [nvarchar] (10) COLLATE SQL_Latin1_General_CP1_CI_AS NOT NULL,
) ON [PRIMARY]

DELETE
FROM tblZStudentTestReport
WHERE form = @form AND term = @test

GO

------------------------------------------------------------------------------------------------
-- stpOutputTestReport
------------------------------------------------------------------------------------------------

if exists (select * from dbo.sysobjects where id = object_id(N'[dbo].[stpOutputTestReport]') and OBJECTPROPERTY(id, N'IsProcedure') = 1)
drop procedure [dbo].[stpOutputTestReport]
GO

CREATE PROCEDURE dbo.stpOutputTestReport
@form tinyint, @test tinyint
AS

--Master
INSERT tblZStudentTestReport (term, Class, Num, form, idStudent, CName, EName, Gender, StuID, CTeacher)
SELECT @test, s.class, right('0' + convert(nvarchar (2), numberClass), 2), @form, s.idStudent, s.nameChinese, s.nameEnglish, s.gender, right('0000' + convert(nvarchar (5), s.idStudent), 5), s2.nameChinese + N'¦Ñ®v'
FROM tblStudent s
INNER JOIN tblStaffClass sc ON s.class = sc.class AND flgHead = 1
INNER JOIN tblStaff s2 ON sc.idStaff = s2.idStaff
WHERE idStudent IN (
SELECT distinct s.idStudent
FROM tblStudent s
INNER JOIN tblClass c ON s.class = c.class AND c.form = @form
INNER JOIN tblForm f ON c.form = f.form
INNER JOIN tblStudentSubject ss ON s.idStudent = ss.idStudent
WHERE flgTerm1 = 1
)
ORDER BY s.class, numberClass

--Result
UPDATE tblZStudentTestReport SET Sbj01_EName = Sbj_EName, Sbj01_CName = Sbj_CName, Sbj01_1 = Sbj_1, Sbj01_2 = Sbj_2, Sbj01_3 = Sbj_3, Lsn_01 = Lsn, Asm_01 = Asm FROM tblZStudentTestReport zsr, ##tblResultRow rr WHERE term = @test AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 1
UPDATE tblZStudentTestReport SET Sbj02_EName = Sbj_EName, Sbj02_CName = Sbj_CName, Sbj02_1 = Sbj_1, Sbj02_2 = Sbj_2, Sbj02_3 = Sbj_3, Lsn_02 = Lsn, Asm_02 = Asm FROM tblZStudentTestReport zsr, ##tblResultRow rr WHERE term = @test AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 2
UPDATE tblZStudentTestReport SET Sbj03_EName = Sbj_EName, Sbj03_CName = Sbj_CName, Sbj03_1 = Sbj_1, Sbj03_2 = Sbj_2, Sbj03_3 = Sbj_3, Lsn_03 = Lsn, Asm_03 = Asm FROM tblZStudentTestReport zsr, ##tblResultRow rr WHERE term = @test AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 3
UPDATE tblZStudentTestReport SET Sbj04_EName = Sbj_EName, Sbj04_CName = Sbj_CName, Sbj04_1 = Sbj_1, Sbj04_2 = Sbj_2, Sbj04_3 = Sbj_3, Lsn_04 = Lsn, Asm_04 = Asm FROM tblZStudentTestReport zsr, ##tblResultRow rr WHERE term = @test AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 4
UPDATE tblZStudentTestReport SET Sbj05_EName = Sbj_EName, Sbj05_CName = Sbj_CName, Sbj05_1 = Sbj_1, Sbj05_2 = Sbj_2, Sbj05_3 = Sbj_3, Lsn_05 = Lsn, Asm_05 = Asm FROM tblZStudentTestReport zsr, ##tblResultRow rr WHERE term = @test AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 5
UPDATE tblZStudentTestReport SET Sbj06_EName = Sbj_EName, Sbj06_CName = Sbj_CName, Sbj06_1 = Sbj_1, Sbj06_2 = Sbj_2, Sbj06_3 = Sbj_3, Lsn_06 = Lsn, Asm_06 = Asm FROM tblZStudentTestReport zsr, ##tblResultRow rr WHERE term = @test AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 6
UPDATE tblZStudentTestReport SET Sbj07_EName = Sbj_EName, Sbj07_CName = Sbj_CName, Sbj07_1 = Sbj_1, Sbj07_2 = Sbj_2, Sbj07_3 = Sbj_3, Lsn_07 = Lsn, Asm_07 = Asm FROM tblZStudentTestReport zsr, ##tblResultRow rr WHERE term = @test AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 7
UPDATE tblZStudentTestReport SET Sbj08_EName = Sbj_EName, Sbj08_CName = Sbj_CName, Sbj08_1 = Sbj_1, Sbj08_2 = Sbj_2, Sbj08_3 = Sbj_3, Lsn_08 = Lsn, Asm_08 = Asm FROM tblZStudentTestReport zsr, ##tblResultRow rr WHERE term = @test AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 8
UPDATE tblZStudentTestReport SET Sbj09_EName = Sbj_EName, Sbj09_CName = Sbj_CName, Sbj09_1 = Sbj_1, Sbj09_2 = Sbj_2, Sbj09_3 = Sbj_3, Lsn_09 = Lsn, Asm_09 = Asm FROM tblZStudentTestReport zsr, ##tblResultRow rr WHERE term = @test AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 9
UPDATE tblZStudentTestReport SET Sbj10_EName = Sbj_EName, Sbj10_CName = Sbj_CName, Sbj10_1 = Sbj_1, Sbj10_2 = Sbj_2, Sbj10_3 = Sbj_3, Lsn_10 = Lsn, Asm_10 = Asm FROM tblZStudentTestReport zsr, ##tblResultRow rr WHERE term = @test AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 10
UPDATE tblZStudentTestReport SET Sbj11_EName = Sbj_EName, Sbj11_CName = Sbj_CName, Sbj11_1 = Sbj_1, Sbj11_2 = Sbj_2, Sbj11_3 = Sbj_3, Lsn_11 = Lsn, Asm_11 = Asm FROM tblZStudentTestReport zsr, ##tblResultRow rr WHERE term = @test AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 11
UPDATE tblZStudentTestReport SET Sbj12_EName = Sbj_EName, Sbj12_CName = Sbj_CName, Sbj12_1 = Sbj_1, Sbj12_2 = Sbj_2, Sbj12_3 = Sbj_3, Lsn_12 = Lsn, Asm_12 = Asm FROM tblZStudentTestReport zsr, ##tblResultRow rr WHERE term = @test AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 12
UPDATE tblZStudentTestReport SET Sbj13_EName = Sbj_EName, Sbj13_CName = Sbj_CName, Sbj13_1 = Sbj_1, Sbj13_2 = Sbj_2, Sbj13_3 = Sbj_3, Lsn_13 = Lsn, Asm_13 = Asm FROM tblZStudentTestReport zsr, ##tblResultRow rr WHERE term = @test AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 13
UPDATE tblZStudentTestReport SET Sbj14_EName = Sbj_EName, Sbj14_CName = Sbj_CName, Sbj14_1 = Sbj_1, Sbj14_2 = Sbj_2, Sbj14_3 = Sbj_3, Lsn_14 = Lsn, Asm_14 = Asm FROM tblZStudentTestReport zsr, ##tblResultRow rr WHERE term = @test AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 14
UPDATE tblZStudentTestReport SET Sbj15_EName = Sbj_EName, Sbj15_CName = Sbj_CName, Sbj15_1 = Sbj_1, Sbj15_2 = Sbj_2, Sbj15_3 = Sbj_3, Lsn_15 = Lsn, Asm_15 = Asm FROM tblZStudentTestReport zsr, ##tblResultRow rr WHERE term = @test AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 15
UPDATE tblZStudentTestReport SET Sbj16_EName = Sbj_EName, Sbj16_CName = Sbj_CName, Sbj16_1 = Sbj_1, Sbj16_2 = Sbj_2, Sbj16_3 = Sbj_3, Lsn_16 = Lsn, Asm_16 = Asm FROM tblZStudentTestReport zsr, ##tblResultRow rr WHERE term = @test AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 16
UPDATE tblZStudentTestReport SET Sbj17_EName = Sbj_EName, Sbj17_CName = Sbj_CName, Sbj17_1 = Sbj_1, Sbj17_2 = Sbj_2, Sbj17_3 = Sbj_3, Lsn_17 = Lsn, Asm_17 = Asm FROM tblZStudentTestReport zsr, ##tblResultRow rr WHERE term = @test AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 17
UPDATE tblZStudentTestReport SET Sbj18_EName = Sbj_EName, Sbj18_CName = Sbj_CName, Sbj18_1 = Sbj_1, Sbj18_2 = Sbj_2, Sbj18_3 = Sbj_3, Lsn_18 = Lsn, Asm_18 = Asm FROM tblZStudentTestReport zsr, ##tblResultRow rr WHERE term = @test AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 18
UPDATE tblZStudentTestReport SET Sbj19_EName = Sbj_EName, Sbj19_CName = Sbj_CName, Sbj19_1 = Sbj_1, Sbj19_2 = Sbj_2, Sbj19_3 = Sbj_3, Lsn_19 = Lsn, Asm_19 = Asm FROM tblZStudentTestReport zsr, ##tblResultRow rr WHERE term = @test AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 19
UPDATE tblZStudentTestReport SET Sbj20_EName = Sbj_EName, Sbj20_CName = Sbj_CName, Sbj20_1 = Sbj_1, Sbj20_2 = Sbj_2, Sbj20_3 = Sbj_3, Lsn_20 = Lsn, Asm_20 = Asm FROM tblZStudentTestReport zsr, ##tblResultRow rr WHERE term = @test AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 20
UPDATE tblZStudentTestReport SET Sbj21_EName = Sbj_EName, Sbj21_CName = Sbj_CName, Sbj21_1 = Sbj_1, Sbj21_2 = Sbj_2, Sbj21_3 = Sbj_3, Lsn_21 = Lsn, Asm_21 = Asm FROM tblZStudentTestReport zsr, ##tblResultRow rr WHERE term = @test AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 21
UPDATE tblZStudentTestReport SET Sbj22_EName = Sbj_EName, Sbj22_CName = Sbj_CName, Sbj22_1 = Sbj_1, Sbj22_2 = Sbj_2, Sbj22_3 = Sbj_3, Lsn_22 = Lsn, Asm_22 = Asm FROM tblZStudentTestReport zsr, ##tblResultRow rr WHERE term = @test AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 22
UPDATE tblZStudentTestReport SET Sbj23_EName = Sbj_EName, Sbj23_CName = Sbj_CName, Sbj23_1 = Sbj_1, Sbj23_2 = Sbj_2, Sbj23_3 = Sbj_3, Lsn_23 = Lsn, Asm_23 = Asm FROM tblZStudentTestReport zsr, ##tblResultRow rr WHERE term = @test AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 23
UPDATE tblZStudentTestReport SET Sbj24_EName = Sbj_EName, Sbj24_CName = Sbj_CName, Sbj24_1 = Sbj_1, Sbj24_2 = Sbj_2, Sbj24_3 = Sbj_3, Lsn_24 = Lsn, Asm_24 = Asm FROM tblZStudentTestReport zsr, ##tblResultRow rr WHERE term = @test AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 24
UPDATE tblZStudentTestReport SET Sbj25_EName = Sbj_EName, Sbj25_CName = Sbj_CName, Sbj25_1 = Sbj_1, Sbj25_2 = Sbj_2, Sbj25_3 = Sbj_3, Lsn_25 = Lsn, Asm_25 = Asm FROM tblZStudentTestReport zsr, ##tblResultRow rr WHERE term = @test AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 25
UPDATE tblZStudentTestReport SET Sbj26_EName = Sbj_EName, Sbj26_CName = Sbj_CName, Sbj26_1 = Sbj_1, Sbj26_2 = Sbj_2, Sbj26_3 = Sbj_3, Lsn_26 = Lsn, Asm_26 = Asm FROM tblZStudentTestReport zsr, ##tblResultRow rr WHERE term = @test AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 26
UPDATE tblZStudentTestReport SET Sbj27_EName = Sbj_EName, Sbj27_CName = Sbj_CName, Sbj27_1 = Sbj_1, Sbj27_2 = Sbj_2, Sbj27_3 = Sbj_3, Lsn_27 = Lsn, Asm_27 = Asm FROM tblZStudentTestReport zsr, ##tblResultRow rr WHERE term = @test AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 27

GO

------------------------------------------------------------------------------------------------
-- stpGenerateTestReport
------------------------------------------------------------------------------------------------

if exists (select * from dbo.sysobjects where id = object_id(N'[dbo].[stpGenerateTestReport]') and OBJECTPROPERTY(id, N'IsProcedure') = 1)
drop procedure [dbo].[stpGenerateTestReport]
GO

CREATE PROCEDURE dbo.stpGenerateTestReport
@form tinyint, @test tinyint
AS

EXEC stpInitializeTestReport @form, @test

-- Result
IF @test = 1 
BEGIN
	INSERT ##tblResultRow (idStudent, row, idSubject, flgScore, Sbj_EName, Sbj_CName, Sbj_1, Sbj_2, Sbj_3, Lsn, Asm)
	SELECT s.idStudent, 0,
	su.idSubject,
	CASE WHEN flgScore is null THEN 1 ELSE flgScore END,
	su.nameEnglish,
	su.nameChinese,
	CASE WHEN score_1 is null THEN '--'
	ELSE CASE WHEN score_1 < 495 THEN N'(' + convert(nvarchar(6), convert(decimal(7,0), score_1 / 10.0)) + CASE WHEN flgRemark_1 = 1 THEN N'*' ELSE N'' END + N')' ELSE  ' ' + convert(nvarchar(6), convert(decimal(7,0), score_1 / 10.0)) + CASE WHEN flgRemark_1 = 1 THEN N'*' ELSE N'' END END
	END AS result_1,
	CASE WHEN score_2 is null THEN '--'
	ELSE CASE WHEN score_2 < 495 THEN N'(' + convert(nvarchar(6), convert(decimal(7,0), score_2 / 10.0)) + CASE WHEN flgRemark_2 = 1 THEN N'*' ELSE N'' END + N')' ELSE  ' ' + convert(nvarchar(6), convert(decimal(7,0), score_2 / 10.0)) + CASE WHEN flgRemark_2 = 1 THEN N'*' ELSE N'' END END
	END AS result_2,
	'--' AS result_final,
	'--', '--'
	FROM tblStudent s
	INNER JOIN tblClass c ON s.class = c.class
	INNER JOIN tblForm f ON c.form = f.form  AND f.form = @form
	INNER JOIN tblStudentSubject ss ON s.idStudent = ss.idStudent
	INNER JOIN tblSubject su ON su.idSubject = ss.idSubject
	INNER JOIN tblPaper p ON p.formGroup = f.formGroup AND ss.idSubject = p.idPaper
	INNER JOIN (
	SELECT sps.idStudent, p.idSubject, sps.idPaper,
	floor(1000.0 * sps.score_test_1 / fpr.score_test_1) as score_1, flgRemark_1,
	floor(1000.0 * sps.score_test_2 / fpr.score_test_2) as score_2, flgRemark_2,
	null as score_final
	FROM tblStudent s
	INNER JOIN tblClass c ON s.class = c.class AND c.form = @form
	INNER JOIN tblForm f ON c.form = f.form
	INNER JOIN tblStudentPaperScore sps ON sps.idStudent = s.idStudent
	INNER JOIN tblFormPaperScore fpr ON fpr.form = f.form AND fpr.idPaper = sps.idPaper
	INNER JOIN tblPaper p ON p.idPaper = sps.idPaper AND p.formGroup = f.formGroup AND p.flgscore = 1
	WHERE sps.score_test_1 is not null or sps.score_test_2 is not null 
	) r ON r.idStudent = s.idStudent AND ss.idSubject = r.idSubject
	ORDER BY s.class, s.numberClass, p.keyOrder
END
ELSE
BEGIN
	INSERT ##tblResultRow (idStudent, row, idSubject, flgScore, Sbj_EName, Sbj_CName, Sbj_1, Sbj_2, Sbj_3, Lsn, Asm)
	SELECT s.idStudent, 0,
	su.idSubject,
	CASE WHEN flgScore is null THEN 1 ELSE flgScore END,
	su.nameEnglish,
	su.nameChinese,
	CASE WHEN score_1 is null THEN '--'
	ELSE CASE WHEN score_1 < 495 THEN N'(' + convert(nvarchar(6), convert(decimal(7,0), score_1 / 10.0)) + CASE WHEN flgRemark_1 = 1 THEN N'*' ELSE N'' END + N')' ELSE  ' ' + convert(nvarchar(6), convert(decimal(7,0), score_1 / 10.0)) + CASE WHEN flgRemark_1 = 1 THEN N'*' ELSE N'' END END
	END AS result_1,
	CASE WHEN score_2 is null THEN '--'
	ELSE CASE WHEN score_2 < 495 THEN N'(' + convert(nvarchar(6), convert(decimal(7,0), score_2 / 10.0)) + CASE WHEN flgRemark_2 = 1 THEN N'*' ELSE N'' END + N')' ELSE  ' ' + convert(nvarchar(6), convert(decimal(7,0), score_2 / 10.0)) + CASE WHEN flgRemark_2 = 1 THEN N'*' ELSE N'' END END
	END AS result_2,
	'--' AS result_final,
	CASE WHEN sa.lesson_1 is null THEN '--' ELSE sa.lesson_1 + N'¡@' + a1.nameChinese END,
	CASE WHEN sa.assessment_1 is null THEN '--' ELSE sa.assessment_1 + N'¡@' + a2.nameChinese END 
	FROM tblStudent s
	INNER JOIN tblClass c ON s.class = c.class
	INNER JOIN tblForm f ON c.form = f.form  AND f.form = @form
	INNER JOIN tblStudentSubject ss ON s.idStudent = ss.idStudent
	INNER JOIN tblSubject su ON su.idSubject = ss.idSubject
	INNER JOIN tblPaper p ON p.formGroup = f.formGroup AND ss.idSubject = p.idPaper
	INNER JOIN tblStudentAttitude sa ON s.idStudent = sa.idStudent AND su.idSubject = sa.idSubject
	LEFT JOIN tblAttitude a1 on sa.lesson_1 = a1.grade
	LEFT JOIN tblAttitude a2 on sa.assessment_1 = a2.grade
	LEFT JOIN (
	SELECT sps.idStudent, p.idSubject, sps.idPaper,
	floor(1000.0 * sps.score_test_1 / fpr.score_test_1) as score_1, flgRemark_1,
	floor(1000.0 * sps.score_test_2 / fpr.score_test_2) as score_2, flgRemark_2,
	null as score_final
	FROM tblStudent s
	INNER JOIN tblClass c ON s.class = c.class AND c.form = @form
	INNER JOIN tblForm f ON c.form = f.form
	INNER JOIN tblStudentPaperScore sps ON sps.idStudent = s.idStudent
	INNER JOIN tblFormPaperScore fpr ON fpr.form = f.form AND fpr.idPaper = sps.idPaper
	INNER JOIN tblPaper p ON p.idPaper = sps.idPaper AND p.formGroup = f.formGroup AND p.flgscore = 1
	WHERE sps.score_test_1 is not null or sps.score_test_2 is not null 
	UNION
	SELECT s.idStudent, p.idSubject, p.idPaper,
	null as score_1, '',
	null as score_2, '',
	null as score_final
	FROM tblStudent s
	INNER JOIN tblClass c ON s.class = c.class AND c.form = @form
	INNER JOIN tblForm f ON c.form = f.form
	INNER JOIN tblStudentSubject ss ON s.idStudent = ss.idStudent
	INNER JOIN tblPaper p ON ss.idSubject = p.idSubject AND p.formGroup = f.formGroup AND p.flgscore = 0
	) r ON r.idStudent = s.idStudent AND ss.idSubject = r.idSubject
	ORDER BY s.class, s.numberClass, p.keyOrder
END

UPDATE ##tblResultRow
SET row = tpr.idRow - r.min_row + 1
FROM ##tblResultRow tpr, (
SELECT idStudent, min(idRow) AS min_row
FROM ##tblResultRow
GROUP BY idStudent) r
WHERE r.idStudent = tpr.idStudent

exec stpOutputTestReport @form, @test

GO

------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------

stpGenerateTestReport 5, 2
GO

