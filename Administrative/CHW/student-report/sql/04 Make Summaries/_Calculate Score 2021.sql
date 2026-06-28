------------------------------------------------------------------------------------------------
-- stpCalculateScore
------------------------------------------------------------------------------------------------

if exists (select * from dbo.sysobjects where id = object_id(N'[dbo].[stpCalculateScore]') and OBJECTPROPERTY(id, N'IsProcedure') = 1)
drop procedure [dbo].[stpCalculateScore]
GO

CREATE PROCEDURE dbo.stpCalculateScore_2021
@form tinyint, @term tinyint
AS


--!Calculate Paper Scores

--Print '!A'
-- Initialize
DELETE
FROM tblZStudentRank2
WHERE form = @form and term in (0, @term)

--Print '!B'
--Regular
--KK changed to 4-digit
INSERT tblZStudentRank2(idStudent, form, idPaper, flgStandard, section, term, score, flgIgnore, flgAbsent)
SELECT sp.idStudent, sp.form, sp.idPaper, 0, 'R', @term, floor(
(CASE WHEN fpw.weightTest > 0 AND fps.scoreTest IS NOT null AND sps.scoreTest IS NOT null THEN cast(10000.0 as real) * fpw.weightTest * sps.scoreTest / fps.scoreTest ELSE 0.0 END +
 CASE WHEN fpw.weightRegular > 0 AND fps.scoreRegular IS NOT null AND sps.scoreRegular IS NOT null THEN cast(10000.0 as real) * fpw.weightRegular * sps.scoreRegular / fps.scoreRegular ELSE 0.0 END) / 
(fpw.weightTest + fpw.weightRegular)
), 
case when sps.flgIgnore is null then 0 else sps.flgIgnore end, 
case when sps.flgIgnore is null then 0 else sps.flgAbsent end
FROM vwStudentPaper sp
INNER JOIN vwFormPaperScore fps ON fps.form = sp.form AND fps.idPaper = sp.idPaper AND fps.term = @term
INNER JOIN vwFormPaperWeight fpw ON fpw.form = sp.form AND fpw.idPaper = sp.idPaper AND (fpw.weightTest > 0 OR fpw.weightRegular > 0) AND fpw.term = @term
LEFT JOIN vwStudentPaperScore sps ON sp.idStudent = sps.idStudent AND sp.idPaper = sps.idPaper AND sps.term = @term
WHERE sp.form = @form AND sp.idSubject = sp.idPaper AND ((@term = 1 AND sp.flgTerm1 = 1) OR (@term = 2 AND sp.flgTerm2 = 1)) AND (fpw.weightTest + fpw.weightRegular > 0)

--Print '!C'
--Exam (total mark)
--KK changed to 4-digit
INSERT tblZStudentRank2(idStudent, form, idPaper, flgStandard, section, term, score, flgIgnore, flgAbsent)
SELECT sp.idStudent, sp.form, sp.idPaper, 0, 'E', @term, floor(
CASE WHEN fps.scoreExam IS NOT null AND sps.scoreExam IS NOT null THEN cast(10000.0 as real) * fpw.weightExam * sps.scoreExam / fps.scoreExam ELSE 0.0 END / fpw.weightExam
), 
case when sps.flgIgnore is null then 0 else sps.flgIgnore end, 
case when sps.flgIgnore is null then 0 else sps.flgAbsent end
FROM vwStudentPaper sp
INNER JOIN vwFormPaperScore fps ON fps.form = sp.form AND fps.idPaper = sp.idPaper AND fps.term = @term
INNER JOIN vwFormPaperWeight fpw ON fpw.form = sp.form AND fpw.idPaper = sp.idPaper AND fpw.weightExam > 0 AND fpw.term = @term
LEFT JOIN vwStudentPaperScore sps ON sp.idStudent = sps.idStudent AND sp.idPaper = sps.idPaper AND sps.term = @term
WHERE sp.form = @form AND ((@term = 1 AND sp.flgTerm1 = 1) OR (@term = 2 AND sp.flgTerm2 = 1)) AND (sp.flgCompound = 0 OR sp.idSubject <> sp.idPaper) AND fpw.weightExam > 0

