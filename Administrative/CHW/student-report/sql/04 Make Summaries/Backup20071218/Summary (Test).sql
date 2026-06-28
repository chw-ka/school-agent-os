------------------------------------------------------------------------------------------------
-- stpOutputTestPaperRankScore
------------------------------------------------------------------------------------------------

if exists (select * from dbo.sysobjects where id = object_id(N'[dbo].[stpOutputTestPaperRankScore]') and OBJECTPROPERTY(id, N'IsProcedure') = 1)
drop procedure [dbo].[stpOutputTestPaperRankScore]
GO

CREATE PROCEDURE dbo.stpOutputTestPaperRankScore
@form tinyint, @test tinyint
AS

--score_1, score_2

IF @test = 1
BEGIN
	-- Initialize Term 1
	INSERT tblZStudentTestPaperRank (idStudent, idPaper)
	SELECT DISTINCT sps.idStudent, p.idSubject
	FROM tblStudentPaperScore sps
	INNER JOIN tblStudent s ON s.idStudent = sps.idStudent 
	INNER JOIN tblClass c ON s.class = c.class
	INNER JOIN tblForm f ON f.form = c.form
	INNER JOIN tblPaper p ON p.idPaper = sps.idPaper and p.formGroup = f.formGroup
	WHERE sps.score_test_1 is not null AND sps.idPaper IN (
	SELECT p.idPaper
	FROM tblForm f
	INNER JOIN tblPaper p ON f.formGroup = p.formGroup
	WHERE f.form = @form AND p.flgScore = 1) AND sps.idStudent IN (
	SELECT idStudent
	FROM tblStudent s
	INNER JOIN tblClass c ON s.class = c.class
	WHERE form = @form)
	AND NOT EXISTS (
	SELECT idStudent, idPaper
	FROM tblZStudentTestPaperRank zstpr
	WHERE idStudent IN (
	SELECT idStudent
	FROM tblStudent s
	INNER JOIN tblClass c ON s.class = c.class
	WHERE form = @form AND zstpr.idStudent = s.idStudent)
	)

	--score_1
	UPDATE tblZStudentTestPaperRank
	SET score_1 = null, flgRemark_1 = 0
	FROM tblZStudentTestPaperRank
	WHERE idStudent IN (
	SELECT idStudent
	FROM tblStudent s
	INNER JOIN tblClass c ON s.class = c.class
	WHERE form = @form)

	UPDATE tblZStudentTestPaperRank
	SET score_1 = cast(1000.0 as real) * sps.score_test_1 / fps.score_test_1, flgRemark_1 = sps.flgRemark_1
	FROM tblZStudentTestPaperRank zstpr, tblStudentPaperScore sps
	INNER JOIN tblFormPaperScore fps ON fps.idPaper = sps.idPaper AND fps.form = @form
	INNER JOIN tblForm f ON f.form = fps.form 
	INNER JOIN tblPaper p ON p.formGroup = f.formGroup AND sps.idPaper = p.idPaper
	WHERE zstpr.idStudent = sps.idStudent AND zstpr.idPaper = p.idSubject AND sps.score_test_1 is not null AND sps.idPaper IN (
	SELECT p.idPaper
	FROM tblForm f
	INNER JOIN tblPaper p ON f.formGroup = p.formGroup
	WHERE f.form = @form AND p.flgScore = 1) AND sps.idStudent IN (
	SELECT idStudent
	FROM tblStudent s
	INNER JOIN tblClass c ON s.class = c.class
	WHERE form = @form)
