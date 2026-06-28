select s.idStudent, s.class, s.numberClass, s.nameChinese, zsr1.score/100.0, zsr2.score/100.0, srr.nameChinese from tblStudentReportRemark srr
inner join tblStudent s on srr.idStudent = s.idStudent
inner join tblZStudentRank2 zsr1 on srr.idStudent = zsr1.idStudent and zsr1.term = 1 and zsr1.section = 'O' and flgStandard = 0 and idPaper = ''
inner join tblZStudentRank2 zsr2 on srr.idStudent = zsr2.idStudent and zsr2.score >= 5000 and zsr2.term = 2 and zsr2.section = 'O' and zsr2.flgStandard = 0 and zsr2.idPaper = ''
where srr.nameChinese like '¸Õ¤É%' 
order by s.class, s.numberClass

