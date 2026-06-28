------------------------------------------------------------------------------------------------
-- stpCalculateAssessment
------------------------------------------------------------------------------------------------

if exists (select * from dbo.sysobjects where id = object_id(N'[dbo].[stpCalculateAssessment]') and OBJECTPROPERTY(id, N'IsProcedure') = 1)
drop procedure [dbo].[stpCalculateAssessment]
GO

CREATE PROCEDURE dbo.stpCalculateAssessment
@form tinyint, @term tinyint
AS

-- add missing form paper score 
INSERT tblFormPaperScore (form, idPaper, formGroup) 
SELECT r.form, r.idSubject, r.form
FROM (
	SELECT distinct ss.form, ss.idSubject
	FROM dbo.vwStudentSubject2 AS ss 
	INNER JOIN dbo.tblAssessmentClass2 AS ac ON ac.class = ss.class 
	INNER JOIN dbo.tblAssessment2 AS a ON ac.idAssessment = a.idAssessment AND ss.idSubject = a.idSubject 
	INNER JOIN dbo.tblFormTerm AS ft ON ss.form = ft.form AND a.dateFrom BETWEEN ft.dateStart AND ft.dateEnd 
	WHERE ft.form = @form and ft.term = @term AND ((ft.term = 1 AND ss.flgTerm1 = 1) OR (ft.term = 2 AND ss.flgTerm2 = 1))
) r
LEFT JOIN tblFormPaperScore fps ON r.form = fps.form AND r.idSubject = fps.idPaper 
WHERE fps.form is null

-- add missing student paper score 
INSERT tblStudentPaperScore (idStudent, idPaper) 
SELECT r.idStudent, r.idSubject 
FROM (
	SELECT distinct ss.idStudent, ss.idSubject
	FROM dbo.vwStudentSubject2 AS ss 
	INNER JOIN dbo.tblAssessmentClass2 AS ac ON ac.class = ss.class 
	INNER JOIN dbo.tblAssessment2 AS a ON ac.idAssessment = a.idAssessment AND ss.idSubject = a.idSubject 
	INNER JOIN dbo.tblFormTerm AS ft ON ss.form = ft.form AND a.dateFrom BETWEEN ft.dateStart AND ft.dateEnd 
	WHERE ft.form = @form and ft.term = @term AND ((ft.term = 1 AND ss.flgTerm1 = 1) OR (ft.term = 2 AND ss.flgTerm2 = 1))
) r
LEFT JOIN tblStudentPaperScore sps ON sps.idStudent = r.idStudent AND sps.idPaper = r.idSubject 
WHERE sps.idStudent is null 

IF @term = 1 
BEGIN
	-- update form assessment scores 
	UPDATE tblFormPaperScore 
	SET score_test_1 = 100
	FROM tblFormPaperScore fps
	INNER JOIN ( 
		SELECT distinct ss.form, ss.idSubject
		FROM dbo.vwStudentSubject2 AS ss 
		INNER JOIN dbo.tblAssessmentClass2 AS ac ON ac.class = ss.class 
		INNER JOIN dbo.tblAssessment2 AS a ON ac.idAssessment = a.idAssessment AND ss.idSubject = a.idSubject 
		INNER JOIN dbo.tblFormTerm AS ft ON ss.form = ft.form AND a.dateFrom BETWEEN ft.dateStart AND ft.dateEnd 
		WHERE ft.form = @form and ft.term = @term AND ((ft.term = 1 AND ss.flgTerm1 = 1) OR (ft.term = 2 AND ss.flgTerm2 = 1))
	) r ON fps.form = r.form AND fps.idPaper = r.idSubject 

	-- update student assessment scores 
	UPDATE tblStudentPaperScore 
	SET score_test_1 = score
	FROM tblStudentPaperScore sps 
	INNER JOIN ( 
	SELECT sa.form, sa.idStudent, sa.idSubject, floor(sum(case when credit is null then 0 else credit end) * 100.0 / sum(maxCredit) + .5) as score 
	FROM vwStudentAssessment2 sa 
	WHERE sa.term = @term AND flgTaken = 1
	GROUP BY sa.form, sa.idStudent, sa.idSubject ) r ON sps.idStudent = r.idStudent AND sps.idPaper = r.idSubject 
	WHERE r.form = @form
END
ELSE
BEGIN
	-- update form assessment scores 
	UPDATE tblFormPaperScore 
	SET score_test_2 = 100
	FROM tblFormPaperScore fps
	INNER JOIN ( 
		SELECT distinct ss.form, ss.idSubject
		FROM dbo.vwStudentSubject2 AS ss 
		INNER JOIN dbo.tblAssessmentClass2 AS ac ON ac.class = ss.class 
		INNER JOIN dbo.tblAssessment2 AS a ON ac.idAssessment = a.idAssessment AND ss.idSubject = a.idSubject 
		INNER JOIN dbo.tblFormTerm AS ft ON ss.form = ft.form AND a.dateFrom BETWEEN ft.dateStart AND ft.dateEnd 
		WHERE ft.form = @form and ft.term = @term AND ((ft.term = 1 AND ss.flgTerm1 = 1) OR (ft.term = 2 AND ss.flgTerm2 = 1))
	) r ON fps.form = r.form AND fps.idPaper = r.idSubject 

	-- update student assessment scores 
	UPDATE tblStudentPaperScore 
	SET score_test_2 = score
	FROM tblStudentPaperScore sps 
	INNER JOIN ( 
	SELECT sa.form, sa.idStudent, sa.idSubject, floor(sum(case when credit is null then 0 else credit end) * 100.0 / sum(maxCredit) + .5) as score 
	FROM vwStudentAssessment2 sa 
	WHERE sa.term = @term AND flgTaken = 1
	GROUP BY sa.form, sa.idStudent, sa.idSubject ) r ON sps.idStudent = r.idStudent AND sps.idPaper = r.idSubject 
	WHERE r.form = @form
END

--Execute when completed
UPDATE tblAssessment2 
SET flgCompleted = 1 
WHERE idAssessment IN ( 
	SELECT distinct a.idAssessment
	FROM dbo.vwStudentSubject2 AS ss 
	INNER JOIN dbo.tblAssessmentClass2 AS ac ON ac.class = ss.class 
	INNER JOIN dbo.tblAssessment2 AS a ON ac.idAssessment = a.idAssessment AND ss.idSubject = a.idSubject 
	INNER JOIN dbo.tblFormTerm AS ft ON ss.form = ft.form AND a.dateFrom BETWEEN ft.dateStart AND ft.dateEnd 
	WHERE ft.form = @form and ft.term = @term 
)

GO

--2,1  form 2, term 1
stpCalculateAssessment 1, 1
GO
stpCalculateAssessment 2, 1
GO
stpCalculateAssessment 3, 1
GO

update tblAssessment2
set flgCompleted = 0
where dateFrom >= '2022-09-01 00:00:00.000'

--2,1  form 2, term 2
stpCalculateAssessment 1, 2
GO
stpCalculateAssessment 2, 2
GO
stpCalculateAssessment 3, 2
GO

update tblAssessment2
set flgCompleted = 0
where dateFrom >= '2023-01-21 00:00:00.000'

