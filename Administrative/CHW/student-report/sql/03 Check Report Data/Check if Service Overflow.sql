select s.idStudent, s.class, s.numberClass, s.nameChinese, 
case when numA is null then 0 else numA end + 
case when numB is null then 0 else numB end + 
case when numC is null then 0 else numC end 
as num
from tblStudent s
left join (
select sup.idStudent, count(*) as numA
from tblStudentUnitPost sup
inner join tblUnit u on sup.idUnit = u.idUnit
where idUnitGroup = 7
group by sup.idStudent
) r1 on s.idStudent = r1.idStudent
left join (
select scp.idStudent, count(*) as numB
from tblStudentClassPost scp
group by scp.idStudent
) r2 on s.idStudent = r2.idStudent
left join (
select ssp.idStudent, count(*) as numC
from tblStudentSubjectPost ssp
group by ssp.idStudent
) r3 on s.idStudent = r3.idStudent
where 
case when numA is null then 0 else numA end + 
case when numB is null then 0 else numB end + 
case when numC is null then 0 else numC end > 4
order by s.class, s.numberClass


select * 
from (
select sup.idStudent, u.nameChinese + case when p.idPost <> 101 then p.nameChinese else '' end as namePost
from tblStudentUnitPost sup
inner join tblUnit u on sup.idUnit = u.idUnit
inner join tblPost p on sup.idPost = p.idPost
where idUnitGroup = 7
union
select scp.idStudent, cu.nameChinese + case when p.idPost <> 101 then p.nameChinese else '' end
from tblStudentClassPost scp
inner join tblClassUnit cu on scp.idClassUnit = cu.idClassUnit
inner join tblPost p on scp.idPost = p.idPost
union
select ssp.idStudent, p.nameChinese + N'¬ì¬ìªø'
from tblStudentSubjectPost ssp
inner join vwStudentSubject ss on ssp.idStudent = ss.idStudent and ssp.idSubject = ss.idSubject
inner join tblPaper p on p.formGroup = ss.formGroup and p.idPaper = ss.idSubject
) r
where idStudent = 5037