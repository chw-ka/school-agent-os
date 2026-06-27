select *
from tblStudentReportRemark
where idStudent in (
select idStudent
from tblStudent 
where left(class, 1) in ('1', '2', '4', '6')
)

insert tblStudentReportRemark (idStudent, row, term, nameChinese)
select idStudent, 0, 2, N'試升中七'
from tblZStudentRank
where score_final < 500 and idStudent in (
select idStudent
from tblStudent 
where left(class, 1) in ('6')
)

delete
from tblZStudentReport
where term = 2 and idStudent in (
select idStudent
from tblZStudentRank
where score_final >= 500 and idStudent in (
select idStudent
from tblStudent 
where left(class, 1) in ('1', '2')
)
)

select idStudent 
from tblZStudentReport
where term = 2 and idStudent not in (
select idStudent
from tblSTudentReportRemark
) and idStudent in (
select idStudent
from tblStudent 
where left(class, 1) in ('4')
)

delete
from tblZStudentReport
where term = 2 and idStudent in (
select idStudent
from tblSTudentReportRemark
) 
and idStudent in (
select idStudent
from tblStudent 
where left(class, 1) in ('4')
)

select s.idStudent, s.class, s.numberClass, s.nameChinese
from tblStudent s
inner join tblZStudentReport zsr on s.idStudent = zsr.idStudent and zsr.term = 2
where s.idStudent not in (select idStudent from tblStudentReportRemark) and left(s.class, 1) in ('1', '2', '4', '6')
order by s.class, s.numberClass


select *
from tblStudentReportRemark

insert tblStudentReportRemark (idStudent, row, term, nameChinese)
select s.idSTudent, 0, 2, N'試升中二'
from tblStudent s
inner join tblZStudentReport zsr on s.idStudent = zsr.idStudent and zsr.term = 2
where s.idStudent not in (select idStudent from tblStudentReportRemark) and left(s.class, 1) in ('1')
order by s.class, s.numberClass

insert tblStudentReportRemark (idStudent, row, term, nameChinese)
select s.idSTudent, 0, 2, N'試升中三'
from tblStudent s
inner join tblZStudentReport zsr on s.idStudent = zsr.idStudent and zsr.term = 2
where s.idStudent not in (select idStudent from tblStudentReportRemark) and left(s.class, 1) in ('2')
order by s.class, s.numberClass

insert tblStudentReportRemark (idStudent, row, term, nameChinese)
select s.idSTudent, 0, 2, N'試升中五'
from tblStudent s
inner join tblZStudentReport zsr on s.idStudent = zsr.idStudent and zsr.term = 2
where s.idStudent not in (select idStudent from tblStudentReportRemark) and left(s.class, 1) in ('4')
order by s.class, s.numberClass

delete 
from tblZStudentReport
where idStudent in (select idStudent from tblSTudent where left(class, 1) in ('1', '2', '4')) and term = 2
and idStudent not in (select idStudent from tblStudentReportRemark where nameChinese  in (N'試升中二', N'試升中三', N'試升中五'))


update tblStudentReportRemark
set nameChinese = N'重讀中四'
where nameChinese = N'試升中五'

delete 
from tblZStudentReport
where idStudent in (select idStudent from tblSTudent where left(class, 1) in ('1', '2', '4')) and term = 2
and idStudent not in (select idStudent from tblStudentReportRemark where nameChinese  in (N'重讀中一', N'重讀中二', N'重讀中四'))