END
ELSE
BEGIN
	-- Initialize Term 2
	INSERT tblZStudentTestPaperRank (idStudent, idPaper)
	SELECT DISTINCT sps.idStudent, p.idSubject
	FROM tblStudentPaperScore sps
	INNER JOIN tblStudent s ON s.idStudent = sps.idStudent 
	INNER JOIN tblClass c ON s.class = c.class
	INNER JOIN tblForm f ON f.form = c.form
	INNER JOIN tblPaper p ON p.idPaper = sps.idPaper and p.formGroup = f.formGroup
	WHERE sps.score_test_2 is not null AND sps.idPaper IN (
	SELECT p.idPaper
	FROM tblForm f
	INNER JOIN tblPaper p ON f.formGroup = p.formGroup
	WHERE f.form = @form AND p.flgScore = 1) AND sps.idStudent IN (
	SELECT idStudent
	FROM tblStudent s
	INNER JOIN tblClass c ON s.class = c.class
	WHERE form = @form)
	AND NOT EXISTS (
	SELECT idStudent, idPaper
	FROM tblZStudentTestPaperRank zstpr
	WHERE idStudent IN (
	SELECT idStudent
	FROM tblStudent s
	INNER JOIN tblClass c ON s.class = c.class
	WHERE form = @form AND zstpr.idStudent = s.idStudent)
	)

	--score_2
	UPDATE tblZStudentTestPaperRank
	SET score_2 = null, flgRemark_2 = 0
	FROM tblZStudentTestPaperRank zstpr
	WHERE idStudent IN (
	SELECT idStudent
	FROM tblStudent s
	INNER JOIN tblClass c ON s.class = c.class
	WHERE form = @form)

	UPDATE tblZStudentTestPaperRank
	SET score_2 = cast(1000.0 as real) * sps.score_test_2 / fps.score_test_2, flgRemark_2 = sps.flgRemark_2
	FROM tblZStudentTestPaperRank zstpr, tblStudentPaperScore sps
	INNER JOIN tblFormPaperScore fps ON fps.idPaper = sps.idPaper AND fps.form = @form
	INNER JOIN tblForm f ON f.form = fps.form 
	INNER JOIN tblPaper p ON p.formGroup = f.formGroup AND sps.idPaper = p.idPaper
	WHERE zstpr.idStudent = sps.idStudent AND zstpr.idPaper = p.idSubject AND sps.score_test_2 is not null AND sps.idPaper IN (
	SELECT p.idPaper
	FROM tblForm f
	INNER JOIN tblPaper p ON f.formGroup = p.formGroup
	WHERE f.form = @form AND p.flgScore = 1) AND sps.idStudent IN (
	SELECT idStudent
	FROM tblStudent s
	INNER JOIN tblClass c ON s.class = c.class
	WHERE form = @form)
END

--clear unnecessary entities
DELETE
FROM tblZStudentTestPaperRank
WHERE score_1 is null AND score_2 is null

GO

------------------------------------------------------------------------------------------------
-- stpOutputTestPaperRank
------------------------------------------------------------------------------------------------

if exists (select * from dbo.sysobjects where id = object_id(N'[dbo].[stpOutputTestPaperRank]') and OBJECTPROPERTY(id, N'IsProcedure') = 1)
drop procedure [dbo].[stpOutputTestPaperRank]
GO

CREATE PROCEDURE dbo.stpOutputTestPaperRank
@form tinyint
AS

--class
UPDATE tblZStudentTestPaperRank
SET rank_class_1 = null
FROM tblZStudentTestPaperRank zstpr
INNER JOIN tblStudent s ON zstpr.idStudent = s.idStudent
INNER JOIN tblClass c ON s.class = c.class
WHERE form = @form

UPDATE tblZStudentTestPaperRank
SET rank_class_2 = null
FROM tblZStudentTestPaperRank zstpr
INNER JOIN tblStudent s ON zstpr.idStudent = s.idStudent
INNER JOIN tblClass c ON s.class = c.class
WHERE form = @form

UPDATE tblZStudentTestPaperRank
SET rank_class_1 = rank
FROM (
SELECT idStudent, idPaper, count(idStudent) + 1 AS rank
FROM (
SELECT zstpr1.idStudent, zstpr1.idPaper, zstpr1.score_1
FROM tblZStudentTestPaperRank zstpr1
INNER JOIN tblStudent s1 ON zstpr1.idStudent = s1.idStudent
INNER JOIN tblClass c1 ON s1.class = c1.class, tblZStudentTestPaperRank zstpr2
INNER JOIN tblStudent s2 ON zstpr2.idStudent = s2.idStudent
WHERE zstpr2.idPaper = zstpr1.idPaper AND zstpr1.score_1 < zstpr2.score_1 AND c1.form = @form AND s1.class = s2.class ) rA
GROUP BY idStudent, idPaper ) rB, tblZStudentTestPaperRank zstpr
WHERE zstpr.idStudent = rB.idStudent AND zstpr.idPaper = rB.idPaper