--Print '!D'
--Exam (Subject) (Chi, Eng) (total mark)
-- program unchanged, but the data is corrected to 1 d.p.
INSERT tblZStudentRank2(idStudent, form, idPaper, flgStandard, section, term, score, flgIgnore, flgAbsent)
SELECT sp.idStudent, sp.form, sp.idSubject, 0, 'E', @term, floor(sum(floor(case when score is null then 0.0 else score end / 10.0 + .5) * 10.0 * case when weight is null then 0.0 else weight end) / sum(case when weight is null then 0.0 else weight end)), 0, 0
FROM vwStudentPaper sp
LEFT JOIN tblZStudentRank2 zsr ON sp.idStudent = zsr.idStudent and sp.idPaper = zsr.idPaper  AND zsr.flgStandard = 0 AND zsr.section = 'E' AND zsr.term = @term 
LEFT JOIN tblFormPaperWeight fpw ON sp.form = fpw.form AND sp.idPaper = fpw.idPaper AND zsr.flgIgnore = 0
WHERE sp.form = @form AND sp.idSubject <> sp.idPaper AND ((@term = 1 AND sp.flgTerm1 = 1) OR (@term = 2 AND sp.flgTerm2 = 1))
GROUP BY sp.idStudent, sp.form, sp.idSubject

--Print '!E'
--Overall
-- program unchanged, but the data is corrected to 1 d.p.
INSERT tblZStudentRank2(idStudent, form, idPaper, flgStandard, section, term, score)
SELECT sp.idStudent, sp.form, sp.idPaper, 0, 'O', @term, floor(
	(
		CASE WHEN fpw.weightTest > 0 OR fpw.weightRegular > 0 THEN 
			case when zsr1.score is null then 0.0 else floor(zsr1.score / 10.0 + .5) * 10.0 end * (fpw.weightTest + fpw.weightRegular)
		ELSE 
			0.0 
		END +
		CASE WHEN fpw.weightExam > 0 THEN 
			case when zsr2.score is null then 0.0 else floor(zsr2.score / 10.0 + .5) * 10.0 end * fpw.weightExam
		ELSE 
			0.0 
		END
	) /
	(
		CASE WHEN fpw.weightTest > 0 OR fpw.weightRegular > 0 THEN 
			fpw.weightTest + fpw.weightRegular 
		ELSE 
			0.0 
		END +
		CASE WHEN fpw.weightExam > 0 THEN 
			fpw.weightExam 
		ELSE 
			0.0 
		END
	)
)
FROM vwStudentPaper sp
INNER JOIN vwFormPaperWeight fpw ON fpw.form = sp.form AND fpw.idPaper = sp.idPaper AND (fpw.weightTest > 0 OR fpw.weightRegular > 0 OR fpw.weightExam > 0) AND fpw.term = @term
LEFT JOIN tblZStudentRank2 zsr1 on sp.idStudent = zsr1.idStudent and sp.idPaper = zsr1.idPaper and zsr1.flgStandard = 0 AND zsr1.section = 'R' AND zsr1.term = @term
LEFT JOIN tblZStudentRank2 zsr2 on sp.idStudent = zsr2.idStudent and sp.idPaper = zsr2.idPaper and zsr2.flgStandard = 0 AND zsr2.section = 'E' AND zsr2.term = @term
WHERE sp.form = @form AND sp.idSubject = sp.idPaper AND ((@term = 1 AND sp.flgTerm1 = 1) OR (@term = 2 AND sp.flgTerm2 = 1)) AND (zsr1.score is not null OR zsr2.score is not null)

