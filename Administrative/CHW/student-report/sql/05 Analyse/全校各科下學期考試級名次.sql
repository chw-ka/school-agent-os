select s.class, s.numberClass, s.nameChinese, a.idStudent, a.form, a.idPaper, a.score/100, a.rankForm, 
(select count(*) from db18_19.dbo.tblZStudentRank2 b where b.form = a.form and b.idPaper = a.idPaper and flgStandard = 0 and section = 'E' and term = 2)
from db18_19.dbo.tblZStudentRank2 a
left join tblStudent s on a.idStudent = s.idStudent
where not idPaper in ('', 'CH1', 'CH2', 'CH3', 'CH4', 'EG1', 'EG2', 'EG3', 'EG4') and flgStandard = 0 and section = 'E' and term = 2 and a.form in (1,2,3,4,5)
order by form, idPaper, rankForm