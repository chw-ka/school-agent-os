---------------------------------------------
--Class Rank

select f.form, '', rank_class_final, s.class, s.numberClass, s.nameEnglish, s.nameChinese, score_final / 10.0 as score
from tblStudent s
inner join tblClass c on c.class = s.class
inner join tblForm f on f.form = c.form
inner join tblZStudentRank zsr on s.idStudent = zsr.idStudent
where rank_class_final < 4 and f.form in (1, 2, 3, 4, 6)
order by s.class, rank_class_final

---------------------------------------------
--Paper Rank

select f.form, p.idPaper, rank_form_final, s.class, s.numberClass, s.nameEnglish, s.nameChinese, score_final / 10.0 as score
from tblStudent s
inner join tblClass c on s.class = c.class
inner join tblForm f on c.form = f.form
inner join tblZStudentPaperRank zspr on s.idStudent = zspr.idStudent
inner join tblPaper p on zspr.idPaper = p.idPaper and f.formGroup = p.formGroup and (p.idSubject = p.idPaper OR p.idSubject is null)
where rank_form_final = 1 and f.form in (1, 2, 3, 4, 6)
order by f.form, keyOrder, rank_form_final

----------------------------------------------
--S1-3 Form-Best

select f.form, '', rank_form_final, s.class, s.numberClass, s.nameEnglish, s.nameChinese, score_final / 10.0 as score
from tblStudent s
inner join tblClass c on s.class = c.class
inner join tblForm f on c.form = f.form
inner join tblZStudentRank zsr on s.idStudent = zsr.idStudent
where rank_form_final < 3 and f.form < 4
order by f.form, rank_form_final

----------------------------------------------
--S4-7 Form-Best

-------------------
--Standard Score

declare @form tinyint
set @form = 6

select top 2 f.form, '', '', s.class, s.numberClass, s.nameEnglish, s.nameChinese, avg(((score_final / 10.0) - mean) / sd) as score, count( * ) as numSubject, sc.idStaff 
from tblStudent s
inner join tblClass c on s.class = c.class
inner join tblForm f on c.form = f.form
inner join tblZStudentPaperRank zspr on s.idStudent = zspr.idStudent
INNER JOIN tblPaper p ON zspr.idPaper = p.idPaper AND f.formGroup = p.formGroup AND (p.idSubject = p.idPaper OR p.idSubject is null) 
INNER JOIN tblStaffClass sc ON sc.class = s.class AND flgHead = 1 
INNER JOIN (
select f.form, p.idPaper, avg(score_final / 10.0) as mean, stdev(score_final / 10.0) as sd
from tblStudent s
inner join tblClass c on s.class = c.class
inner join tblForm f on c.form = f.form
inner join tblZStudentPaperRank zspr on s.idStudent = zspr.idStudent
INNER JOIN tblPaper p ON zspr.idPaper = p.idPaper AND f.formGroup = p.formGroup AND (p.idSubject = p.idPaper OR p.idSubject is null) 
group by f.form, p.idPaper
) r on f.form = r.form and p.idPaper = r.idPaper 
where f.form = @form and p.idPaper <> 'RES'
group by f.form, s.class, s.numberClass, s.nameEnglish, s.nameChinese, sc.idStaff 
order by score desc

-------------------
--Other reference method

SELECT top 10 f.form, score_final / 10.0 as avgScore, numSubject, s.class, s.numberClass, s.nameEnglish, s.nameChinese, sc.idStaff 
FROM tblStudent s 
INNER JOIN tblClass c ON s.class = c.class 
INNER JOIN tblForm f ON c.form = f.form 
INNER JOIN tblZStudentRank zsr ON s.idStudent = zsr.idStudent 
INNER JOIN tblStaffClass sc ON sc.class = s.class AND flgHead = 1 
INNER JOIN ( 
SELECT s.idStudent, count( * ) as numSubject 
FROM tblStudent s 
INNER JOIN tblClass c ON s.class = c.class 
INNER JOIN tblForm f ON c.form = f.form 
INNER JOIN tblZStudentPaperRank zspr ON s.idStudent = zspr.idStudent 
INNER JOIN tblPaper p ON zspr.idPaper = p.idPaper AND f.formGroup = p.formGroup AND (p.idSubject = p.idPaper OR p.idSubject is null) 
WHERE rank_form_final is NOT null 
GROUP BY s.idStudent ) r ON r.idStudent = s.idStudent 
WHERE f.form = 5 AND score_final is NOT null 
ORDER BY f.form, score_final desc