--Print '!F'
--Standard Paper Scores
INSERT tblZStudentRank2(idStudent, form, idPaper, flgStandard, section, term, score)
SELECT sp.idSTudent, sp.form, sp.idPaper, 1, zsr.section, zsr.term, 
CASE WHEN zsr.score is null or r.sd is null THEN null else ((zsr.score / 10.0) - r.mean) / r.sd END
FROM vwStudentPaper sp 
INNER JOIN tblZStudentRank2 zsr ON sp.idStudent = zsr.idStudent and sp.idPaper = zsr.idPaper
LEFT JOIN (
	SELECT sp.form, sp.idPaper, zsr.flgStandard, zsr.section, zsr.term, avg(zsr.score / 10.0) as mean, stdev(zsr.score / 10.0) as sd
	FROM vwStudentPaper sp 
	INNER JOIN tblZStudentRank2 zsr ON sp.idStudent = zsr.idStudent and sp.idPaper = zsr.idPaper
	WHERE zsr.score is not null
	GROUP BY sp.form, sp.idPaper, zsr.flgStandard, zsr.section, zsr.term
) r ON sp.form = r.form AND sp.idPaper = r.idPaper AND zsr.flgStandard = r.flgStandard AND zsr.section = r.section AND zsr.term = r.term and r.sd > 0
WHERE sp.form = @form AND zsr.term = @term AND zsr.flgStandard = 0 AND ((@term = 1 AND sp.flgTerm1 = 1) OR (@term = 2 AND sp.flgTerm2 = 1))

--Print '!G'
--!Calculate Average Scores
INSERT tblZStudentRank2(idStudent, form, idPaper, flgStandard, section, term, score)
SELECT sp.idStudent, sp.form, '', zsr.flgStandard, zsr.section, zsr.term, 
floor(sum(floor(case when zsr.score is null then 0.0 else zsr.score end  / 10.0 + .5) * 10.0 * fpw.weight) / sum(fpw.weight) + .5)
FROM vwStudentPaper sp
INNER JOIN tblZStudentRank2 zsr ON sp.idStudent = zsr.idStudent and sp.idPaper = zsr.idPaper and zsr.flgIgnore = 0
INNER JOIN tblFormPaperWeight fpw ON sp.form = fpw.form AND zsr.idPaper = fpw.idPaper AND fpw.weight > 0
WHERE sp.form = @form AND zsr.flgStandard = 0 AND zsr.term = @term AND ((@term = 1 AND sp.flgTerm1 = 1) OR (@term = 2 AND sp.flgTerm2 = 1))
GROUP BY sp.idStudent, sp.form, zsr.flgStandard, zsr.section, zsr.term

--Print '!H'
--!Calculate Standard Average Scores
INSERT tblZStudentRank2(idStudent, form, idPaper, flgStandard, section, term, score)
SELECT sp.idStudent, sp.form, '', zsr.flgStandard, zsr.section, zsr.term, 
sum(case when zsr.score is null then 0.0 else zsr.score end * fpw.weight) / sum(fpw.weight)
FROM vwStudentPaper sp
INNER JOIN tblZStudentRank2 zsr ON sp.idStudent = zsr.idStudent and sp.idPaper = zsr.idPaper and zsr.flgIgnore = 0
INNER JOIN tblFormPaperWeight fpw ON sp.form = fpw.form AND zsr.idPaper = fpw.idPaper AND fpw.weight > 0
WHERE sp.form = @form AND zsr.flgStandard = 1 AND zsr.term = @term AND ((@term = 1 AND sp.flgTerm1 = 1) OR (@term = 2 AND sp.flgTerm2 = 1))
GROUP BY sp.idStudent, sp.form, zsr.flgStandard, zsr.section, zsr.term

--Print '!I'
--!Calculate Year Scores
INSERT tblZStudentRank2(idStudent, form, idPaper, flgStandard, section, term, score)
SELECT sp.idStudent, sp.form, sp.idPaper, 0, sp.section, 0,
case 
	when zsr1.score is not null and zsr2.score is not null then
		floor(
			(
				case when zsr1.score is not null then floor(zsr1.score / 10.0 + .5) * 10.0 * ftw.weight_1 else 0 end + 
				case when zsr2.score is not null then floor(zsr2.score / 10.0 + .5) * 10.0 * ftw.weight_2 else 0 end 
			) / 
			(
				case when zsr1.score is not null then ftw.weight_1 else 0 end + 
				case when zsr2.score is not null then ftw.weight_2 else 0 end
			)
		)
	when zsr1.score is not null then
		zsr1.score
	when zsr2.score is not null then
		zsr2.score
	else 
		null
