-- S1 to S5 Term 1
select s.idStudent, zsr2.form, s.class, s.numberClass, s.nameChinese, s.gender, zsr2.idPaper, zsr2.score / 100 as score1, zsr2.rankClass, zsr2.rankForm from tblZStudentRank2 zsr2
inner join tblStudent s on zsr2.idStudent = s.idStudent
where flgStandard = 0 and section = 'O' and term = 1 and (form in (1,2,3) or (form in (4,5) and idPaper in ('', 'CHI', 'ENG', 'MTH', 'LST', 'CSD'))) and rankClass in (1,2,3,4,5)
order by form, class, idPaper, score1 desc 


-- S1 to S5 Term 2
select s.idStudent, zsr2.form, s.class, s.numberClass, s.nameChinese, s.gender, zsr2.idPaper, zsr2.score / 100 as score1, zsr2.rankClass, zsr2.rankForm from tblZStudentRank2 zsr2
inner join tblStudent s on zsr2.idStudent = s.idStudent
where flgStandard = 0 and section = 'O' and term = 2 and (form in (1,2,3) or (form in (4,5) and idPaper in ('', 'CHI', 'ENG', 'MTH', 'LST', 'CSD'))) and rankClass in (1,2,3,4,5)
order by form, class, idPaper, score1 desc 



-- S6 Whole school year
select s.idStudent, zsr2.form, s.class, s.numberClass, s.nameChinese, s.gender, zsr2.idPaper, zsr2.score / 100 as score1, zsr2.rankClass, zsr2.rankForm from tblZStudentRank2 zsr2
inner join tblStudent s on zsr2.idStudent = s.idStudent
where flgStandard = 0 and section = 'O' and term = 2 and ((form in (6) and idPaper in ('', 'CHI', 'ENG', 'MTH', 'LST', 'CSD'))) and rankClass in (1,2,3,4,5)
order by form, class, idPaper, score1 desc 