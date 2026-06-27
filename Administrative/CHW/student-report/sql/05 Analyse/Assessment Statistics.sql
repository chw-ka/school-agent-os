-- total students
select form, count(*)
from vwStudent s
group by form
order by form

select cast(form as varchar(1)) + idSubject + cast(src as varchar(1)), *
from (
select 1 as src, N'評估總數' as statement, s.form, a.idSubject, count(*) as num, p.keyOrder
from tblAssessment a 
inner join tblStudentAssessment sa on a.idAssessment = sa.idAssessment
inner join vwStudent s on s.idStudent = sa.idStudent 
inner join tblPaper p on s.formGroup = p.formGroup and p.idSubject = a.idSubject
where modeAssessment in (0, 2)
group by s.form, a.idSubject, p.keyOrder
union 
select 2 as src, N'達標' as statement, s.form, a.idSubject, count(*) as num, p.keyOrder
from tblAssessment a 
inner join tblAssessmentGrade ag on a.idAssessment = ag.idAssessment AND ag.grade = 'C'
inner join tblStudentAssessment sa on a.idAssessment = sa.idAssessment
inner join vwStudent s on s.idStudent = sa.idStudent
inner join tblPaper p on s.formGroup = p.formGroup and p.idSubject = a.idSubject
where flgAchieve = 0 and ((modeAssessment = 0 and sa.grade in ('A', 'B', 'C')) OR (modeAssessment = 2 and sa.score >= ag.min_score))
group by s.form, a.idSubject, p.keyOrder
union 
select 3 as src, N'補達標' as statement, s.form, a.idSubject, count(*) as num, p.keyOrder
from tblAssessment a 
inner join tblAssessmentGrade ag on a.idAssessment = ag.idAssessment AND ag.grade = 'C'
inner join tblStudentAssessment sa on a.idAssessment = sa.idAssessment
inner join vwStudent s on s.idStudent = sa.idStudent
inner join tblPaper p on s.formGroup = p.formGroup and p.idSubject = a.idSubject
where modeAssessment in (0, 2) and flgAchieve = 1
group by s.form, a.idSubject, p.keyOrder
union 
select 4 as src, N'未達標' as statement, s.form, a.idSubject, count(*) as num, p.keyOrder
from tblAssessment a 
inner join tblAssessmentGrade ag on a.idAssessment = ag.idAssessment AND ag.grade = 'C'
inner join tblStudentAssessment sa on a.idAssessment = sa.idAssessment
inner join vwStudent s on s.idStudent = sa.idStudent 
inner join tblPaper p on s.formGroup = p.formGroup and p.idSubject = a.idSubject
where flgAchieve = 0 and 
((modeAssessment = 0 AND (sa.grade = 'D' or sa.grade is null)) OR 
 (modeAssessment = 2 AND (sa.score < ag.min_score or sa.score is null)))
group by s.form, a.idSubject, p.keyOrder
) r
where form < 4
order by form, keyOrder, src

--Meet the target
select cast(form as varchar(1)) + idSubject + replace(cast(lbound as varchar(3)), '.0', ''), *
from (
select r1.*, case when num is null then 0 else num end as num
from (
	select *
	from (
		select distinct f.form, a.idSubject, keyOrder
		from tblAssessment a
		inner join tblForm f on f.form = cast(left(classRemark, 1) as tinyint)
		inner join tblPaper p on p.formGroup = f.formGroup and a.idSubject = p.idPaper
		where modeAssessment in (0, 2)
	) r1, (
		select 1.0 as lbound union
		select 0.9 as lbound union
		select 0.8 as lbound union
		select 0.7 as lbound union
		select 0.6 as lbound union
		select 0.5 as lbound union
		select 0.4 as lbound union
		select 0.3 as lbound union
		select 0.2 as lbound union
		select 0.1 as lbound union	
		select 0.0 as lbound
	) r2
) r1
left join (
	select r1.form, r1.idSubject, floor(r1.score * 10.0 / r2.score) / 10.0 as lbound, count(*) as num
	from 	(
		select s.idStudent, s.form, a.idSubject, 
		sum(
		case when flgAchieve = 1 then 
			agc.credit
		else
			case 
				when a.modeAssessment = 0 then ag.credit 
				when a.modeAssessment = 2 then 
					case 
						when sa.score >= aga.min_score then aga.credit 
						when sa.score >= agb.min_score then agb.credit 
						when sa.score >= agc.min_score then agc.credit
						else 0 
					end
			end
		end) as score
		from tblAssessment a 
		inner join tblAssessmentGrade aga on a.idAssessment = aga.idAssessment AND aga.grade = 'A'
		inner join tblAssessmentGrade agb on a.idAssessment = agb.idAssessment AND agb.grade = 'B'
		inner join tblAssessmentGrade agc on a.idAssessment = agc.idAssessment AND agc.grade = 'C'
		inner join tblStudentAssessment sa on a.idAssessment = sa.idAssessment
		inner join vwStudent s on s.idStudent = sa.idStudent 
		left join tblAssessmentGrade ag on a.idAssessment = ag.idAssessment AND ag.grade = sa.grade
		where modeAssessment in (0, 2) 
		group by s.idStudent, s.form, a.idSubject
	) r1
	inner join (
		select cast(left(classRemark, 1) as tinyint) as form, idSubject, sum(a.maxCredit) as score
		from tblAssessment a
		where modeAssessment in (0, 2)
		group by cast(left(classRemark, 1) as tinyint) , idSubject
	) r2 on r1.form = r2.form and r1.idSubject = r2.idSubject
	group by r1.form, r1.idSubject, floor(r1.score * 10.0 / r2.score) / 10.0
) r2 on r1.lbound = r2.lbound and r1.form = r2.form and r1.idSubject = r2.idSubject
) r
where form < 4
order by form, keyOrder, lbound desc
