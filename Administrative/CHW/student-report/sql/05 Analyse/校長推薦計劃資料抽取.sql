select s.class, s.numberClass, s.nameChinese, a.score / 100.0 as CHI, a.rankForm as rankCHI, b.score/100.0 as ENG, b.rankForm as rankENG, d.numLate_2, c.numHW, d.dayAbsent_2 from tblStudent s
inner join tblZStudentRank2 a on a.idStudent = s.idStudent and a.flgStandard = 0 and a.section = 'O' and a.term = 2 and a.idPaper = 'CHI'
inner join tblZStudentRank2 b on b.idStudent = s.idStudent and b.flgStandard = 0 and b.section = 'O' and b.term = 2 and b.idPaper = 'ENG'
left join (select idStudent, count(idStudent) as numHW from tblStudentMistake c where c.idMistake = 3 and c.idStudent in (select idStudent from tblStudent where left(class,1) = 6) group by c.idStudent) c on c.idStudent= s.idStudent
left join tblStudentDiscipline d on d.idStudent = s.idStudent
where left(s.class,1) = 6
order by s.class, s.numberClass