end 
FROM (
	SELECT r.idStudent, r.class, r.idSubject, r.idPaper, r.form, r.formGroup, r.flgTerm1, r.flgTerm2, r.flgCompound, ps.section 
	FROM ( 
	SELECT idStudent, class, idSubject, idPaper, form, formGroup, flgTerm1, flgTerm2, flgCompound 
	FROM vwStudentPaper 
	WHERE flgScore = 1 AND idSubject = idPaper ) r, tblPaperSection ps
) sp
INNER JOIN tblStudent s ON s.idStudent = sp.idStudent
INNER JOIN tblFormPaperWeight fpw ON sp.form = fpw.form AND sp.idPaper = fpw.idPaper and (
	sp.section = 'O' OR (
		(sp.flgTerm1 = 1 AND (
			(sp.section = 'R' and (fpw.weight_regular_1 + fpw.weight_test_1 > 0)) OR
			(sp.section = 'E' and fpw.weight_exam_1 > 0)
		)) OR 
		(sp.flgTerm2 = 1 AND (
			(sp.section = 'R' and (fpw.weight_regular_2 + fpw.weight_test_2 > 0)) OR
			(sp.section = 'E' and fpw.weight_exam_2 > 0)
		))
	) 
)
INNER JOIN tblFormTermWeight ftw ON sp.form = ftw.form
LEFT JOIN tblZStudentRank2 zsr1 ON sp.idStudent = zsr1.idStudent and sp.idPaper = zsr1.idPaper and zsr1.flgStandard = 0 AND zsr1.section = sp.section and zsr1.term = 1 and sp.flgTerm1 = 1
LEFT JOIN tblZStudentRank2 zsr2 ON sp.idStudent = zsr2.idStudent and sp.idPaper = zsr2.idPaper and zsr2.flgStandard = 0 AND zsr2.section = sp.section and zsr2.term = 2 and sp.flgTerm2 = 1
WHERE sp.form = @form AND ((@term = 1 and sp.flgTerm1 = 1) OR (@term = 2 and sp.flgTerm2 = 1)  OR (@form = 3 and  sp.idPaper in ('CMP', 'BIO', 'CHM')) )

INSERT tblZStudentRank2(idStudent, form, idPaper, flgStandard, section, term, score)
SELECT sp.idStudent, sp.form, sp.idPaper, 0, sp.section, 0,
case when zsr1.score is not null or zsr2.score is not null then
	floor(
		(
			case when zsr1.score is not null then zsr1.score * ftw.weight_1 else 0 end + 
			case when zsr2.score is not null then zsr2.score * ftw.weight_2 else 0 end 
		) / 
		(
			case when zsr1.score is not null then ftw.weight_1 else 0 end + 
			case when zsr2.score is not null then ftw.weight_2 else 0 end
		) + .5
	)
else
	null
end 
FROM (
	SELECT r.idStudent, r.class, r.idSubject, r.idPaper, r.form, r.formGroup, r.flgTerm1, r.flgTerm2, r.flgCompound, ps.section 
	FROM ( 
	SELECT idStudent, class, '' as idSubject, '' as idPaper, form, formGroup, flgTerm1, flgTerm2, 0 as flgCompound
	FROM vwStudent ) r, tblPaperSection ps
) sp
INNER JOIN tblStudent s ON s.idStudent = sp.idStudent
INNER JOIN tblFormTermWeight ftw ON sp.form = ftw.form
LEFT JOIN tblZStudentRank2 zsr1 ON sp.idStudent = zsr1.idStudent and sp.idPaper = zsr1.idPaper and zsr1.flgStandard = 0 AND zsr1.section = sp.section and zsr1.term = 1 and sp.flgTerm1 = 1
LEFT JOIN tblZStudentRank2 zsr2 ON sp.idStudent = zsr2.idStudent and sp.idPaper = zsr2.idPaper and zsr2.flgStandard = 0 AND zsr2.section = sp.section and zsr2.term = 2 and sp.flgTerm2 = 1
WHERE sp.form = @form AND ((@term = 1 and sp.flgTerm1 = 1) OR (@term = 2 and sp.flgTerm2 = 1)      )

