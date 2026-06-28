------------------------------------------------------------------------------------------------
-- stpGenerateReport
------------------------------------------------------------------------------------------------

if exists (select * from dbo.sysobjects where id = object_id(N'[dbo].[stpGenerateReport]') and OBJECTPROPERTY(id, N'IsProcedure') = 1)
drop procedure [dbo].[stpGenerateReport_S123_2013]
GO

CREATE PROCEDURE dbo.stpGenerateReport_S123_2013
@form tinyint, @term tinyint
AS

------------------------------------------------------------------------------------------------
-- Initialize
------------------------------------------------------------------------------------------------

if exists (select * from tempdb..sysobjects where name = '##tblResultRow')
drop table [tempdb].[dbo].[##tblResultRow]

--PRINT 'A'

CREATE TABLE [dbo].[##tblResultRow] (
	[idRow] [smallint] IDENTITY (1, 1) NOT NULL,
	[idStudent] [int] NOT NULL,
	[row] [smallint] NOT NULL,
	[idSubject] [char] (3) NOT NULL,
	[flgScore] [char] (3) NOT NULL,
	[Sbj_EName] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[Sbj_CName] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[Sbj_1] [nvarchar] (10) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[Sbj_2] [nvarchar] (10) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[Sbj_3] [nvarchar] (10) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[Lsn] [nvarchar] (10) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[Asm] [nvarchar] (10) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
) ON [PRIMARY]

if exists (select * from tempdb..sysobjects where name = '##tblServiceRow')
drop table [tempdb].[dbo].[##tblServiceRow]

CREATE TABLE [dbo].[##tblServiceRow] (
	[idRow] [smallint] IDENTITY (1, 1) NOT NULL,
	[idStudent] [int] NOT NULL,
	[row] [smallint] NOT NULL,
	[srv] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL
) ON [PRIMARY]

if exists (select * from tempdb..sysobjects where name = '##tblIndRow')
drop table [tempdb].[dbo].[##tblIndRow]

CREATE TABLE [dbo].[##tblIndRow] (
	[idRow] [smallint] IDENTITY (1, 1) NOT NULL,
	[idStudent] [int] NOT NULL,
	[row] [smallint] NOT NULL,
	[ind] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[sep] [nvarchar] (1) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL
) ON [PRIMARY]

if exists (select * from tempdb..sysobjects where name = '##tblInd')
drop table [tempdb].[dbo].[##tblInd]

CREATE TABLE [dbo].[##tblInd] (
	[idStudent] [int] NOT NULL,
	[flgNewLine] [bit] NOT NULL,
	[ind01] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[ind02] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[ind03] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[ind04] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[ind05] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[ind06] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[ind07] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[ind08] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[ind09] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[ind10] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[ind11] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[ind12] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[ind13] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[ind14] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[ind15] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[ind16] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[ind17] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[ind18] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[ind19] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[ind20] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[sep01] [nvarchar] (1) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[sep02] [nvarchar] (1) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[sep03] [nvarchar] (1) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[sep04] [nvarchar] (1) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[sep05] [nvarchar] (1) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[sep06] [nvarchar] (1) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[sep07] [nvarchar] (1) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[sep08] [nvarchar] (1) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[sep09] [nvarchar] (1) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[sep10] [nvarchar] (1) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[sep11] [nvarchar] (1) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[sep12] [nvarchar] (1) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[sep13] [nvarchar] (1) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[sep14] [nvarchar] (1) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[sep15] [nvarchar] (1) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[sep16] [nvarchar] (1) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[sep17] [nvarchar] (1) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[sep18] [nvarchar] (1) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[sep19] [nvarchar] (1) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[sep20] [nvarchar] (1) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL
) ON [PRIMARY]

if exists (select * from tempdb..sysobjects where name = '##tblECARow')
drop table [tempdb].[dbo].[##tblECARow]

CREATE TABLE [dbo].[##tblECARow] (
	[idRow] [smallint] IDENTITY (1, 1) NOT NULL,
	[idStudent] [int] NOT NULL,
	[row] [smallint] NOT NULL,
	[eca] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL
) ON [PRIMARY]

if exists (select * from tempdb..sysobjects where name = '##tblECA')
drop table [tempdb].[dbo].[##tblECA]

CREATE TABLE [dbo].[##tblECA] (
	[idStudent] [int] NOT NULL,
	[flgNewLine] [bit] NOT NULL,
	[eca01] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[eca02] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[eca03] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[eca04] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[eca05] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[eca06] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[eca07] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[eca08] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[eca09] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[eca10] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[eca11] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[eca12] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL
) ON [PRIMARY]

if exists (select * from tempdb..sysobjects where name = '##tblAwardRow')
drop table [tempdb].[dbo].[##tblAwardRow]

CREATE TABLE [dbo].[##tblAwardRow] (
	[idRow] [smallint] IDENTITY (1, 1) NOT NULL,
	[idStudent] [int] NOT NULL,
	[row] [smallint] NOT NULL,
	[awd] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL
) ON [PRIMARY]

if exists (select * from tempdb..sysobjects where name = '##tblAward')
drop table [tempdb].[dbo].[##tblAward]

CREATE TABLE [dbo].[##tblAward] (
	[idStudent] [int] NOT NULL,
	[flgNewLine] [bit] NOT NULL,
	[awd01] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[awd02] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[awd03] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[awd04] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[awd05] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[awd06] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[awd07] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[awd08] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[awd09] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[awd10] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[awd11] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[awd12] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL
) ON [PRIMARY]

if exists (select * from tempdb..sysobjects where name = '##tblRemarkRow')
drop table [tempdb].[dbo].[##tblRemarkRow]

CREATE TABLE [dbo].[##tblRemarkRow] (
	[idRow] [smallint] IDENTITY (1, 1) NOT NULL,
	[idStudent] [int] NOT NULL,
	[row] [smallint] NOT NULL,
	[rem] [nvarchar] (100) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL
) ON [PRIMARY]

if exists (select * from tempdb..sysobjects where name = '##tblRemark')
drop table [tempdb].[dbo].[##tblRemark]

CREATE TABLE [dbo].[##tblRemark] (
	[idStudent] [int] NOT NULL,
	[flgNewLine] [bit] NOT NULL,
	[rem01] [nvarchar] (100) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[rem02] [nvarchar] (100) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[rem03] [nvarchar] (100) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[rem04] [nvarchar] (100) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[rem05] [nvarchar] (100) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[rem06] [nvarchar] (100) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[rem07] [nvarchar] (100) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[rem08] [nvarchar] (100) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[rem09] [nvarchar] (100) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[rem10] [nvarchar] (100) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[rem11] [nvarchar] (100) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[rem12] [nvarchar] (100) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL
) ON [PRIMARY]

--PRINT 'B'

DELETE
FROM tblZStudentReport2
WHERE form = @form AND term = @term

------------------------------------------------------------------------------------------------
-- Process
------------------------------------------------------------------------------------------------

--PRINT 'C'
-- KK 4-digit
-- Result
INSERT ##tblResultRow (idStudent, row, idSubject, flgScore, Sbj_EName, Sbj_CName, Sbj_1, Sbj_2, Sbj_3, Lsn, Asm)
SELECT 
	s.idStudent, 0, r.idSubject, p.flgScore,
	CASE WHEN r.idPaper = r.idSubject THEN '' ELSE N'　'  END + p.nameEnglish + CASE WHEN p.remarkEnglish is not null THEN ' (' + p.remarkEnglish + ')' ELSE '' END,
	CASE WHEN r.idPaper = r.idSubject THEN '' ELSE N'　'  END + p.nameChinese + CASE WHEN p.remarkChinese is not null THEN ' (' + p.remarkChinese + ')' ELSE '' END,
	N'　' + CASE WHEN r.idPaper = r.idSubject THEN '' ELSE N'　'  END + r.result_1,
	N'　' + CASE WHEN r.idPaper = r.idSubject THEN '' ELSE N'　'  END + r.result_2,
			r.result_final,
	CASE WHEN r.idPaper = r.idSubject THEN
		CASE WHEN @term = 1 THEN
			CASE WHEN sa.lesson_1 is null THEN '' ELSE sa.lesson_1 + N'　' + a1.nameChinese END
		ELSE
			CASE WHEN sa.lesson_2 is null THEN '' ELSE sa.lesson_2 + N'　' + a3.nameChinese END
		END
	ELSE ''
	END,
	CASE WHEN r.idPaper = r.idSubject THEN
		CASE WHEN @term = 1 THEN
			CASE WHEN sa.assessment_1 is null THEN '' ELSE sa.assessment_1 + N'　' + a2.nameChinese END
		ELSE
			CASE WHEN sa.assessment_2 is null THEN '' ELSE sa.assessment_2 + N'　' + a4.nameChinese END
		END
	ELSE ''
	END
FROM vwStudent s
INNER JOIN (
	SELECT sp.idStudent, sp.idPaper, sp.idSubject,
	CASE 
		WHEN zsr1.flgIgnore = 1 THEN N'豁免'
		ELSE 
			CASE WHEN sp.idSubject = sp.idPaper THEN
				CASE WHEN zsr1.score is null
				THEN ''
				ELSE 
					CASE WHEN zsr1.score < 4950 THEN N'(' + convert(nvarchar(6), convert(decimal(7,0), zsr1.score / 100.0)) + N')' ELSE  ' ' + convert(nvarchar(6), convert(decimal(7,0), zsr1.score / 100.0)) END
				END
			ELSE
				''
			END
	END AS result_1,
	CASE 
		WHEN zsr2.flgIgnore = 1 THEN N'豁免'
		WHEN zsr2.flgAbsent = 1 THEN N'缺席'
		ELSE 
			CASE WHEN zsr2.score is null 
			THEN ''
			ELSE 
				CASE WHEN zsr2.score < 4950 THEN N'(' + convert(nvarchar(6), convert(decimal(7,0), zsr2.score / 100.0)) + N')' ELSE  ' ' + convert(nvarchar(6), convert(decimal(7,0), zsr2.score / 100.0)) END
			END
	END AS result_2,
	CASE 
		WHEN zsr1.flgIgnore = 1 AND zsr2.flgIgnore = 1 THEN N''
		ELSE
			CASE WHEN sp.idSubject = sp.idPaper THEN
				CASE 
					WHEN zsr3.score is null THEN ''
					ELSE 
						CASE WHEN zsr3.score < 4950 THEN N'(' + convert(nvarchar(6), convert(decimal(7,0), zsr3.score / 100.0)) + N')' ELSE  ' ' + convert(nvarchar(6), convert(decimal(7,0), zsr3.score / 100.0)) END
				END
			ELSE
				''
			END
	END AS result_final
	FROM vwStudentPaper sp
	LEFT JOIN tblZStudentRank2 zsr1 ON sp.idStudent = zsr1.idStudent AND sp.idPaper = zsr1.idPaper AND zsr1.flgStandard = 0 AND zsr1.section = 'R' AND zsr1.term = @term 
	LEFT JOIN tblZStudentRank2 zsr2 ON sp.idStudent = zsr2.idStudent AND sp.idPaper = zsr2.idPaper AND zsr2.flgStandard = 0 AND zsr2.section = 'E' AND zsr2.term = @term 
	LEFT JOIN tblZStudentRank2 zsr3 ON sp.idStudent = zsr3.idStudent AND sp.idPaper = zsr3.idPaper AND zsr3.flgStandard = 0 AND zsr3.section = 'O' AND zsr3.term = @term 
	WHERE sp.flgScore = 1 AND sp.form = @form AND ((@term = 1 AND sp.flgTerm1 = 1) OR (@term = 2 AND sp.flgTerm2 = 1))
	UNION
	SELECT sp.idStudent, sp.idPaper, sp.idSubject,
	'', '',
	CASE WHEN @term = 1 THEN
		CASE
			WHEN sps.flgIgnore_1 = 1 or grade_exam_1 = '#' THEN N'豁免' 
			WHEN sps.flgAbsent_1 = 1 or grade_exam_1 is null THEN N'缺席'
			ELSE
				CASE WHEN grade_exam_1 = 'D' THEN '(' + grade_exam_1 + ')' ELSE ' ' + grade_exam_1 END
		END
	ELSE
		CASE 
			WHEN sps.flgIgnore_2 = 1 or grade_exam_2 = '#' THEN N'豁免' 
			WHEN sps.flgAbsent_2 = 1 or grade_exam_2 is null THEN N'缺席'
			ELSE
				CASE WHEN grade_exam_2 = 'D' THEN '(' + grade_exam_2 + ')' ELSE ' ' + grade_exam_2 END
		END
	END
	FROM vwStudentPaper sp
	LEFT JOIN tblStudentPaperScore sps ON sp.idStudent = sps.idStudent AND sp.idPaper = sps.idPaper
	WHERE sp.flgScore = 0 AND sp.idPaper <> 'OTH' AND sp.form = @form AND ((@term = 1 AND sp.flgTerm1 = 1) OR (@term = 2 AND sp.flgTerm2 = 1))
) r ON r.idStudent = s.idStudent
INNER JOIN tblPaper p ON p.idPaper = r.idPaper AND p.formGroup = s.formGroup
LEFT JOIN tblStudentAttitude sa ON s.idStudent = sa.idStudent AND r.idPaper = sa.idSubject
LEFT JOIN tblAttitude a1 on sa.lesson_1 = a1.grade
LEFT JOIN tblAttitude a2 on sa.assessment_1 = a2.grade
LEFT JOIN tblAttitude a3 on sa.lesson_2 = a3.grade
LEFT JOIN tblAttitude a4 on sa.assessment_2 = a4.grade
ORDER BY s.class, s.numberClass, p.keyOrder

UPDATE ##tblResultRow
SET row = tpr.idRow - r.min_row + 1
FROM ##tblResultRow tpr, (
SELECT idStudent, min(idRow) AS min_row
FROM ##tblResultRow
GROUP BY idStudent) r
WHERE r.idStudent = tpr.idStudent

UPDATE ##tblResultRow
SET row = row + 1
WHERE idSubject <> 'ENG'

UPDATE ##tblResultRow
SET row = row + 1
WHERE idSubject <> 'CHI' AND idSubject <> 'ENG'

UPDATE ##tblResultRow
SET row = row + 1
WHERE flgScore = 0

-- Added by CM 2014_02_25
-- 刪除基督教倫理科和電腦認知科平時分數顯示
UPDATE ##tblResultRow
set Sbj_1 = ''
WHERE idSubject in ('CES', 'CMP')

-- Service
--PRINT 'D'

INSERT ##tblServiceRow (idStudent, row, srv)
SELECT s.idStudent, 0, srv
FROM vwStudent s
INNER JOIN (
SELECT idStudent, cu.nameChinese + CASE WHEN p.idPost <> 101 THEN p.nameChinese ELSE '' END + CASE WHEN ecac.nameChinese is not null THEN char(13) + char(10) + '(' + ecac.nameChinese + ')' ELSE '' END AS srv, 2000 - p.keyOrder as src
FROM tblStudentClassPost scp
INNER JOIN tblClassUnit cu ON cu.idClassUnit = scp.idClassUnit
INNER JOIN tblPost p ON p.idPost = scp.idPost
LEFT JOIN tblECAComment ecac ON ecac.idComment = scp.idComment AND @term = 2
UNION
SELECT idStudent, s.nameChinese + N'科' + CASE WHEN p.idPost <> 101 THEN p.nameChinese ELSE '' END + CASE WHEN ecac.nameChinese is not null THEN char(13) + char(10) + '(' + ecac.nameChinese + ')' ELSE '' END AS srv, 3000 + s.keyOrder as src
FROM tblStudentSubjectPost ssp
INNER JOIN tblSubject s ON ssp.idSubject = s.idSubject
INNER JOIN tblPost p ON p.idPost = ssp.idPost
LEFT JOIN tblECAComment ecac ON ecac.idComment = ssp.idComment AND @term = 2
UNION
SELECT idStudent, u.nameChinese + CASE WHEN p.idPost <> 101 THEN p.nameChinese ELSE '' END + CASE WHEN ecac.nameChinese is not null THEN char(13) + char(10) + '(' + ecac.nameChinese + ')' ELSE '' END AS srv, 5000 - p.keyOrder as src
FROM tblStudentUnitPost sup
INNER JOIN tblUnit u ON u.idUnit = sup.idUnit
INNER JOIN tblPost p ON p.idPost = sup.idPost
LEFT JOIN tblECAComment ecac ON ecac.idComment = sup.idComment AND @term = 2
WHERE u.idUnitGroup = 7
) r ON s.idStudent = r.idStudent
WHERE s.form = @form
ORDER BY s.idStudent, r.src

UPDATE ##tblServiceRow
SET row = tpr.idRow - r.min_row + 1
FROM ##tblServiceRow tpr, (
SELECT idStudent, min(idRow) AS min_row
FROM ##tblServiceRow
GROUP BY idStudent) r
WHERE r.idStudent = tpr.idStudent

-- Ind Row
--PRINT 'E'

INSERT ##tblIndRow (idStudent, ind, sep, row)
SELECT sp.idStudent, p.nameChinese + convert(nvarchar(5), weight) as ind, ' ' as sep, p.keyOrder as keyKey
FROM vwStudentPaper sp 
INNER JOIN tblFormPaperWeight fpw ON sp.form = fpw.form AND sp.idPaper = fpw.idPaper AND fpw.weight > 0
INNER JOIN tblPaper p ON p.idPaper = fpw.idPaper AND p.formGroup = sp.formGroup
WHERE sp.form = @form AND sp.form < 6 AND sp.idSubject = sp.idPaper and ((sp.flgTerm1 = 1 and @term = 1) or (sp.flgTerm2 = 1 and @term = 2))
UNION
SELECT zsr.idStudent, N'( ) 表示不及格', N'　', 1000
FROM tblZStudentRank2 zsr
WHERE zsr.score < 495 AND zsr.form = @form AND zsr.flgStandard = 0 AND zsr.term = @term
UNION
SELECT sps.idStudent, N'( ) 表示不及格', N'　', 1000
FROM tblStudentPaperScore sps
INNER JOIN vwStudent s ON sps.idStudent = s.idStudent
WHERE s.form = @form AND ((@term = 1 AND grade_exam_1 = 'D') OR (@term = 2 AND grade_exam_2 = 'D'))
ORDER BY idStudent, keyKey

UPDATE ##tblIndRow
SET row = tir.idRow - r.min_row + 1
FROM ##tblIndRow tir, (
SELECT idStudent, min(idRow) AS min_row
FROM ##tblIndRow
GROUP BY idStudent) r
WHERE r.idStudent = tir.idStudent

--Ind
INSERT ##tblInd (idStudent, flgNewLine, ind01, ind02, ind03, ind04, ind05, ind06, ind07, ind08, ind09, ind10, ind11, ind12, ind13, ind14, ind15, ind16, ind17, ind18, ind19, ind20, sep01, sep02, sep03, sep04, sep05, sep06, sep07, sep08, sep09, sep10, sep11, sep12, sep13, sep14, sep15, sep16, sep17, sep18, sep19, sep20)
SELECT idStudent, 0, CASE WHEN @form < 6 THEN N'各科比重為：' ELSE '' END + ind, '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', sep, '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''
FROM ##tblIndRow
WHERE row = 1

UPDATE ##tblInd SET ind02 = ind, sep02 = sep FROM ##tblInd ind, ##tblIndRow indr WHERE ind.idStudent = indr.idStudent AND row = 2
UPDATE ##tblInd SET ind03 = ind, sep03 = sep FROM ##tblInd ind, ##tblIndRow indr WHERE ind.idStudent = indr.idStudent AND row = 3
UPDATE ##tblInd SET ind04 = ind, sep04 = sep FROM ##tblInd ind, ##tblIndRow indr WHERE ind.idStudent = indr.idStudent AND row = 4
UPDATE ##tblInd SET ind05 = ind, sep05 = sep FROM ##tblInd ind, ##tblIndRow indr WHERE ind.idStudent = indr.idStudent AND row = 5
UPDATE ##tblInd SET ind06 = ind, sep06 = sep FROM ##tblInd ind, ##tblIndRow indr WHERE ind.idStudent = indr.idStudent AND row = 6
UPDATE ##tblInd SET ind07 = ind, sep07 = sep FROM ##tblInd ind, ##tblIndRow indr WHERE ind.idStudent = indr.idStudent AND row = 7
UPDATE ##tblInd SET ind08 = ind, sep08 = sep FROM ##tblInd ind, ##tblIndRow indr WHERE ind.idStudent = indr.idStudent AND row = 8
UPDATE ##tblInd SET ind09 = ind, sep09 = sep FROM ##tblInd ind, ##tblIndRow indr WHERE ind.idStudent = indr.idStudent AND row = 9
UPDATE ##tblInd SET ind10 = ind, sep10 = sep FROM ##tblInd ind, ##tblIndRow indr WHERE ind.idStudent = indr.idStudent AND row = 10
UPDATE ##tblInd SET ind11 = ind, sep11 = sep FROM ##tblInd ind, ##tblIndRow indr WHERE ind.idStudent = indr.idStudent AND row = 11
UPDATE ##tblInd SET ind12 = ind, sep12 = sep FROM ##tblInd ind, ##tblIndRow indr WHERE ind.idStudent = indr.idStudent AND row = 12
UPDATE ##tblInd SET ind13 = ind, sep13 = sep FROM ##tblInd ind, ##tblIndRow indr WHERE ind.idStudent = indr.idStudent AND row = 13
UPDATE ##tblInd SET ind14 = ind, sep14 = sep FROM ##tblInd ind, ##tblIndRow indr WHERE ind.idStudent = indr.idStudent AND row = 14
UPDATE ##tblInd SET ind15 = ind, sep15 = sep FROM ##tblInd ind, ##tblIndRow indr WHERE ind.idStudent = indr.idStudent AND row = 15
UPDATE ##tblInd SET ind16 = ind, sep16 = sep FROM ##tblInd ind, ##tblIndRow indr WHERE ind.idStudent = indr.idStudent AND row = 16
UPDATE ##tblInd SET ind17 = ind, sep17 = sep FROM ##tblInd ind, ##tblIndRow indr WHERE ind.idStudent = indr.idStudent AND row = 17
UPDATE ##tblInd SET ind18 = ind, sep18 = sep FROM ##tblInd ind, ##tblIndRow indr WHERE ind.idStudent = indr.idStudent AND row = 18
UPDATE ##tblInd SET ind19 = ind, sep19 = sep FROM ##tblInd ind, ##tblIndRow indr WHERE ind.idStudent = indr.idStudent AND row = 19
UPDATE ##tblInd SET ind20 = ind, sep20 = sep FROM ##tblInd ind, ##tblIndRow indr WHERE ind.idStudent = indr.idStudent AND row = 20

UPDATE ##tblInd SET ind01 = ind01 + sep02 WHERE ind02 <> ''
UPDATE ##tblInd SET ind02 = ind02 + sep03 WHERE ind03 <> ''
UPDATE ##tblInd SET ind03 = ind03 + sep04 WHERE ind04 <> ''
UPDATE ##tblInd SET ind04 = ind04 + sep05 WHERE ind05 <> ''
UPDATE ##tblInd SET ind05 = ind05 + sep06 WHERE ind06 <> ''
UPDATE ##tblInd SET ind06 = ind06 + sep07 WHERE ind07 <> ''
UPDATE ##tblInd SET ind07 = ind07 + sep08 WHERE ind08 <> ''
UPDATE ##tblInd SET ind08 = ind08 + sep09 WHERE ind09 <> ''
UPDATE ##tblInd SET ind09 = ind09 + sep10 WHERE ind10 <> ''
UPDATE ##tblInd SET ind10 = ind10 + sep11 WHERE ind11 <> ''
UPDATE ##tblInd SET ind11 = ind11 + sep12 WHERE ind12 <> ''
UPDATE ##tblInd SET ind12 = ind12 + sep13 WHERE ind13 <> ''
UPDATE ##tblInd SET ind13 = ind13 + sep14 WHERE ind14 <> ''
UPDATE ##tblInd SET ind14 = ind14 + sep15 WHERE ind15 <> ''
UPDATE ##tblInd SET ind15 = ind15 + sep16 WHERE ind16 <> ''
UPDATE ##tblInd SET ind16 = ind16 + sep17 WHERE ind17 <> ''
UPDATE ##tblInd SET ind17 = ind17 + sep18 WHERE ind18 <> ''
UPDATE ##tblInd SET ind18 = ind18 + sep19 WHERE ind19 <> ''
UPDATE ##tblInd SET ind19 = ind19 + sep20 WHERE ind20 <> ''

UPDATE ##tblInd SET ind01 = ind01 + char(13) + char(10), flgNewLine = 1
WHERE flgNewLine = 0 AND len(ind01 + ind02) > 83
UPDATE ##tblInd SET ind02 = ind02 + char(13) + char(10), flgNewLine = 1
WHERE flgNewLine = 0 AND len(ind01 + ind02 + ind03) > 83
UPDATE ##tblInd SET ind03 = ind03 + char(13) + char(10), flgNewLine = 1
WHERE flgNewLine = 0 AND len(ind01 + ind02 + ind03 + ind04) > 83
UPDATE ##tblInd SET ind04 = ind04 + char(13) + char(10), flgNewLine = 1
WHERE flgNewLine = 0 AND len(ind01 + ind02 + ind03 + ind04 + ind05) > 83
UPDATE ##tblInd SET ind05 = ind05 + char(13) + char(10), flgNewLine = 1
WHERE flgNewLine = 0 AND len(ind01 + ind02 + ind03 + ind04 + ind05 + ind06) > 83
UPDATE ##tblInd SET ind06 = ind06 + char(13) + char(10), flgNewLine = 1
WHERE flgNewLine = 0 AND len(ind01 + ind02 + ind03 + ind04 + ind05 + ind06 + ind07) > 83
UPDATE ##tblInd SET ind07 = ind07 + char(13) + char(10), flgNewLine = 1
WHERE flgNewLine = 0 AND len(ind01 + ind02 + ind03 + ind04 + ind05 + ind06 + ind07 + ind08) > 83
UPDATE ##tblInd SET ind08 = ind08 + char(13) + char(10), flgNewLine = 1
WHERE flgNewLine = 0 AND len(ind01 + ind02 + ind03 + ind04 + ind05 + ind06 + ind07 + ind08 + ind09) > 83
UPDATE ##tblInd SET ind09 = ind09 + char(13) + char(10), flgNewLine = 1
WHERE flgNewLine = 0 AND len(ind01 + ind02 + ind03 + ind04 + ind05 + ind06 + ind07 + ind08 + ind09 + ind10) > 83
UPDATE ##tblInd SET ind10 = ind10 + char(13) + char(10), flgNewLine = 1
WHERE flgNewLine = 0 AND len(ind01 + ind02 + ind03 + ind04 + ind05 + ind06 + ind07 + ind08 + ind09 + ind10 + ind11) > 83
UPDATE ##tblInd SET ind11 = ind11 + char(13) + char(10), flgNewLine = 1
WHERE flgNewLine = 0 AND len(ind01 + ind02 + ind03 + ind04 + ind05 + ind06 + ind07 + ind08 + ind09 + ind10 + ind11 + ind12) > 83
UPDATE ##tblInd SET ind12 = ind12 + char(13) + char(10), flgNewLine = 1
WHERE flgNewLine = 0 AND len(ind01 + ind02 + ind03 + ind04 + ind05 + ind06 + ind07 + ind08 + ind09 + ind10 + ind11 + ind12 + ind13) > 83
UPDATE ##tblInd SET ind13 = ind13 + char(13) + char(10), flgNewLine = 1
WHERE flgNewLine = 0 AND len(ind01 + ind02 + ind03 + ind04 + ind05 + ind06 + ind07 + ind08 + ind09 + ind10 + ind11 + ind12 + ind13 + ind14) > 83
UPDATE ##tblInd SET ind14 = ind14 + char(13) + char(10), flgNewLine = 1
WHERE flgNewLine = 0 AND len(ind01 + ind02 + ind03 + ind04 + ind05 + ind06 + ind07 + ind08 + ind09 + ind10 + ind11 + ind12 + ind13 + ind14 + ind15) > 83
UPDATE ##tblInd SET ind15 = ind15 + char(13) + char(10), flgNewLine = 1
WHERE flgNewLine = 0 AND len(ind01 + ind02 + ind03 + ind04 + ind05 + ind06 + ind07 + ind08 + ind09 + ind10 + ind11 + ind12 + ind13 + ind14 + ind15 + ind16) > 83
UPDATE ##tblInd SET ind16 = ind16 + char(13) + char(10), flgNewLine = 1
WHERE flgNewLine = 0 AND len(ind01 + ind02 + ind03 + ind04 + ind05 + ind06 + ind07 + ind08 + ind09 + ind10 + ind11 + ind12 + ind13 + ind14 + ind15 + ind16 + ind17) > 83
UPDATE ##tblInd SET ind17 = ind17 + char(13) + char(10), flgNewLine = 1
WHERE flgNewLine = 0 AND len(ind01 + ind02 + ind03 + ind04 + ind05 + ind06 + ind07 + ind08 + ind09 + ind10 + ind11 + ind12 + ind13 + ind14 + ind15 + ind16 + ind17 + ind18) > 83
UPDATE ##tblInd SET ind18 = ind18 + char(13) + char(10), flgNewLine = 1
WHERE flgNewLine = 0 AND len(ind01 + ind02 + ind03 + ind04 + ind05 + ind06 + ind07 + ind08 + ind09 + ind10 + ind11 + ind12 + ind13 + ind14 + ind15 + ind16 + ind17 + ind18 + ind19) > 83
UPDATE ##tblInd SET ind19 = ind19 + char(13) + char(10), flgNewLine = 1
WHERE flgNewLine = 0 AND len(ind01 + ind02 + ind03 + ind04 + ind05 + ind06 + ind07 + ind08 + ind09 + ind10 + ind11 + ind12 + ind13 + ind14 + ind15 + ind16 + ind17 + ind18 + ind19 + ind20) > 83

-- ECA Row
--PRINT 'F'

INSERT ##tblECARow (idStudent, row, eca)
SELECT s.idStudent, 0,  replace(u.nameChinese + CASE WHEN p.idPost <> 101 THEN p.nameChinese ELSE '' END + CASE WHEN ecac.nameChinese is not null THEN '(' + ecac.nameChinese + ')' ELSE '' END, ' ', '') AS srv
FROM vwStudent s
INNER JOIN tblStudentUnitPost sup ON s.idStudent = sup.idStudent
INNER JOIN tblUnit u ON u.idUnit = sup.idUnit
INNER JOIN tblPost p ON p.idPost = sup.idPost
LEFT JOIN tblECAComment ecac ON ecac.idComment = sup.idComment AND @term = 2
WHERE s.form = @form and idUnitGroup not in (7, 9)
ORDER BY s.idStudent, p.keyOrder desc, sup.idUnit

UPDATE ##tblECARow
SET eca = replace(eca, N'(男)', '')

UPDATE ##tblECARow
SET eca = replace(eca, N'(女)', '')

UPDATE ##tblECARow
SET eca = replace(eca, N'(外)', '')

UPDATE ##tblECARow
SET eca = replace(eca, N'(內)', '')

UPDATE ##tblECARow
SET row = tpr.idRow - r.min_row + 1
FROM ##tblECARow tpr, (
SELECT idStudent, min(idRow) AS min_row
FROM ##tblECARow
GROUP BY idStudent) r
WHERE r.idStudent = tpr.idStudent

-- ECA
INSERT ##tblECA (idStudent, flgNewLine, eca01, eca02, eca03, eca04, eca05, eca06, eca07, eca08, eca09, eca10, eca11, eca12)
SELECT idStudent, 0, eca, '', '', '', '', '', '', '', '', '', '', ''
FROM ##tblECARow
WHERE row = 1

UPDATE ##tblECA SET eca02 = eca FROM ##tblECA eca, ##tblECARow ecar WHERE eca.idStudent = ecar.idStudent AND row = 2
UPDATE ##tblECA SET eca03 = eca FROM ##tblECA eca, ##tblECARow ecar WHERE eca.idStudent = ecar.idStudent AND row = 3
UPDATE ##tblECA SET eca04 = eca FROM ##tblECA eca, ##tblECARow ecar WHERE eca.idStudent = ecar.idStudent AND row = 4
UPDATE ##tblECA SET eca05 = eca FROM ##tblECA eca, ##tblECARow ecar WHERE eca.idStudent = ecar.idStudent AND row = 5
UPDATE ##tblECA SET eca06 = eca FROM ##tblECA eca, ##tblECARow ecar WHERE eca.idStudent = ecar.idStudent AND row = 6
UPDATE ##tblECA SET eca07 = eca FROM ##tblECA eca, ##tblECARow ecar WHERE eca.idStudent = ecar.idStudent AND row = 7
UPDATE ##tblECA SET eca08 = eca FROM ##tblECA eca, ##tblECARow ecar WHERE eca.idStudent = ecar.idStudent AND row = 8
UPDATE ##tblECA SET eca09 = eca FROM ##tblECA eca, ##tblECARow ecar WHERE eca.idStudent = ecar.idStudent AND row = 9
UPDATE ##tblECA SET eca10 = eca FROM ##tblECA eca, ##tblECARow ecar WHERE eca.idStudent = ecar.idStudent AND row = 10
UPDATE ##tblECA SET eca11 = eca FROM ##tblECA eca, ##tblECARow ecar WHERE eca.idStudent = ecar.idStudent AND row = 11
UPDATE ##tblECA SET eca12 = eca FROM ##tblECA eca, ##tblECARow ecar WHERE eca.idStudent = ecar.idStudent AND row = 12

UPDATE ##tblECA SET eca01 = eca01 + N'、' WHERE eca02 <> ''
UPDATE ##tblECA SET eca02 = eca02 + N'、' WHERE eca03 <> ''
UPDATE ##tblECA SET eca03 = eca03 + N'、' WHERE eca04 <> ''
UPDATE ##tblECA SET eca04 = eca04 + N'、' WHERE eca05 <> ''
UPDATE ##tblECA SET eca05 = eca05 + N'、' WHERE eca06 <> ''
UPDATE ##tblECA SET eca06 = eca06 + N'、' WHERE eca07 <> ''
UPDATE ##tblECA SET eca07 = eca07 + N'、' WHERE eca08 <> ''
UPDATE ##tblECA SET eca08 = eca08 + N'、' WHERE eca09 <> ''
UPDATE ##tblECA SET eca09 = eca09 + N'、' WHERE eca10 <> ''
UPDATE ##tblECA SET eca10 = eca10 + N'、' WHERE eca11 <> ''
UPDATE ##tblECA SET eca11 = eca11 + N'、' WHERE eca12 <> ''

UPDATE ##tblECA SET eca01 = eca01 + char(13) + char(10), flgNewLine = 1
WHERE flgNewLine = 0 AND len(eca01 + eca02) > 54
UPDATE ##tblECA SET eca02 = eca02 + char(13) + char(10), flgNewLine = 1
WHERE flgNewLine = 0 AND len(eca01 + eca02 + eca03) > 54
UPDATE ##tblECA SET eca03 = eca03 + char(13) + char(10), flgNewLine = 1
WHERE flgNewLine = 0 AND len(eca01 + eca02 + eca03 + eca04) > 54
UPDATE ##tblECA SET eca04 = eca04 + char(13) + char(10), flgNewLine = 1
WHERE flgNewLine = 0 AND len(eca01 + eca02 + eca03 + eca04 + eca05) > 54
UPDATE ##tblECA SET eca05 = eca05 + char(13) + char(10), flgNewLine = 1
WHERE flgNewLine = 0 AND len(eca01 + eca02 + eca03 + eca04 + eca05 + eca06) > 54
UPDATE ##tblECA SET eca06 = eca06 + char(13) + char(10), flgNewLine = 1
WHERE flgNewLine = 0 AND len(eca01 + eca02 + eca03 + eca04 + eca05 + eca06 + eca07) > 54
UPDATE ##tblECA SET eca07 = eca07 + char(13) + char(10), flgNewLine = 1
WHERE flgNewLine = 0 AND len(eca01 + eca02 + eca03 + eca04 + eca05 + eca06 + eca07 + eca08) > 54
UPDATE ##tblECA SET eca08 = eca08 + char(13) + char(10), flgNewLine = 1
WHERE flgNewLine = 0 AND len(eca01 + eca02 + eca03 + eca04 + eca05 + eca06 + eca07 + eca08 + eca09) > 54
UPDATE ##tblECA SET eca09 = eca09 + char(13) + char(10), flgNewLine = 1
WHERE flgNewLine = 0 AND len(eca01 + eca02 + eca03 + eca04 + eca05 + eca06 + eca07 + eca08 + eca09 + eca10) > 54
UPDATE ##tblECA SET eca10 = eca10 + char(13) + char(10), flgNewLine = 1
WHERE flgNewLine = 0 AND len(eca01 + eca02 + eca03 + eca04 + eca05 + eca06 + eca07 + eca08 + eca09 + eca10 + eca11) > 54
UPDATE ##tblECA SET eca11 = eca11 + char(13) + char(10), flgNewLine = 1
WHERE flgNewLine = 0 AND len(eca01 + eca02 + eca03 + eca04 + eca05 + eca06 + eca07 + eca08 + eca09 + eca10 + eca11 + eca12) > 54

--PRINT 'G'

IF @term = 2
BEGIN
	-- Award Row
	INSERT ##tblAwardRow (idStudent, row, awd)
	SELECT idStudent, 0, awd
	FROM (
	SELECT s.idStudent, sa.nameChinese as awd, sa.idRow as idRow
	FROM vwStudent s
	INNER JOIN tblStudentAward sa ON sa.idStudent = s.idStudent 
	WHERE sa.term = @term AND s.form = @form
	UNION
	SELECT s.idStudent, u.nameChinese + case p.idPost when 101 then '' else p.nameChinese end as awd, 100 as idRow
	from vwStudent s
	INNER JOIN tblStudentUnitPost sup ON sup.idStudent = s.idStudent
	INNER JOIN tblUnit u ON sup.idUnit = u.idUnit and idUnitGroup = 9
	INNER JOIN tblPost p ON sup.idPost = p.idPost
	WHERE s.form = @form
	) r
	ORDER BY idStudent, idRow

	UPDATE ##tblAwardRow
	SET row = tpr.idRow - r.min_row + 1
	FROM ##tblAwardRow tpr, (
	SELECT idStudent, min(idRow) AS min_row
	FROM ##tblAwardRow
	GROUP BY idStudent) r
	WHERE r.idStudent = tpr.idStudent

	--Award
	INSERT ##tblAward (idStudent, flgNewLine, awd01, awd02, awd03, awd04, awd05, awd06, awd07, awd08, awd09, awd10, awd11, awd12)
	SELECT idStudent, 0, awd, '', '', '', '', '', '', '', '', '', '', ''
	FROM ##tblAwardRow
	WHERE row = 1

	UPDATE ##tblAward SET awd02 = awd FROM ##tblAward awd, ##tblAwardRow awdr WHERE awd.idStudent = awdr.idStudent AND row = 2
	UPDATE ##tblAward SET awd03 = awd FROM ##tblAward awd, ##tblAwardRow awdr WHERE awd.idStudent = awdr.idStudent AND row = 3
	UPDATE ##tblAward SET awd04 = awd FROM ##tblAward awd, ##tblAwardRow awdr WHERE awd.idStudent = awdr.idStudent AND row = 4
	UPDATE ##tblAward SET awd05 = awd FROM ##tblAward awd, ##tblAwardRow awdr WHERE awd.idStudent = awdr.idStudent AND row = 5
	UPDATE ##tblAward SET awd06 = awd FROM ##tblAward awd, ##tblAwardRow awdr WHERE awd.idStudent = awdr.idStudent AND row = 6
	UPDATE ##tblAward SET awd07 = awd FROM ##tblAward awd, ##tblAwardRow awdr WHERE awd.idStudent = awdr.idStudent AND row = 7
	UPDATE ##tblAward SET awd08 = awd FROM ##tblAward awd, ##tblAwardRow awdr WHERE awd.idStudent = awdr.idStudent AND row = 8
	UPDATE ##tblAward SET awd09 = awd FROM ##tblAward awd, ##tblAwardRow awdr WHERE awd.idStudent = awdr.idStudent AND row = 9
	UPDATE ##tblAward SET awd10 = awd FROM ##tblAward awd, ##tblAwardRow awdr WHERE awd.idStudent = awdr.idStudent AND row = 10
	UPDATE ##tblAward SET awd11 = awd FROM ##tblAward awd, ##tblAwardRow awdr WHERE awd.idStudent = awdr.idStudent AND row = 11
	UPDATE ##tblAward SET awd12 = awd FROM ##tblAward awd, ##tblAwardRow awdr WHERE awd.idStudent = awdr.idStudent AND row = 12

	UPDATE ##tblAward SET awd01 = awd01 + N'、' WHERE awd02 <> ''
	UPDATE ##tblAward SET awd02 = awd02 + N'、' WHERE awd03 <> ''
	UPDATE ##tblAward SET awd03 = awd03 + N'、' WHERE awd04 <> ''
	UPDATE ##tblAward SET awd04 = awd04 + N'、' WHERE awd05 <> ''
	UPDATE ##tblAward SET awd05 = awd05 + N'、' WHERE awd06 <> ''
	UPDATE ##tblAward SET awd06 = awd06 + N'、' WHERE awd07 <> ''
	UPDATE ##tblAward SET awd07 = awd07 + N'、' WHERE awd08 <> ''
	UPDATE ##tblAward SET awd08 = awd08 + N'、' WHERE awd09 <> ''
	UPDATE ##tblAward SET awd09 = awd09 + N'、' WHERE awd10 <> ''
	UPDATE ##tblAward SET awd10 = awd10 + N'、' WHERE awd11 <> ''
	UPDATE ##tblAward SET awd11 = awd11 + N'、' WHERE awd12 <> ''

	UPDATE ##tblAward SET awd01 = awd01 + char(13) + char(10), flgNewLine = 1
	WHERE flgNewLine = 0 AND len(awd01 + awd02) > 53
	UPDATE ##tblAward SET awd02 = awd02 + char(13) + char(10), flgNewLine = 1
	WHERE flgNewLine = 0 AND len(awd01 + awd02 + awd03) > 53
	UPDATE ##tblAward SET awd03 = awd03 + char(13) + char(10), flgNewLine = 1
	WHERE flgNewLine = 0 AND len(awd01 + awd02 + awd03 + awd04) > 53
	UPDATE ##tblAward SET awd04 = awd04 + char(13) + char(10), flgNewLine = 1
	WHERE flgNewLine = 0 AND len(awd01 + awd02 + awd03 + awd04 + awd05) > 53
	UPDATE ##tblAward SET awd05 = awd05 + char(13) + char(10), flgNewLine = 1
	WHERE flgNewLine = 0 AND len(awd01 + awd02 + awd03 + awd04 + awd05 + awd06) > 53
	UPDATE ##tblAward SET awd06 = awd06 + char(13) + char(10), flgNewLine = 1
	WHERE flgNewLine = 0 AND len(awd01 + awd02 + awd03 + awd04 + awd05 + awd06 + awd07) > 53
	UPDATE ##tblAward SET awd07 = awd07 + char(13) + char(10), flgNewLine = 1
	WHERE flgNewLine = 0 AND len(awd01 + awd02 + awd03 + awd04 + awd05 + awd06 + awd07 + awd08) > 53
	UPDATE ##tblAward SET awd08 = awd08 + char(13) + char(10), flgNewLine = 1
	WHERE flgNewLine = 0 AND len(awd01 + awd02 + awd03 + awd04 + awd05 + awd06 + awd07 + awd08 + awd09) > 53
	UPDATE ##tblAward SET awd09 = awd09 + char(13) + char(10), flgNewLine = 1
	WHERE flgNewLine = 0 AND len(awd01 + awd02 + awd03 + awd04 + awd05 + awd06 + awd07 + awd08 + awd09 + awd10) > 53
	UPDATE ##tblAward SET awd10 = awd10 + char(13) + char(10), flgNewLine = 1
	WHERE flgNewLine = 0 AND len(awd01 + awd02 + awd03 + awd04 + awd05 + awd06 + awd07 + awd08 + awd09 + awd10 + awd11) > 53
	UPDATE ##tblAward SET awd11 = awd11 + char(13) + char(10), flgNewLine = 1
	WHERE flgNewLine = 0 AND len(awd01 + awd02 + awd03 + awd04 + awd05 + awd06 + awd07 + awd08 + awd09 + awd10 + awd11 + awd12) > 53
END

--PRINT 'H'

--Remark Row
INSERT ##tblRemarkRow (idStudent, row, rem)
SELECT idStudent, 0, rem
FROM (
SELECT idStudent, N'獲' + awd01 + awd02 + awd03 + awd04 + awd05 + awd06 + awd07 + awd08 + awd09 + awd10 + awd11 + awd12 as rem, 1 as src
FROM ##tblAward
UNION
SELECT distinct idStudent,
CASE WHEN total1 > 0 THEN
	N'德行表現優異獲' +
	CASE WHEN large1 > 0 THEN N' ' + convert(nvarchar(5), large1) + N' 大功' ELSE '' END +
	CASE WHEN small1 > 0 THEN N' ' + convert(nvarchar(5), small1) + N' 小功' ELSE '' END +
	CASE WHEN merit1 > 0 THEN N' ' + convert(nvarchar(5), merit1) + N' 優點' ELSE '' END
ELSE '' END +
CASE WHEN total2 > 0 THEN
	CASE WHEN total1 > 0 THEN N'、' ELSE '' END + 
	N'出外參賽為校爭光獲' +
	CASE WHEN large2 > 0 THEN N' ' + convert(nvarchar(5), large2) + N' 大功' ELSE '' END +
	CASE WHEN small2 > 0 THEN N' ' + convert(nvarchar(5), small2) + N' 小功' ELSE '' END +
	CASE WHEN merit2 > 0 THEN N' ' + convert(nvarchar(5), merit2) + N' 優點' ELSE '' END
ELSE ''END +
CASE WHEN total3 > 0 THEN
	CASE WHEN total1 + total2 > 0 THEN N'、' ELSE '' END + 
	N'校內服務表現優異獲' +
	CASE WHEN large3 > 0 THEN N' ' + convert(nvarchar(5), large3) + N' 大功' ELSE '' END +
	CASE WHEN small3 > 0 THEN N' ' + convert(nvarchar(5), small3) + N' 小功' ELSE '' END +
	CASE WHEN merit3 > 0 THEN N' ' + convert(nvarchar(5), merit3) + N' 優點' ELSE '' END
ELSE ''END +
CASE WHEN total4 > 0 THEN
	CASE WHEN total1 + total2 + total3 > 0 THEN N'、' ELSE '' END + 
	N'校外服務表現優異獲' +
	CASE WHEN large4 > 0 THEN N' ' + convert(nvarchar(5), large4) + N' 大功' ELSE '' END +
	CASE WHEN small4 > 0 THEN N' ' + convert(nvarchar(5), small4) + N' 小功' ELSE '' END +
	CASE WHEN merit4 > 0 THEN N' ' + convert(nvarchar(5), merit4) + N' 優點' ELSE '' END
ELSE ''END 
as rem, 2 as src
FROM (
	SELECT sr.idStudent,
	numMerit1_1 as total1,
	floor(numMerit1_1 / 9) as large1,
	floor((numMerit1_1 - floor(numMerit1_1 / 9) * 9) / 3) as small1,
	numMerit1_1 - floor(numMerit1_1 / 9) * 9 - floor((numMerit1_1 - floor(numMerit1_1 / 9) * 9) / 3) * 3  as merit1,
	numMerit2_1 as total2,
	floor(numMerit2_1 / 9) as large2,
	floor((numMerit2_1 - floor(numMerit2_1 / 9) * 9) / 3) as small2,
	numMerit2_1 - floor(numMerit2_1 / 9) * 9 - floor((numMerit2_1 - floor(numMerit2_1 / 9) * 9) / 3) * 3  as merit2,
	numMerit3_1 as total3,
	floor(numMerit3_1 / 9) as large3,
	floor((numMerit3_1 - floor(numMerit3_1 / 9) * 9) / 3) as small3,
	numMerit3_1 - floor(numMerit3_1 / 9) * 9 - floor((numMerit3_1 - floor(numMerit3_1 / 9) * 9) / 3) * 3  as merit3, 
	numMerit4_1 as total4,
	floor(numMerit4_1 / 9) as large4,
	floor((numMerit4_1 - floor(numMerit4_1 / 9) * 9) / 3) as small4,
	numMerit4_1 - floor(numMerit4_1 / 9) * 9 - floor((numMerit4_1 - floor(numMerit4_1 / 9) * 9) / 3) * 3  as merit4
	FROM tblStudentReward sr
	INNER JOIN vwStudent s ON sr.idStudent = s.idStudent
	WHERE s.form = @form AND (numMerit1_1 > 0 OR numMerit2_1 > 0 OR numMerit3_1 > 0 OR numMerit4_1 > 0) and @term = 0
	UNION
	SELECT sr.idStudent,
	numMerit1_2 as total1,
	floor(numMerit1_2 / 9) as large1,
	floor((numMerit1_2 - floor(numMerit1_2 / 9) * 9) / 3) as small1,
	numMerit1_2 - floor(numMerit1_2 / 9) * 9 - floor((numMerit1_2 - floor(numMerit1_2 / 9) * 9) / 3) * 3  as merit1,
	numMerit2_2 as total2,
	floor(numMerit2_2 / 9) as large2,
	floor((numMerit2_2 - floor(numMerit2_2 / 9) * 9) / 3) as small2,
	numMerit2_2 - floor(numMerit2_2 / 9) * 9 - floor((numMerit2_2 - floor(numMerit2_2 / 9) * 9) / 3) * 3  as merit2,
	numMerit3_2 as total3,
	floor(numMerit3_2 / 9) as large3,
	floor((numMerit3_2 - floor(numMerit3_2 / 9) * 9) / 3) as small3,
	numMerit3_2 - floor(numMerit3_2 / 9) * 9 - floor((numMerit3_2 - floor(numMerit3_2 / 9) * 9) / 3) * 3  as merit3, 
	numMerit4_2 as total4,
	floor(numMerit4_2 / 9) as large4,
	floor((numMerit4_2 - floor(numMerit4_2 / 9) * 9) / 3) as small4,
	numMerit4_2 - floor(numMerit4_2 / 9) * 9 - floor((numMerit4_2 - floor(numMerit4_2 / 9) * 9) / 3) * 3  as merit4
	FROM tblStudentReward sr
	INNER JOIN vwStudent s ON sr.idStudent = s.idStudent
	WHERE s.form = @form AND (numMerit1_2 > 0 OR numMerit2_2 > 0 OR numMerit3_2 > 0 OR numMerit4_2 > 0) and @term = 2
) r
UNION
SELECT distinct idStudent,
CASE WHEN @form in (5, 7) THEN N'' ELSE CASE @term WHEN 1 then N'上學期' ELSE N'下學期' end END +
CASE WHEN totalDS > 0 THEN
	N'因紀律問題記' +
	CASE WHEN largeDS > 0 THEN N' ' + convert(nvarchar(5), largeDS) + N' 大過' ELSE '' END +
	CASE WHEN smallDS > 0 THEN N' ' + convert(nvarchar(5), smallDS) + N' 小過' ELSE '' END +
	CASE WHEN demeritDS > 0 THEN N' ' + convert(nvarchar(5), demeritDS) + N' 缺點' ELSE '' END
ELSE '' END +
CASE WHEN totalHW > 0 THEN
	CASE WHEN totalDS > 0 THEN N'、' ELSE '' END + N'因交功課問題記' +
	CASE WHEN largeHW > 0 THEN N' ' + convert(nvarchar(5), largeHW) + N' 大過' ELSE '' END +
	CASE WHEN smallHW > 0 THEN N' ' + convert(nvarchar(5), smallHW) + N' 小過' ELSE '' END +
	CASE WHEN demeritHW > 0 THEN N' ' + convert(nvarchar(5), demeritHW) + N' 缺點' ELSE '' END
ELSE ''END as rem, 3 as src
FROM (
	SELECT sd.idStudent,
	numDemeritDS_1 as totalDS,
	floor(numDemeritDS_1 / 9) as largeDS,
	floor((numDemeritDS_1 - floor(numDemeritDS_1 / 9) * 9) / 3) as smallDS,
	numDemeritDS_1 - floor(numDemeritDS_1 / 9) * 9 - floor((numDemeritDS_1 - floor(numDemeritDS_1 / 9) * 9) / 3) * 3  as demeritDS,
	numDemeritHW_1 as totalHW,
	floor(numDemeritHW_1 / 9) as largeHW,
	floor((numDemeritHW_1 - floor(numDemeritHW_1 / 9) * 9) / 3) as smallHW,
	numDemeritHW_1 - floor(numDemeritHW_1 / 9) * 9 - floor((numDemeritHW_1 - floor(numDemeritHW_1 / 9) * 9) / 3) * 3  as demeritHW
	FROM tblStudentDiscipline sd
	INNER JOIN vwStudent s ON sd.idStudent = s.idStudent
	WHERE s.form = @form and @term = 1 AND (numDemeritDS_1 > 0 OR numDemeritHW_1 > 0) 
	UNION
	SELECT sd.idStudent,
	numDemeritDS_2 as totalDS,
	floor(numDemeritDS_2 / 9) as largeDS,
	floor((numDemeritDS_2 - floor(numDemeritDS_2 / 9) * 9) / 3) as smallDS,
	numDemeritDS_2 - floor(numDemeritDS_2 / 9) * 9 - floor((numDemeritDS_2 - floor(numDemeritDS_2 / 9) * 9) / 3) * 3  as demeritDS,
	numDemeritHW_2 as totalHW,
	floor(numDemeritHW_2 / 9) as largeHW,
	floor((numDemeritHW_2 - floor(numDemeritHW_2 / 9) * 9) / 3) as smallHW,
	numDemeritHW_2 - floor(numDemeritHW_2 / 9) * 9 - floor((numDemeritHW_2 - floor(numDemeritHW_2 / 9) * 9) / 3) * 3  as demeritHW
	FROM tblStudentDiscipline sd
	INNER JOIN vwStudent s ON sd.idStudent = s.idStudent
	WHERE s.form = @form AND @term = 2 AND (numDemeritDS_2 > 0 OR numDemeritHW_2 > 0)
) r
UNION
SELECT idStudent, eca01 + eca02 + eca03 + eca04 + eca05 + eca06 + eca07 + eca08 + eca09 + eca10 + eca11 + eca12 as rem, 4 as src
FROM ##tblECA
UNION
SELECT srr.idStudent, srr.nameChinese as rem, 100 + row as src
FROM tblStudentReportRemark srr
INNER JOIN vwStudent s ON srr.idStudent = s.idStudent 
WHERE s.form = @form AND srr.term = @term
) r
ORDER BY idStudent, src

--PRINT 'H1'

UPDATE ##tblRemarkRow
SET row = tpr.idRow - r.min_row + 1
FROM ##tblRemarkRow tpr, (
SELECT idStudent, min(idRow) AS min_row
FROM ##tblRemarkRow
GROUP BY idStudent) r
WHERE r.idStudent = tpr.idStudent

--PRINT 'H2'

-- Remark
INSERT ##tblRemark (idStudent, flgNewLine, rem01, rem02, rem03, rem04, rem05, rem06, rem07, rem08, rem09, rem10, rem11, rem12)
SELECT idStudent, 0, rem, '', '', '', '', '', '', '', '', '', '', ''
FROM ##tblRemarkRow
WHERE row = 1

UPDATE ##tblRemark SET rem02 = rem FROM ##tblRemark rem, ##tblRemarkRow remr WHERE rem.idStudent = remr.idStudent AND row = 2
UPDATE ##tblRemark SET rem03 = rem FROM ##tblRemark rem, ##tblRemarkRow remr WHERE rem.idStudent = remr.idStudent AND row = 3
UPDATE ##tblRemark SET rem04 = rem FROM ##tblRemark rem, ##tblRemarkRow remr WHERE rem.idStudent = remr.idStudent AND row = 4
UPDATE ##tblRemark SET rem05 = rem FROM ##tblRemark rem, ##tblRemarkRow remr WHERE rem.idStudent = remr.idStudent AND row = 5
UPDATE ##tblRemark SET rem06 = rem FROM ##tblRemark rem, ##tblRemarkRow remr WHERE rem.idStudent = remr.idStudent AND row = 6
UPDATE ##tblRemark SET rem07 = rem FROM ##tblRemark rem, ##tblRemarkRow remr WHERE rem.idStudent = remr.idStudent AND row = 7
UPDATE ##tblRemark SET rem08 = rem FROM ##tblRemark rem, ##tblRemarkRow remr WHERE rem.idStudent = remr.idStudent AND row = 8
UPDATE ##tblRemark SET rem09 = rem FROM ##tblRemark rem, ##tblRemarkRow remr WHERE rem.idStudent = remr.idStudent AND row = 9
UPDATE ##tblRemark SET rem10 = rem FROM ##tblRemark rem, ##tblRemarkRow remr WHERE rem.idStudent = remr.idStudent AND row = 10
UPDATE ##tblRemark SET rem11 = rem FROM ##tblRemark rem, ##tblRemarkRow remr WHERE rem.idStudent = remr.idStudent AND row = 11
UPDATE ##tblRemark SET rem12 = rem FROM ##tblRemark rem, ##tblRemarkRow remr WHERE rem.idStudent = remr.idStudent AND row = 12

UPDATE ##tblRemark SET rem01 = rem01 + char(13) + char(10) WHERE rem02 <> ''
UPDATE ##tblRemark SET rem02 = rem02 + char(13) + char(10) WHERE rem03 <> ''
UPDATE ##tblRemark SET rem03 = rem03 + char(13) + char(10) WHERE rem04 <> ''
UPDATE ##tblRemark SET rem04 = rem04 + char(13) + char(10) WHERE rem05 <> ''
UPDATE ##tblRemark SET rem05 = rem05 + char(13) + char(10) WHERE rem06 <> ''
UPDATE ##tblRemark SET rem06 = rem06 + char(13) + char(10) WHERE rem07 <> ''
UPDATE ##tblRemark SET rem07 = rem07 + char(13) + char(10) WHERE rem08 <> ''
UPDATE ##tblRemark SET rem08 = rem08 + char(13) + char(10) WHERE rem09 <> ''
UPDATE ##tblRemark SET rem09 = rem09 + char(13) + char(10) WHERE rem10 <> ''
UPDATE ##tblRemark SET rem10 = rem10 + char(13) + char(10) WHERE rem11 <> ''
UPDATE ##tblRemark SET rem11 = rem11 + char(13) + char(10) WHERE rem12 <> ''

------------------------------------------------------------------------------------------------
-- Output
------------------------------------------------------------------------------------------------
--PRINT 'I'

--Master
INSERT tblZStudentReport2 (term, Class, Num, form, idStudent, [Year], Term_CName, Term_EName, CName, EName, Gender, StuID, CTeacher)
SELECT @term, s.class, dbo.fnLeadingZero(s.numberClass, 2) as numberClass, @form, s.idStudent, dbo.fnYearSchool(dbo.fnYearCurr()), CASE WHEN @term = 1 THEN N'上' ELSE N'下' END, cast(@term as nvarchar(1)), s.nameChinese, s.nameEnglish, s.gender, s.codeStudent, s2.nameChinese + N'老師' 
FROM vwStudent s 
INNER JOIN tblStaffClass sc ON s.class = sc.class AND flgHead = 1 
INNER JOIN tblStaff s2 ON sc.idStaff = s2.idStaff 
WHERE s.idStudent IN ( 
SELECT distinct idStudent 
FROM vwStudentSubject 
WHERE form = @form AND ((flgTerm1 = 1 AND @term = 1) OR (flgTerm2 = 1 AND @term = 2)) ) AND ((s.flgTerm1 = 1 AND @term = 1) OR (s.flgTerm2 = 1 AND @term = 2))

--Result
UPDATE tblZStudentReport2 SET Sbj01_EName = Sbj_EName, Sbj01_CName = Sbj_CName, Sbj01_1 = Sbj_1, Sbj01_2 = Sbj_2, Sbj01_3 = Sbj_3, Lsn_01 = Lsn, Asm_01 = Asm FROM tblZStudentReport2 zsr, ##tblResultRow rr WHERE term = @term AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 1
UPDATE tblZStudentReport2 SET Sbj02_EName = Sbj_EName, Sbj02_CName = Sbj_CName, Sbj02_1 = Sbj_1, Sbj02_2 = Sbj_2, Sbj02_3 = Sbj_3, Lsn_02 = Lsn, Asm_02 = Asm FROM tblZStudentReport2 zsr, ##tblResultRow rr WHERE term = @term AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 2
UPDATE tblZStudentReport2 SET Sbj03_EName = Sbj_EName, Sbj03_CName = Sbj_CName, Sbj03_1 = Sbj_1, Sbj03_2 = Sbj_2, Sbj03_3 = Sbj_3, Lsn_03 = Lsn, Asm_03 = Asm FROM tblZStudentReport2 zsr, ##tblResultRow rr WHERE term = @term AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 3
UPDATE tblZStudentReport2 SET Sbj04_EName = Sbj_EName, Sbj04_CName = Sbj_CName, Sbj04_1 = Sbj_1, Sbj04_2 = Sbj_2, Sbj04_3 = Sbj_3, Lsn_04 = Lsn, Asm_04 = Asm FROM tblZStudentReport2 zsr, ##tblResultRow rr WHERE term = @term AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 4
UPDATE tblZStudentReport2 SET Sbj05_EName = Sbj_EName, Sbj05_CName = Sbj_CName, Sbj05_1 = Sbj_1, Sbj05_2 = Sbj_2, Sbj05_3 = Sbj_3, Lsn_05 = Lsn, Asm_05 = Asm FROM tblZStudentReport2 zsr, ##tblResultRow rr WHERE term = @term AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 5
UPDATE tblZStudentReport2 SET Sbj06_EName = Sbj_EName, Sbj06_CName = Sbj_CName, Sbj06_1 = Sbj_1, Sbj06_2 = Sbj_2, Sbj06_3 = Sbj_3, Lsn_06 = Lsn, Asm_06 = Asm FROM tblZStudentReport2 zsr, ##tblResultRow rr WHERE term = @term AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 6
UPDATE tblZStudentReport2 SET Sbj07_EName = Sbj_EName, Sbj07_CName = Sbj_CName, Sbj07_1 = Sbj_1, Sbj07_2 = Sbj_2, Sbj07_3 = Sbj_3, Lsn_07 = Lsn, Asm_07 = Asm FROM tblZStudentReport2 zsr, ##tblResultRow rr WHERE term = @term AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 7
UPDATE tblZStudentReport2 SET Sbj08_EName = Sbj_EName, Sbj08_CName = Sbj_CName, Sbj08_1 = Sbj_1, Sbj08_2 = Sbj_2, Sbj08_3 = Sbj_3, Lsn_08 = Lsn, Asm_08 = Asm FROM tblZStudentReport2 zsr, ##tblResultRow rr WHERE term = @term AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 8
UPDATE tblZStudentReport2 SET Sbj09_EName = Sbj_EName, Sbj09_CName = Sbj_CName, Sbj09_1 = Sbj_1, Sbj09_2 = Sbj_2, Sbj09_3 = Sbj_3, Lsn_09 = Lsn, Asm_09 = Asm FROM tblZStudentReport2 zsr, ##tblResultRow rr WHERE term = @term AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 9
UPDATE tblZStudentReport2 SET Sbj10_EName = Sbj_EName, Sbj10_CName = Sbj_CName, Sbj10_1 = Sbj_1, Sbj10_2 = Sbj_2, Sbj10_3 = Sbj_3, Lsn_10 = Lsn, Asm_10 = Asm FROM tblZStudentReport2 zsr, ##tblResultRow rr WHERE term = @term AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 10
UPDATE tblZStudentReport2 SET Sbj11_EName = Sbj_EName, Sbj11_CName = Sbj_CName, Sbj11_1 = Sbj_1, Sbj11_2 = Sbj_2, Sbj11_3 = Sbj_3, Lsn_11 = Lsn, Asm_11 = Asm FROM tblZStudentReport2 zsr, ##tblResultRow rr WHERE term = @term AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 11
UPDATE tblZStudentReport2 SET Sbj12_EName = Sbj_EName, Sbj12_CName = Sbj_CName, Sbj12_1 = Sbj_1, Sbj12_2 = Sbj_2, Sbj12_3 = Sbj_3, Lsn_12 = Lsn, Asm_12 = Asm FROM tblZStudentReport2 zsr, ##tblResultRow rr WHERE term = @term AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 12
UPDATE tblZStudentReport2 SET Sbj13_EName = Sbj_EName, Sbj13_CName = Sbj_CName, Sbj13_1 = Sbj_1, Sbj13_2 = Sbj_2, Sbj13_3 = Sbj_3, Lsn_13 = Lsn, Asm_13 = Asm FROM tblZStudentReport2 zsr, ##tblResultRow rr WHERE term = @term AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 13
UPDATE tblZStudentReport2 SET Sbj14_EName = Sbj_EName, Sbj14_CName = Sbj_CName, Sbj14_1 = Sbj_1, Sbj14_2 = Sbj_2, Sbj14_3 = Sbj_3, Lsn_14 = Lsn, Asm_14 = Asm FROM tblZStudentReport2 zsr, ##tblResultRow rr WHERE term = @term AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 14
UPDATE tblZStudentReport2 SET Sbj15_EName = Sbj_EName, Sbj15_CName = Sbj_CName, Sbj15_1 = Sbj_1, Sbj15_2 = Sbj_2, Sbj15_3 = Sbj_3, Lsn_15 = Lsn, Asm_15 = Asm FROM tblZStudentReport2 zsr, ##tblResultRow rr WHERE term = @term AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 15
UPDATE tblZStudentReport2 SET Sbj16_EName = Sbj_EName, Sbj16_CName = Sbj_CName, Sbj16_1 = Sbj_1, Sbj16_2 = Sbj_2, Sbj16_3 = Sbj_3, Lsn_16 = Lsn, Asm_16 = Asm FROM tblZStudentReport2 zsr, ##tblResultRow rr WHERE term = @term AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 16
UPDATE tblZStudentReport2 SET Sbj17_EName = Sbj_EName, Sbj17_CName = Sbj_CName, Sbj17_1 = Sbj_1, Sbj17_2 = Sbj_2, Sbj17_3 = Sbj_3, Lsn_17 = Lsn, Asm_17 = Asm FROM tblZStudentReport2 zsr, ##tblResultRow rr WHERE term = @term AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 17
UPDATE tblZStudentReport2 SET Sbj18_EName = Sbj_EName, Sbj18_CName = Sbj_CName, Sbj18_1 = Sbj_1, Sbj18_2 = Sbj_2, Sbj18_3 = Sbj_3, Lsn_18 = Lsn, Asm_18 = Asm FROM tblZStudentReport2 zsr, ##tblResultRow rr WHERE term = @term AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 18
UPDATE tblZStudentReport2 SET Sbj19_EName = Sbj_EName, Sbj19_CName = Sbj_CName, Sbj19_1 = Sbj_1, Sbj19_2 = Sbj_2, Sbj19_3 = Sbj_3, Lsn_19 = Lsn, Asm_19 = Asm FROM tblZStudentReport2 zsr, ##tblResultRow rr WHERE term = @term AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 19
UPDATE tblZStudentReport2 SET Sbj20_EName = Sbj_EName, Sbj20_CName = Sbj_CName, Sbj20_1 = Sbj_1, Sbj20_2 = Sbj_2, Sbj20_3 = Sbj_3, Lsn_20 = Lsn, Asm_20 = Asm FROM tblZStudentReport2 zsr, ##tblResultRow rr WHERE term = @term AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 20
UPDATE tblZStudentReport2 SET Sbj21_EName = Sbj_EName, Sbj21_CName = Sbj_CName, Sbj21_1 = Sbj_1, Sbj21_2 = Sbj_2, Sbj21_3 = Sbj_3, Lsn_21 = Lsn, Asm_21 = Asm FROM tblZStudentReport2 zsr, ##tblResultRow rr WHERE term = @term AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 21
UPDATE tblZStudentReport2 SET Sbj22_EName = Sbj_EName, Sbj22_CName = Sbj_CName, Sbj22_1 = Sbj_1, Sbj22_2 = Sbj_2, Sbj22_3 = Sbj_3, Lsn_22 = Lsn, Asm_22 = Asm FROM tblZStudentReport2 zsr, ##tblResultRow rr WHERE term = @term AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 22
UPDATE tblZStudentReport2 SET Sbj23_EName = Sbj_EName, Sbj23_CName = Sbj_CName, Sbj23_1 = Sbj_1, Sbj23_2 = Sbj_2, Sbj23_3 = Sbj_3, Lsn_23 = Lsn, Asm_23 = Asm FROM tblZStudentReport2 zsr, ##tblResultRow rr WHERE term = @term AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 23
UPDATE tblZStudentReport2 SET Sbj24_EName = Sbj_EName, Sbj24_CName = Sbj_CName, Sbj24_1 = Sbj_1, Sbj24_2 = Sbj_2, Sbj24_3 = Sbj_3, Lsn_24 = Lsn, Asm_24 = Asm FROM tblZStudentReport2 zsr, ##tblResultRow rr WHERE term = @term AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 24
UPDATE tblZStudentReport2 SET Sbj25_EName = Sbj_EName, Sbj25_CName = Sbj_CName, Sbj25_1 = Sbj_1, Sbj25_2 = Sbj_2, Sbj25_3 = Sbj_3, Lsn_25 = Lsn, Asm_25 = Asm FROM tblZStudentReport2 zsr, ##tblResultRow rr WHERE term = @term AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 25
UPDATE tblZStudentReport2 SET Sbj26_EName = Sbj_EName, Sbj26_CName = Sbj_CName, Sbj26_1 = Sbj_1, Sbj26_2 = Sbj_2, Sbj26_3 = Sbj_3, Lsn_26 = Lsn, Asm_26 = Asm FROM tblZStudentReport2 zsr, ##tblResultRow rr WHERE term = @term AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 26
UPDATE tblZStudentReport2 SET Sbj27_EName = Sbj_EName, Sbj27_CName = Sbj_CName, Sbj27_1 = Sbj_1, Sbj27_2 = Sbj_2, Sbj27_3 = Sbj_3, Lsn_27 = Lsn, Asm_27 = Asm FROM tblZStudentReport2 zsr, ##tblResultRow rr WHERE term = @term AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 27

--average
-- KK 4-digit

IF @form < 6
BEGIN
	UPDATE tblZStudentReport2 
	SET ave3 = '(' + convert(nvarchar(6), convert(decimal(7,1), zsr.score / 100.0)) + ')' 
	FROM tblZStudentReport2 zr 
	INNER JOIN tblZStudentRank2 zsr ON zsr.idStudent = zr.idStudent AND zsr.idPaper = '' AND zsr.flgStandard = 0 AND zsr.section = 'O' AND zsr.term = zr.term
	WHERE zr.term = @term AND zr.form = @form AND zsr.score < 500

	UPDATE tblZStudentReport2 
	SET ave3 = convert(nvarchar(6), convert(decimal(7,1), zsr.score / 100.0))
	FROM tblZStudentReport2 zr 
	INNER JOIN tblZStudentRank2 zsr ON zsr.idStudent = zr.idStudent AND zsr.idPaper = '' AND zsr.flgStandard = 0 AND zsr.section = 'O' AND zsr.term = zr.term
	WHERE zr.term = @term AND zr.form = @form AND zsr.score >= 500
END
ELSE
BEGIN
	UPDATE tblZStudentReport2 
	SET ave3 = '--' 
	WHERE term = @term AND form = @form
END

--class rank
IF @form = 3
BEGIN
	UPDATE tblZStudentReport2
	SET CRank3 = convert(nvarchar(5), zsr.rankClass) + '/' + convert(nvarchar(5), r.numStudent)
	FROM tblZStudentReport2 zr 
	INNER JOIN tblZStudentRank2 zsr ON zr.idStudent = zsr.idStudent AND zsr.idPaper = '' AND zsr.flgStandard = 0 AND zsr.section = 'O' AND zr.term = zsr.term
	INNER JOIN tblStudent s ON zr.idStudent = s.idStudent
	INNER JOIN (
	SELECT class, count( * ) as numStudent
	FROM tblStudent
	WHERE (@term = 1 AND flgTerm1 = 1) OR (@term = 2 AND flgTerm2 = 1)
	GROUP BY class) r ON s.class = r.class
	WHERE zr.term = @term AND zr.form = @form AND zsr.rankClass <= 3

	UPDATE tblZStudentReport2 
	SET CRank3 = '--' 
	FROM tblZStudentReport2 zr 
	INNER JOIN tblZStudentRank2 zsr ON zr.idStudent = zsr.idStudent AND zsr.idPaper = '' AND zsr.flgStandard = 0 AND zsr.section = 'O' AND zr.term = zsr.term
	WHERE zr.term = @term AND zr.form = @form AND zsr.rankClass > 3	
END
ELSE
BEGIN
	IF @form >= 6
	BEGIN
		UPDATE tblZStudentReport2 
		SET CRank3 = '--' 
		WHERE term = @term AND form = @form
	END
	ELSE
	BEGIN
		UPDATE tblZStudentReport2
		SET CRank3 = convert(nvarchar(5), zsr.rankClass) + '/' + convert(nvarchar(5), r.numStudent)
		FROM tblZStudentReport2 zr 
		INNER JOIN tblZStudentRank2 zsr ON zr.idStudent = zsr.idStudent AND zsr.idPaper = '' AND zsr.flgStandard = 0 AND zsr.section = 'O' AND zr.term = zsr.term
		INNER JOIN tblStudent s ON zr.idStudent = s.idStudent
		INNER JOIN (
		SELECT class, count( * ) as numStudent
		FROM tblStudent
		WHERE (@term = 1 AND flgTerm1 = 1) OR (@term = 2 AND flgTerm2 = 1)
		GROUP BY class) r ON s.class = r.class
		WHERE zr.term = @term AND zr.form = @form
	END
END

--form rank
IF @form >= 3
BEGIN
	UPDATE tblZStudentReport2 
	SET FRank3 = '--' 
	WHERE term = @term AND form = @form	
END
ELSE
BEGIN
	UPDATE tblZStudentReport2
	SET FRank3 = convert(nvarchar(5), zsr.rankForm) + '/' + convert(nvarchar(5), r.numStudent)
	FROM tblZStudentReport2 zr 
	INNER JOIN tblZStudentRank2 zsr ON zr.idStudent = zsr.idStudent AND zsr.idPaper = '' AND zsr.flgStandard = 0 AND zsr.section = 'O' AND zr.term = zsr.term
	INNER JOIN (
	SELECT form, count( * ) as numStudent
	FROM vwStudent
	WHERE (@term = 1 AND flgTerm1 = 1) OR (@term = 2 AND flgTerm2 = 1)
	GROUP BY form) r ON zr.form = r.form
	WHERE zr.term = @term AND zr.form = @form
END

--days present
IF @term = 1 
BEGIN
	UPDATE tblZStudentReport2 
	SET Attend3 = convert(nvarchar (10), sd.dayAbsent_1) 
	FROM tblZStudentReport2 zr
	INNER JOIN tblStudentDiscipline sd ON zr.idStudent = sd.idStudent
	WHERE zr.term = @term AND zr.form = @form
END
ELSE
BEGIN
	UPDATE tblZStudentReport2 
	SET Attend3 = convert(nvarchar (10), sd.dayAbsent_2) 
	FROM tblZStudentReport2 zr
	INNER JOIN tblStudentDiscipline sd ON zr.idStudent = sd.idStudent
	WHERE zr.term = @term AND zr.form = @form
END

--times late
IF @term = 1 
BEGIN
	UPDATE tblZStudentReport2 
	SET Late3 = convert(nvarchar (10), numLate_1) 
	FROM tblZStudentReport2 zr 
	INNER JOIN tblStudentDiscipline sd ON zr.idStudent = sd.idStudent
	WHERE zr.term = @term AND zr.form = @form
END
ELSE
BEGIN
	UPDATE tblZStudentReport2 
	SET Late3 = convert(nvarchar (10), numLate_2) 
	FROM tblZStudentReport2 zr 
	INNER JOIN tblStudentDiscipline sd ON zr.idStudent = sd.idStudent
	WHERE zr.term = @term AND zr.form = @form
END

--conduct
IF @term = 1
BEGIN
	UPDATE tblZStudentReport2 SET Cnd01 = conduct_1_1 FROM tblZStudentReport2 zsr, tblStudentConduct sc WHERE term = @term AND form = @form AND zsr.idStudent = sc.idStudent AND conduct_1_1 is not null
	UPDATE tblZStudentReport2 SET Cnd02 = conduct_2_1 FROM tblZStudentReport2 zsr, tblStudentConduct sc WHERE term = @term AND form = @form AND zsr.idStudent = sc.idStudent AND conduct_2_1 is not null
	UPDATE tblZStudentReport2 SET Cnd03 = conduct_3_1 FROM tblZStudentReport2 zsr, tblStudentConduct sc WHERE term = @term AND form = @form AND zsr.idStudent = sc.idStudent AND conduct_3_1 is not null
	UPDATE tblZStudentReport2 SET Cnd04 = conduct_4_1 FROM tblZStudentReport2 zsr, tblStudentConduct sc WHERE term = @term AND form = @form AND zsr.idStudent = sc.idStudent AND conduct_4_1 is not null
	UPDATE tblZStudentReport2 SET Cnd05 = conduct_5_1 FROM tblZStudentReport2 zsr, tblStudentConduct sc WHERE term = @term AND form = @form AND zsr.idStudent = sc.idStudent AND conduct_5_1 is not null
END
ELSE
BEGIN
	UPDATE tblZStudentReport2 SET Cnd01 = conduct_1_2 FROM tblZStudentReport2 zsr, tblStudentConduct sc WHERE term = @term AND form = @form AND zsr.idStudent = sc.idStudent AND conduct_1_2 is not null
	UPDATE tblZStudentReport2 SET Cnd02 = conduct_2_2 FROM tblZStudentReport2 zsr, tblStudentConduct sc WHERE term = @term AND form = @form AND zsr.idStudent = sc.idStudent AND conduct_2_2 is not null
	UPDATE tblZStudentReport2 SET Cnd03 = conduct_3_2 FROM tblZStudentReport2 zsr, tblStudentConduct sc WHERE term = @term AND form = @form AND zsr.idStudent = sc.idStudent AND conduct_3_2 is not null
	UPDATE tblZStudentReport2 SET Cnd04 = conduct_4_2 FROM tblZStudentReport2 zsr, tblStudentConduct sc WHERE term = @term AND form = @form AND zsr.idStudent = sc.idStudent AND conduct_4_2 is not null
	UPDATE tblZStudentReport2 SET Cnd05 = conduct_5_2 FROM tblZStudentReport2 zsr, tblStudentConduct sc WHERE term = @term AND form = @form AND zsr.idStudent = sc.idStudent AND conduct_5_2 is not null
END

--comment
IF @term = 1
BEGIN
	UPDATE tblZStudentReport2 SET Cmt01 = custom_1_1 FROM tblZStudentReport2 zsr, tblStudentComment sc WHERE term = @term AND form = @form AND zsr.idStudent = sc.idStudent AND custom_1_1 is not null
	UPDATE tblZStudentReport2 SET Cmt02 = custom_2_1 FROM tblZStudentReport2 zsr, tblStudentComment sc WHERE term = @term AND form = @form AND zsr.idStudent = sc.idStudent AND custom_2_1 is not null
	UPDATE tblZStudentReport2 SET Cmt03 = custom_3_1 FROM tblZStudentReport2 zsr, tblStudentComment sc WHERE term = @term AND form = @form AND zsr.idStudent = sc.idStudent AND custom_3_1 is not null
	UPDATE tblZStudentReport2 SET Cmt04 = custom_4_1 FROM tblZStudentReport2 zsr, tblStudentComment sc WHERE term = @term AND form = @form AND zsr.idStudent = sc.idStudent AND custom_4_1 is not null

	UPDATE tblZStudentReport2 SET Cmt01 = comment FROM tblZStudentReport2 zsr, tblStudentComment sc, tblComment c WHERE term = @term AND form = @form AND zsr.idStudent = sc.idStudent AND sc.comment_1_1 = c.idComment AND sc.comment_1_1 is not null
	UPDATE tblZStudentReport2 SET Cmt02 = comment FROM tblZStudentReport2 zsr, tblStudentComment sc, tblComment c WHERE term = @term AND form = @form AND zsr.idStudent = sc.idStudent AND sc.comment_2_1 = c.idComment AND sc.comment_2_1 is not null
	UPDATE tblZStudentReport2 SET Cmt03 = comment FROM tblZStudentReport2 zsr, tblStudentComment sc, tblComment c WHERE term = @term AND form = @form AND zsr.idStudent = sc.idStudent AND sc.comment_3_1 = c.idComment AND sc.comment_3_1 is not null
	UPDATE tblZStudentReport2 SET Cmt04 = comment FROM tblZStudentReport2 zsr, tblStudentComment sc, tblComment c WHERE term = @term AND form = @form AND zsr.idStudent = sc.idStudent AND sc.comment_4_1 = c.idComment AND sc.comment_4_1 is not null
END
ELSE
BEGIN
	UPDATE tblZStudentReport2 SET Cmt01 = custom_1_2 FROM tblZStudentReport2 zsr, tblStudentComment sc WHERE term = @term AND form = @form AND zsr.idStudent = sc.idStudent AND custom_1_2 is not null
	UPDATE tblZStudentReport2 SET Cmt02 = custom_2_2 FROM tblZStudentReport2 zsr, tblStudentComment sc WHERE term = @term AND form = @form AND zsr.idStudent = sc.idStudent AND custom_2_2 is not null
	UPDATE tblZStudentReport2 SET Cmt03 = custom_3_2 FROM tblZStudentReport2 zsr, tblStudentComment sc WHERE term = @term AND form = @form AND zsr.idStudent = sc.idStudent AND custom_3_2 is not null
	UPDATE tblZStudentReport2 SET Cmt04 = custom_4_2 FROM tblZStudentReport2 zsr, tblStudentComment sc WHERE term = @term AND form = @form AND zsr.idStudent = sc.idStudent AND custom_4_2 is not null

	UPDATE tblZStudentReport2 SET Cmt01 = comment FROM tblZStudentReport2 zsr, tblStudentComment sc, tblComment c WHERE term = @term AND form = @form AND zsr.idStudent = sc.idStudent AND sc.comment_1_2 = c.idComment AND sc.comment_1_2 is not null
	UPDATE tblZStudentReport2 SET Cmt02 = comment FROM tblZStudentReport2 zsr, tblStudentComment sc, tblComment c WHERE term = @term AND form = @form AND zsr.idStudent = sc.idStudent AND sc.comment_2_2 = c.idComment AND sc.comment_2_2 is not null
	UPDATE tblZStudentReport2 SET Cmt03 = comment FROM tblZStudentReport2 zsr, tblStudentComment sc, tblComment c WHERE term = @term AND form = @form AND zsr.idStudent = sc.idStudent AND sc.comment_3_2 = c.idComment AND sc.comment_3_2 is not null
	UPDATE tblZStudentReport2 SET Cmt04 = comment FROM tblZStudentReport2 zsr, tblStudentComment sc, tblComment c WHERE term = @term AND form = @form AND zsr.idStudent = sc.idStudent AND sc.comment_4_2 = c.idComment AND sc.comment_4_2 is not null
END

--service
UPDATE tblZStudentReport2 SET Srv01 = srv FROM tblZStudentReport2 zsr, ##tblServiceRow sr WHERE term = @term AND form = @form AND zsr.idStudent = sr.idStudent AND sr.row = 1
UPDATE tblZStudentReport2 SET Srv02 = srv FROM tblZStudentReport2 zsr, ##tblServiceRow sr WHERE term = @term AND form = @form AND zsr.idStudent = sr.idStudent AND sr.row = 2
UPDATE tblZStudentReport2 SET Srv03 = srv FROM tblZStudentReport2 zsr, ##tblServiceRow sr WHERE term = @term AND form = @form AND zsr.idStudent = sr.idStudent AND sr.row = 3
UPDATE tblZStudentReport2 SET Srv04 = srv FROM tblZStudentReport2 zsr, ##tblServiceRow sr WHERE term = @term AND form = @form AND zsr.idStudent = sr.idStudent AND sr.row = 4

--remark
UPDATE tblZStudentReport2 
SET Rem = rem01 + rem02 + rem03 + rem04 + rem05 + rem06 + rem07 + rem08 + rem09 + rem10 + rem11 + rem12
FROM tblZStudentReport2 zsr 
INNER JOIN ##tblRemark rr ON zsr.idStudent = rr.idStudent
WHERE zsr.term = @term AND zsr.form = @form 

--ind
UPDATE tblZStudentReport2 
SET Ind = ind01 + ind02 + ind03 + ind04 + ind05 + ind06 + ind07 + ind08 + ind09 + ind10 + ind11 + ind12 + ind13 + ind14 + ind15 + ind16 + ind17 + ind18 + ind19 + ind20 
FROM tblZStudentReport2 zsr 
INNER JOIN ##tblInd ir ON zsr.idStudent = ir.idStudent
WHERE zsr.term = @term AND zsr.form = @form 

GO

------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------


stpGenerateReport_S123_2013 1, 1
GO
stpGenerateReport_S123_2013 2, 1
GO
stpGenerateReport_S123_2013 3, 1
GO

