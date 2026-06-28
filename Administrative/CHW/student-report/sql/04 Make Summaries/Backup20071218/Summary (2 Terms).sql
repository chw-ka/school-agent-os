--For general use with "2 term" approach (S1, S2, S3, S4, S5, S6).

------------------------------------------------------------------------------------------------
-- stpOutputPaperRankScore
------------------------------------------------------------------------------------------------

if exists (select * from dbo.sysobjects where id = object_id(N'[dbo].[stpOutputPaperRankScore]') and OBJECTPROPERTY(id, N'IsProcedure') = 1)
drop procedure [dbo].[stpOutputPaperRankScore]
GO

CREATE PROCEDURE dbo.stpOutputPaperRankScore
@form tinyint, @term tinyint
AS

--score_1, score_2

IF @term = 1
BEGIN
	-- Initialize Term 1
	INSERT tblZStudentPaperRank (idStudent, idPaper)
	SELECT sp.idStudent, sp.idPaper
	FROM vwStudentPaper sp
	INNER JOIN tblStudentPaperScore sps ON sps.idStudent = sp.idStudent and sps.idPaper = sp.idPaper
	INNER JOIN tblFormPaperWeight fpw ON sp.form = fpw.form and sp.idPaper = fpw.idPaper AND (fpw.weight_test_1 > 0 OR fpw.weight_regular_1 > 0 OR fpw.weight_exam_1 > 0)
	LEFT JOIN tblZStudentPaperRank zspr ON sp.idStudent = zspr.idStudent and sp.idPaper = zspr.idPaper
	WHERE sp.form = @form and sp.flgTerm1 = 1 and (sps.score_test_1 is not null OR sps.score_regular_1 is not null OR sps.score_exam_1 is not null) and zspr.idStudent is null

	--score_1
	UPDATE tblZStudentPaperRank
	SET score_1 = null, score_final = null, flgIgnore_1 = 1, flgRemark_1 = 0
	FROM tblZStudentPaperRank zspr
	INNER JOIN vwStudent s ON s.idStudent = zspr.idStudent
	WHERE s.form = @form

	UPDATE tblZStudentPaperRank
	SET score_1 = floor(
	(CASE WHEN weight_test_1 <> 0 AND fps.score_test_1 IS NOT null AND sps.score_test_1 IS NOT null THEN cast(1000.0 as real) * weight_test_1 * sps.score_test_1 / fps.score_test_1 ELSE 0.0 END +
	 CASE WHEN weight_regular_1 <> 0 AND fps.score_regular_1 IS NOT null AND sps.score_regular_1 IS NOT null THEN cast(1000.0 as real) * weight_regular_1 * sps.score_regular_1 / fps.score_regular_1 ELSE 0.0 END +
	 CASE WHEN weight_exam_1 <> 0 AND fps.score_exam_1 IS NOT null AND sps.score_exam_1 IS NOT null THEN cast(1000.0 as real) * weight_exam_1 * sps.score_exam_1 / fps.score_exam_1 ELSE 0.0 END) /
	(CASE WHEN weight_test_1 <> 0 AND fps.score_test_1 IS NOT null THEN weight_test_1 ELSE 0.0 END +
 	 CASE WHEN weight_regular_1 <> 0 AND fps.score_regular_1 IS NOT null THEN weight_regular_1 ELSE 0.0 END +
	 CASE WHEN weight_exam_1 <> 0 AND fps.score_exam_1 IS NOT null THEN weight_exam_1 ELSE 0.0 END)
	), flgIgnore_1 = sps.flgIgnore_1, flgRemark_1 = sps.flgRemark_1
	FROM tblZStudentPaperRank zspr
	INNER JOIN vwStudent s ON zspr.idStudent = s.idStudent
	INNER JOIN tblStudentPaperScore sps ON s.idStudent = sps.idStudent AND zspr.idPaper = sps.idPaper
	INNER JOIN tblFormPaperScore fps ON fps.form = s.form AND fps.idPaper = sps.idPaper
	INNER JOIN tblFormPaperWeight fpw ON fpw.form = s.form AND fpw.idPaper = sps.idPaper AND (fpw.weight_test_1 > 0 OR fpw.weight_regular_1 > 0 OR fpw.weight_exam_1 > 0)
	WHERE s.form = @form AND (sps.score_test_1 is not null OR sps.score_regular_1 is not null OR sps.score_exam_1 is not null)

	--subject score 1
	INSERT tblZStudentPaperRank (idStudent, idPaper)
	SELECT DISTINCT s.idStudent, p.idSubject
	FROM vwStudent s
	INNER JOIN tblZStudentPaperRank zspr ON s.idStudent = zspr.idStudent
	INNER JOIN tblFormPaperWeight fpw ON s.form = fpw.form AND zspr.idPaper = fpw.idPaper AND (fpw.weight_test_1 > 0 OR fpw.weight_regular_1 > 0 OR fpw.weight_exam_1 > 0)
	INNER JOIN tblPaper p ON zspr.idPaper = p.idPaper AND p.idSubject <> p.idPaper AND p.formGroup = s.formGroup
	LEFT JOIN tblZStudentPaperRank zspr2 ON s.idStudent = zspr2.idStudent and p.idSubject = zspr2.idPaper
	WHERE s.form = @form AND s.flgTerm1 = 1 and zspr.score_1 is not null and zspr.flgIgnore_1 = 0 AND zspr2.idStudent is null

	UPDATE tblZStudentPaperRank
	SET score_1 = r.score_1, flgIgnore_1 = 0
	FROM tblZStudentPaperRank zspr, (
	SELECT zspr.idStudent, p.idSubject, score_1 = floor(sum(floor(score_1 / 10.0 + .5) * 10.0 * weight) / sum(weight))
	FROM tblZStudentPaperRank zspr
	INNER JOIN vwStudent s ON s.idStudent = zspr.idStudent
	INNER JOIN tblFormPaperWeight fpw ON s.form = fpw.form AND zspr.idPaper = fpw.idPaper
	INNER JOIN tblPaper p ON zspr.idPaper = p.idPaper AND p.idSubject <> p.idPaper AND s.formGroup = p.formGroup
	WHERE s.form = @form AND zspr.flgIgnore_1 = 0
	GROUP BY zspr.idStudent, p.idSubject) r
	WHERE zspr.idStudent = r.idStudent AND zspr.idPaper = r.idSubject