UPDATE tblZStudentTestPaperRank
SET rank_class_2 = rank
FROM (
SELECT idStudent, idPaper, count(idStudent) + 1 AS rank
FROM (
SELECT zstpr1.idStudent, zstpr1.idPaper, zstpr1.score_2
FROM tblZStudentTestPaperRank zstpr1
INNER JOIN tblStudent s1 ON zstpr1.idStudent = s1.idStudent
INNER JOIN tblClass c1 ON s1.class = c1.class, tblZStudentTestPaperRank zstpr2
INNER JOIN tblStudent s2 ON zstpr2.idStudent = s2.idStudent
WHERE zstpr2.idPaper = zstpr1.idPaper AND zstpr1.score_2 < zstpr2.score_2 AND c1.form = @form AND s1.class = s2.class ) rA
GROUP BY idStudent, idPaper ) rB, tblZStudentTestPaperRank zstpr
WHERE zstpr.idStudent = rB.idStudent AND zstpr.idPaper = rB.idPaper

UPDATE tblZStudentTestPaperRank
SET rank_class_1 = 1
FROM tblZStudentTestPaperRank zstpr
INNER JOIN tblStudent s ON zstpr.idStudent = s.idStudent
INNER JOIN tblClass c ON s.class = c.class
WHERE form = @form AND score_1 is NOT null AND rank_class_1 is null

UPDATE tblZStudentTestPaperRank
SET rank_class_2 = 1
FROM tblZStudentTestPaperRank zstpr
INNER JOIN tblStudent s ON zstpr.idStudent = s.idStudent
INNER JOIN tblClass c ON s.class = c.class
WHERE form = @form AND score_2 is NOT null AND rank_class_2 is null

--form
UPDATE tblZStudentTestPaperRank
SET rank_form_1 = null
FROM tblZStudentTestPaperRank zstpr
INNER JOIN tblStudent s ON zstpr.idStudent = s.idStudent
INNER JOIN tblClass c ON s.class = c.class
WHERE form = @form

UPDATE tblZStudentTestPaperRank
SET rank_form_2 = null
FROM tblZStudentTestPaperRank zstpr
INNER JOIN tblStudent s ON zstpr.idStudent = s.idStudent
INNER JOIN tblClass c ON s.class = c.class
WHERE form = @form

UPDATE tblZStudentTestPaperRank
SET rank_form_1 = rank
FROM (
SELECT idStudent, idPaper, count(idStudent) + 1 AS rank
FROM (
SELECT zstpr1.idStudent, zstpr1.idPaper, zstpr1.score_1
FROM tblZStudentTestPaperRank zstpr1
INNER JOIN tblStudent s1 ON zstpr1.idStudent = s1.idStudent
INNER JOIN tblClass c1 ON s1.class = c1.class, tblZStudentTestPaperRank zstpr2
INNER JOIN tblStudent s2 ON zstpr2.idStudent = s2.idStudent
INNER JOIN tblClass c2 ON s2.class = c2.class
WHERE zstpr2.idPaper = zstpr1.idPaper AND zstpr1.score_1 < zstpr2.score_1 AND c1.form = @form AND c1.form = c2.form ) rA
GROUP BY idStudent, idPaper ) rB, tblZStudentTestPaperRank zstpr
WHERE zstpr.idStudent = rB.idStudent AND zstpr.idPaper = rB.idPaper

UPDATE tblZStudentTestPaperRank
SET rank_form_2 = rank
FROM (
SELECT idStudent, idPaper, count(idStudent) + 1 AS rank
FROM (
SELECT zstpr1.idStudent, zstpr1.idPaper, zstpr1.score_2
FROM tblZStudentTestPaperRank zstpr1
INNER JOIN tblStudent s1 ON zstpr1.idStudent = s1.idStudent
INNER JOIN tblClass c1 ON s1.class = c1.class, tblZStudentTestPaperRank zstpr2
INNER JOIN tblStudent s2 ON zstpr2.idStudent = s2.idStudent
INNER JOIN tblClass c2 ON s2.class = c2.class
WHERE zstpr2.idPaper = zstpr1.idPaper AND zstpr1.score_2 < zstpr2.score_2 AND c1.form = @form AND c1.form = c2.form ) rA
GROUP BY idStudent, idPaper ) rB, tblZStudentTestPaperRank zstpr
WHERE zstpr.idStudent = rB.idStudent AND zstpr.idPaper = rB.idPaper

