
select c.form, p.idPaper, avg(score_final / 10.0) as mean, sum(case when score_final >= 495 then 1 else 0 end) * 1.0 / count(*) as pass_rate
from tblZStudentPaperRank zspr 
inner join tblStudent s on zspr.idStudent = s.idStudent
inner join tblClass c on s.class = c.class
inner join tblForm f on c.form = f.form
inner join tblPaper p on p.idPaper = zspr.idPaper and p.formGroup = f.formGroup and flgScore = 1
group by c.form, p.idPaper
having avg(score_final / 10.0) is not null
union
select c.form, p.idPaper, null as mean, sum(case when grade_exam_2 = 'A' or grade_exam_2 = 'B' or grade_exam_2 = 'C' then 1 else 0 end) * 1.0 / count(*) as pass_rate
from tblStudentPaperScore sps
inner join tblStudent s on sps.idStudent = s.idStudent
inner join tblClass c on s.class = c.class
inner join tblForm f on c.form = f.form
inner join tblPaper p on sps.idPaper = p.idPaper and p.formGroup = f.formGroup and flgScore = 0 
where grade_exam_2 <> '#'
group by c.form, p.idPaper
order by p.idPaper, c.form