END
ELSE
BEGIN
	-- Initialize Term 2
	INSERT tblZStudentPaperRank (idStudent, idPaper)
	SELECT sp.idStudent, sp.idPaper
	FROM vwStudentPaper sp
	INNER JOIN tblStudentPaperScore sps ON sps.idStudent = sp.idStudent and sps.idPaper = sp.idPaper
	INNER JOIN tblFormPaperWeight fpw ON sp.form = fpw.form and sp.idPaper = fpw.idPaper AND (fpw.weight_test_2 > 0 OR fpw.weight_regular_2 > 0 OR fpw.weight_exam_2 > 0)
	LEFT JOIN tblZStudentPaperRank zspr ON sp.idStudent = zspr.idStudent and sp.idPaper = zspr.idPaper
	WHERE sp.form = @form and sp.flgTerm2 = 1 and (sps.score_test_2 is not null OR sps.score_regular_2 is not null OR sps.score_exam_2 is not null) and zspr.idStudent is null

	--score_2
	UPDATE tblZStudentPaperRank
	SET score_2 = null, score_final = null, flgIgnore_2 = 1, flgRemark_2 = 0
	FROM tblZStudentPaperRank zspr
	INNER JOIN vwStudent s ON s.idStudent = zspr.idStudent
	WHERE s.form = @form

	UPDATE tblZStudentPaperRank
	SET score_2 = floor(
	(CASE WHEN weight_test_2 <> 0 AND fps.score_test_2 IS NOT null AND sps.score_test_2 IS NOT null THEN cast(1000.0 as real) * weight_test_2 * sps.score_test_2 / fps.score_test_2 ELSE 0.0 END +
	 CASE WHEN weight_regular_2 <> 0 AND fps.score_regular_2 IS NOT null AND sps.score_regular_2 IS NOT null THEN cast(1000.0 as real) * weight_regular_2 * sps.score_regular_2 / fps.score_regular_2 ELSE 0.0 END +
	 CASE WHEN weight_exam_2 <> 0 AND fps.score_exam_2 IS NOT null AND sps.score_exam_2 IS NOT null THEN cast(1000.0 as real) * weight_exam_2 * sps.score_exam_2 / fps.score_exam_2 ELSE 0.0 END) /
	(CASE WHEN weight_test_2 <> 0 AND fps.score_test_2 IS NOT null THEN weight_test_2 ELSE 0.0 END +
 	 CASE WHEN weight_regular_2 <> 0 AND fps.score_regular_2 IS NOT null THEN weight_regular_2 ELSE 0.0 END +
	 CASE WHEN weight_exam_2 <> 0 AND fps.score_exam_2 IS NOT null THEN weight_exam_2 ELSE 0.0 END)
	), flgIgnore_2 = sps.flgIgnore_2, flgRemark_2 = sps.flgRemark_2
	FROM tblZStudentPaperRank zspr
	INNER JOIN vwStudent s ON zspr.idStudent = s.idStudent
	INNER JOIN tblStudentPaperScore sps ON s.idStudent = sps.idStudent AND zspr.idPaper = sps.idPaper
	INNER JOIN tblFormPaperScore fps ON fps.form = s.form AND fps.idPaper = sps.idPaper
	INNER JOIN tblFormPaperWeight fpw ON fpw.form = s.form AND fpw.idPaper = sps.idPaper AND (fpw.weight_test_2 > 0 OR fpw.weight_regular_2 > 0 OR fpw.weight_exam_2 > 0)
	WHERE s.form = @form AND zspr.idStudent = s.idStudent AND zspr.idPaper = sps.idPaper AND (sps.score_test_2 is not null OR sps.score_regular_2 is not null OR sps.score_exam_2 is not null)

	--subject score 2
	INSERT tblZStudentPaperRank (idStudent, idPaper)
	SELECT DISTINCT s.idStudent, p.idSubject
	FROM vwStudent s
	INNER JOIN tblZStudentPaperRank zspr ON s.idStudent = zspr.idStudent
	INNER JOIN tblFormPaperWeight fpw ON s.form = fpw.form AND zspr.idPaper = fpw.idPaper AND (fpw.weight_test_2 > 0 OR fpw.weight_regular_2 > 0 OR fpw.weight_exam_2 > 0)
	INNER JOIN tblPaper p ON zspr.idPaper = p.idPaper AND p.idSubject <> p.idPaper AND p.formGroup = s.formGroup
	LEFT JOIN tblZStudentPaperRank zspr2 ON s.idStudent = zspr2.idStudent and p.idSubject = zspr2.idPaper
	WHERE s.form = @form AND s.flgTerm2 = 1 and zspr.score_2 is not null and zspr.flgIgnore_2 = 0 AND zspr2.idStudent is null

	UPDATE tblZStudentPaperRank
	SET score_2 = r.score_2, flgIgnore_2 = 0
	FROM tblZStudentPaperRank zspr, (
	SELECT zspr.idStudent, p.idSubject, score_2 = floor(sum(floor(score_2 / 10.0 + .5) * 10.0 * weight) / sum(weight))
	FROM tblZStudentPaperRank zspr
	INNER JOIN vwStudent s ON s.idStudent = zspr.idStudent
	INNER JOIN tblFormPaperWeight fpw ON s.form = fpw.form AND zspr.idPaper = fpw.idPaper
	INNER JOIN tblPaper p ON zspr.idPaper = p.idPaper AND p.idSubject <> p.idPaper AND s.formGroup = p.formGroup
	WHERE s.form = @form AND zspr.flgIgnore_2 = 0
	GROUP BY zspr.idStudent, p.idSubject) r
	WHERE zspr.idStudent = r.idStudent AND zspr.idPaper = r.idSubject
END

--clear unnecessary entities
DELETE
FROM tblZStudentPaperRank
WHERE score_1 is null AND score_2 is null AND score_final is null

--score_final
--(DUE to DROP Subject)
IF @term = 1
BEGIN
	UPDATE tblZStudentPaperRank
	SET score_final = zspr.score_1
	FROM tblZStudentPaperRank zspr
	INNER JOIN vwStudent s ON zspr.idStudent = s.idStudent
	INNER JOIN tblPaper p ON p.idPaper = zspr.idPaper AND s.formGroup = p.formGroup AND (p.idPaper = p.idSubject or p.idSubject is null)
	WHERE s.form = @form AND zspr.score_1 is NOT null AND zspr.score_2 is null
END
ELSE
BEGIN
	UPDATE tblZStudentPaperRank
	SET score_final = zspr.score_2
	FROM tblZStudentPaperRank zspr
	INNER JOIN vwStudent s ON zspr.idStudent = s.idStudent
	INNER JOIN tblPaper p ON p.idPaper = zspr.idPaper AND s.formGroup = p.formGroup AND (p.idPaper = p.idSubject or p.idSubject is null)
	WHERE s.form = @form AND zspr.score_1 is null AND zspr.score_2 is NOT null

	UPDATE tblZStudentPaperRank
	SET score_final = floor((floor(zspr.score_1 / 10.0 + .5) * 10.0 * ftw.weight_1 + floor(zspr.score_2 / 10.0 + .5) * 10.0 * ftw.weight_2 ) / (ftw.weight_1 + ftw.weight_2))
	FROM tblZStudentPaperRank zspr
	INNER JOIN vwStudent s ON zspr.idStudent = s.idStudent
	INNER JOIN tblFormTermWeight ftw ON s.form = ftw.form
	INNER JOIN tblPaper p ON p.idPaper = zspr.idPaper AND s.formGroup = p.formGroup AND (p.idPaper = p.idSubject or p.idSubject is null)
	WHERE s.form = @form AND zspr.score_1 is NOT null AND zspr.score_2 is NOT null
END

GO

------------------------------------------------------------------------------------------------
-- stpOutputPaperRank
------------------------------------------------------------------------------------------------

if exists (select * from dbo.sysobjects where id = object_id(N'[dbo].[stpOutputPaperRank]') and OBJECTPROPERTY(id, N'IsProcedure') = 1)
drop procedure [dbo].[stpOutputPaperRank]
GO

CREATE PROCEDURE dbo.stpOutputPaperRank
@form tinyint
AS

--class
UPDATE tblZStudentPaperRank
SET rank_class_1 = null, rank_class_2 = null, rank_class_final = null
FROM tblZStudentPaperRank zspr
INNER JOIN vwStudent s ON zspr.idStudent = s.idStudent
WHERE s.form = @form

