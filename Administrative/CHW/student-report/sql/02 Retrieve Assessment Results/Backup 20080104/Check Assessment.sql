--Check if assessment results has any empty entries (whole class).
SELECT distinct ss.idStaff, ac.class, a.idSubject 
FROM tblAssessment a 
INNER JOIN tblAssessmentClass ac ON a.idAssessment = ac.idAssessment 
INNER JOIN tblClass c ON ac.class = c.class 
INNER JOIN vwStaffSubject ss ON ss.class = ac.class AND a.idSubject = ss.idSubject 
LEFT JOIN ( 
SELECT distinct sa.idAssessment, ss.class 
FROM tblStudentAssessment sa 
INNER JOIN tblAssessment a ON a.idAssessment = sa.idAssessment 
INNER JOIN vwStudentSubject ss ON sa.idStudent = ss.idStudent AND ss.idSubject = a.idSubject 
WHERE sa.grade is NOT null OR sa.score is NOT null ) r ON a.idAssessment = r.idAssessment AND ac.class = r.class 
WHERE r.idAssessment is null -- AND c.form IN (1, 2, 3) 
ORDER BY ss.idStaff, ac.class, a.idSubject

--Check if undesired value found in field "test" in tblStudentSubjectScore
SELECT distinct ss.idStaff, ss.class, ss.idSubject 
FROM tblStudentAssessment sa 
INNER JOIN tblAssessment a ON sa.idAssessment = a.idAssessment 
INNER JOIN vwStudentPaper sp ON sa.idStudent = sp.idStudent AND a.idSubject = sp.idSubject
INNER JOIN tblStudentPaperScore sps ON sa.idStudent = sps.idStudent AND sp.idPaper = sps.idPaper 
INNER JOIN vwStaffSubject ss ON sp.class = ss.class AND sp.idSubject = ss.idSubject 
INNER JOIN tblFormTerm ft ON sp.form = ft.form AND (a.dateAssessment between ft.dateStart AND ft.dateEnd) 
WHERE ((score_test_1 is NOT null AND ft.term = 1) OR (score_test_2 is NOT null AND ft.term = 2)) 
ORDER BY ss.idStaff, ss.class, ss.idSubject

--Check if form Subject weight is incorrect
SELECT distinct fpw.form, fpw.idPaper
FROM tblAssessment a
INNER JOIN tblAssessmentClass ac ON a.idAssessment = ac.idAssessment
INNER JOIN tblClass c ON ac.class = c.class
INNER JOIN tblForm f on f.form = c.form
INNER JOIN tblPaper p on f.formGroup = p.formGroup and a.idSubject = p.idSubject
INNER JOIN tblFormPaperWeight fpw ON fpw.form = c.form and fpw.idPaper = p.idPaper
INNER JOIN tblFormTerm ft ON c.form = ft.form AND (a.dateAssessment between ft.dateStart AND ft.dateEnd) 
WHERE ((weight_test_1 is null AND ft.term = 1) OR (weight_test_2 is null AND ft.term = 2))  -- AND fpw.form IN (1, 2, 4, 6) AND term = 1 
ORDER BY fpw.form, fpw.idPaper
