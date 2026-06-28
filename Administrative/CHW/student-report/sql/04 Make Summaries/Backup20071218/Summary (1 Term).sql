--For general use with "1 term" approach (S7).

------------------------------------------------------------------------------------------------
-- stpOutputPaperRankScore2
------------------------------------------------------------------------------------------------

if exists (select * from dbo.sysobjects where id = object_id(N'[dbo].[stpOutputPaperRankScore2]') and OBJECTPROPERTY(id, N'IsProcedure') = 1)
drop procedure [dbo].[stpOutputPaperRankScore2]
GO

CREATE PROCEDURE dbo.stpOutputPaperRankScore2
@form tinyint
AS

-- Initialize Paper Score
INSERT tblZStudentPaperRank (idStudent, idPaper)
SELECT sp.idStudent, sp.idPaper
FROM vwStudentPaper sp
INNER JOIN tblStudentPaperScore sps ON sps.idStudent = sp.idStudent and sps.idPaper = sp.idPaper
INNER JOIN tblFormPaperWeight fpw ON sp.form = fpw.form and sp.idPaper = fpw.idPaper
AND (fpw.weight_test_1 > 0 OR fpw.weight_regular_1 > 0 OR fpw.weight_exam_1 > 0
OR   fpw.weight_test_2 > 0 OR fpw.weight_regular_2 > 0 OR fpw.weight_exam_2 > 0)
LEFT JOIN tblZStudentPaperRank zspr ON sp.idStudent = zspr.idStudent and sp.idPaper = zspr.idPaper
WHERE sp.form = @form and (sp.flgTerm1 = 1 or sp.flgTerm2 = 1) and zspr.idStudent is null
and (sps.score_test_1 is not null OR sps.score_regular_1 is not null OR sps.score_exam_1 is not null
OR   sps.score_test_2 is not null OR sps.score_regular_2 is not null OR sps.score_exam_2 is not null)

UPDATE tblZStudentPaperRank
SET score_1 = null, score_2 = null, score_final = null, flgRemark_1 = 0, flgRemark_2 = 0
FROM tblZStudentPaperRank zspr
INNER JOIN vwStudent s ON zspr.idStudent = s.idStudent
WHERE s.form = @form

-- Calculate Paper Score
UPDATE tblZStudentPaperRank
SET
score_1 =
case when 
	CASE WHEN weight_test_1 <> 0 THEN weight_test_1 ELSE 0.0 END +
	CASE WHEN weight_regular_1 <> 0 THEN weight_regular_1 ELSE 0.0 END +
	CASE WHEN weight_test_2 <> 0 THEN weight_test_2 ELSE 0.0 END +
	CASE WHEN weight_regular_2 <> 0 THEN weight_regular_2 ELSE 0.0 END = 0.0
THEN
	null
ELSE
	floor(
	(CASE WHEN weight_test_1 <> 0 AND sps.score_test_1 IS NOT null THEN cast(1000.0 as real) * weight_test_1 * sps.score_test_1 / fps.score_test_1 ELSE 0.0 END +
	 CASE WHEN weight_regular_1 <> 0 AND sps.score_regular_1 IS NOT null THEN cast(1000.0 as real) * weight_regular_1 * sps.score_regular_1 / fps.score_regular_1 ELSE 0.0 END +
	 CASE WHEN weight_test_2 <> 0 AND sps.score_test_2 IS NOT null THEN cast(1000.0 as real) * weight_test_2 * sps.score_test_2 / fps.score_test_2 ELSE 0.0 END +
	 CASE WHEN weight_regular_2 <> 0 AND sps.score_regular_2 IS NOT null THEN cast(1000.0 as real) * weight_regular_2 * sps.score_regular_2 / fps.score_regular_2 ELSE 0.0 END) /
	(CASE WHEN weight_test_1 <> 0 THEN weight_test_1 ELSE 0.0 END +
	 CASE WHEN weight_regular_1 <> 0 THEN weight_regular_1 ELSE 0.0 END +
	 CASE WHEN weight_test_2 <> 0 THEN weight_test_2 ELSE 0.0 END +
	 CASE WHEN weight_regular_2 <> 0 THEN weight_regular_2 ELSE 0.0 END)
	)
END,
score_2 =
CASE WHEN
	CASE WHEN weight_exam_1 <> 0 THEN weight_exam_1 ELSE 0.0 END +
	CASE WHEN weight_exam_2 <> 0 THEN weight_exam_2 ELSE 0.0 END = 0.0