UPDATE tblZStudentTestPaperRank
SET rank_form_1 = 1
FROM tblZStudentTestPaperRank zstpr
INNER JOIN tblStudent s ON zstpr.idStudent = s.idStudent
INNER JOIN tblClass c ON s.class = c.class
WHERE form = @form AND score_1 is NOT null AND rank_form_1 is null

UPDATE tblZStudentTestPaperRank
SET rank_form_2 = 1
FROM tblZStudentTestPaperRank zstpr
INNER JOIN tblStudent s ON zstpr.idStudent = s.idStudent
INNER JOIN tblClass c ON s.class = c.class
WHERE form = @form AND score_2 is NOT null AND rank_form_2 is null

GO

------------------------------------------------------------------------------------------------
-- stpOutputTestRankScore
------------------------------------------------------------------------------------------------

if exists (select * from dbo.sysobjects where id = object_id(N'[dbo].[stpOutputTestRankScore]') and OBJECTPROPERTY(id, N'IsProcedure') = 1)
drop procedure [dbo].[stpOutputTestRankScore]
GO

CREATE PROCEDURE dbo.stpOutputTestRankScore
@form tinyint, @test tinyint
AS

IF @test = 1
BEGIN
	-- score_1
	INSERT tblZStudentTestRank (idStudent)
	SELECT DISTINCT zstpr.idStudent
	FROM tblZStudentTestPaperRank zstpr
	INNER JOIN tblStudent s ON s.idStudent = zstpr.idStudent
	INNER JOIN tblClass c ON s.class = c.class
	INNER JOIN tblForm f ON f.form = c.form
	INNER JOIN tblFormPaperWeight fpw ON zstpr.idPaper = fpw.idPaper AND c.form = @form AND c.form = fpw.form
	INNER JOIN tblPaper p ON zstpr.idPaper = p.idSubject AND p.formGroup = f.formGroup
	WHERE score_1 is not null AND NOT EXISTS (
	SELECT idStudent
	FROM tblZStudentTestRank zstr
	WHERE idStudent IN (
	SELECT idStudent
	FROM tblStudent s
	INNER JOIN tblClass c ON s.class = c.class
	WHERE form = @form AND zstpr.idStudent = zstr.idStudent)
	)

	UPDATE tblZStudentTestRank
	SET score_1 = null
	FROM tblZStudentTestRank zstr
	INNER JOIN tblStudent s ON zstr.idStudent = s.idStudent
	INNER JOIN tblClass c ON s.class = c.class
	WHERE form = @form

	UPDATE tblZStudentTestRank
	SET score_1 = r.score_1
	FROM tblZStudentTestRank zstr,
	(SELECT zstpr.idStudent, score_1 = floor(sum(floor(score_1 / 10.0 + .5) * 10.0 * weight) / sum(weight) + .5)
	FROM tblZStudentTestPaperRank zstpr
	INNER JOIN tblSubject sj ON sj.idSubject = zstpr.idPaper
	INNER JOIN tblStudent s ON s.idStudent = zstpr.idStudent
	INNER JOIN tblClass c ON s.class = c.class
	INNER JOIN tblForm f ON f.form = c.form
	INNER JOIN tblFormPaperWeight fpw ON zstpr.idPaper = fpw.idPaper AND c.form = @form AND c.form = fpw.form AND weight > 0
	WHERE zstpr.score_1 is not null
	GROUP BY zstpr.idStudent) r
	WHERE zstr.idStudent = r.idStudent
