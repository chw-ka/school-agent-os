-- Exists graded paper have weight
select *
from vwStudentPaper sp
inner join tblPaper p  on sp.formGroup = p.formGroup and sp.idPaper = p.idPaper
inner join tblFormPaperWeight fpw on sp.form = fpw.form and sp.idPaper = fpw.idPaper
where sp.flgScore = 0 

-- Exists scored paper have no weight
select *
from vwStudentPaper sp
inner join tblPaper p  on sp.formGroup = p.formGroup and sp.idPaper = p.idPaper
left join tblFormPaperWeight fpw on sp.form = fpw.form and sp.idPaper = fpw.idPaper
where sp.flgScore = 1 and 
(weight_test_1 is null or weight_test_1 = 0) and 
(weight_regular_1 is null or weight_regular_1 = 0) and
(weight_exam_1 is null or weight_exam_1 = 0) and
(weight_test_2 is null or weight_test_2 = 0) and 
(weight_regular_2 is null or weight_regular_2 = 0) and
(weight_exam_2 is null or weight_exam_2 = 0)

-- All Paper Weight Info
SELECT p.idSubject, p.idPaper, f.form, p.nameChinese, p.nameEnglish, weight, weight_test_1, weight_regular_1, weight_exam_1, weight_test_2, weight_regular_2, weight_exam_2 
FROM tblFormPaperWeight fpw 
INNER JOIN tblForm f ON f.form = fpw.form 
INNER JOIN tblPaper p ON p.idPaper = fpw.idPaper AND p.formGroup = f.formGroup 
ORDER BY p.idSubject, p.idPaper, f.form

SELECT ss.idStaff, p.formGroup, p.idPaper, p.nameChinese, p.nameEnglish, weight, weight_test_1, weight_regular_1, weight_exam_1, weight_test_2, weight_regular_2, weight_exam_2 
FROM tblStaffHeadSubject ss
INNER JOIN (SELECT distinct form, idSubject from vwStudentSubject) r ON r.idSubject = ss.idSubject
INNER JOIN tblPaper p ON (ss.idSubject = p.idPaper or ss.idSubject = p.idSubject) and r.form = p.formGroup
left join tblFormPaperWeight fpw on fpw.form = p.formGroup and fpw.idPaper = p.idPaper
where ss.idSubject <> 'OTH' and p.flgScore = 1
ORDER BY ss.idStaff, p.formGroup, p.keyOrder

