--Whole year
select s.idStudent, s.class, s.numberClass, s.nameChinese, b.score / 100.0, b.rankForm, a.score /100.0 as MTHScore, a.rankForm as MTHRank from tblStudent s
left join tblZStudentRank2 b on s.idStudent = b.idStudent and b.term = 0 and b.flgStandard = 0 and b.section = 'O' and b.idPaper = '' and b.form = 3 
left join tblZStudentRank2 a on s.idStudent = a.idStudent and a.term = 0 and a.flgStandard = 0 and a.section = 'O' and a.idPaper = '' and a.form = 3 
where left(class,1) = 3
order by b.rankForm


-- Whole year mth (For MM2 grouping)


--Term 1
select s.idStudent, s.class, s.numberClass, s.nameChinese, zsr2.score / 100.0, zsr2.rankForm from tblStudent s
left join tblZStudentRank2 zsr2 on s.idStudent = zsr2.idStudent and term = 1 and flgStandard = 0 and section = 'O' and idPaper = '' and form = 3 
where left(class,1) = 3
order by zsr2.rankForm