UPDATE tblZStudentPaperRank
SET rank_class_1 = rank
FROM tblZStudentPaperRank zspr, (
SELECT idStudent, idPaper, count(idStudent) + 1 AS rank
FROM (
SELECT zspr1.idStudent, zspr1.idPaper, zspr1.score_1
FROM
tblZStudentPaperRank zspr1
INNER JOIN vwStudent s1 ON zspr1.idStudent = s1.idStudent,
tblZStudentPaperRank zspr2
INNER JOIN vwStudent s2 ON zspr2.idStudent = s2.idStudent
WHERE s1.form = @form AND s1.class = s2.class AND zspr1.idPaper = zspr2.idPaper AND zspr1.score_1 < zspr2.score_1 ) rA
GROUP BY idStudent, idPaper ) rB
WHERE zspr.idStudent = rB.idStudent AND zspr.idPaper = rB.idPaper

UPDATE tblZStudentPaperRank
SET rank_class_2 = rank
FROM tblZStudentPaperRank zspr, (
SELECT idStudent, idPaper, count(idStudent) + 1 AS rank
FROM (
SELECT zspr1.idStudent, zspr1.idPaper, zspr1.score_2
FROM
tblZStudentPaperRank zspr1
INNER JOIN vwStudent s1 ON zspr1.idStudent = s1.idStudent,
tblZStudentPaperRank zspr2
INNER JOIN vwStudent s2 ON zspr2.idStudent = s2.idStudent
WHERE s1.form = @form AND s1.class = s2.class AND zspr1.idPaper = zspr2.idPaper AND zspr1.score_2 < zspr2.score_2 ) rA
GROUP BY idStudent, idPaper ) rB
WHERE zspr.idStudent = rB.idStudent AND zspr.idPaper = rB.idPaper

UPDATE tblZStudentPaperRank
SET rank_class_final = rank
FROM tblZStudentPaperRank zspr, (
SELECT idStudent, idPaper, count(idStudent) + 1 AS rank
FROM (
SELECT zspr1.idStudent, zspr1.idPaper, zspr1.score_final
FROM
tblZStudentPaperRank zspr1
INNER JOIN vwStudent s1 ON zspr1.idStudent = s1.idStudent,
tblZStudentPaperRank zspr2
INNER JOIN vwStudent s2 ON zspr2.idStudent = s2.idStudent
WHERE s1.form = @form AND s1.class = s2.class AND zspr1.idPaper = zspr2.idPaper AND zspr1.score_final < zspr2.score_final ) rA
GROUP BY idStudent, idPaper ) rB
WHERE zspr.idStudent = rB.idStudent AND zspr.idPaper = rB.idPaper

UPDATE tblZStudentPaperRank
SET rank_class_1 = 1
FROM tblZStudentPaperRank zspr
INNER JOIN vwStudent s ON zspr.idStudent = s.idStudent
WHERE s.form = @form AND score_1 is NOT null AND rank_class_1 is null

UPDATE tblZStudentPaperRank
SET rank_class_2 = 1
FROM tblZStudentPaperRank zspr
INNER JOIN vwStudent s ON zspr.idStudent = s.idStudent
WHERE s.form = @form AND score_2 is NOT null AND rank_class_2 is null

UPDATE tblZStudentPaperRank
SET rank_class_final = 1
FROM tblZStudentPaperRank zspr
INNER JOIN vwStudent s ON zspr.idStudent = s.idStudent
WHERE s.form = @form AND score_final is NOT null AND rank_class_final is null

--form
UPDATE tblZStudentPaperRank
SET rank_form_1 = null, rank_form_2 = null, rank_form_final = null
FROM tblZStudentPaperRank zspr
INNER JOIN vwStudent s ON zspr.idStudent = s.idStudent
WHERE s.form = @form

UPDATE tblZStudentPaperRank
SET rank_form_1 = rank
FROM (
SELECT idStudent, idPaper, count(idStudent) + 1 AS rank
FROM (
SELECT zspr1.idStudent, zspr1.idPaper, zspr1.score_1
FROM
tblZStudentPaperRank zspr1
INNER JOIN vwStudent s1 ON zspr1.idStudent = s1.idStudent,
tblZStudentPaperRank zspr2
INNER JOIN vwStudent s2 ON zspr2.idStudent = s2.idStudent
WHERE s1.form = @form AND s1.form = s2.form AND zspr1.idPaper = zspr2.idPaper AND zspr1.score_1 < zspr2.score_1 ) rA
GROUP BY idStudent, idPaper ) rB, tblZStudentPaperRank zspr
WHERE zspr.idStudent = rB.idStudent AND zspr.idPaper = rB.idPaper

UPDATE tblZStudentPaperRank
SET rank_form_2 = rank
FROM (
SELECT idStudent, idPaper, count(idStudent) + 1 AS rank
FROM (
SELECT zspr1.idStudent, zspr1.idPaper, zspr1.score_2
FROM
tblZStudentPaperRank zspr1
INNER JOIN vwStudent s1 ON zspr1.idStudent = s1.idStudent,
tblZStudentPaperRank zspr2
INNER JOIN vwStudent s2 ON zspr2.idStudent = s2.idStudent
WHERE s1.form = @form AND s1.form = s2.form AND zspr1.idPaper = zspr2.idPaper AND zspr1.score_2 < zspr2.score_2 ) rA
GROUP BY idStudent, idPaper ) rB, tblZStudentPaperRank zspr
WHERE zspr.idStudent = rB.idStudent AND zspr.idPaper = rB.idPaper

UPDATE tblZStudentPaperRank
SET rank_form_final = rank
FROM (
SELECT idStudent, idPaper, count(idStudent) + 1 AS rank
FROM (
SELECT zspr1.idStudent, zspr1.idPaper, zspr1.score_final
FROM
tblZStudentPaperRank zspr1
INNER JOIN vwStudent s1 ON zspr1.idStudent = s1.idStudent,
tblZStudentPaperRank zspr2
INNER JOIN vwStudent s2 ON zspr2.idStudent = s2.idStudent
WHERE s1.form = @form AND s1.form = s2.form AND zspr1.idPaper = zspr2.idPaper AND zspr1.score_final < zspr2.score_final ) rA
GROUP BY idStudent, idPaper ) rB, tblZStudentPaperRank zspr
WHERE zspr.idStudent = rB.idStudent AND zspr.idPaper = rB.idPaper

UPDATE tblZStudentPaperRank
SET rank_form_1 = 1
FROM tblZStudentPaperRank zspr
INNER JOIN vwStudent s ON zspr.idStudent = s.idStudent
WHERE s.form = @form AND score_1 is NOT null AND rank_form_1 is null

UPDATE tblZStudentPaperRank
SET rank_form_2 = 1
FROM tblZStudentPaperRank zspr
INNER JOIN vwStudent s ON zspr.idStudent = s.idStudent
WHERE s.form = @form AND score_2 is NOT null AND rank_form_2 is null

UPDATE tblZStudentPaperRank
SET rank_form_final = 1
FROM tblZStudentPaperRank zspr
INNER JOIN vwStudent s ON zspr.idStudent = s.idStudent
WHERE s.form = @form AND score_final is NOT null AND rank_form_final is null

GO

------------------------------------------------------------------------------------------------
-- stpOutputRankScore
------------------------------------------------------------------------------------------------

if exists (select * from dbo.sysobjects where id = object_id(N'[dbo].[stpOutputRankScore]') and OBJECTPROPERTY(id, N'IsProcedure') = 1)
drop procedure [dbo].[stpOutputRankScore]
GO

CREATE PROCEDURE dbo.stpOutputRankScore
@form tinyint, @term tinyint
AS

