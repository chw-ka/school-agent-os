------------------------------------------------------------------------------------------------
-- stpCalculateAssessment
------------------------------------------------------------------------------------------------

if exists (select * from dbo.sysobjects where id = object_id(N'[dbo].[stpCalculateAssessment]') and OBJECTPROPERTY(id, N'IsProcedure') = 1)
drop procedure [dbo].[stpCalculateAssessment]
GO

CREATE PROCEDURE dbo.stpCalculateAssessment
@form tinyint, @term tinyint
AS
-- indicate assessments for calculating
UPDATE tblAssessment 
SET flgCalculate = 1 
WHERE idAssessment IN ( 
SELECT distinct a.idAssessment 
FROM tblAssessment a 
INNER JOIN tblAssessmentClass ac ON a.idAssessment = ac.idAssessment 
INNER JOIN tblClass c ON ac.class = c.class 
INNER JOIN tblFormTerm ft ON c.form = ft.form AND (a.dateAssessment between ft.dateStart AND ft.dateEnd) 
WHERE ft.form = @form AND ft.term = @term )

-- add missing form paper score 
INSERT tblFormPaperScore (form, idPaper, formGroup) 
SELECT distinct c.form, p.idPaper, f.formGroup 
FROM tblAssessment a 
INNER JOIN tblAssessmentClass ac ON a.idAssessment = ac.idAssessment 
INNER JOIN tblClass c ON ac.class = c.class 
INNER JOIN tblForm f ON f.form = c.form
INNER JOIN tblPaper p ON p.idSubject = a.idSubject and f.formGroup = p.formGroup
LEFT JOIN tblFormPaperScore fps ON c.form = fps.form AND p.idPaper = fps.idPaper 
WHERE fps.form is null AND a.flgCalculate = 1 and f.form = @form

-- add missing student paper score 
INSERT tblStudentPaperScore (idStudent, idPaper) 
SELECT distinct sa.idStudent, sp.idPaper 
FROM tblStudentAssessment sa 
INNER JOIN tblAssessment a ON sa.idAssessment = a.idAssessment AND a.flgCalculate = 1 
INNER JOIN vwStudentPaper sp ON sp.idStudent = sa.idStudent AND sp.idSubject = a.idSubject AND ((@term = 1 AND flgTerm1 = 1) OR (@term = 2 AND flgTerm2 = 1)) 
LEFT JOIN tblStudentPaperScore sps ON sps.idStudent = sa.idStudent AND sps.idPaper = sp.idPaper 
WHERE sps.idStudent is null AND (sa.grade is NOT null OR sa.score is NOT null) AND sa.idStudent IN ( 
SELECT idStudent 
FROM tblStudent s 
INNER JOIN tblClass c ON s.class = c.class and c.form = @form)

IF @term = 1 
BEGIN
	-- update form assessment scores 
	UPDATE tblFormPaperScore 
	SET score_test_1 = credit 
	FROM tblFormPaperScore fps, ( 
		SELECT r.form, p.idPaper, sum(maxCredit) as credit 
		FROM tblAssessment a 
		INNER JOIN ( 
			SELECT distinct ac.idAssessment, c.form 
			FROM tblAssessmentClass ac 
			INNER JOIN tblClass c ON ac.class = c.class 
		) r ON a.idAssessment = r.idAssessment 
		INNER JOIN tblForm f ON f.form = r.form 
		INNER JOIN tblPaper p ON p.idSubject = a.idSubject and p.formGroup = f.formGroup
		WHERE a.flgCalculate = 1 and r.form = @form
		GROUP BY r.form, p.idPaper
	) r2 
	WHERE fps.form = r2.form AND fps.idPaper = r2.idPaper 

	-- update student assessment scores 
	UPDATE tblStudentPaperScore 
	SET score_test_1 = credit 
	FROM tblStudentPaperScore sps, (
	 	SELECT sa.idStudent, p.idPaper, sum(CASE WHEN a.modeAssessment = 2 THEN CASE WHEN sa.score is null THEN 0 ELSE CASE WHEN flgAchieve = 1 THEN agc.credit ELSE CASE WHEN sa.score >= aga.min_score THEN aga.credit ELSE CASE WHEN sa.score >= agb.min_score THEN agb.credit ELSE CASE WHEN sa.score >= agc.min_score THEN agc.credit ELSE 0 END END END END END ELSE CASE WHEN a.modeAssessment = 1 THEN CASE WHEN sa.score is null THEN 0 ELSE sa.score END ELSE CASE WHEN flgAchieve = 1 THEN agc.credit ELSE CASE WHEN ag.credit is null THEN 0 ELSE ag.credit END END END END) as credit
		FROM tblAssessment a 
		INNER JOIN tblStudentAssessment sa ON sa.idAssessment = a.idAssessment 
		INNER JOIN vwStudentSubject ss ON ss.idStudent = sa.idStudent AND ss.idSubject = a.idSubject AND flgTerm1 = 1
		INNER JOIN tblPaper p ON p.idSubject = ss.idSubject and p.formGroup = ss.formGroup
		LEFT JOIN tblAssessmentGrade ag ON sa.grade = ag.grade AND a.idAssessment = ag.idAssessment 
		LEFT JOIN tblAssessmentGrade aga ON aga.grade = 'A' AND a.idAssessment = aga.idAssessment 
		LEFT JOIN tblAssessmentGrade agb ON agb.grade = 'B' AND a.idAssessment = agb.idAssessment 
		LEFT JOIN tblAssessmentGrade agc ON agc.grade = 'C' AND a.idAssessment = agc.idAssessment 
		WHERE flgCalculate = 1 and form = @form
		GROUP BY sa.idStudent, p.idPaper
	) r2 
	WHERE sps.idStudent = r2.idStudent AND sps.idPaper = r2.idPaper