SELECT top 10 f.form, avg(rank_form_final * 1.0) as avgRank, count( * ) as numSubject, s.class, s.numberClass, s.nameEnglish, s.nameChinese, sc.idStaff 
FROM tblStudent s 
INNER JOIN tblClass c ON s.class = c.class 
INNER JOIN tblForm f ON c.form = f.form 
INNER JOIN tblZStudentPaperRank zspr ON s.idStudent = zspr.idStudent 
INNER JOIN tblPaper p ON zspr.idPaper = p.idPaper AND f.formGroup = p.formGroup AND (p.idSubject = p.idPaper OR p.idSubject is null) 
INNER JOIN tblStaffClass sc ON sc.class = s.class AND flgHead = 1 
WHERE f.form = 5 AND rank_form_final is NOT null 
GROUP BY f.form, s.class, s.numberClass, s.nameEnglish, s.nameChinese, sc.idStaff 
ORDER BY f.form, avg(rank_form_final * 1.0)

SELECT top 10 f.form, sum(rank_form_final * 1.0 * numParticipant) / sum(numParticipant) as wAvgRank, count( * ) as numSubject, s.class, s.numberClass, s.nameEnglish, s.nameChinese, sc.idStaff 
FROM tblStudent s 
INNER JOIN tblClass c ON s.class = c.class 
INNER JOIN tblForm f ON c.form = f.form 
INNER JOIN tblZStudentPaperRank zspr ON s.idStudent = zspr.idStudent 
INNER JOIN tblPaper p ON zspr.idPaper = p.idPaper AND f.formGroup = p.formGroup AND (p.idSubject = p.idPaper OR p.idSubject is null) 
INNER JOIN tblStaffClass sc ON sc.class = s.class AND flgHead = 1 
INNER JOIN ( 
SELECT f.form, idPaper, count( * ) as numParticipant 
FROM tblStudent s 
INNER JOIN tblClass c ON s.class = c.class 
INNER JOIN tblForm f ON c.form = f.form 
INNER JOIN tblZStudentPaperRank zspr ON s.idStudent = zspr.idStudent 
WHERE score_final is NOT null 
GROUP BY f.form, idPaper ) r ON f.form = r.form AND p.idPaper = r.idPaper 
WHERE f.form = 5 AND rank_form_final is NOT null 
GROUP BY f.form, s.class, s.numberClass, s.nameEnglish, s.nameChinese, sc.idStaff 
ORDER BY f.form, sum(rank_form_final * 1.0 * numParticipant) / sum(numParticipant)

----------------------------------------------

SELECT f.form, p.idPaper, score_final / 10.0, s.class, s.numberClass, s.nameEnglish, s.nameChinese, r1.idStaff 
FROM tblStudent s 
INNER JOIN tblClass c ON s.class = c.class 
INNER JOIN tblForm f ON c.form = f.form 
INNER JOIN tblZStudentPaperRank zspr ON s.idStudent = zspr.idStudent 
INNER JOIN tblPaper p ON zspr.idPaper = p.idPaper AND f.formGroup = p.formGroup AND (p.idSubject = p.idPaper OR p.idSubject is null) 
INNER JOIN ( 
SELECT sfs1.idStaff, sfs1.form, sfs1.idSubject, count( * ) as num 
FROM tblStaffFormSubject sfs1 
INNER JOIN tblStaffFormSubject sfs2 ON sfs1.idStaff = sfs2.idStaff AND sfs1.idSubject = sfs2.idSubject 
GROUP BY sfs1.idStaff, sfs1.form, sfs1.idSubject ) r1 ON r1.form = f.form AND r1.idSubject = p.idPaper 
INNER JOIN ( 
SELECT form, idSubject, min(num) as num 
FROM ( 
SELECT sfs1.idStaff, sfs1.form, sfs1.idSubject, count( * ) as num 
FROM tblStaffFormSubject sfs1 
INNER JOIN tblStaffFormSubject sfs2 ON sfs1.idStaff = sfs2.idStaff AND sfs1.idSubject = sfs2.idSubject 
GROUP BY sfs1.idStaff, sfs1.form, sfs1.idSubject) r2 
GROUP BY form, idSubject ) r3 ON r1.form = r3.form AND r1.idSubject = r3.idSubject AND r1.num = r3.num 
WHERE f.form = 5 AND rank_form_final = 1 
ORDER BY f.form, keyOrder, s.class

