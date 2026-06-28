select form, p.idPaper, p.nameChinese, s.class, s.numberClass, s.nameChinese, ss.remark, score_final / 10.0
from vwStudent s
inner join tblStudentSubject ss on s.idStudent = ss.idStudent 
inner join tblPaper p on p.formGroup = s.formGroup and p.idPaper = ss.idSubject 
left join tblZStudentPaperRank zspr on s.idStudent = zspr.idStudent and ss.idSubject = zspr.idPaper
where  form in (5, 7) and (rank_form_final = 1)
order by form, p.keyOrder


select form, p.idPaper, p.nameChinese, s.class, s.numberClass, s.nameChinese, ss.remark, score_final / 10.0
from vwStudent s
inner join tblStudentSubject ss on s.idStudent = ss.idStudent 
inner join tblPaper p on p.formGroup = s.formGroup and p.idPaper = ss.idSubject 
inner join tblZStudentPaperRank zspr on s.idStudent = zspr.idStudent and ss.idSubject = zspr.idPaper
where  form in (5, 7) and p.idPaper = 'ENG' and ss.remark = 'N,B'
order by score_final desc

select s.class, s.numberClass, s.nameChinese, rank_class_final, score_final / 10.0
from vwStudent s
inner join tblZStudentRank zsr on s.idStudent = zsr.idStudent
where form in (5, 7) and rank_class_final < 4
order by class, rank_class_final

