------------------------------------------------------------------------------------------------
-- stpInitializeReport
------------------------------------------------------------------------------------------------

if exists (select * from dbo.sysobjects where id = object_id(N'[dbo].[stpInitializeReport]') and OBJECTPROPERTY(id, N'IsProcedure') = 1)
drop procedure [dbo].[stpInitializeReport]
GO

CREATE PROCEDURE dbo.stpInitializeReport
@form tinyint, @term tinyint
AS

if exists (select * from tempdb..sysobjects where name = '##tblResultRow')
drop table [tempdb].[dbo].[##tblResultRow]

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

if exists (select * from tempdb..sysobjects where name = '##tblKeyRow')
drop table [tempdb].[dbo].[##tblKeyRow]

CREATE TABLE [dbo].[##tblKeyRow] (
	[idRow] [smallint] IDENTITY (1, 1) NOT NULL,
	[idStudent] [int] NOT NULL,
	[row] [smallint] NOT NULL,
	[key] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL
) ON [PRIMARY]

if exists (select * from tempdb..sysobjects where name = '##tblKey')
drop table [tempdb].[dbo].[##tblKey]

CREATE TABLE [dbo].[##tblKey] (
	[idStudent] [int] NOT NULL,
	[flgNewLine] [bit] NOT NULL,
	[key01] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[key02] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[key03] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[key04] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[key05] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[key06] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[key07] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[key08] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[key09] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[key10] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[key11] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[key12] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL
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

if exists (select * from tempdb..sysobjects where name = '##tblWeightRow')
drop table [tempdb].[dbo].[##tblWeightRow]

CREATE TABLE [dbo].[##tblWeightRow] (
	[idRow] [smallint] IDENTITY (1, 1) NOT NULL,
	[idStudent] [int] NOT NULL,
	[row] [smallint] NOT NULL,
	[wgt] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL
) ON [PRIMARY]

if exists (select * from tempdb..sysobjects where name = '##tblWeight')
drop table [tempdb].[dbo].[##tblWeight]

CREATE TABLE [dbo].[##tblWeight] (
	[idStudent] [int] NOT NULL,
	[flgNewLine] [bit] NOT NULL,
	[wgt01] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[wgt02] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[wgt03] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[wgt04] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[wgt05] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[wgt06] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[wgt07] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[wgt08] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[wgt09] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[wgt10] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[wgt11] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL,
	[wgt12] [nvarchar] (50) COLLATE Chinese_Taiwan_Stroke_CI_AS NOT NULL
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

DELETE
FROM tblZStudentReport
WHERE form = @form AND term = @term

GO

------------------------------------------------------------------------------------------------
-- stpOutputReport
------------------------------------------------------------------------------------------------

if exists (select * from dbo.sysobjects where id = object_id(N'[dbo].[stpOutputReport]') and OBJECTPROPERTY(id, N'IsProcedure') = 1)
drop procedure [dbo].[stpOutputReport]
GO

CREATE PROCEDURE dbo.stpOutputReport
@form tinyint, @term tinyint
AS

--Master
INSERT tblZStudentReport (term, Class, Num, form, idStudent, CName, EName, Gender, StuID, CTeacher)
SELECT distinct @term, s.class, dbo.fnLeadingZero(s.numberClass, 2) as numberClass, @form, s.idStudent, s.nameChinese, s.nameEnglish, s.gender, codeStudent, s2.nameChinese + N'老師'
FROM vwStudent s
INNER JOIN tblStaffClass sc ON s.class = sc.class AND flgHead = 1
INNER JOIN tblStaff s2 ON sc.idStaff = s2.idStaff
INNER JOIN tblStudentSubject ss ON s.idStudent = ss.idStudent
WHERE s.form = @form AND
	  ((s.flgTerm1 = 1 and @term = 1) or (s.flgTerm2 = 1 and @term = 2)) AND
	  ((ss.flgTerm1 = 1 and @term = 1) or (ss.flgTerm2 = 1 and @term = 2))
ORDER by s.class, numberClass

--Result
UPDATE tblZStudentReport SET Sbj01_EName = Sbj_EName, Sbj01_CName = Sbj_CName, Sbj01_1 = Sbj_1, Sbj01_2 = Sbj_2, Sbj01_3 = Sbj_3, Lsn_01 = Lsn, Asm_01 = Asm FROM tblZStudentReport zsr, ##tblResultRow rr WHERE term = @term AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 1
UPDATE tblZStudentReport SET Sbj02_EName = Sbj_EName, Sbj02_CName = Sbj_CName, Sbj02_1 = Sbj_1, Sbj02_2 = Sbj_2, Sbj02_3 = Sbj_3, Lsn_02 = Lsn, Asm_02 = Asm FROM tblZStudentReport zsr, ##tblResultRow rr WHERE term = @term AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 2
UPDATE tblZStudentReport SET Sbj03_EName = Sbj_EName, Sbj03_CName = Sbj_CName, Sbj03_1 = Sbj_1, Sbj03_2 = Sbj_2, Sbj03_3 = Sbj_3, Lsn_03 = Lsn, Asm_03 = Asm FROM tblZStudentReport zsr, ##tblResultRow rr WHERE term = @term AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 3
UPDATE tblZStudentReport SET Sbj04_EName = Sbj_EName, Sbj04_CName = Sbj_CName, Sbj04_1 = Sbj_1, Sbj04_2 = Sbj_2, Sbj04_3 = Sbj_3, Lsn_04 = Lsn, Asm_04 = Asm FROM tblZStudentReport zsr, ##tblResultRow rr WHERE term = @term AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 4
UPDATE tblZStudentReport SET Sbj05_EName = Sbj_EName, Sbj05_CName = Sbj_CName, Sbj05_1 = Sbj_1, Sbj05_2 = Sbj_2, Sbj05_3 = Sbj_3, Lsn_05 = Lsn, Asm_05 = Asm FROM tblZStudentReport zsr, ##tblResultRow rr WHERE term = @term AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 5
UPDATE tblZStudentReport SET Sbj06_EName = Sbj_EName, Sbj06_CName = Sbj_CName, Sbj06_1 = Sbj_1, Sbj06_2 = Sbj_2, Sbj06_3 = Sbj_3, Lsn_06 = Lsn, Asm_06 = Asm FROM tblZStudentReport zsr, ##tblResultRow rr WHERE term = @term AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 6
UPDATE tblZStudentReport SET Sbj07_EName = Sbj_EName, Sbj07_CName = Sbj_CName, Sbj07_1 = Sbj_1, Sbj07_2 = Sbj_2, Sbj07_3 = Sbj_3, Lsn_07 = Lsn, Asm_07 = Asm FROM tblZStudentReport zsr, ##tblResultRow rr WHERE term = @term AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 7
UPDATE tblZStudentReport SET Sbj08_EName = Sbj_EName, Sbj08_CName = Sbj_CName, Sbj08_1 = Sbj_1, Sbj08_2 = Sbj_2, Sbj08_3 = Sbj_3, Lsn_08 = Lsn, Asm_08 = Asm FROM tblZStudentReport zsr, ##tblResultRow rr WHERE term = @term AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 8
UPDATE tblZStudentReport SET Sbj09_EName = Sbj_EName, Sbj09_CName = Sbj_CName, Sbj09_1 = Sbj_1, Sbj09_2 = Sbj_2, Sbj09_3 = Sbj_3, Lsn_09 = Lsn, Asm_09 = Asm FROM tblZStudentReport zsr, ##tblResultRow rr WHERE term = @term AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 9
UPDATE tblZStudentReport SET Sbj10_EName = Sbj_EName, Sbj10_CName = Sbj_CName, Sbj10_1 = Sbj_1, Sbj10_2 = Sbj_2, Sbj10_3 = Sbj_3, Lsn_10 = Lsn, Asm_10 = Asm FROM tblZStudentReport zsr, ##tblResultRow rr WHERE term = @term AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 10
UPDATE tblZStudentReport SET Sbj11_EName = Sbj_EName, Sbj11_CName = Sbj_CName, Sbj11_1 = Sbj_1, Sbj11_2 = Sbj_2, Sbj11_3 = Sbj_3, Lsn_11 = Lsn, Asm_11 = Asm FROM tblZStudentReport zsr, ##tblResultRow rr WHERE term = @term AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 11
UPDATE tblZStudentReport SET Sbj12_EName = Sbj_EName, Sbj12_CName = Sbj_CName, Sbj12_1 = Sbj_1, Sbj12_2 = Sbj_2, Sbj12_3 = Sbj_3, Lsn_12 = Lsn, Asm_12 = Asm FROM tblZStudentReport zsr, ##tblResultRow rr WHERE term = @term AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 12
UPDATE tblZStudentReport SET Sbj13_EName = Sbj_EName, Sbj13_CName = Sbj_CName, Sbj13_1 = Sbj_1, Sbj13_2 = Sbj_2, Sbj13_3 = Sbj_3, Lsn_13 = Lsn, Asm_13 = Asm FROM tblZStudentReport zsr, ##tblResultRow rr WHERE term = @term AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 13
UPDATE tblZStudentReport SET Sbj14_EName = Sbj_EName, Sbj14_CName = Sbj_CName, Sbj14_1 = Sbj_1, Sbj14_2 = Sbj_2, Sbj14_3 = Sbj_3, Lsn_14 = Lsn, Asm_14 = Asm FROM tblZStudentReport zsr, ##tblResultRow rr WHERE term = @term AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 14
UPDATE tblZStudentReport SET Sbj15_EName = Sbj_EName, Sbj15_CName = Sbj_CName, Sbj15_1 = Sbj_1, Sbj15_2 = Sbj_2, Sbj15_3 = Sbj_3, Lsn_15 = Lsn, Asm_15 = Asm FROM tblZStudentReport zsr, ##tblResultRow rr WHERE term = @term AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 15
UPDATE tblZStudentReport SET Sbj16_EName = Sbj_EName, Sbj16_CName = Sbj_CName, Sbj16_1 = Sbj_1, Sbj16_2 = Sbj_2, Sbj16_3 = Sbj_3, Lsn_16 = Lsn, Asm_16 = Asm FROM tblZStudentReport zsr, ##tblResultRow rr WHERE term = @term AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 16
UPDATE tblZStudentReport SET Sbj17_EName = Sbj_EName, Sbj17_CName = Sbj_CName, Sbj17_1 = Sbj_1, Sbj17_2 = Sbj_2, Sbj17_3 = Sbj_3, Lsn_17 = Lsn, Asm_17 = Asm FROM tblZStudentReport zsr, ##tblResultRow rr WHERE term = @term AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 17
UPDATE tblZStudentReport SET Sbj18_EName = Sbj_EName, Sbj18_CName = Sbj_CName, Sbj18_1 = Sbj_1, Sbj18_2 = Sbj_2, Sbj18_3 = Sbj_3, Lsn_18 = Lsn, Asm_18 = Asm FROM tblZStudentReport zsr, ##tblResultRow rr WHERE term = @term AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 18
UPDATE tblZStudentReport SET Sbj19_EName = Sbj_EName, Sbj19_CName = Sbj_CName, Sbj19_1 = Sbj_1, Sbj19_2 = Sbj_2, Sbj19_3 = Sbj_3, Lsn_19 = Lsn, Asm_19 = Asm FROM tblZStudentReport zsr, ##tblResultRow rr WHERE term = @term AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 19
UPDATE tblZStudentReport SET Sbj20_EName = Sbj_EName, Sbj20_CName = Sbj_CName, Sbj20_1 = Sbj_1, Sbj20_2 = Sbj_2, Sbj20_3 = Sbj_3, Lsn_20 = Lsn, Asm_20 = Asm FROM tblZStudentReport zsr, ##tblResultRow rr WHERE term = @term AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 20
UPDATE tblZStudentReport SET Sbj21_EName = Sbj_EName, Sbj21_CName = Sbj_CName, Sbj21_1 = Sbj_1, Sbj21_2 = Sbj_2, Sbj21_3 = Sbj_3, Lsn_21 = Lsn, Asm_21 = Asm FROM tblZStudentReport zsr, ##tblResultRow rr WHERE term = @term AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 21
UPDATE tblZStudentReport SET Sbj22_EName = Sbj_EName, Sbj22_CName = Sbj_CName, Sbj22_1 = Sbj_1, Sbj22_2 = Sbj_2, Sbj22_3 = Sbj_3, Lsn_22 = Lsn, Asm_22 = Asm FROM tblZStudentReport zsr, ##tblResultRow rr WHERE term = @term AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 22
UPDATE tblZStudentReport SET Sbj23_EName = Sbj_EName, Sbj23_CName = Sbj_CName, Sbj23_1 = Sbj_1, Sbj23_2 = Sbj_2, Sbj23_3 = Sbj_3, Lsn_23 = Lsn, Asm_23 = Asm FROM tblZStudentReport zsr, ##tblResultRow rr WHERE term = @term AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 23
UPDATE tblZStudentReport SET Sbj24_EName = Sbj_EName, Sbj24_CName = Sbj_CName, Sbj24_1 = Sbj_1, Sbj24_2 = Sbj_2, Sbj24_3 = Sbj_3, Lsn_24 = Lsn, Asm_24 = Asm FROM tblZStudentReport zsr, ##tblResultRow rr WHERE term = @term AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 24
UPDATE tblZStudentReport SET Sbj25_EName = Sbj_EName, Sbj25_CName = Sbj_CName, Sbj25_1 = Sbj_1, Sbj25_2 = Sbj_2, Sbj25_3 = Sbj_3, Lsn_25 = Lsn, Asm_25 = Asm FROM tblZStudentReport zsr, ##tblResultRow rr WHERE term = @term AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 25
UPDATE tblZStudentReport SET Sbj26_EName = Sbj_EName, Sbj26_CName = Sbj_CName, Sbj26_1 = Sbj_1, Sbj26_2 = Sbj_2, Sbj26_3 = Sbj_3, Lsn_26 = Lsn, Asm_26 = Asm FROM tblZStudentReport zsr, ##tblResultRow rr WHERE term = @term AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 26
UPDATE tblZStudentReport SET Sbj27_EName = Sbj_EName, Sbj27_CName = Sbj_CName, Sbj27_1 = Sbj_1, Sbj27_2 = Sbj_2, Sbj27_3 = Sbj_3, Lsn_27 = Lsn, Asm_27 = Asm FROM tblZStudentReport zsr, ##tblResultRow rr WHERE term = @term AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 27

--average
IF @form < 6
BEGIN
	UPDATE tblZStudentReport SET ave1 = '(' + replace(convert(nvarchar(6), convert(decimal(7,1), zsr.score_1 / 10.0)), '.0', '') + ')' FROM tblZStudentRank zsr, tblZStudentReport zr WHERE term = @term AND zr.form = @form AND zsr.idStudent = zr.idStudent AND zsr.score_1< 500
	UPDATE tblZStudentReport SET ave1 = replace(convert(nvarchar(6), convert(decimal(7,1), zsr.score_1 / 10.0)), '.0', '') FROM tblZStudentRank zsr, tblZStudentReport zr WHERE term = @term AND zr.form = @form AND zsr.idStudent = zr.idStudent AND zsr.score_1>=  500
	IF @term = 2
	BEGIN
		UPDATE tblZStudentReport SET ave2 = '(' + replace(convert(nvarchar(6), convert(decimal(7,1), zsr.score_2 / 10.0)), '.0', '') + ')' FROM tblZStudentRank zsr, tblZStudentReport zr WHERE term = @term AND zr.form = @form AND zsr.idStudent = zr.idStudent AND zsr.score_2 < 500
		UPDATE tblZStudentReport SET ave2 =  replace(convert(nvarchar(6), convert(decimal(7,1), zsr.score_2 / 10.0)), '.0', '') FROM tblZStudentRank zsr, tblZStudentReport zr WHERE term = @term AND zr.form = @form AND zsr.idStudent = zr.idStudent AND zsr.score_2 >=  500
		UPDATE tblZStudentReport SET ave3 = '(' + replace(convert(nvarchar(6), convert(decimal(7,1), zsr.score_final / 10.0)), '.0', '') + ')' FROM tblZStudentRank zsr, tblZStudentReport zr WHERE term = @term AND zr.form = @form AND zsr.idStudent = zr.idStudent AND zsr.score_final < 500
		UPDATE tblZStudentReport SET ave3 = replace(convert(nvarchar(6), convert(decimal(7,1), zsr.score_final / 10.0)), '.0', '') FROM tblZStudentRank zsr, tblZStudentReport zr WHERE term = @term AND zr.form = @form AND zsr.idStudent = zr.idStudent AND zsr.score_final >=  500
	END
END
ELSE
BEGIN
	UPDATE tblZStudentReport SET ave1 = '--' FROM tblZStudentReport zr WHERE term = @term AND zr.form = @form
	IF @term = 2
	BEGIN
		UPDATE tblZStudentReport SET ave2 = '--', ave3 = '--' FROM tblZStudentReport zr WHERE term = @term AND zr.form = @form
	END
END

--class rank
IF @term = 1
	IF @form = 3
	BEGIN
		UPDATE tblZStudentReport
SET CRank1 = convert(nvarchar(5), rank_class_1) + '/' + convert(nvarchar(5), r.numStudent)
FROM tblZStudentRank zsr, tblZStudentReport zr, tblStudent s, (
SELECT class, count( * ) as numStudent
FROM tblStudent
GROUP BY class) r
WHERE term = @term AND zr.form = @form AND zsr.idStudent = zr.idStudent AND s.idStudent = zsr.idStudent AND r.class = s.class AND zsr.rank_class_1 <= 3
		UPDATE tblZStudentReport SET CRank1 = '--' FROM tblZStudentRank zsr, tblZStudentReport zr WHERE term = @term AND zr.form = @form AND zsr.idStudent = zr.idStudent AND zsr.rank_class_1 > 3
	END
	ELSE
	BEGIN
		IF @form >= 6
		BEGIN
			UPDATE tblZStudentReport SET CRank1 = '--' FROM tblZStudentRank zsr, tblZStudentReport zr WHERE term = @term AND zr.form = @form AND zsr.idStudent = zr.idStudent
		END
		ELSE
		BEGIN
			UPDATE tblZStudentReport SET CRank1 = convert(nvarchar(5), rank_class_1) + '/' + convert(nvarchar(5), r.numStudent) FROM tblZStudentRank zsr, tblZStudentReport zr, tblStudent s, (SELECT class, count(*) as numStudent FROM tblStudent GROUP BY class) r WHERE term = @term AND zr.form = @form AND zsr.idStudent = zr.idStudent AND s.idStudent = zsr.idStudent AND r.class = s.class
		END
	END
ELSE
BEGIN
	UPDATE tblZStudentReport SET CRank1 = '--' WHERE term = @term AND form = @form
	UPDATE tblZStudentReport SET CRank2 = '--' WHERE term = @term AND form = @form

	IF @form = 3
	BEGIN
		UPDATE tblZStudentReport SET CRank3 = convert(nvarchar(5), rank_class_final) + '/' + convert(nvarchar(5), r.numStudent) FROM tblZStudentRank zsr, tblZStudentReport zr, tblStudent s, (SELECT class, count(*) as numStudent FROM tblStudent s INNER JOIN tblZStudentRank zsr ON s.idStudent = zsr.idStudent GROUP BY class) r WHERE term = @term AND zr.form = @form AND zsr.idStudent = zr.idStudent AND s.idStudent = zsr.idStudent AND r.class = s.class AND zsr.rank_class_final <= 3
		UPDATE tblZStudentReport SET CRank3 = '--' FROM tblZStudentRank zsr, tblZStudentReport zr WHERE term = @term AND zr.form = @form AND zsr.idStudent = zr.idStudent AND zsr.rank_class_final > 3
	END
	ELSE
	BEGIN
		IF @form >= 6
		BEGIN
			UPDATE tblZStudentReport SET CRank3 = '--' FROM tblZStudentRank zsr, tblZStudentReport zr WHERE term = @term AND zr.form = @form AND zsr.idStudent = zr.idStudent
		END
		ELSE
		BEGIN
			UPDATE tblZStudentReport SET CRank3 = convert(nvarchar(5), rank_class_final) + '/' + convert(nvarchar(5), r.numStudent) FROM tblZStudentRank zsr, tblZStudentReport zr, tblStudent s, (SELECT class, count(*) as numStudent FROM tblStudent s INNER JOIN tblZStudentRank zsr ON s.idStudent = zsr.idStudent GROUP BY class) r WHERE term = @term AND zr.form = @form AND zsr.idStudent = zr.idStudent AND s.idStudent = zsr.idStudent AND r.class = s.class
		END
	END
END

--form rank
IF @form >= 3
BEGIN
	UPDATE tblZStudentReport SET FRank1 = '--' WHERE term = @term AND form = @form
	IF @term = 2
	BEGIN
		UPDATE tblZStudentReport SET FRank2 = '--' WHERE term = @term AND form = @form
		UPDATE tblZStudentReport SET FRank3 = '--' WHERE term = @term AND form = @form
	END
END
ELSE
BEGIN
	IF @term = 1
		UPDATE tblZStudentReport SET FRank1 = convert(nvarchar(5), rank_form_1) + '/' + convert(nvarchar(5), r.numStudent) FROM tblZStudentRank zsr, tblZStudentReport zr, tblStudent s, (SELECT form, count(*) as numStudent FROM tblStudent s INNER JOIN tblClass c ON s.class = c.class INNER JOIN tblZStudentRank zsr ON s.idStudent = zsr.idStudent GROUP BY form) r WHERE term = @term AND zr.form = @form AND zsr.idStudent = zr.idStudent AND s.idStudent = zsr.idStudent AND r.form = zr.form
	ELSE
	BEGIN
		UPDATE tblZStudentReport SET FRank1 = '--' WHERE term = @term AND form = @form
		UPDATE tblZStudentReport SET FRank2 = '--' WHERE term = @term AND form = @form
		UPDATE tblZStudentReport SET FRank3 = convert(nvarchar(5), rank_form_final) + '/' + convert(nvarchar(5), r.numStudent) FROM tblZStudentRank zsr, tblZStudentReport zr, tblStudent s, (SELECT form, count(*) as numStudent FROM tblStudent s INNER JOIN tblClass c ON s.class = c.class INNER JOIN tblZStudentRank zsr ON s.idStudent = zsr.idStudent GROUP BY form) r WHERE term = @term AND zr.form = @form AND zsr.idStudent = zr.idStudent AND s.idStudent = zsr.idStudent AND r.form = zr.form
	END
END

--days present
UPDATE tblZStudentReport SET Attend1 = convert(nvarchar (10), sd.dayAbsent_1) FROM tblStudentDiscipline sd, tblZStudentReport zsr INNER JOIN tblFormDayPresent fdp ON term = @term AND zsr.form = @form AND fdp.form = @form WHERE sd.idStudent = zsr.idStudent
IF @term = 2
BEGIN
	UPDATE tblZStudentReport SET Attend2 = convert(nvarchar (10), sd.dayAbsent_2) FROM tblStudentDiscipline sd, tblZStudentReport zsr WHERE sd.idStudent = zsr.idStudent
	UPDATE tblZStudentReport SET Attend3 = convert(nvarchar (10), sd.dayAbsent_1 + sd.dayAbsent_2) FROM tblStudentDiscipline sd, tblZStudentReport zsr WHERE sd.idStudent = zsr.idStudent
END

--times late
UPDATE tblZStudentReport SET Late1 = convert(nvarchar (10), numLate_1) FROM tblStudentDiscipline sd, tblZStudentReport zsr WHERE term = @term AND form = @form AND sd.idStudent = zsr.idStudent
IF @term = 2
BEGIN
	UPDATE tblZStudentReport SET Late2 = convert(nvarchar (10), numLate_2) FROM tblStudentDiscipline sd, tblZStudentReport zsr WHERE term = @term AND form = @form AND sd.idStudent = zsr.idStudent
	UPDATE tblZStudentReport SET Late3 = convert(nvarchar (10), numLate_1 + numLate_2) FROM tblStudentDiscipline sd, tblZStudentReport zsr WHERE term = @term AND form = @form AND sd.idStudent = zsr.idStudent
END

--conduct
IF @term = 1
BEGIN
	UPDATE tblZStudentReport SET Cnd01 = conduct_1_1 FROM tblZStudentReport zsr, tblStudentConduct sc WHERE term = @term AND form = @form AND zsr.idStudent = sc.idStudent AND conduct_1_1 is not null
	UPDATE tblZStudentReport SET Cnd02 = conduct_2_1 FROM tblZStudentReport zsr, tblStudentConduct sc WHERE term = @term AND form = @form AND zsr.idStudent = sc.idStudent AND conduct_2_1 is not null
	UPDATE tblZStudentReport SET Cnd03 = conduct_3_1 FROM tblZStudentReport zsr, tblStudentConduct sc WHERE term = @term AND form = @form AND zsr.idStudent = sc.idStudent AND conduct_3_1 is not null
	UPDATE tblZStudentReport SET Cnd04 = conduct_4_1 FROM tblZStudentReport zsr, tblStudentConduct sc WHERE term = @term AND form = @form AND zsr.idStudent = sc.idStudent AND conduct_4_1 is not null
	UPDATE tblZStudentReport SET Cnd05 = conduct_5_1 FROM tblZStudentReport zsr, tblStudentConduct sc WHERE term = @term AND form = @form AND zsr.idStudent = sc.idStudent AND conduct_5_1 is not null
END
ELSE
BEGIN
	UPDATE tblZStudentReport SET Cnd01 = conduct_1_2 FROM tblZStudentReport zsr, tblStudentConduct sc WHERE term = @term AND form = @form AND zsr.idStudent = sc.idStudent AND conduct_1_2 is not null
	UPDATE tblZStudentReport SET Cnd02 = conduct_2_2 FROM tblZStudentReport zsr, tblStudentConduct sc WHERE term = @term AND form = @form AND zsr.idStudent = sc.idStudent AND conduct_2_2 is not null
	UPDATE tblZStudentReport SET Cnd03 = conduct_3_2 FROM tblZStudentReport zsr, tblStudentConduct sc WHERE term = @term AND form = @form AND zsr.idStudent = sc.idStudent AND conduct_3_2 is not null
	UPDATE tblZStudentReport SET Cnd04 = conduct_4_2 FROM tblZStudentReport zsr, tblStudentConduct sc WHERE term = @term AND form = @form AND zsr.idStudent = sc.idStudent AND conduct_4_2 is not null
	UPDATE tblZStudentReport SET Cnd05 = conduct_5_2 FROM tblZStudentReport zsr, tblStudentConduct sc WHERE term = @term AND form = @form AND zsr.idStudent = sc.idStudent AND conduct_5_2 is not null
END

--comment
IF @term = 1
BEGIN
	UPDATE tblZStudentReport SET Cmt01 = custom_1_1 FROM tblZStudentReport zsr, tblStudentComment sc WHERE term = @term AND form = @form AND zsr.idStudent = sc.idStudent AND custom_1_1 is not null
	UPDATE tblZStudentReport SET Cmt02 = custom_2_1 FROM tblZStudentReport zsr, tblStudentComment sc WHERE term = @term AND form = @form AND zsr.idStudent = sc.idStudent AND custom_2_1 is not null
	UPDATE tblZStudentReport SET Cmt03 = custom_3_1 FROM tblZStudentReport zsr, tblStudentComment sc WHERE term = @term AND form = @form AND zsr.idStudent = sc.idStudent AND custom_3_1 is not null
	UPDATE tblZStudentReport SET Cmt04 = custom_4_1 FROM tblZStudentReport zsr, tblStudentComment sc WHERE term = @term AND form = @form AND zsr.idStudent = sc.idStudent AND custom_4_1 is not null

	UPDATE tblZStudentReport SET Cmt01 = comment FROM tblZStudentReport zsr, tblStudentComment sc, tblComment c WHERE term = @term AND form = @form AND zsr.idStudent = sc.idStudent AND sc.comment_1_1 = c.idComment AND sc.comment_1_1 is not null
	UPDATE tblZStudentReport SET Cmt02 = comment FROM tblZStudentReport zsr, tblStudentComment sc, tblComment c WHERE term = @term AND form = @form AND zsr.idStudent = sc.idStudent AND sc.comment_2_1 = c.idComment AND sc.comment_2_1 is not null
	UPDATE tblZStudentReport SET Cmt03 = comment FROM tblZStudentReport zsr, tblStudentComment sc, tblComment c WHERE term = @term AND form = @form AND zsr.idStudent = sc.idStudent AND sc.comment_3_1 = c.idComment AND sc.comment_3_1 is not null
	UPDATE tblZStudentReport SET Cmt04 = comment FROM tblZStudentReport zsr, tblStudentComment sc, tblComment c WHERE term = @term AND form = @form AND zsr.idStudent = sc.idStudent AND sc.comment_4_1 = c.idComment AND sc.comment_4_1 is not null
END
ELSE
BEGIN
	UPDATE tblZStudentReport SET Cmt01 = custom_1_2 FROM tblZStudentReport zsr, tblStudentComment sc WHERE term = @term AND form = @form AND zsr.idStudent = sc.idStudent AND custom_1_2 is not null
	UPDATE tblZStudentReport SET Cmt02 = custom_2_2 FROM tblZStudentReport zsr, tblStudentComment sc WHERE term = @term AND form = @form AND zsr.idStudent = sc.idStudent AND custom_2_2 is not null
	UPDATE tblZStudentReport SET Cmt03 = custom_3_2 FROM tblZStudentReport zsr, tblStudentComment sc WHERE term = @term AND form = @form AND zsr.idStudent = sc.idStudent AND custom_3_2 is not null
	UPDATE tblZStudentReport SET Cmt04 = custom_4_2 FROM tblZStudentReport zsr, tblStudentComment sc WHERE term = @term AND form = @form AND zsr.idStudent = sc.idStudent AND custom_4_2 is not null

	UPDATE tblZStudentReport SET Cmt01 = comment FROM tblZStudentReport zsr, tblStudentComment sc, tblComment c WHERE term = @term AND form = @form AND zsr.idStudent = sc.idStudent AND sc.comment_1_2 = c.idComment AND sc.comment_1_2 is not null
	UPDATE tblZStudentReport SET Cmt02 = comment FROM tblZStudentReport zsr, tblStudentComment sc, tblComment c WHERE term = @term AND form = @form AND zsr.idStudent = sc.idStudent AND sc.comment_2_2 = c.idComment AND sc.comment_2_2 is not null
	UPDATE tblZStudentReport SET Cmt03 = comment FROM tblZStudentReport zsr, tblStudentComment sc, tblComment c WHERE term = @term AND form = @form AND zsr.idStudent = sc.idStudent AND sc.comment_3_2 = c.idComment AND sc.comment_3_2 is not null
	UPDATE tblZStudentReport SET Cmt04 = comment FROM tblZStudentReport zsr, tblStudentComment sc, tblComment c WHERE term = @term AND form = @form AND zsr.idStudent = sc.idStudent AND sc.comment_4_2 = c.idComment AND sc.comment_4_2 is not null
END

--service
UPDATE tblZStudentReport SET Srv01 = srv FROM tblZStudentReport zsr, ##tblServiceRow sr WHERE term = @term AND form = @form AND zsr.idStudent = sr.idStudent AND sr.row = 1
UPDATE tblZStudentReport SET Srv02 = srv FROM tblZStudentReport zsr, ##tblServiceRow sr WHERE term = @term AND form = @form AND zsr.idStudent = sr.idStudent AND sr.row = 2
UPDATE tblZStudentReport SET Srv03 = srv FROM tblZStudentReport zsr, ##tblServiceRow sr WHERE term = @term AND form = @form AND zsr.idStudent = sr.idStudent AND sr.row = 3
UPDATE tblZStudentReport SET Srv04 = srv FROM tblZStudentReport zsr, ##tblServiceRow sr WHERE term = @term AND form = @form AND zsr.idStudent = sr.idStudent AND sr.row = 4

--remark
UPDATE tblZStudentReport SET Rem01 = rem FROM tblZStudentReport zsr, ##tblRemarkRow rr WHERE term = @term AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 1
UPDATE tblZStudentReport SET Rem02 = rem FROM tblZStudentReport zsr, ##tblRemarkRow rr WHERE term = @term AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 2
UPDATE tblZStudentReport SET Rem03 = rem FROM tblZStudentReport zsr, ##tblRemarkRow rr WHERE term = @term AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 3
UPDATE tblZStudentReport SET Rem04 = rem FROM tblZStudentReport zsr, ##tblRemarkRow rr WHERE term = @term AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 4
UPDATE tblZStudentReport SET Rem05 = rem FROM tblZStudentReport zsr, ##tblRemarkRow rr WHERE term = @term AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 5
UPDATE tblZStudentReport SET Rem06 = rem FROM tblZStudentReport zsr, ##tblRemarkRow rr WHERE term = @term AND form = @form AND zsr.idStudent = rr.idStudent AND rr.row = 6

GO

------------------------------------------------------------------------------------------------
-- stpGenerateReport
------------------------------------------------------------------------------------------------

if exists (select * from dbo.sysobjects where id = object_id(N'[dbo].[stpGenerateReport]') and OBJECTPROPERTY(id, N'IsProcedure') = 1)
drop procedure [dbo].[stpGenerateReport]
GO

CREATE PROCEDURE dbo.stpGenerateReport
@form tinyint, @term tinyint
AS

EXEC stpInitializeReport @form, @term

-- Result
IF @form = 5 or @form = 7 --(For 1 Term Case)
BEGIN
	INSERT ##tblResultRow (idStudent, row, idSubject, flgScore, Sbj_EName, Sbj_CName, Sbj_1, Sbj_2, Sbj_3, Lsn, Asm)
	SELECT s.idStudent, 0,
	CASE WHEN su.idSubject is null THEN sx.idSubject ELSE su.idSubject END,
	CASE WHEN flgScore is null THEN 1 ELSE flgScore END,
	CASE WHEN r.idPaper = su.idSubject THEN '' ELSE N'　'  END + p.nameEnglish + CASE WHEN p.remarkEnglish is not null THEN ' ' + p.remarkEnglish ELSE '' END,
	CASE WHEN r.idPaper = su.idSubject THEN '' ELSE N'　'  END + p.nameChinese + CASE WHEN p.remarkChinese is not null THEN ' ' + p.remarkChinese ELSE '' END,
	r.result_1,
	r.result_2,
	N'　' + CASE WHEN r.idPaper = su.idSubject THEN '' ELSE N'　'  END + r.result_final,
	CASE WHEN r.idPaper = su.idSubject THEN
		CASE WHEN sa.lesson_2 is null THEN '--' ELSE sa.lesson_2 + N'　' + a3.nameChinese END
	ELSE ''
	END,
	CASE WHEN r.idPaper = su.idSubject THEN
		CASE WHEN sa.assessment_2 is null THEN '--' ELSE sa.assessment_2 + N'　' + a4.nameChinese END
	ELSE ''
	END
	FROM tblStudent s
	INNER JOIN tblClass c ON s.class = c.class
	INNER JOIN tblForm f ON c.form = f.form  AND f.form = @form
	INNER JOIN (
	SELECT zspr.idStudent, zspr.idPaper,
	CASE WHEN p.idSubject is null THEN
		''
	ELSE
		CASE WHEN zspr.flgIgnore_1 = 1 
		THEN ' #'
		ELSE
			CASE WHEN score_1 is null 
			THEN ' --'
			ELSE 
				CASE WHEN score_1 < 495 THEN N'(' + convert(nvarchar(6), convert(decimal(7,0), score_1 / 10.0)) + CASE WHEN flgRemark_1 = 1 THEN N'*' ELSE N'' END + N')' ELSE  ' ' + convert(nvarchar(6), convert(decimal(7,0), score_1 / 10.0)) + CASE WHEN flgRemark_1 = 1 THEN N'*' ELSE N'' END END		
			END
		END 
	END AS result_1,
	CASE WHEN p.idSubject is null THEN
		''
	ELSE
		CASE WHEN zspr.flgIgnore_2 = 1 
		THEN ' #'
		ELSE
			CASE WHEN score_2 is null 
			THEN ' --'
			ELSE 
				CASE WHEN score_2 < 495 THEN N'(' + convert(nvarchar(6), convert(decimal(7,0), score_2 / 10.0)) + CASE WHEN flgRemark_2 = 1 THEN N'*' ELSE N'' END + N')' ELSE  ' ' + convert(nvarchar(6), convert(decimal(7,0), score_2 / 10.0)) + CASE WHEN flgRemark_2 = 1 THEN N'*' ELSE N'' END END
			END
		END
	END AS result_2,
	CASE WHEN zspr.flgIgnore_1 = 1 AND zspr.flgIgnore_2 = 1 AND p.idSubject is not null
	THEN '#'
	ELSE
		CASE WHEN score_final is null 
		THEN '--'
		ELSE 
			CASE WHEN score_final < 495 THEN N'(' + convert(nvarchar(6), convert(decimal(7,0), score_final / 10.0)) + CASE WHEN flgRemark_2 = 1 THEN N'*' ELSE N'' END + N')' ELSE  ' ' + convert(nvarchar(6), convert(decimal(7,0), score_final / 10.0)) + CASE WHEN flgRemark_2 = 1 THEN N'*' ELSE N'' END END
		END 
	END AS result_final
	FROM tblZStudentPaperRank zspr
	INNER JOIN tblStudent s ON zspr.idStudent = s.idStudent
	INNER JOIN tblClass c ON s.class = c.class AND c.form = @form
	INNER JOIN tblForm f ON c.form = f.form
	INNER JOIN tblPaper p ON p.formGroup = f.formGroup AND p.idPaper = zspr.idPaper AND p.flgScore = 1
	UNION
	SELECT sps.idStudent, sps.idPaper, ' --' as result_1, ' --' as result_2,
	CASE WHEN grade_exam_1 is null THEN
		CASE WHEN grade_exam_2 is null THEN
			' --'
		ELSE
			CASE WHEN grade_exam_2 in ('D') THEN '(' + grade_exam_2 + ')' ELSE ' ' + grade_exam_2 END
		END
	ELSE
		CASE WHEN grade_exam_1 in ('D') THEN '(' + grade_exam_1 + ')' ELSE ' ' + grade_exam_1 END
	END AS result_final
	FROM tblStudentPaperScore sps
	INNER JOIN tblStudent s ON sps.idStudent = s.idStudent
	INNER JOIN tblClass c ON s.class = c.class AND c.form = @form
	INNER JOIN tblForm f ON c.form = f.form
	INNER JOIN tblPaper p ON p.formGroup = f.formGroup AND p.idPaper = sps.idPaper AND p.flgScore = 0
	) r ON r.idStudent = s.idStudent
	INNER JOIN
	(tblPaper p
	LEFT JOIN tblSubject sx ON sx.idSubject = p.idSubject) ON p.idPaper = r.idPaper AND p.formGroup = f.formGroup
	LEFT JOIN tblSubject su ON su.idSubject = r.idPaper
	LEFT JOIN tblStudentAttitude sa ON s.idStudent = sa.idStudent AND r.idPaper = sa.idSubject
	LEFT JOIN tblAttitude a1 on sa.lesson_1 = a1.grade
	LEFT JOIN tblAttitude a2 on sa.assessment_1 = a2.grade
	LEFT JOIN tblAttitude a3 on sa.lesson_2 = a3.grade
	LEFT JOIN tblAttitude a4 on sa.assessment_2 = a4.grade
	ORDER BY s.class, s.numberClass, p.keyOrder
END
ELSE
BEGIN
	INSERT ##tblResultRow (idStudent, row, idSubject,  flgScore, Sbj_EName, Sbj_CName, Sbj_1, Sbj_2, Sbj_3, Lsn, Asm)
	SELECT s.idStudent, 0,
	CASE WHEN su.idSubject is null THEN sx.idSubject ELSE su.idSubject END,
	CASE WHEN flgScore is null THEN 1 ELSE flgScore END,
	CASE WHEN r.idPaper = su.idSubject THEN '' ELSE N'　'  END + p.nameEnglish + CASE WHEN p.remarkEnglish is not null THEN ' ' + p.remarkEnglish ELSE '' END,
	CASE WHEN r.idPaper = su.idSubject THEN '' ELSE N'　'  END + p.nameChinese + CASE WHEN p.remarkChinese is not null THEN ' ' + p.remarkChinese ELSE '' END,
	N'　' + CASE WHEN r.idPaper = su.idSubject THEN '' ELSE N'　'  END + r.result_1,
	N'　' + CASE WHEN r.idPaper = su.idSubject THEN '' ELSE N'　'  END + CASE WHEN @term = 1 THEN '' ELSE r.result_2 END,
	        CASE WHEN r.idPaper = su.idSubject THEN CASE WHEN @term = 1 THEN '' ELSE r.result_final END ELSE '' END,
	CASE WHEN r.idPaper = su.idSubject THEN
		CASE WHEN @term = 1 THEN
			CASE WHEN sa.lesson_1 is null THEN '--' ELSE sa.lesson_1 + N'　' + a1.nameChinese END
		ELSE
			CASE WHEN @form < 4 THEN
				CASE WHEN sa.lesson_2 is null THEN
					CASE WHEN sa.lesson_1 is null THEN '--' ELSE sa.lesson_1 + N'　' + a1.nameChinese END
				ELSE
					sa.lesson_2 + N'　' + a3.nameChinese
				END
			ELSE
				CASE WHEN sa.lesson_2 is null THEN '--' ELSE sa.lesson_2 + N'　' + a3.nameChinese END
			END
		END
	ELSE ''
	END,
	CASE WHEN r.idPaper = su.idSubject THEN
		CASE WHEN @term = 1 THEN
			CASE WHEN sa.assessment_1 is null THEN '--' ELSE sa.assessment_1 + N'　' + a2.nameChinese END
		ELSE
			CASE WHEN @form < 4 THEN
				CASE WHEN sa.assessment_2 is null THEN
					CASE WHEN sa.assessment_1 is null THEN '--' ELSE sa.assessment_1 + N'　' + a2.nameChinese END
				ELSE
					sa.assessment_2 + N'　' + a4.nameChinese
				END
			ELSE
				CASE WHEN sa.assessment_2 is null THEN '--' ELSE sa.assessment_2 + N'　' + a4.nameChinese END
			END
		END
	ELSE ''
	END
	FROM tblStudent s
	INNER JOIN tblClass c ON s.class = c.class
	INNER JOIN tblForm f ON c.form = f.form  AND f.form = @form
	INNER JOIN (
	SELECT zspr.idStudent, zspr.idPaper,
	CASE WHEN zspr.flgIgnore_1 = 1 
	THEN ' #'
	ELSE 
		CASE WHEN score_1 is null 
		THEN ' --'
		ELSE 
			CASE WHEN score_1 < 495 THEN N'(' + convert(nvarchar(6), convert(decimal(7,0), score_1 / 10.0)) + CASE WHEN flgRemark_1 = 1 THEN N'*' ELSE N'' END + N')' ELSE  ' ' + convert(nvarchar(6), convert(decimal(7,0), score_1 / 10.0)) + CASE WHEN flgRemark_1 = 1 THEN N'*' ELSE N'' END END
		END
	END AS result_1,
	CASE WHEN zspr.flgIgnore_2 = 1 
	THEN ' #'
	ELSE 
		CASE WHEN score_2 is null 
		THEN ' --'
		ELSE 
			CASE WHEN score_2 < 495 THEN N'(' + convert(nvarchar(6), convert(decimal(7,0), score_2 / 10.0)) + CASE WHEN flgRemark_2 = 1 THEN N'*' ELSE N'' END + N')' ELSE  ' ' + convert(nvarchar(6), convert(decimal(7,0), score_2 / 10.0)) + CASE WHEN flgRemark_2 = 1 THEN N'*' ELSE N'' END END
		END 
	END AS result_2,
	CASE WHEN zspr.flgIgnore_1 = 1 AND zspr.flgIgnore_2 = 1 AND p.idSubject is not null
	THEN '#'
	ELSE
		CASE WHEN score_final is null 
		THEN '--'
		ELSE 
			CASE WHEN score_final < 495 THEN N'(' + convert(nvarchar(6), convert(decimal(7,0), score_final / 10.0)) + N')' ELSE  ' ' + convert(nvarchar(6), convert(decimal(7,0), score_final / 10.0)) END
		END
	END AS result_final
	FROM tblZStudentPaperRank zspr
	INNER JOIN tblStudent s ON zspr.idStudent = s.idStudent
	INNER JOIN tblClass c ON s.class = c.class AND c.form = @form
	INNER JOIN tblForm f ON c.form = f.form
	INNER JOIN tblPaper p ON p.formGroup = f.formGroup AND p.idPaper = zspr.idPaper AND p.flgScore = 1
	UNION
	SELECT sps.idStudent, sps.idPaper,
	CASE WHEN grade_exam_1 is null THEN
		'--'
	ELSE
		CASE WHEN grade_exam_1 in ('D') THEN '(' + grade_exam_1 + ')' ELSE ' ' + grade_exam_1 END
	END AS result_1,
	CASE WHEN grade_exam_2 is null THEN
		'--'
	ELSE
		CASE WHEN grade_exam_2 in ('D') THEN '(' + grade_exam_2 + ')' ELSE ' ' + grade_exam_2 END
	END AS result_2,
	'' AS result_final
	FROM tblStudentPaperScore sps
	INNER JOIN tblStudent s ON sps.idStudent = s.idStudent
	INNER JOIN tblClass c ON s.class = c.class AND c.form = @form
	INNER JOIN tblForm f ON c.form = f.form
	INNER JOIN tblPaper p ON p.formGroup = f.formGroup AND p.idPaper = sps.idPaper AND p.flgScore = 0
	) r ON r.idStudent = s.idStudent
	INNER JOIN
	(tblPaper p
	LEFT JOIN tblSubject sx ON sx.idSubject = p.idSubject) ON p.idPaper = r.idPaper AND p.formGroup = f.formGroup
	LEFT JOIN tblSubject su ON su.idSubject = r.idPaper
	LEFT JOIN tblStudentAttitude sa ON s.idStudent = sa.idStudent AND r.idPaper = sa.idSubject
	LEFT JOIN tblAttitude a1 on sa.lesson_1 = a1.grade
	LEFT JOIN tblAttitude a2 on sa.assessment_1 = a2.grade
	LEFT JOIN tblAttitude a3 on sa.lesson_2 = a3.grade
	LEFT JOIN tblAttitude a4 on sa.assessment_2 = a4.grade
	ORDER BY s.class, s.numberClass, p.keyOrder
END

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

UPDATE ##tblResultRow
SET row = row + 1
WHERE idSubject = 'PBL'

-- Service
INSERT ##tblServiceRow (idStudent, row, srv)
SELECT s.idStudent, 0, srv
FROM tblStudent s
INNER JOIN tblClass c ON s.class = c.class
INNER JOIN tblForm f ON c.form = f.form  AND f.form = @form
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
ORDER BY s.idStudent, r.src

UPDATE ##tblServiceRow
SET row = tpr.idRow - r.min_row + 1
FROM ##tblServiceRow tpr, (
SELECT idStudent, min(idRow) AS min_row
FROM ##tblServiceRow
GROUP BY idStudent) r
WHERE r.idStudent = tpr.idStudent

-- Key Row
INSERT ##tblKeyRow (idStudent, row, [key])
SELECT idStudent, 0, [key]
FROM (
SELECT distinct zspr.idStudent, N'不及格之分數均以 (　) 表示' as [key], 0 as keyKey
FROM tblZStudentPaperRank zspr
INNER JOIN tblStudent s ON zspr.idStudent = s.idStudent
INNER JOIN tblClass c ON s.class = c.class
INNER JOIN tblForm f ON c.form = f.form  AND f.form = @form
WHERE score_1 < 495 OR score_2 < 495
UNION
SELECT distinct sps.idStudent, N'不及格之分數均以 (　) 表示' as [key], 0 as keyKey
FROM tblStudentPaperScore sps
INNER JOIN tblStudent s ON sps.idStudent = s.idStudent
INNER JOIN tblClass c ON s.class = c.class
INNER JOIN tblForm f ON c.form = f.form  AND f.form = @form
WHERE grade_exam_1 in ('D') OR grade_exam_2 in ('D')
UNION
SELECT distinct sps.idStudent, N'獲豁免應考之科目以 # 表示' as [key], 1 as keyKey
FROM tblStudentPaperScore sps
INNER JOIN tblStudent s ON sps.idStudent = s.idStudent
INNER JOIN tblClass c ON s.class = c.class
INNER JOIN tblForm f ON c.form = f.form  AND f.form = @form
WHERE grade_exam_1 = '#' OR grade_exam_2 = '#' OR flgIgnore_1 = 1 OR flgIgnore_2 = 1
UNION
SELECT distinct zspr.idStudent, N'有 * 號者代表因缺考而獲評估之分數' as [key], 2 as keyKey
FROM tblZStudentPaperRank zspr
INNER JOIN tblStudent s ON zspr.idStudent = s.idStudent
INNER JOIN tblClass c ON s.class = c.class
INNER JOIN tblForm f ON c.form = f.form  AND f.form = @form
WHERE flgRemark_1 = 1 OR flgRemark_2 = 1
) r
ORDER BY idStudent, keyKey

UPDATE ##tblKeyRow
SET row = tpr.idRow - r.min_row + 1
FROM ##tblKeyRow tpr, (
SELECT idStudent, min(idRow) AS min_row
FROM ##tblKeyRow
GROUP BY idStudent) r
WHERE r.idStudent = tpr.idStudent

-- Key
INSERT ##tblKey (idStudent, flgNewLine, key01, key02, key03, key04, key05, key06, key07, key08, key09, key10, key11, key12)
SELECT idStudent, 0, [key], '', '', '', '', '', '', '', '', '', '', ''
FROM ##tblKeyRow
WHERE row = 1

UPDATE ##tblKey SET key02 = [key] FROM ##tblKey key2, ##tblKeyRow keyr WHERE key2.idStudent = keyr.idStudent AND row = 2
UPDATE ##tblKey SET key03 = [key] FROM ##tblKey key2, ##tblKeyRow keyr WHERE key2.idStudent = keyr.idStudent AND row = 3
UPDATE ##tblKey SET key04 = [key] FROM ##tblKey key2, ##tblKeyRow keyr WHERE key2.idStudent = keyr.idStudent AND row = 4
UPDATE ##tblKey SET key05 = [key] FROM ##tblKey key2, ##tblKeyRow keyr WHERE key2.idStudent = keyr.idStudent AND row = 5
UPDATE ##tblKey SET key06 = [key] FROM ##tblKey key2, ##tblKeyRow keyr WHERE key2.idStudent = keyr.idStudent AND row = 6
UPDATE ##tblKey SET key07 = [key] FROM ##tblKey key2, ##tblKeyRow keyr WHERE key2.idStudent = keyr.idStudent AND row = 7
UPDATE ##tblKey SET key08 = [key] FROM ##tblKey key2, ##tblKeyRow keyr WHERE key2.idStudent = keyr.idStudent AND row = 8
UPDATE ##tblKey SET key09 = [key] FROM ##tblKey key2, ##tblKeyRow keyr WHERE key2.idStudent = keyr.idStudent AND row = 9
UPDATE ##tblKey SET key10 = [key] FROM ##tblKey key2, ##tblKeyRow keyr WHERE key2.idStudent = keyr.idStudent AND row = 10
UPDATE ##tblKey SET key11 = [key] FROM ##tblKey key2, ##tblKeyRow keyr WHERE key2.idStudent = keyr.idStudent AND row = 11
UPDATE ##tblKey SET key12 = [key] FROM ##tblKey key2, ##tblKeyRow keyr WHERE key2.idStudent = keyr.idStudent AND row = 12

UPDATE ##tblKey SET key01 = key01 + N'、' WHERE key02 <> ''
UPDATE ##tblKey SET key02 = key02 + N'、' WHERE key03 <> ''
UPDATE ##tblKey SET key03 = key03 + N'、' WHERE key04 <> ''
UPDATE ##tblKey SET key04 = key04 + N'、' WHERE key05 <> ''
UPDATE ##tblKey SET key05 = key05 + N'、' WHERE key06 <> ''
UPDATE ##tblKey SET key06 = key06 + N'、' WHERE key07 <> ''
UPDATE ##tblKey SET key07 = key07 + N'、' WHERE key08 <> ''
UPDATE ##tblKey SET key08 = key08 + N'、' WHERE key09 <> ''
UPDATE ##tblKey SET key09 = key09 + N'、' WHERE key10 <> ''
UPDATE ##tblKey SET key10 = key10 + N'、' WHERE key11 <> ''
UPDATE ##tblKey SET key11 = key11 + N'、' WHERE key12 <> ''

UPDATE ##tblKey SET key01 = key01 + char(13) + char(10), flgNewLine = 1
WHERE flgNewLine = 0 AND len(key01 + key02) > 54
UPDATE ##tblKey SET key02 = key02 + char(13) + char(10), flgNewLine = 1
WHERE flgNewLine = 0 AND len(key01 + key02 + key03) > 54
UPDATE ##tblKey SET key03 = key03 + char(13) + char(10), flgNewLine = 1
WHERE flgNewLine = 0 AND len(key01 + key02 + key03 + key04) > 54
UPDATE ##tblKey SET key04 = key04 + char(13) + char(10), flgNewLine = 1
WHERE flgNewLine = 0 AND len(key01 + key02 + key03 + key04 + key05) > 54
UPDATE ##tblKey SET key05 = key05 + char(13) + char(10), flgNewLine = 1
WHERE flgNewLine = 0 AND len(key01 + key02 + key03 + key04 + key05 + key06) > 54
UPDATE ##tblKey SET key06 = key06 + char(13) + char(10), flgNewLine = 1
WHERE flgNewLine = 0 AND len(key01 + key02 + key03 + key04 + key05 + key06 + key07) > 54
UPDATE ##tblKey SET key07 = key07 + char(13) + char(10), flgNewLine = 1
WHERE flgNewLine = 0 AND len(key01 + key02 + key03 + key04 + key05 + key06 + key07 + key08) > 54
UPDATE ##tblKey SET key08 = key08 + char(13) + char(10), flgNewLine = 1
WHERE flgNewLine = 0 AND len(key01 + key02 + key03 + key04 + key05 + key06 + key07 + key08 + key09) > 54
UPDATE ##tblKey SET key09 = key09 + char(13) + char(10), flgNewLine = 1
WHERE flgNewLine = 0 AND len(key01 + key02 + key03 + key04 + key05 + key06 + key07 + key08 + key09 + key10) > 54
UPDATE ##tblKey SET key10 = key10 + char(13) + char(10), flgNewLine = 1
WHERE flgNewLine = 0 AND len(key01 + key02 + key03 + key04 + key05 + key06 + key07 + key08 + key09 + key10 + key11) > 54
UPDATE ##tblKey SET key11 = key11 + char(13) + char(10), flgNewLine = 1
WHERE flgNewLine = 0 AND len(key01 + key02 + key03 + key04 + key05 + key06 + key07 + key08 + key09 + key10 + key11 + key12) > 54

-- ECA Row
INSERT ##tblECARow (idStudent, row, eca)
SELECT s.idStudent, 0,  replace(u.nameChinese + CASE WHEN p.idPost <> 101 THEN p.nameChinese ELSE '' END + CASE WHEN ecac.nameChinese is not null THEN '(' + ecac.nameChinese + ')' ELSE '' END, ' ', '') AS srv
FROM tblStudent s
INNER JOIN tblClass c ON s.class = c.class
INNER JOIN tblForm f ON c.form = f.form  AND f.form = @form
INNER JOIN tblStudentUnitPost sup ON s.idStudent = sup.idStudent
INNER JOIN tblUnit u ON u.idUnit = sup.idUnit
INNER JOIN tblPost p ON p.idPost = sup.idPost
LEFT JOIN tblECAComment ecac ON ecac.idComment = sup.idComment AND @term = 2
WHERE idUnitGroup not in (7, 9)
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

IF @form < 6
BEGIN
	--Weight Row
	INSERT ##tblWeightRow (idStudent, row, wgt)
	SELECT s.idStudent, 0, CASE WHEN p.nameChinese is not null THEN p.nameChinese ELSE sj.nameChinese END + convert(nvarchar(5), weight)
	FROM tblStudent s
	INNER JOIN tblClass c ON s.class = c.class
	INNER JOIN tblForm f ON c.form = f.form  AND f.form = @form
	INNER JOIN tblStudentSubject ss ON ss.idStudent = s.idStudent
	INNER JOIN tblSubject sj ON ss.idSubject = sj.idSubject
	INNER JOIN tblFormPaperWeight fpw ON f.form = fpw.form AND ss.idSubject = fpw.idPaper AND weight > 0
	LEFT JOIN tblPaper p ON p.idPaper = fpw.idPaper AND p.formGroup = f.formGroup
	ORDER BY s.idStudent, sj.keyOrder

	UPDATE ##tblWeightRow
	SET row = tpr.idRow - r.min_row + 1
	FROM ##tblWeightRow tpr, (
	SELECT idStudent, min(idRow) AS min_row
	FROM ##tblWeightRow
	GROUP BY idStudent) r
	WHERE r.idStudent = tpr.idStudent

	--Weight
	INSERT ##tblWeight (idStudent, flgNewLine, wgt01, wgt02, wgt03, wgt04, wgt05, wgt06, wgt07, wgt08, wgt09, wgt10, wgt11, wgt12)
	SELECT idStudent, 0, wgt, '', '', '', '', '', '', '', '', '', '', ''
	FROM ##tblWeightRow
	WHERE row = 1

	UPDATE ##tblWeight SET wgt02 = wgt FROM ##tblWeight wgt, ##tblWeightRow wgtr WHERE wgt.idStudent = wgtr.idStudent AND row = 2
	UPDATE ##tblWeight SET wgt03 = wgt FROM ##tblWeight wgt, ##tblWeightRow wgtr WHERE wgt.idStudent = wgtr.idStudent AND row = 3
	UPDATE ##tblWeight SET wgt04 = wgt FROM ##tblWeight wgt, ##tblWeightRow wgtr WHERE wgt.idStudent = wgtr.idStudent AND row = 4
	UPDATE ##tblWeight SET wgt05 = wgt FROM ##tblWeight wgt, ##tblWeightRow wgtr WHERE wgt.idStudent = wgtr.idStudent AND row = 5
	UPDATE ##tblWeight SET wgt06 = wgt FROM ##tblWeight wgt, ##tblWeightRow wgtr WHERE wgt.idStudent = wgtr.idStudent AND row = 6
	UPDATE ##tblWeight SET wgt07 = wgt FROM ##tblWeight wgt, ##tblWeightRow wgtr WHERE wgt.idStudent = wgtr.idStudent AND row = 7
	UPDATE ##tblWeight SET wgt08 = wgt FROM ##tblWeight wgt, ##tblWeightRow wgtr WHERE wgt.idStudent = wgtr.idStudent AND row = 8
	UPDATE ##tblWeight SET wgt09 = wgt FROM ##tblWeight wgt, ##tblWeightRow wgtr WHERE wgt.idStudent = wgtr.idStudent AND row = 9
	UPDATE ##tblWeight SET wgt10 = wgt FROM ##tblWeight wgt, ##tblWeightRow wgtr WHERE wgt.idStudent = wgtr.idStudent AND row = 10
	UPDATE ##tblWeight SET wgt11 = wgt FROM ##tblWeight wgt, ##tblWeightRow wgtr WHERE wgt.idStudent = wgtr.idStudent AND row = 11
	UPDATE ##tblWeight SET wgt12 = wgt FROM ##tblWeight wgt, ##tblWeightRow wgtr WHERE wgt.idStudent = wgtr.idStudent AND row = 12

	UPDATE ##tblWeight SET wgt01 = wgt01 + N' ' WHERE wgt02 <> ''
	UPDATE ##tblWeight SET wgt02 = wgt02 + N' ' WHERE wgt03 <> ''
	UPDATE ##tblWeight SET wgt03 = wgt03 + N' ' WHERE wgt04 <> ''
	UPDATE ##tblWeight SET wgt04 = wgt04 + N' ' WHERE wgt05 <> ''
	UPDATE ##tblWeight SET wgt05 = wgt05 + N' ' WHERE wgt06 <> ''
	UPDATE ##tblWeight SET wgt06 = wgt06 + N' ' WHERE wgt07 <> ''
	UPDATE ##tblWeight SET wgt07 = wgt07 + N' ' WHERE wgt08 <> ''
	UPDATE ##tblWeight SET wgt08 = wgt08 + N' ' WHERE wgt09 <> ''
	UPDATE ##tblWeight SET wgt09 = wgt09 + N' ' WHERE wgt10 <> ''
	UPDATE ##tblWeight SET wgt10 = wgt10 + N' ' WHERE wgt11 <> ''
	UPDATE ##tblWeight SET wgt11 = wgt11 + N' ' WHERE wgt12 <> ''

	UPDATE ##tblWeight SET wgt01 = wgt01 + char(13) + char(10), flgNewLine = 1
	WHERE flgNewLine = 0 AND len(wgt01 + wgt02) > 66
	UPDATE ##tblWeight SET wgt02 = wgt02 + char(13) + char(10), flgNewLine = 1
	WHERE flgNewLine = 0 AND len(wgt01 + wgt02 + wgt03) > 66
	UPDATE ##tblWeight SET wgt03 = wgt03 + char(13) + char(10), flgNewLine = 1
	WHERE flgNewLine = 0 AND len(wgt01 + wgt02 + wgt03 + wgt04) > 66
	UPDATE ##tblWeight SET wgt04 = wgt04 + char(13) + char(10), flgNewLine = 1
	WHERE flgNewLine = 0 AND len(wgt01 + wgt02 + wgt03 + wgt04 + wgt05) > 66
	UPDATE ##tblWeight SET wgt05 = wgt05 + char(13) + char(10), flgNewLine = 1
	WHERE flgNewLine = 0 AND len(wgt01 + wgt02 + wgt03 + wgt04 + wgt05 + wgt06) > 66
	UPDATE ##tblWeight SET wgt06 = wgt06 + char(13) + char(10), flgNewLine = 1
	WHERE flgNewLine = 0 AND len(wgt01 + wgt02 + wgt03 + wgt04 + wgt05 + wgt06 + wgt07) > 66
	UPDATE ##tblWeight SET wgt07 = wgt07 + char(13) + char(10), flgNewLine = 1
	WHERE flgNewLine = 0 AND len(wgt01 + wgt02 + wgt03 + wgt04 + wgt05 + wgt06 + wgt07 + wgt08) > 66
	UPDATE ##tblWeight SET wgt08 = wgt08 + char(13) + char(10), flgNewLine = 1
	WHERE flgNewLine = 0 AND len(wgt01 + wgt02 + wgt03 + wgt04 + wgt05 + wgt06 + wgt07 + wgt08 + wgt09) > 66
	UPDATE ##tblWeight SET wgt09 = wgt09 + char(13) + char(10), flgNewLine = 1
	WHERE flgNewLine = 0 AND len(wgt01 + wgt02 + wgt03 + wgt04 + wgt05 + wgt06 + wgt07 + wgt08 + wgt09 + wgt10) > 66
END

IF @term = 2
BEGIN
	-- Award Row
	INSERT ##tblAwardRow (idStudent, row, awd)
	SELECT idStudent, 0, awd
	FROM (
	SELECT s.idStudent, sa.nameChinese as awd, sa.idRow as idRow
	FROM tblStudent s
	INNER JOIN tblClass c ON s.class = c.class
	INNER JOIN tblForm f ON c.form = f.form  AND f.form = @form
	INNER JOIN tblStudentAward sa ON sa.idStudent = s.idStudent AND sa.term = @term
	UNION
	SELECT s.idStudent, u.nameChinese + case p.idPost when 101 then '' else p.nameChinese end as awd, 100 as idRow
	from tblStudent s
	INNER JOIN tblClass c ON s.class = c.class
	INNER JOIN tblForm f ON c.form = f.form  AND f.form = @form
	INNER JOIN tblStudentUnitPost sup ON sup.idStudent = s.idStudent
	INNER JOIN tblUnit u ON sup.idUnit = u.idUnit and idUnitGroup = 9
	INNER JOIN tblPost p ON sup.idPost = p.idPost
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

--Remark
INSERT ##tblRemarkRow (idStudent, row, rem)
SELECT idStudent, 0, rem
FROM (
SELECT idStudent, key01 + key02 + key03 + key04 + key05 + key06 + key07 + key08 + key09 + key10 + key11 + key12 as rem, 1 as src
FROM ##tblKey
UNION
SELECT idStudent, N'各科比重為：' + wgt01 + wgt02 + wgt03 + wgt04 + wgt05 + wgt06 + wgt07 + wgt08 + wgt09 + wgt10 + wgt11 + wgt12 as rem, 2 as src
FROM ##tblWeight
UNION
SELECT idStudent, N'獲' + awd01 + awd02 + awd03 + awd04 + awd05 + awd06 + awd07 + awd08 + awd09 + awd10 + awd11 + awd12 as rem, 3 as src
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
as rem, 4 as src
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
	INNER JOIN tblStudent s ON sr.idStudent = s.idStudent
	INNER JOIN tblClass c ON s.class = c.class
	INNER JOIN tblForm f ON c.form = f.form AND f.form = @form AND @term = 1
	WHERE numMerit1_1 > 0 OR numMerit2_1 > 0 OR numMerit3_1 > 0 OR numMerit4_1 > 0
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
	INNER JOIN tblStudent s ON sr.idStudent = s.idStudent
	INNER JOIN tblClass c ON s.class = c.class
	INNER JOIN tblForm f ON c.form = f.form AND f.form = @form AND @term = 2
	WHERE numMerit1_2 > 0 OR numMerit2_2 > 0 OR numMerit3_2 > 0 OR numMerit4_2 > 0
) r
UNION
SELECT distinct idStudent,
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
ELSE ''END as rem, 5 as src
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
	INNER JOIN tblStudent s ON sd.idStudent = s.idStudent
	INNER JOIN tblClass c ON s.class = c.class
	INNER JOIN tblForm f ON c.form = f.form AND f.form = @form AND @term = 1
	WHERE numDemeritDS_1 > 0 OR numDemeritHW_1 > 0
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
	INNER JOIN tblStudent s ON sd.idStudent = s.idStudent
	INNER JOIN tblClass c ON s.class = c.class 
	INNER JOIN tblForm f ON c.form = f.form AND f.form = @form AND @term = 2
	WHERE numDemeritDS_2 > 0 OR numDemeritHW_2 > 0
) r
UNION
SELECT idStudent, eca01 + eca02 + eca03 + eca04 + eca05 + eca06 + eca07 + eca08 + eca09 + eca10 + eca11 + eca12 as rem, 6 as src
FROM ##tblECA
UNION
SELECT srr.idStudent, srr.nameChinese as rem, 100 + row as src
FROM tblStudentReportRemark srr
INNER JOIN tblStudent s ON srr.idStudent = s.idStudent AND srr.term = @term
INNER JOIN tblClass c ON s.class = c.class
INNER JOIN tblForm f ON c.form = f.form  AND f.form = @form
) r
ORDER BY idStudent, src

UPDATE ##tblRemarkRow
SET row = tpr.idRow - r.min_row + 1
FROM ##tblRemarkRow tpr, (
SELECT idStudent, min(idRow) AS min_row
FROM ##tblRemarkRow
GROUP BY idStudent) r
WHERE r.idStudent = tpr.idStudent

exec stpOutputReport @form, @term

GO

------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------
--stpGenerateReport 5, 2
--GO

--stpGenerateReport 7, 2
--GO
stpGenerateReport 1, 2
GO

stpGenerateReport 2, 2
GO

stpGenerateReport 3, 2
GO

stpGenerateReport 4, 2
GO

stpGenerateReport 6, 2
GO