END
ELSE
BEGIN
	-- update form assessment scores 
	UPDATE tblFormPaperScore 
	SET score_test_2 = credit 
	FROM tblFormPaperScore fps, ( 
		SELECT r.form, p.idPaper, sum(maxCredit) as credit 
		FROM tblAssessment a 
		INNER JOIN ( 
			SELECT distinct ac.idAssessment, c.form 
			FROM tblAssessmentClass ac 
			INNER JOIN tblClass c ON ac.class = c.class 
		) r ON a.idAssessment = r.idAssessment 
		INNER JOIN tblForm f ON f.form = r.form 
		INNER JOIN tblPaper p ON p.idSubject = a.idSubject and p.formGroup = f.formGroup
		WHERE a.flgCalculate = 1 and r.form = @form
		GROUP BY r.form, p.idPaper
	) r2 
	WHERE fps.form = r2.form AND fps.idPaper = r2.idPaper 
	
	-- update student assessment scores 
	UPDATE tblStudentPaperScore 
	SET score_test_2 = credit 
	FROM tblStudentPaperScore sps, (
	 	SELECT sa.idStudent, p.idPaper, sum(CASE WHEN a.modeAssessment = 2 THEN CASE WHEN sa.score is null THEN 0 ELSE CASE WHEN flgAchieve = 1 THEN agc.credit ELSE CASE WHEN sa.score >= aga.min_score THEN aga.credit ELSE CASE WHEN sa.score >= agb.min_score THEN agb.credit ELSE CASE WHEN sa.score >= agc.min_score THEN agc.credit ELSE 0 END END END END END ELSE CASE WHEN a.modeAssessment = 1 THEN CASE WHEN sa.score is null THEN 0 ELSE sa.score END ELSE CASE WHEN flgAchieve = 1 THEN agc.credit ELSE CASE WHEN ag.credit is null THEN 0 ELSE ag.credit END END END END) as credit
		FROM tblAssessment a 
		INNER JOIN tblStudentAssessment sa ON sa.idAssessment = a.idAssessment 
		INNER JOIN vwStudentSubject ss ON ss.idStudent = sa.idStudent AND ss.idSubject = a.idSubject AND flgTerm2 = 1
		INNER JOIN tblPaper p ON p.idSubject = ss.idSubject and p.formGroup = ss.formGroup 
		LEFT JOIN tblAssessmentGrade ag ON sa.grade = ag.grade AND a.idAssessment = ag.idAssessment 
		LEFT JOIN tblAssessmentGrade aga ON aga.grade = 'A' AND a.idAssessment = aga.idAssessment 
		LEFT JOIN tblAssessmentGrade agb ON agb.grade = 'B' AND a.idAssessment = agb.idAssessment 
		LEFT JOIN tblAssessmentGrade agc ON agc.grade = 'C' AND a.idAssessment = agc.idAssessment 
		WHERE flgCalculate = 1 and form = @form
		GROUP BY sa.idStudent, p.idPaper
	) r2 
	WHERE sps.idStudent = r2.idStudent AND sps.idPaper = r2.idPaper
END

--Execute when completed
UPDATE tblAssessment 
SET flgCalculate = 0, flgComplete = 1
WHERE flgCalculate = 1
GO

stpCalculateAssessment 1, 2
GO
stpCalculateAssessment 2, 2
GO
stpCalculateAssessment 3, 2
GO


sel