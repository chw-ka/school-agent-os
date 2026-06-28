SELECT distinct ss.idStaff as score, ss.idStaff as attitude, case when r.idStaff is not null then r.idStaff else '' end as assessment
FROM tblStaffSubject ss
INNER JOIN tblClass c on ss.class = c.class
LEFT JOIN (
SELECT distinct s.idStaff 
FROM tblStaff s 
INNER JOIN tblStaffSubject ss ON s.idStaff = ss.idStaff 
INNER JOIN tblClass c ON ss.class = c.class 
INNER JOIN tblForm f ON c.form = f.form 
INNER JOIN tblPaper p ON p.idSubject = ss.idSubject AND p.formGroup = f.formGroup 
INNER JOIN tblAssessmentClass ac ON c.class = ac.class 
INNER JOIN tblAssessment a ON a.idPaper = p.idPaper AND a.idAssessment = ac.idAssessment 
) r on ss.idStaff = r.idStaff
WHERE c.form in (1, 2, 4, 6)
ORDER BY ss.idStaff