IF @term = 1
BEGIN
	-- score_1
	INSERT tblZStudentRank (idStudent)
	SELECT DISTINCT zspr.idStudent
	FROM tblZStudentPaperRank zspr
	INNER JOIN vwStudent s ON s.idStudent = zspr.idStudent
	INNER JOIN tblFormPaperWeight fpw ON s.form = fpw.form AND zspr.idPaper = fpw.idPaper
	INNER JOIN tblPaper p ON zspr.idPaper = p.idPaper AND p.formGroup = s.formGroup AND (p.idSubject = p.idPaper OR p.idSubject is null)
	LEFT JOIN tblZStudentRank zsr ON s.idStudent = zsr.idStudent
	WHERE s.form = @form and zspr.score_1 is not null AND zsr.idStudent is null

	UPDATE tblZStudentRank
	SET score_1 = null, score_final = null
	FROM tblZStudentRank zsr
	INNER JOIN vwStudent s ON zsr.idStudent = s.idStudent
	WHERE s.form = @form

	UPDATE tblZStudentRank
	SET score_1 = r.score_1
	FROM tblZStudentRank zsr, (
	SELECT zspr.idStudent, score_1 = floor(sum(floor(score_1 / 10.0 + .5) * 10.0 * weight) / sum(weight) + .5)
	FROM tblZStudentPaperRank zspr
	INNER JOIN vwStudent s ON s.idStudent = zspr.idStudent
	INNER JOIN tblPaper p ON zspr.idPaper = p.idPaper AND p.formGroup = s.formGroup AND (p.idSubject = p.idPaper OR p.idSubject is null)
	INNER JOIN tblFormPaperWeight fpw ON s.form = fpw.form AND zspr.idPaper = fpw.idPaper AND weight > 0
	WHERE s.form = @form AND zspr.score_1 is not null
	GROUP BY zspr.idStudent) r
	WHERE zsr.idStudent = r.idStudent
END
ELSE
BEGIN
	-- score_2
	INSERT tblZStudentRank (idStudent)
	SELECT DISTINCT zspr.idStudent
	FROM tblZStudentPaperRank zspr
	INNER JOIN vwStudent s ON s.idStudent = zspr.idStudent
	INNER JOIN tblFormPaperWeight fpw ON s.form = fpw.form AND zspr.idPaper = fpw.idPaper
	INNER JOIN tblPaper p ON zspr.idPaper = p.idPaper AND p.formGroup = s.formGroup AND (p.idSubject = p.idPaper OR p.idSubject is null)
	LEFT JOIN tblZStudentRank zsr ON s.idStudent = zsr.idStudent
	WHERE s.form = @form and zspr.score_2 is not null AND zsr.idStudent is null

	UPDATE tblZStudentRank
	SET score_2 = null, score_final = null
	FROM tblZStudentRank zsr
	INNER JOIN vwStudent s ON zsr.idStudent = s.idStudent
	WHERE s.form = @form

	UPDATE tblZStudentRank
	SET score_2 = r.score_2
	FROM tblZStudentRank zsr, (
	SELECT zspr.idStudent, score_2 = floor(sum(floor(score_2 / 10.0 + .5) * 10.0 * weight) / sum(weight) + .5)
	FROM tblZStudentPaperRank zspr
	INNER JOIN vwStudent s ON s.idStudent = zspr.idStudent
	INNER JOIN tblPaper p ON zspr.idPaper = p.idPaper AND p.formGroup = s.formGroup AND (p.idSubject = p.idPaper OR p.idSubject is null)
	INNER JOIN tblFormPaperWeight fpw ON s.form = fpw.form AND zspr.idPaper = fpw.idPaper AND weight > 0
	WHERE s.form = @form AND zspr.score_2 is not null
	GROUP BY zspr.idStudent) r
	WHERE zsr.idStudent = r.idStudent
END

UPDATE tblZStudentRank
SET score_final = floor((zsr.score_1 * ftw.weight_1 + zsr.score_2 * ftw.weight_2 ) * 1.0 / (ftw.weight_1 + ftw.weight_2) + .5)
FROM tblZStudentRank zsr
INNER JOIN vwStudent s ON zsr.idStudent = s.idStudent
INNER JOIN tblFormTermWeight ftw ON s.form = ftw.form
WHERE s.form = @form AND zsr.score_1 is NOT null AND zsr.score_2 is NOT null

UPDATE tblZStudentRank
SET score_final = score_2
FROM tblZStudentRank zsr
INNER JOIN vwStudent s ON zsr.idStudent = s.idStudent
WHERE s.form = @form AND zsr.score_1 is null AND zsr.score_2 is NOT null

DELETE
FROM tblZStudentRank
WHERE score_1 is null and score_2 is null and score_final is null

GO

------------------------------------------------------------------------------------------------
-- stpOutputRank
------------------------------------------------------------------------------------------------

if exists (select * from dbo.sysobjects where id = object_id(N'[dbo].[stpOutputRank]') and OBJECTPROPERTY(id, N'IsProcedure') = 1)
drop procedure [dbo].[stpOutputRank]
GO

CREATE PROCEDURE dbo.stpOutputRank
@form tinyint
AS

--class
UPDATE tblZStudentRank
SET rank_class_1 = null, rank_class_2 = null, rank_class_final = null
FROM tblZStudentRank zsr
INNER JOIN vwStudent s ON zsr.idStudent = s.idStudent
WHERE s.form = @form

UPDATE tblZStudentRank
SET rank_class_1 = rank
FROM (
SELECT idStudent, count(idStudent) + 1 AS rank
FROM (
SELECT zsr1.idStudent, zsr1.score_1
FROM tblZStudentRank zsr1
INNER JOIN vwStudent s1 ON zsr1.idStudent = s1.idStudent,
tblZStudentRank zsr2
INNER JOIN vwStudent s2 ON zsr2.idStudent = s2.idStudent
WHERE s1.form = @form AND s1.class = s2.class AND zsr1.score_1 < zsr2.score_1 ) rA
GROUP BY idStudent ) rB, tblZStudentRank zsr
WHERE zsr.idStudent = rB.idStudent

UPDATE tblZStudentRank
SET rank_class_2 = rank
FROM (
SELECT idStudent, count(idStudent) + 1 AS rank
FROM (
SELECT zsr1.idStudent, zsr1.score_2
FROM tblZStudentRank zsr1
INNER JOIN vwStudent s1 ON zsr1.idStudent = s1.idStudent,
tblZStudentRank zsr2
INNER JOIN vwStudent s2 ON zsr2.idStudent = s2.idStudent
WHERE s1.form = @form AND s1.class = s2.class AND zsr1.score_2 < zsr2.score_2 ) rA
GROUP BY idStudent ) rB, tblZStudentRank zsr
WHERE zsr.idStudent = rB.idStudent

UPDATE tblZStudentRank
SET rank_class_final = rank
FROM (
SELECT idStudent, count(idStudent) + 1 AS rank
FROM (
SELECT zsr1.idStudent, zsr1.score_final
FROM tblZStudentRank zsr1
INNER JOIN vwStudent s1 ON zsr1.idStudent = s1.idStudent,
tblZStudentRank zsr2
INNER JOIN vwStudent s2 ON zsr2.idStudent = s2.idStudent
WHERE s1.form = @form AND s1.class = s2.class AND zsr1.score_final < zsr2.score_final ) rA
GROUP BY idStudent ) rB, tblZStudentRank zsr
WHERE zsr.idStudent = rB.idStudent

UPDATE tblZStudentRank
SET rank_class_1 = 1
FROM tblZStudentRank zsr
INNER JOIN vwStudent s ON zsr.idStudent = s.idStudent
WHERE s.form = @form AND score_1 is NOT null AND rank_class_1 is null

