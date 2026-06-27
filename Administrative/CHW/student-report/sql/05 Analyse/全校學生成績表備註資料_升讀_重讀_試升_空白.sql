select s.idStudent, s.class, s.numberClass, s.nameChinese, srr.nameChinese from tblStudent s
left join tblStudentReportRemark srr on s.idStudent = srr.idStudent and srr.term = 2
where left(class,1) in (1,2,3,4,5)
order by s.class, s.numberClass