END
ELSE
BEGIN
	-- score_2
	INSERT tblZStudentTestRank (idStudent)
	SELECT DISTINCT zstpr.idStudent
	FROM tblZStudentTestPaperRank zstpr
	INNER JOIN tblStudent s ON s.idStudent = zstpr.idStudent
	INNER JOIN tblClass c ON s.class = c.class
	INNER JOIN tblForm f ON f.form = c.form
	INNER JOIN tblFormPaperWeight fpw ON zstpr.idPaper = fpw.idPaper AND c.form = @form AND c.form = fpw.form
	INNER JOIN tblPaper p ON zstpr.idPaper = p.idSubject AND p.formGroup = f.formGroup
	WHERE score_2 is not null AND NOT EXISTS (
	SELECT idStudent
	FROM tblZStudentTestRank zstr
	WHERE idStudent IN (
	SELECT idStudent
	FROM tblStudent s
	INNER JOIN tblClass c ON s.class = c.class
	WHERE form = @form AND zstpr.idStudent = zstr.idStudent)
	)

	UPDATE tblZStudentTestRank
	SET score_2 = null
	FROM tblZStudentTestRank zstr
	INNER JOIN tblStudent s ON zstr.idStudent = s.idStudent
	INNER JOIN tblClass c ON s.class = c.class
	WHERE form = @form

	UPDATE tblZStudentTestRank
	SET score_2 = r.score_2
	FROM tblZStudentTestRank zstr,
	(SELECT zstpr.idStudent, score_2 = floor(sum(floor(score_2 / 10.0 + .5) * 10.0 * weight) / sum(weight) + .5)
	FROM tblZStudentTestPaperRank zstpr
	INNER JOIN tblSubject sj ON sj.idSubject = zstpr.idPaper
	INNER JOIN tblStudent s ON s.idStudent = zstpr.idStudent
	INNER JOIN tblClass c ON s.class = c.class
	INNER JOIN tblForm f ON f.form = c.form
	INNER JOIN tblFormPaperWeight fpw ON zstpr.idPaper = fpw.idPaper AND c.form = @form AND c.form = fpw.form AND weight > 0
	WHERE zstpr.score_2 is not null
	GROUP BY zstpr.idStudent) r
	WHERE zstr.idStudent = r.idStudent
END

DELETE
FROM tblZStudentTestRank
WHERE score_1 is null and score_2 is null

GO


------------------------------------------------------------------------------------------------
-- stpOutputTestRank
------------------------------------------------------------------------------------------------

if exists (select * from dbo.sysobjects where id = object_id(N'[dbo].[stpOutputTestRank]') and OBJECTPROPERTY(id, N'IsProcedure') = 1)
drop procedure [dbo].[stpOutputTestRank]
GO

CREATE PROCEDURE dbo.stpOutputTestRank
@form tinyint
AS

--class
UPDATE tblZStudentTestRank
SET rank_class_1 = null
FROM tblZStudentTestRank zstr
INNER JOIN tblStudent s ON zstr.idStudent = s.idStudent
INNER JOIN tblClass c ON s.class = c.class
WHERE form = @form

UPDATE tblZStudentTestRank
SET rank_class_2 = null
FROM tblZStudentTestRank zstr
INNER JOIN tblStudent s ON zstr.idStudent = s.idStudent
INNER JOIN tblClass c ON s.class = c.class
WHERE form = @form

UPDATE tblZStudentTestRank
SET rank_class_1 = rank
FROM (
SELECT idStudent, count(idStudent) + 1 AS rank
FROM (
SELECT zstr1.idStudent, zstr1.score_1
FROM tblZStudentTestRank zstr1
INNER JOIN tblStudent s1 ON zstr1.idStudent = s1.idStudent
INNER JOIN tblClass c1 ON s1.class = c1.class, tblZStudentTestRank zstr2
INNER JOIN tblStudent s2 ON zstr2.idStudent = s2.idStudent
WHERE zstr1.score_1 < zstr2.score_1 AND c1.form = @form AND s1.class = s2.class ) rA
GROUP BY idStudent ) rB, tblZStudentTestRank zstr
WHERE zstr.idStudent = rB.idStudent

UPDATE tblZStudentTestRank
SET rank_class_2 = rank
FROM (
SELECT idStudent, count(idStudent) + 1 AS rank
FROM (
SELECT zstr1.idStudent, zstr1.score_2
FROM tblZStudentTestRank zstr1
INNER JOIN tblStudent s1 ON zstr1.idStudent = s1.idStudent
INNER JOIN tblClass c1 ON s1.class = c1.class, tblZStudentTestRank zstr2
INNER JOIN tblStudent s2 ON zstr2.idStudent = s2.idStudent
WHERE zstr1.score_2 < zstr2.score_2 AND c1.form = @form AND s1.class = s2.class ) rA
GROUP BY idStudent ) rB, tblZStudentTestRank zstr
WHERE zstr.idStudent = rB.idStudent