UPDATE tblZStudentRank
SET rank_class_2 = 1
FROM tblZStudentRank zsr
INNER JOIN vwStudent s ON zsr.idStudent = s.idStudent
WHERE s.form = @form AND score_2 is NOT null AND rank_class_2 is null

UPDATE tblZStudentRank
SET rank_class_final = 1
FROM tblZStudentRank zsr
INNER JOIN vwStudent s ON zsr.idStudent = s.idStudent
WHERE s.form = @form AND score_final is NOT null AND rank_class_final is null

--form
UPDATE tblZStudentRank
SET rank_form_1 = null, rank_form_2 = null, rank_form_final = null
FROM tblZStudentRank zsr
INNER JOIN vwStudent s ON zsr.idStudent = s.idStudent
WHERE s.form = @form

IF @form < 4
BEGIN
	UPDATE tblZStudentRank
	SET rank_form_1 = rank
	FROM (
	SELECT idStudent, count(idStudent) + 1 AS rank
	FROM (
	SELECT zsr1.idStudent, zsr1.score_1
	FROM
	tblZStudentRank zsr1
	INNER JOIN vwStudent s1 ON zsr1.idStudent = s1.idStudent,
	tblZStudentRank zsr2
	INNER JOIN vwStudent s2 ON zsr2.idStudent = s2.idStudent
	WHERE s1.form = @form AND s1.form = s2.form AND zsr1.score_1 < zsr2.score_1 ) rA
	GROUP BY idStudent ) rB, tblZStudentRank zsr
	WHERE zsr.idStudent = rB.idStudent

	UPDATE tblZStudentRank
	SET rank_form_2 = rank
	FROM (
	SELECT idStudent, count(idStudent) + 1 AS rank
	FROM (
	SELECT zsr1.idStudent, zsr1.score_2
	FROM
	tblZStudentRank zsr1
	INNER JOIN vwStudent s1 ON zsr1.idStudent = s1.idStudent,
	tblZStudentRank zsr2
	INNER JOIN vwStudent s2 ON zsr2.idStudent = s2.idStudent
	WHERE s1.form = @form AND s1.form = s2.form AND zsr1.score_2 < zsr2.score_2 ) rA
	GROUP BY idStudent ) rB, tblZStudentRank zsr
	WHERE zsr.idStudent = rB.idStudent

	UPDATE tblZStudentRank
	SET rank_form_final = rank
	FROM (
	SELECT idStudent, count(idStudent) + 1 AS rank
	FROM (
	SELECT zsr1.idStudent, zsr1.score_final
	FROM
	tblZStudentRank zsr1
	INNER JOIN vwStudent s1 ON zsr1.idStudent = s1.idStudent,
	tblZStudentRank zsr2
	INNER JOIN vwStudent s2 ON zsr2.idStudent = s2.idStudent
	WHERE s1.form = @form AND s1.form = s2.form AND zsr1.score_final < zsr2.score_final ) rA
	GROUP BY idStudent ) rB, tblZStudentRank zsr
	WHERE zsr.idStudent = rB.idStudent

	UPDATE tblZStudentRank
	SET rank_form_1 = 1
	FROM tblZStudentRank zsr
	INNER JOIN vwStudent s ON zsr.idStudent = s.idStudent
	WHERE s.form = @form AND score_1 is NOT null AND rank_form_1 is null

	UPDATE tblZStudentRank
	SET rank_form_2 = 1
	FROM tblZStudentRank zsr
	INNER JOIN vwStudent s ON zsr.idStudent = s.idStudent
	WHERE s.form = @form AND score_2 is NOT null AND rank_form_2 is null

	UPDATE tblZStudentRank
	SET rank_form_final = 1
	FROM tblZStudentRank zsr
	INNER JOIN vwStudent s ON zsr.idStudent = s.idStudent
	WHERE s.form = @form AND score_final is NOT null AND rank_form_final is null
END

GO

------------------------------------------------------------------------------------------------
-- stpOutputPaperRankStandardScore
------------------------------------------------------------------------------------------------

if exists (select * from dbo.sysobjects where id = object_id(N'[dbo].[stpOutputPaperRankStandardScore]') and OBJECTPROPERTY(id, N'IsProcedure') = 1)
drop procedure [dbo].[stpOutputPaperRankStandardScore]
GO

CREATE PROCEDURE dbo.stpOutputPaperRankStandardScore
@form tinyint, @term tinyint
AS

IF @term = 1
BEGIN
	UPDATE tblZStudentPaperRank
	SET scoreStd1 = null, scoreStdFinal = null
	FROM tblZStudentPaperRank zspr
	INNER JOIN vwStudent s ON zspr.idStudent = s.idStudent
	where s.form = @form

	UPDATE tblZStudentPaperRank
	SET scoreStd1 = r.score
	FROM tblZStudentPaperRank zspr, (
	SELECT s.idStudent, zspr.idPaper, ((score_1 / 10.0) - mean) / sd as score
	FROM vwStudent s
	INNER JOIN tblZStudentPaperRank zspr ON s.idStudent = zspr.idStudent
	INNER JOIN tblPaper p ON zspr.idPaper = p.idPaper AND s.formGroup = p.formGroup
	INNER JOIN (
	SELECT s.form, p.idPaper, avg(zspr.score_1 / 10.0) as mean, stdev(zspr.score_1 / 10.0) as sd
	FROM vwStudent s
	INNER JOIN tblZStudentPaperRank zspr ON s.idStudent = zspr.idStudent
	INNER JOIN tblPaper p ON zspr.idPaper = p.idPaper AND s.formGroup = p.formGroup
	WHERE zspr.score_1 is not null
	GROUP BY s.form, p.idPaper ) r ON s.form = r.form AND p.idPaper = r.idPaper
	WHERE s.form = @form and zspr.score_1 is not null ) r
	WHERE zspr.idStudent = r.idStudent and zspr.idPaper = r.idPaper
END
ELSE
BEGIN
	UPDATE tblZStudentPaperRank
	SET scoreStd2 = null, scoreStdFinal = null
	FROM tblZStudentPaperRank zspr
	INNER JOIN vwStudent s ON zspr.idStudent = s.idStudent
	where s.form = @form

	UPDATE tblZStudentPaperRank
	SET scoreStd2 = r.score
	FROM tblZStudentPaperRank zspr, (
	SELECT s.idStudent, zspr.idPaper, ((score_2 / 10.0) - mean) / sd as score
	FROM vwStudent s
	INNER JOIN tblZStudentPaperRank zspr ON s.idStudent = zspr.idStudent
	INNER JOIN tblPaper p ON zspr.idPaper = p.idPaper AND s.formGroup = p.formGroup
	INNER JOIN (
	SELECT s.form, p.idPaper, avg(zspr.score_2 / 10.0) as mean, stdev(zspr.score_2 / 10.0) as sd
	FROM vwStudent s
	INNER JOIN tblZStudentPaperRank zspr ON s.idStudent = zspr.idStudent
	INNER JOIN tblPaper p ON zspr.idPaper = p.idPaper AND s.formGroup = p.formGroup
	WHERE zspr.score_2 is not null
	GROUP BY s.form, p.idPaper ) r ON s.form = r.form AND p.idPaper = r.idPaper
	WHERE s.form = @form and zspr.score_2 is not null ) r
	WHERE zspr.idStudent = r.idStudent and zspr.idPaper = r.idPaper
END

