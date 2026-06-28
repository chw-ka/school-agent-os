select top 30 s.class, s.numberClass, s.nameChinese, rA.num as numA, rB.num as numB, rC.num as numC,rD.num as numD, rA.num * 1.0 / (rA.num + rB.num + rC.num + rD.num) as rateA
from tblStudent s
inner join (
select idStudent, 
sum(case when lesson_2     = 'A' then 1 else 0 end) + 
sum(case when assessment_2 = 'A' then 1 else 0 end) as num 
from tblStudentAttitude
group by idStudent
) rA on s.idStudent = rA.idStudent
inner join (
select idStudent, 
sum(case when lesson_2     = 'B' then 1 else 0 end) + 
sum(case when assessment_2 = 'B' then 1 else 0 end) as num
from tblStudentAttitude
group by idStudent
) rB on s.idStudent = rB.idStudent
inner join (
select idStudent, 
sum(case when lesson_2     = 'C' then 1 else 0 end) + 
sum(case when assessment_2 = 'C' then 1 else 0 end) as num
from tblStudentAttitude
group by idStudent
) rC on s.idStudent = rC.idStudent
inner join (
select idStudent, 
sum(case when lesson_2     = 'D' then 1 else 0 end) + 
sum(case when assessment_2 = 'D' then 1 else 0 end) as num
from tblStudentAttitude
group by idStudent
) rD on s.idStudent = rD.idStudent
where rA.num + rB.num + rC.num + rD.num > 0
order by rateA desc, numA desc, numB desc, numC desc, numD desc