UPDATE tblZStudentTestRank
SET rank_class_1 = 1
FROM tblZStudentTestRank zstr
INNER JOIN tblStudent s ON zstr.idStudent = s.idStudent
INNER JOIN tblClass c ON s.class = c.class
WHERE form = @form AND score_1 is NOT null AND rank_class_1 is null

UPDATE tblZStudentTestRank
SET rank_class_2 = 1
FROM tblZStudentTestRank zstr
INNER JOIN tblStudent s ON zstr.idStudent = s.idStudent
INNER JOIN tblClass c ON s.class = c.class
WHERE form = @form AND score_2 is NOT null AND rank_class_2 is null

--form
UPDATE tblZStudentTestRank
SET rank_form_1 = null
FROM tblZStudentTestRank zstr
INNER JOIN tblStudent s ON zstr.idStudent = s.idStudent
INNER JOIN tblClass c ON s.class = c.class
WHERE form = @form

UPDATE tblZStudentTestRank
SET rank_form_2 = null
FROM tblZStudentTestRank zstr
INNER JOIN tblStudent s ON zstr.idStudent = s.idStudent
INNER JOIN tblClass c ON s.class = c.class
WHERE form = @form

UPDATE tblZStudentTestRank
SET rank_form_1 = rank
FROM (
SELECT idStudent, count(idStudent) + 1 AS rank
FROM (
SELECT zstr1.idStudent, zstr1.score_1
FROM tblZStudentTestRank zstr1
INNER JOIN tblStudent s1 ON zstr1.idStudent = s1.idStudent
INNER JOIN tblClass c1 ON s1.class = c1.class, tblZStudentTestRank zstr2
INNER JOIN tblStudent s2 ON zstr2.idStudent = s2.idStudent
INNER JOIN tblClass c2 ON s2.class = c2.class
WHERE zstr1.score_1 < zstr2.score_1 AND c1.form = @form AND c1.form = c2.form ) rA
GROUP BY idStudent ) rB, tblZStudentTestRank zstr
WHERE zstr.idStudent = rB.idStudent

UPDATE tblZStudentTestRank
SET rank_form_2 = rank
FROM (
SELECT idStudent, count(idStudent) + 1 AS rank
FROM (
SELECT zstr1.idStudent, zstr1.score_2
FROM tblZStudentTestRank zstr1
INNER JOIN tblStudent s1 ON zstr1.idStudent = s1.idStudent
INNER JOIN tblClass c1 ON s1.class = c1.class, tblZStudentTestRank zstr2
INNER JOIN tblStudent s2 ON zstr2.idStudent = s2.idStudent
INNER JOIN tblClass c2 ON s2.class = c2.class
WHERE zstr1.score_2 < zstr2.score_2 AND c1.form = @form ) rA
GROUP BY idStudent ) rB, tblZStudentTestRank zstr
WHERE zstr.idStudent = rB.idStudent

UPDATE tblZStudentTestRank
SET rank_form_1 = 1
FROM tblZStudentTestRank zstr
INNER JOIN tblStudent s ON zstr.idStudent = s.idStudent
INNER JOIN tblClass c ON s.class = c.class
WHERE form = @form AND score_1 is NOT null AND rank_form_1 is null

UPDATE tblZStudentTestRank
SET rank_form_2 = 1
FROM tblZStudentTestRank zstr
INNER JOIN tblStudent s ON zstr.idStudent = s.idStudent
INNER JOIN tblClass c ON s.class = c.class
WHERE form = @form AND score_2 is NOT null AND rank_form_2 is null

GO

------------------------------------------------------------------------------------------------
-- stpGenerateTestSummary
------------------------------------------------------------------------------------------------

if exists (select * from dbo.sysobjects where id = object_id(N'[dbo].[stpGenerateTestSummary]') and OBJECTPROPERTY(id, N'IsProcedure') = 1)
drop procedure [dbo].[stpGenerateTestSummary]
GO

CREATE PROCEDURE dbo.stpGenerateTestSummary
@form tinyint, @test tinyint
AS

exec stpOutputTestPaperRankScore @form, @test
exec stpOutputTestPaperRank @form

exec stpOutputTestRankScore @form, @test
exec stpOutputTestRank @form

GO

------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------
--delete from tblZStudentTestPaperRank
--go
--delete from tblZStudentTestRank
--go

stpGenerateTestSummary 5, 1
go

stpGenerateTestSummary 5, 2
go