UPDATE tblZStudentPaperRank
SET scoreStdFinal = r.score
FROM tblZStudentPaperRank zspr, (
SELECT s.idStudent, zspr.idPaper, ((score_final / 10.0) - mean) / sd as score
FROM vwStudent s
INNER JOIN tblZStudentPaperRank zspr ON s.idStudent = zspr.idStudent
INNER JOIN tblPaper p ON zspr.idPaper = p.idPaper AND s.formGroup = p.formGroup
INNER JOIN (
SELECT s.form, p.idPaper, avg(zspr.score_final / 10.0) as mean, stdev(zspr.score_final / 10.0) as sd
FROM vwStudent s
INNER JOIN tblZStudentPaperRank zspr ON s.idStudent = zspr.idStudent
INNER JOIN tblPaper p ON zspr.idPaper = p.idPaper AND s.formGroup = p.formGroup
WHERE zspr.score_final is not null
GROUP BY s.form, p.idPaper ) r ON s.form = r.form AND p.idPaper = r.idPaper
WHERE s.form = @form and zspr.score_final is not null ) r
WHERE zspr.idStudent = r.idStudent and zspr.idPaper = r.idPaper

GO

------------------------------------------------------------------------------------------------
-- stpOutputPaperRankStandard
------------------------------------------------------------------------------------------------

if exists (select * from dbo.sysobjects where id = object_id(N'[dbo].[stpOutputPaperRankStandard]') and OBJECTPROPERTY(id, N'IsProcedure') = 1)
drop procedure [dbo].[stpOutputPaperRankStandard]
GO

CREATE PROCEDURE dbo.stpOutputPaperRankStandard
@form tinyint
AS

UPDATE tblZStudentPaperRank
SET rankStdClass1 = null, rankStdClass2 = null, rankStdClassFinal = null, rankStdForm1 = null, rankStdForm2 = null, rankStdFormFinal = null
FROM tblZStudentPaperRank zspr
INNER JOIN vwStudent s ON zspr.idStudent = s.idStudent
WHERE s.form = @form

--Class
UPDATE tblZStudentPaperRank
SET rankStdClass1 = rank
FROM (
SELECT idStudent, idPaper, count(idStudent) + 1 AS rank
FROM (
SELECT zspr1.idStudent, zspr1.idPaper, zspr1.scoreStd1
FROM
tblZStudentPaperRank zspr1
INNER JOIN vwStudent s1 ON zspr1.idStudent = s1.idStudent,
tblZStudentPaperRank zspr2
INNER JOIN vwStudent s2 ON zspr2.idStudent = s2.idStudent
WHERE s1.form = @form AND s1.class = s2.class AND zspr1.idPaper = zspr2.idPaper AND zspr1.scoreStd1 < zspr2.scoreStd1 ) rA
GROUP BY idStudent, idPaper ) rB, tblZStudentPaperRank zspr
WHERE zspr.idStudent = rB.idStudent AND zspr.idPaper = rB.idPaper

UPDATE tblZStudentPaperRank
SET rankStdClass2 = rank
FROM (
SELECT idStudent, idPaper, count(idStudent) + 1 AS rank
FROM (
SELECT zspr1.idStudent, zspr1.idPaper, zspr1.scoreStd2
FROM
tblZStudentPaperRank zspr1
INNER JOIN vwStudent s1 ON zspr1.idStudent = s1.idStudent,
tblZStudentPaperRank zspr2
INNER JOIN vwStudent s2 ON zspr2.idStudent = s2.idStudent
WHERE s1.form = @form AND s1.class = s2.class AND zspr1.idPaper = zspr2.idPaper AND zspr1.scoreStd2 < zspr2.scoreStd2 ) rA
GROUP BY idStudent, idPaper ) rB, tblZStudentPaperRank zspr
WHERE zspr.idStudent = rB.idStudent AND zspr.idPaper = rB.idPaper

UPDATE tblZStudentPaperRank
SET rankStdClassFinal = rank
FROM (
SELECT idStudent, idPaper, count(idStudent) + 1 AS rank
FROM (
SELECT zspr1.idStudent, zspr1.idPaper, zspr1.scoreStdFinal
FROM
tblZStudentPaperRank zspr1
INNER JOIN vwStudent s1 ON zspr1.idStudent = s1.idStudent,
tblZStudentPaperRank zspr2
INNER JOIN vwStudent s2 ON zspr2.idStudent = s2.idStudent
WHERE s1.form = @form AND s1.class = s2.class AND zspr1.idPaper = zspr2.idPaper AND zspr1.scoreStdFinal < zspr2.scoreStdFinal ) rA
GROUP BY idStudent, idPaper ) rB, tblZStudentPaperRank zspr
WHERE zspr.idStudent = rB.idStudent AND zspr.idPaper = rB.idPaper

UPDATE tblZStudentPaperRank
SET rankStdClass1 = 1
FROM tblZStudentPaperRank zspr
INNER JOIN vwStudent s ON zspr.idStudent = s.idStudent
WHERE s.form = @form AND scoreStd1 is NOT null AND rankStdClass1 is null

UPDATE tblZStudentPaperRank
SET rankStdClass2 = 1
FROM tblZStudentPaperRank zspr
INNER JOIN vwStudent s ON zspr.idStudent = s.idStudent
WHERE s.form = @form AND scoreStd2 is NOT null AND rankStdClass2 is null

UPDATE tblZStudentPaperRank
SET rankStdClassFinal = 1
FROM tblZStudentPaperRank zspr
INNER JOIN vwStudent s ON zspr.idStudent = s.idStudent
WHERE s.form = @form AND scoreStdFinal is NOT null AND rankStdClassFinal is null

--Form
UPDATE tblZStudentPaperRank
SET rankStdForm1 = rank
FROM (
SELECT idStudent, idPaper, count(idStudent) + 1 AS rank
FROM (
SELECT zspr1.idStudent, zspr1.idPaper, zspr1.scoreStd1
FROM
tblZStudentPaperRank zspr1
INNER JOIN vwStudent s1 ON zspr1.idStudent = s1.idStudent,
tblZStudentPaperRank zspr2
INNER JOIN vwStudent s2 ON zspr2.idStudent = s2.idStudent
WHERE s1.form = @form AND s1.form = s2.form AND zspr1.idPaper = zspr2.idPaper AND zspr1.scoreStd1 < zspr2.scoreStd1 ) rA
GROUP BY idStudent, idPaper ) rB, tblZStudentPaperRank zspr
WHERE zspr.idStudent = rB.idStudent AND zspr.idPaper = rB.idPaper

UPDATE tblZStudentPaperRank
SET rankStdForm2 = rank
FROM (
SELECT idStudent, idPaper, count(idStudent) + 1 AS rank
FROM (
SELECT zspr1.idStudent, zspr1.idPaper, zspr1.scoreStd2
FROM
tblZStudentPaperRank zspr1
INNER JOIN vwStudent s1 ON zspr1.idStudent = s1.idStudent,
tblZStudentPaperRank zspr2
INNER JOIN vwStudent s2 ON zspr2.idStudent = s2.idStudent
WHERE s1.form = @form AND s1.form = s2.form AND zspr1.idPaper = zspr2.idPaper AND zspr1.scoreStd2 < zspr2.scoreStd2 ) rA
GROUP BY idStudent, idPaper ) rB, tblZStudentPaperRank zspr
WHERE zspr.idStudent = rB.idStudent AND zspr.idPaper = rB.idPaper

