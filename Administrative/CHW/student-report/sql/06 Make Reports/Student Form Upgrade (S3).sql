insert tblStudentReportRemark (idStudent, row, term, nameChinese)
select s.idStudent, 0, 2, N'原校升讀中四'
from tblStudent s
inner join tblZStudentRank zsr on s.idStudent = zsr.idStudent
where left(class, 1) = '3' and rank_form_final <= 190

insert tblStudentReportRemark (idStudent, row, term, nameChinese)
select s.idStudent, 0, 2, N'如獲教統局派位，可升讀中四或職訓課程'
from tblStudent s
inner join tblZStudentRank zsr on s.idStudent = zsr.idStudent
where left(class, 1) = '3' and rank_form_final > 190