--Print '!J'
--!Calculate Standard Year Scores
INSERT tblZStudentRank2(idStudent, form, idPaper, flgStandard, section, term, score)
SELECT sp.idStudent, sp.form, sp.idPaper, 1, sp.section, 0,
case when zsr1.score is not null or zsr2.score is not null then
	(
		case when zsr1.score is not null then zsr1.score * ftw.weight_1 else 0 end + 
		case when zsr2.score is not null then zsr2.score * ftw.weight_2 else 0 end 
	) / 
	(
		case when zsr1.score is not null then ftw.weight_1 else 0 end + 
		case when zsr2.score is not null then ftw.weight_2 else 0 end
	)
else
	null
end 
FROM (
	SELECT r.idStudent, r.class, r.idSubject, r.idPaper, r.form, r.formGroup, r.flgTerm1, r.flgTerm2, r.flgCompound, ps.section 
	FROM ( 
	SELECT idStudent, class, idSubject, idPaper, form, formGroup, flgTerm1, flgTerm2, flgCompound 
	FROM vwStudentPaper 
	WHERE flgScore = 1 AND idSubject = idPaper ) r, tblPaperSection ps
) sp
INNER JOIN tblFormPaperWeight fpw ON sp.form = fpw.form AND sp.idPaper = fpw.idPaper and (
	sp.section = 'O' OR (
		(sp.flgTerm1 = 1 AND (
			(sp.section = 'R' and (fpw.weight_regular_1 + fpw.weight_test_1 > 0)) OR
			(sp.section = 'E' and fpw.weight_exam_1 > 0)
		)) OR 
		(sp.flgTerm2 = 1 AND (
			(sp.section = 'R' and (fpw.weight_regular_2 + fpw.weight_test_2 > 0)) OR
			(sp.section = 'E' and fpw.weight_exam_2 > 0)
		))
	) 
)
INNER JOIN tblFormTermWeight ftw ON sp.form = ftw.form
LEFT JOIN tblZStudentRank2 zsr1 ON sp.idStudent = zsr1.idStudent and sp.idPaper = zsr1.idPaper and zsr1.flgStandard = 1 AND zsr1.section = sp.section and zsr1.term = 1 and sp.flgTerm1 = 1
LEFT JOIN tblZStudentRank2 zsr2 ON sp.idStudent = zsr2.idStudent and sp.idPaper = zsr2.idPaper and zsr2.flgStandard = 1 AND zsr2.section = sp.section and zsr2.term = 2 and sp.flgTerm2 = 1
WHERE sp.form = @form AND ((@term = 1 and sp.flgTerm1 = 1) OR (@term = 2 and sp.flgTerm2 = 1) OR (@form = 3 and  sp.idPaper in ('CMP', 'BIO', 'CHM')) )

INSERT tblZStudentRank2(idStudent, form, idPaper, flgStandard, section, term, score)
SELECT sp.idStudent, sp.form, sp.idPaper, 1, sp.section, 0,
case when zsr1.score is not null or zsr2.score is not null then
	(
		case when zsr1.score is not null then zsr1.score * ftw.weight_1 else 0 end + 
		case when zsr2.score is not null then zsr2.score * ftw.weight_2 else 0 end 
	) / 
	(
		case when zsr1.score is not null then ftw.weight_1 else 0 end + 
		case when zsr2.score is not null then ftw.weight_2 else 0 end
	)
else
	null
end 
FROM (
	SELECT r.idStudent, r.class, r.idSubject, r.idPaper, r.form, r.formGroup, r.flgTerm1, r.flgTerm2, r.flgCompound, ps.section 
	FROM ( 
	SELECT idStudent, class, '' as idSubject, '' as idPaper, form, formGroup, flgTerm1, flgTerm2, 0 as flgCompound
	FROM vwStudent ) r, tblPaperSection ps
) sp
INNER JOIN tblFormTermWeight ftw ON sp.form = ftw.form
LEFT JOIN tblZStudentRank2 zsr1 ON sp.idStudent = zsr1.idStudent and sp.idPaper = zsr1.idPaper and zsr1.flgStandard = 1 AND zsr1.section = sp.section and zsr1.term = 1 and sp.flgTerm1 = 1
LEFT JOIN tblZStudentRank2 zsr2 ON sp.idStudent = zsr2.idStudent and sp.idPaper = zsr2.idPaper and zsr2.flgStandard = 1 AND zsr2.section = sp.section and zsr2.term = 2 and sp.flgTerm2 = 1
WHERE sp.form = @form AND ((@term = 1 and sp.flgTerm1 = 1) OR (@term = 2 and sp.flgTerm2 = 1))