UPDATE tblZStudentPaperRank
SET rankStdFormFinal = rank
FROM (
SELECT idStudent, idPaper, count(idStudent) + 1 AS rank
FROM (
SELECT zspr1.idStudent, zspr1.idPaper, zspr1.scoreStdFinal
FROM
tblZStudentPaperRank zspr1
INNER JOIN vwStudent s1 ON zspr1.idStudent = s1.idStudent,
tblZStudentPaperRank zspr2
INNER JOIN vwStudent s2 ON zspr2.idStudent = s2.idStudent
WHERE s1.form = @form AND s1.form = s2.form AND zspr1.idPaper = zspr2.idPaper AND zspr1.scoreStdFinal < zspr2.scoreStdFinal ) rA
GROUP BY idStudent, idPaper ) rB, tblZStudentPaperRank zspr
WHERE zspr.idStudent = rB.idStudent AND zspr.idPaper = rB.idPaper

UPDATE tblZStudentPaperRank
SET rankStdForm1 = 1
FROM tblZStudentPaperRank zspr
INNER JOIN vwStudent s ON zspr.idStudent = s.idStudent
WHERE s.form = @form AND scoreStd1 is NOT null AND rankStdForm1 is null

UPDATE tblZStudentPaperRank
SET rankStdForm2 = 1
FROM tblZStudentPaperRank zspr
INNER JOIN vwStudent s ON zspr.idStudent = s.idStudent
WHERE s.form = @form AND scoreStd2 is NOT null AND rankStdForm2 is null

UPDATE tblZStudentPaperRank
SET rankStdFormFinal = 1
FROM tblZStudentPaperRank zspr
INNER JOIN vwStudent s ON zspr.idStudent = s.idStudent
WHERE s.form = @form AND scoreStdFinal is NOT null AND rankStdFormFinal is null

GO

------------------------------------------------------------------------------------------------
-- stpOutputRankStandardScore
------------------------------------------------------------------------------------------------

if exists (select * from dbo.sysobjects where id = object_id(N'[dbo].[stpOutputRankStandardScore]') and OBJECTPROPERTY(id, N'IsProcedure') = 1)
drop procedure [dbo].[stpOutputRankStandardScore]
GO

CREATE PROCEDURE dbo.stpOutputRankStandardScore
@form tinyint, @term tinyint
AS

IF @term = 1
BEGIN
	UPDATE tblZStudentRank
	SET scoreStd1 = null, scoreStdFinal = null
	FROM tblZStudentRank zsr
	INNER JOIN vwStudent s ON zsr.idStudent = s.idStudent
	where s.form = @form

	UPDATE tblZStudentRank
	SET scoreStd1 = r.score
	FROM tblZStudentRank zsr, (
	SELECT s.idStudent, avg(((score_1 / 10.0) - mean) / sd) as score
	FROM vwStudent s
	INNER JOIN tblZStudentPaperRank zspr ON s.idStudent = zspr.idStudent
	INNER JOIN tblPaper p ON zspr.idPaper = p.idPaper AND s.formGroup = p.formGroup AND (p.idSubject = p.idPaper OR p.idSubject is null)
	INNER JOIN (
	SELECT s.form, p.idPaper, avg(zspr.score_1 / 10.0) as mean, stdev(zspr.score_1 / 10.0) as sd
	FROM vwStudent s
	INNER JOIN tblZStudentPaperRank zspr ON s.idStudent = zspr.idStudent
	INNER JOIN tblPaper p ON zspr.idPaper = p.idPaper AND s.formGroup = p.formGroup AND (p.idSubject = p.idPaper OR p.idSubject is null)
	WHERE zspr.score_1 is not null
	GROUP BY s.form, p.idPaper ) r ON s.form = r.form AND p.idPaper = r.idPaper
	WHERE s.form = @form and zspr.score_1 is not null
	GROUP BY s.idStudent) r
	WHERE zsr.idStudent = r.idStudent
END
ELSE
BEGIN
	UPDATE tblZStudentRank
	SET scoreStd2 = null, scoreStdFinal = null
	FROM tblZStudentRank zsr
	INNER JOIN vwStudent s ON zsr.idStudent = s.idStudent
	where s.form = @form

	UPDATE tblZStudentRank
	SET scoreStd2 = r.score
	FROM tblZStudentRank zsr, (
	SELECT s.idStudent, avg(((score_2 / 10.0) - mean) / sd) as score
	FROM vwStudent s
	INNER JOIN tblZStudentPaperRank zspr ON s.idStudent = zspr.idStudent
	INNER JOIN tblPaper p ON zspr.idPaper = p.idPaper AND s.formGroup = p.formGroup AND (p.idSubject = p.idPaper OR p.idSubject is null)
	INNER JOIN (
	SELECT s.form, p.idPaper, avg(zspr.score_2 / 10.0) as mean, stdev(zspr.score_2 / 10.0) as sd
	FROM vwStudent s
	INNER JOIN tblZStudentPaperRank zspr ON s.idStudent = zspr.idStudent
	INNER JOIN tblPaper p ON zspr.idPaper = p.idPaper AND s.formGroup = p.formGroup AND (p.idSubject = p.idPaper OR p.idSubject is null)
	WHERE zspr.score_2 is not null
	GROUP BY s.form, p.idPaper ) r ON s.form = r.form AND p.idPaper = r.idPaper
	WHERE s.form = @form and zspr.score_2 is not null
	GROUP BY s.idStudent) r
	WHERE zsr.idStudent = r.idStudent
END

UPDATE tblZStudentRank
SET scoreStdFinal = r.score
FROM tblZStudentRank zsr, (
SELECT s.idStudent, avg(((score_final / 10.0) - mean) / sd) as score
FROM vwStudent s
INNER JOIN tblZStudentPaperRank zspr ON s.idStudent = zspr.idStudent
INNER JOIN tblPaper p ON zspr.idPaper = p.idPaper AND s.formGroup = p.formGroup AND (p.idSubject = p.idPaper OR p.idSubject is null)
INNER JOIN (
SELECT s.form, p.idPaper, avg(zspr.score_final / 10.0) as mean, stdev(zspr.score_final / 10.0) as sd
FROM vwStudent s
INNER JOIN tblZStudentPaperRank zspr ON s.idStudent = zspr.idStudent
INNER JOIN tblPaper p ON zspr.idPaper = p.idPaper AND s.formGroup = p.formGroup AND (p.idSubject = p.idPaper OR p.idSubject is null)
WHERE zspr.score_final is not null
GROUP BY s.form, p.idPaper ) r ON s.form = r.form AND p.idPaper = r.idPaper
WHERE s.form = @form and zspr.score_final is not null
GROUP BY s.idStudent) r
WHERE zsr.idStudent = r.idStudent

GO


------------------------------------------------------------------------------------------------
-- stpOutputRankStandard
------------------------------------------------------------------------------------------------

if exists (select * from dbo.sysobjects where id = object_id(N'[dbo].[stpOutputRankStandard]') and OBJECTPROPERTY(id, N'IsProcedure') = 1)
drop procedure [dbo].[stpOutputRankStandard]
GO

CREATE PROCEDURE dbo.stpOutputRankStandard
@form tinyint
AS

UPDATE tblZStudentRank
SET rankStdClass1 = null, rankStdClass2 = null, rankStdClassFinal = null, rankStdForm1 = null, rankStdForm2 = null, rankStdFormFinal = null
FROM tblZStudentRank zsr
INNER JOIN vwStudent s ON zsr.idStudent = s.idStudent
WHERE s.form = @form

