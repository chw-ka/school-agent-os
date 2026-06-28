-- 各班首三名（計算平均分）、每班每科首三名（計算該科總分；高中只列出四科主科）
select s.idStudent, s.class, s.numberClass, s.nameChinese, zsr2.idPaper, zsr2.score / 100 score, rankClass from tblZStudentRank2 zsr2
inner join tblStudent s on zsr2.idStudent = s.idStudent
where ((zsr2.form in (1,2,3)) or (zsr2.form in (4,5) and zsr2.idPaper in ('CHI', 'ENG', 'MTH', 'LST', ''))) and 
	  flgStandard = 0 and section = 'O' and term = 1 and rankClass in (1,2,3)
order by zsr2.form, class, idPaper, rankClass