THEN null
ELSE
	floor(
	(
	 CASE WHEN weight_exam_1 <> 0 AND sps.score_exam_1 IS NOT null THEN cast(1000.0 as real) * weight_exam_1 * sps.score_exam_1 / fps.score_exam_1 ELSE 0.0 END +
	 CASE WHEN weight_exam_2 <> 0 AND sps.score_exam_2 IS NOT null THEN cast(1000.0 as real) * weight_exam_2 * sps.score_exam_2 / fps.score_exam_2 ELSE 0.0 END) /
	(CASE WHEN weight_exam_1 <> 0 THEN weight_exam_1 ELSE 0.0 END +
	 CASE WHEN weight_exam_2 <> 0 THEN weight_exam_2 ELSE 0.0 END)
	)
END,
flgRemark_1 = sps.flgRemark_1,
flgRemark_2 = sps.flgRemark_2,
flgIgnore_1 = sps.flgIgnore_1,
flgIgnore_2 = sps.flgIgnore_2
FROM tblZStudentPaperRank zspr
INNER JOIN vwStudent s ON zspr.idStudent = s.idStudent
INNER JOIN tblStudentPaperScore sps ON s.idStudent = sps.idStudent AND zspr.idPaper = sps.idPaper
INNER JOIN tblFormPaperScore fps ON fps.form = s.form AND fps.idPaper = sps.idPaper
INNER JOIN tblFormPaperWeight fpw ON fpw.form = s.form AND fpw.idPaper = sps.idPaper AND (
fpw.weight_test_1 > 0 OR fpw.weight_regular_1 > 0 OR fpw.weight_exam_1 > 0 OR
fpw.weight_test_2 > 0 OR fpw.weight_regular_2 > 0 OR fpw.weight_exam_2 > 0)
WHERE s.form = @form AND (
sps.score_test_1 is not null OR sps.score_regular_1 is not null OR sps.score_exam_1 is not null OR
sps.score_test_2 is not null OR sps.score_regular_2 is not null OR sps.score_exam_2 is not null)

--clear unnecessary entities
DELETE
FROM tblZStudentPaperRank
WHERE score_1 is null AND score_2 is null AND score_final is null

--score_final
UPDATE tblZStudentPaperRank
SET score_final = floor(
	(
		floor(CASE WHEN zspr.score_1 is null THEN 0 ELSE zspr.score_1 END / 10.0 + .5) * 10.0 *
		(CASE WHEN weight_test_1 <> 0 THEN weight_test_1 ELSE 0.0 END +
		 CASE WHEN weight_regular_1 <> 0 THEN weight_regular_1 ELSE 0.0 END +
		 CASE WHEN weight_test_2 <> 0 THEN weight_test_2 ELSE 0.0 END +
		 CASE WHEN weight_regular_2 <> 0 THEN weight_regular_2 ELSE 0.0 END) +
		floor(CASE WHEN zspr.score_2 is null THEN 0 ELSE zspr.score_2 END / 10.0 + .5) * 10.0 *
		(CASE WHEN weight_exam_1 <> 0 THEN weight_exam_1 ELSE 0.0 END +
		 CASE WHEN weight_exam_2 <> 0 THEN weight_exam_2 ELSE 0.0 END)
	) /
	(
		CASE WHEN weight_test_1 <> 0 THEN weight_test_1 ELSE 0.0 END +
		CASE WHEN weight_regular_1 <> 0 THEN weight_regular_1 ELSE 0.0 END +
		CASE WHEN weight_test_2 <> 0 THEN weight_test_2 ELSE 0.0 END +
		CASE WHEN weight_regular_2 <> 0 THEN weight_regular_2 ELSE 0.0 END +
		CASE WHEN weight_exam_1 <> 0 THEN weight_exam_1 ELSE 0.0 END +
		CASE WHEN weight_exam_2 <> 0 THEN weight_exam_2 ELSE 0.0 END
	)
)
FROM tblZStudentPaperRank zspr
INNER JOIN vwStudent s ON s.idStudent = zspr.idStudent
INNER JOIN tblFormPaperWeight fpw ON zspr.idPaper = fpw.idPaper AND s.form = fpw.form
INNER JOIN tblPaper p ON zspr.idPaper = p.idPaper AND s.formGroup = p.formGroup AND (p.idPaper = p.idSubject OR p.idSubject is not null)
WHERE s.form = @form AND (score_1 is not null OR score_2 is not null)

-- Initialize Subject Score
INSERT tblZStudentPaperRank (idStudent, idPaper)
SELECT DISTINCT s.idStudent, p.idSubject
FROM vwStudent s
INNER JOIN tblZStudentPaperRank zspr ON s.idStudent = zspr.idStudent
INNER JOIN tblFormPaperWeight fpw ON s.form = fpw.form AND zspr.idPaper = fpw.idPaper AND (
fpw.weight_test_1 > 0 OR fpw.weight_regular_1 > 0 OR fpw.weight_exam_1 > 0 OR
fpw.weight_test_2 > 0 OR fpw.weight_regular_2 > 0 OR fpw.weight_exam_2 > 0)
INNER JOIN tblPaper p ON zspr.idPaper = p.idPaper AND p.idSubject <> p.idPaper AND p.formGroup = s.formGroup
LEFT JOIN tblZStudentPaperRank zspr2 ON s.idStudent = zspr2.idStudent and p.idSubject = zspr2.idPaper
WHERE s.form = @form AND zspr2.idStudent is null AND (zspr.score_1 is not null OR zspr.score_2 is not null) AND (zspr.flgIgnore_1 = 0 AND zspr.flgIgnore_2 = 0)