--Print '!K'
--!Generate Class Ranks
-- KK 4-digit
UPDATE tblZStudentRank2
SET rankClass = rk
FROM tblZStudentRank2 zsr, (
	SELECT r.idStudent, r.idPaper, r.flgStandard, r.section, r.term, sum(case when r2.class is null then 0 else 1 end) + 1 as rk
	FROM (
		SELECT s.idStudent, s.class, zsr.form, zsr.idPaper, zsr.flgStandard, zsr.section, zsr.term, zsr.score
		FROM tblStudent s
		INNER JOIN tblZStudentRank2 zsr ON s.idStudent = zsr.idStudent
		WHERE zsr.score is not null
	) r
	LEFT JOIN (
		SELECT s.class, zsr.form, zsr.idPaper, zsr.flgStandard, zsr.section, zsr.term, zsr.score
		FROM tblStudent s
		INNER JOIN tblZStudentRank2 zsr ON s.idStudent = zsr.idStudent
		WHERE zsr.score is not null
	) r2 ON r.class = r2.class and r.idPaper = r2.idPaper and r.flgStandard = r2.flgStandard AND r.section = r2.section AND r.term = r2.term and r.score   <  r2.score 
	GROUP BY r.idStudent, r.idPaper, r.flgStandard, r.section, r.term
) r
WHERE zsr.form = @form AND (zsr.term = @term OR zsr.term = 0) and zsr.idStudent = r.idStudent AND zsr.idPaper = r.idPaper AND zsr.flgStandard = r.flgStandard AND zsr.section = r.section AND zsr.term = r.term

--Print '!L'
--!Generate Form Ranks
-- KK 4-digit
UPDATE tblZStudentRank2
SET rankForm = rk
FROM tblZStudentRank2 zsr, (
	SELECT r.idStudent, r.idPaper, r.flgStandard, r.section, r.term, sum(case when r2.form is null then 0 else 1 end) + 1 as rk
	FROM (
		SELECT zsr.idStudent, zsr.form, zsr.idPaper, zsr.flgStandard, zsr.section, zsr.term, zsr.score
		FROM tblZStudentRank2 zsr
		WHERE zsr.score is not null
	) r
	LEFT JOIN (
		SELECT zsr.form, zsr.idPaper, zsr.flgStandard, zsr.section, zsr.term, zsr.score
		FROM tblZStudentRank2 zsr
		WHERE zsr.score is not null
	) r2 ON r.form = r2.form and r.idPaper = r2.idPaper and r.flgStandard = r2.flgStandard AND r.section = r2.section AND r.term = r2.term and  r.score    <  r2.score
	GROUP BY r.idStudent, r.idPaper, r.flgStandard, r.section, r.term
) r
WHERE zsr.form = @form AND (zsr.term = @term OR zsr.term = 0) and zsr.idStudent = r.idStudent AND zsr.idPaper = r.idPaper AND zsr.flgStandard = r.flgStandard AND zsr.section = r.section AND zsr.term = r.term
GO



-- All updated 2021/07/03
--2,1  form 2, term 1

stpCalculateScore_2021 1, 1
GO

stpCalculateScore_2021 2, 1
GO

stpCalculateScore_2021 3, 1
GO

stpCalculateScore_2021 4, 1
GO

stpCalculateScore_2021 5, 1
GO


-- S6 Mock Exam
stpCalculateScore_2021 6, 2
GO

--
--stpCalculateScore 3, 1
--GO
--
--stpCalculateScore 6, 2
--GO
--


--2,1  form 2, term 2

stpCalculateScore_2021 1, 2
GO

stpCalculateScore_2021 2, 2
GO

stpCalculateScore_2021 3, 2
GO

stpCalculateScore_2021 4, 2
GO

stpCalculateScore_2021 5, 2
GO