--Class
UPDATE tblZStudentRank
SET rankStdClass1 = rank
FROM (
SELECT idStudent, count(idStudent) + 1 AS rank
FROM (
SELECT zsr1.idStudent, zsr1.scoreStd1
FROM
tblZStudentRank zsr1
INNER JOIN vwStudent s1 ON zsr1.idStudent = s1.idStudent,
tblZStudentRank zsr2
INNER JOIN vwStudent s2 ON zsr2.idStudent = s2.idStudent
WHERE s1.form = @form AND s1.class = s2.class AND zsr1.scoreStd1 < zsr2.scoreStd1 ) rA
GROUP BY idStudent ) rB, tblZStudentRank zsr
WHERE zsr.idStudent = rB.idStudent

UPDATE tblZStudentRank
SET rankStdClass2 = rank
FROM (
SELECT idStudent, count(idStudent) + 1 AS rank
FROM (
SELECT zsr1.idStudent, zsr1.scoreStd2
FROM
tblZStudentRank zsr1
INNER JOIN vwStudent s1 ON zsr1.idStudent = s1.idStudent,
tblZStudentRank zsr2
INNER JOIN vwStudent s2 ON zsr2.idStudent = s2.idStudent
WHERE s1.form = @form AND s1.class = s2.class AND zsr1.scoreStd2 < zsr2.scoreStd2 ) rA
GROUP BY idStudent ) rB, tblZStudentRank zsr
WHERE zsr.idStudent = rB.idStudent

UPDATE tblZStudentRank
SET rankStdClassFinal = rank
FROM (
SELECT idStudent, count(idStudent) + 1 AS rank
FROM (
SELECT zsr1.idStudent, zsr1.scoreStdFinal
FROM
tblZStudentRank zsr1
INNER JOIN vwStudent s1 ON zsr1.idStudent = s1.idStudent,
tblZStudentRank zsr2
INNER JOIN vwStudent s2 ON zsr2.idStudent = s2.idStudent
WHERE s1.form = @form AND s1.class = s2.class AND zsr1.scoreStdFinal < zsr2.scoreStdFinal ) rA
GROUP BY idStudent ) rB, tblZStudentRank zsr
WHERE zsr.idStudent = rB.idStudent

UPDATE tblZStudentRank
SET rankStdClass1 = 1
FROM tblZStudentRank zsr
INNER JOIN vwStudent s ON zsr.idStudent = s.idStudent
WHERE s.form = @form AND scoreStd1 is NOT null AND rankStdClass1 is null

UPDATE tblZStudentRank
SET rankStdClass2 = 1
FROM tblZStudentRank zsr
INNER JOIN vwStudent s ON zsr.idStudent = s.idStudent
WHERE s.form = @form AND scoreStd2 is NOT null AND rankStdClass2 is null

UPDATE tblZStudentRank
SET rankStdClassFinal = 1
FROM tblZStudentRank zsr
INNER JOIN vwStudent s ON zsr.idStudent = s.idStudent
WHERE s.form = @form AND scoreStdFinal is NOT null AND rankStdClassFinal is null

--Form
UPDATE tblZStudentRank
SET rankStdForm1 = rank
FROM (
SELECT idStudent, count(idStudent) + 1 AS rank
FROM (
SELECT zsr1.idStudent, zsr1.scoreStd1
FROM
tblZStudentRank zsr1
INNER JOIN vwStudent s1 ON zsr1.idStudent = s1.idStudent,
tblZStudentRank zsr2
INNER JOIN vwStudent s2 ON zsr2.idStudent = s2.idStudent
WHERE s1.form = @form AND s1.form = s2.form AND zsr1.scoreStd1 < zsr2.scoreStd1 ) rA
GROUP BY idStudent ) rB, tblZStudentRank zsr
WHERE zsr.idStudent = rB.idStudent

UPDATE tblZStudentRank
SET rankStdForm2 = rank
FROM (
SELECT idStudent, count(idStudent) + 1 AS rank
FROM (
SELECT zsr1.idStudent, zsr1.scoreStd2
FROM
tblZStudentRank zsr1
INNER JOIN vwStudent s1 ON zsr1.idStudent = s1.idStudent,
tblZStudentRank zsr2
INNER JOIN vwStudent s2 ON zsr2.idStudent = s2.idStudent
WHERE s1.form = @form AND s1.form = s2.form AND zsr1.scoreStd2 < zsr2.scoreStd2 ) rA
GROUP BY idStudent ) rB, tblZStudentRank zsr
WHERE zsr.idStudent = rB.idStudent

UPDATE tblZStudentRank
SET rankStdFormFinal = rank
FROM (
SELECT idStudent, count(idStudent) + 1 AS rank
FROM (
SELECT zsr1.idStudent, zsr1.scoreStdFinal
FROM
tblZStudentRank zsr1
INNER JOIN vwStudent s1 ON zsr1.idStudent = s1.idStudent,
tblZStudentRank zsr2
INNER JOIN vwStudent s2 ON zsr2.idStudent = s2.idStudent
WHERE s1.form = @form AND s1.form = s2.form AND zsr1.scoreStdFinal < zsr2.scoreStdFinal ) rA
GROUP BY idStudent ) rB, tblZStudentRank zsr
WHERE zsr.idStudent = rB.idStudent

UPDATE tblZStudentRank
SET rankStdForm1 = 1
FROM tblZStudentRank zsr
INNER JOIN vwStudent s ON zsr.idStudent = s.idStudent
WHERE s.form = @form AND scoreStd1 is NOT null AND rankStdForm1 is null

UPDATE tblZStudentRank
SET rankStdForm2 = 1
FROM tblZStudentRank zsr
INNER JOIN vwStudent s ON zsr.idStudent = s.idStudent
WHERE s.form = @form AND scoreStd2 is NOT null AND rankStdForm2 is null

UPDATE tblZStudentRank
SET rankStdFormFinal = 1
FROM tblZStudentRank zsr
INNER JOIN vwStudent s ON zsr.idStudent = s.idStudent
WHERE s.form = @form AND scoreStdFinal is NOT null AND rankStdFormFinal is null

GO

------------------------------------------------------------------------------------------------
-- stpGenerateSummary
------------------------------------------------------------------------------------------------

if exists (select * from dbo.sysobjects where id = object_id(N'[dbo].[stpGenerateSummary]') and OBJECTPROPERTY(id, N'IsProcedure') = 1)
drop procedure [dbo].[stpGenerateSummary]
GO

CREATE PROCEDURE dbo.stpGenerateSummary
@form tinyint, @term tinyint
AS

IF exists (
	SELECT *
	FROM tblStudentPaperScore sps
	INNER JOIN vwStudent s ON sps.idStudent = s.idStudent
	WHERE s.form = @form
	AND (s.flgTerm1 = 1 and score_test_1 is null AND score_regular_1 is null AND score_exam_1 is null AND grade_exam_1 is null)
	AND (s.flgTerm2 = 1 and score_test_2 is null AND score_regular_2 is null AND score_exam_2 is null AND grade_exam_2 is null)
)
BEGIN
	RAISERROR('Exists students who have no score or grade', 16, 1)
	return
END

exec stpOutputPaperRankScore @form, @term
exec stpOutputPaperRank @form
exec stpOutputRankScore @form, @term
exec stpOutputRank @form

exec stpOutputPaperRankStandardScore @form, @term
exec stpOutputPaperRankStandard @form
exec stpOutputRankStandardScore @form, @term
exec stpOutputRankStandard @form

GO

------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------

stpGenerateSummary 1, 2
GO
stpGenerateSummary 2, 2
GO
stpGenerateSummary 3, 2
GO
stpGenerateSummary 4, 2
GO
stpGenerateSummary 6, 2
GO