-- Calculte Subject Score
UPDATE tblZStudentPaperRank
SET score_final = r.score_final
FROM tblZStudentPaperRank zspr, (
SELECT zspr.idStudent, p.idSubject,
score_final = floor(sum(floor(score_final / 10.0 + .5) * 10.0 * weight) / sum(weight))
FROM tblZStudentPaperRank zspr
INNER JOIN vwStudent s ON s.idStudent = zspr.idStudent
INNER JOIN tblFormPaperWeight fpw ON zspr.idPaper = fpw.idPaper AND s.form = fpw.form
INNER JOIN tblPaper p ON zspr.idPaper = p.idPaper AND p.idSubject <> p.idPaper AND s.formGroup = p.formGroup
WHERE s.form = @form
GROUP BY zspr.idStudent, p.idSubject) r
WHERE zspr.idStudent = r.idStudent AND zspr.idPaper = r.idSubject

GO


------------------------------------------------------------------------------------------------
-- stpOutputRankScore2
------------------------------------------------------------------------------------------------

if exists (select * from dbo.sysobjects where id = object_id(N'[dbo].[stpOutputRankScore2]') and OBJECTPROPERTY(id, N'IsProcedure') = 1)
drop procedure [dbo].[stpOutputRankScore2]
GO

CREATE PROCEDURE dbo.stpOutputRankScore2
@form tinyint
AS
-- score_1, score_2
INSERT tblZStudentRank (idStudent)
SELECT DISTINCT zspr.idStudent
FROM tblZStudentPaperRank zspr
INNER JOIN vwStudent s ON s.idStudent = zspr.idStudent
INNER JOIN tblFormPaperWeight fpw ON s.form = fpw.form AND zspr.idPaper = fpw.idPaper
INNER JOIN tblPaper p ON zspr.idPaper = p.idPaper AND p.formGroup = s.formGroup AND (p.idSubject = p.idPaper OR p.idSubject is null)
LEFT JOIN tblZStudentRank zsr ON s.idStudent = zsr.idStudent
WHERE s.form = @form and (zspr.score_1 is not null OR zspr.score_2 is not null) AND zsr.idStudent is null

UPDATE tblZStudentRank
SET score_1 = null, score_2 = null, score_final = null
FROM tblZStudentRank zsr
INNER JOIN vwStudent s ON zsr.idStudent = s.idStudent
WHERE s.form = @form

-- final
UPDATE tblZStudentRank
SET score_final = r.score_final
FROM tblZStudentRank zsr, (
SELECT zspr.idStudent, score_final = floor(sum(floor(score_final / 10.0 + .5) * 10.0 * weight) / sum(weight) + .5)
FROM tblZStudentPaperRank zspr
INNER JOIN vwStudent s ON s.idStudent = zspr.idStudent
INNER JOIN tblPaper p ON zspr.idPaper = p.idPaper AND p.formGroup = s.formGroup AND (p.idSubject = p.idPaper OR p.idSubject is null)
INNER JOIN tblFormPaperWeight fpw ON s.form = fpw.form AND zspr.idPaper = fpw.idPaper AND weight > 0
WHERE s.form = @form AND zspr.score_final is not null
GROUP BY zspr.idStudent) r
WHERE zsr.idStudent = r.idStudent

DELETE
FROM tblZStudentRank
WHERE score_1 is null AND score_2 is null AND score_final is null

GO


------------------------------------------------------------------------------------------------
-- stpGenerateSummary2
------------------------------------------------------------------------------------------------

if exists (select * from dbo.sysobjects where id = object_id(N'[dbo].[stpGenerateSummary2]') and OBJECTPROPERTY(id, N'IsProcedure') = 1)
drop procedure [dbo].[stpGenerateSummary2]
GO

CREATE PROCEDURE dbo.stpGenerateSummary2
@form tinyint
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

exec stpOutputPaperRankScore2 @form
exec stpOutputPaperRank @form
exec stpOutputRankScore2 @form
exec stpOutputRank @form

exec stpOutputPaperRankStandardScore @form, 2
exec stpOutputPaperRankStandard @form
exec stpOutputRankStandardScore @form, 2
exec stpOutputRankStandard @form

GO

------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------

stpGenerateSummary2 5
go

stpGenerateSummary2 7
go