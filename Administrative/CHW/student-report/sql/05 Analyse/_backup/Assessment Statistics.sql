declare @term as integer
set @term = 2

-- total students
select form, count(*)
from tblStudent s
inner join tblClass c on s.class = c.class
where ((@term = 1 AND flgTerm1 = 1) OR (@term = 2 AND flgTerm2 = 1))
group by form

select 1 as src, N'評估總數' as statement, f.form, a.idPaper, count(*) as num, p.keyOrder
from tblAssessment a 
inner join tblAssessmentGrade ag on a.idAssessment = ag.idAssessment AND ag.grade = 'C'
inner join tblStudentAssessment sa on a.idAssessment = sa.idAssessment
inner join tblStudent s on s.idStudent = sa.idStudent and ((@term = 1 AND flgTerm1 = 1) OR (@term = 2 AND flgTerm2 = 1))
inner join tblClass c on s.class = c.class
inner join tblForm f on c.form = f.form 
inner join tblPaper p on f.formGroup = p.formGroup and p.idPaper = a.idPaper
where a.flgComplete = 1 and 
modeAssessment in (0, 2)
group by f.form, a.idPaper, p.keyOrder
union 
select 2 as src, N'達標' as statement, f.form, a.idPaper, count(*) as num, p.keyOrder
from tblAssessment a 
inner join tblAssessmentGrade ag on a.idAssessment = ag.idAssessment AND ag.grade = 'C'
inner join tblStudentAssessment sa on a.idAssessment = sa.idAssessment
inner join tblStudent s on s.idStudent = sa.idStudent and ((@term = 1 AND flgTerm1 = 1) OR (@term = 2 AND flgTerm2 = 1))
inner join tblClass c on s.class = c.class
inner join tblForm f on c.form = f.form 
inner join tblPaper p on f.formGroup = p.formGroup and p.idPaper = a.idPaper
where a.flgComplete = 1 and 
((modeAssessment = 0 and flgAchieve = 0 and sa.grade in ('A', 'B', 'C')) OR 
 (modeAssessment = 2 and flgAchieve = 0 and sa.score >= ag.min_score))
group by f.form, a.idPaper, p.keyOrder
union 
select 3 as src, N'補達標' as statement, f.form, a.idPaper, count(*) as num, p.keyOrder
from tblAssessment a 
inner join tblAssessmentGrade ag on a.idAssessment = ag.idAssessment AND ag.grade = 'C'
inner join tblStudentAssessment sa on a.idAssessment = sa.idAssessment
inner join tblStudent s on s.idStudent = sa.idStudent and ((@term = 1 AND flgTerm1 = 1) OR (@term = 2 AND flgTerm2 = 1))
inner join tblClass c on s.class = c.class
inner join tblForm f on c.form = f.form 
inner join tblPaper p on f.formGroup = p.formGroup and p.idPaper = a.idPaper
where a.flgComplete = 1 and 
modeAssessment in (0, 2) and flgAchieve = 1
group by f.form, a.idPaper, p.keyOrder
union 
select 4 as src, N'未達標' as statement, f.form, a.idPaper, count(*) as num, p.keyOrder
from tblAssessment a 
inner join tblAssessmentGrade ag on a.idAssessment = ag.idAssessment AND ag.grade = 'C'
inner join tblStudentAssessment sa on a.idAssessment = sa.idAssessment
inner join tblStudent s on s.idStudent = sa.idStudent and ((@term = 1 AND flgTerm1 = 1) OR (@term = 2 AND flgTerm2 = 1))
inner join tblClass c on s.class = c.class
inner join tblForm f on c.form = f.form 
inner join tblPaper p on f.formGroup = p.formGroup and p.idPaper = a.idPaper
where a.flgComplete = 1 and 
((modeAssessment = 0 AND flgAchieve = 0 and (sa.grade = 'D' or sa.grade is null)) OR 
 (modeAssessment = 2 AND flgAchieve = 0 and (sa.score < ag.min_score or sa.score is null)))
group by f.form, a.idPaper, p.keyOrder
order by f.form, p.keyOrder, src

--Meet the target
select r1.*, case when num is null then 0 else num end as num
from (
	select *
	from (
		select distinct f.form, a.idPaper, keyOrder
		from tblAssessment a
		inner join tblForm f on f.form = cast(left(classRemark, 1) as tinyint)
		inner join tblPaper p on p.formGroup = f.formGroup and a.idPaper = p.idPaper
		where a.flgComplete = 1 and modeAssessment in (0, 2)
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
	select r1.form, r1.idPaper, floor(r1.score * 10.0 / r2.score) / 10.0 as lbound, count(*) as num
	from 	(
		select s.idStudent, c.form, a.idPaper, 
		sum(
		case when flgAchieve = 1 then 
			agc.credit
		else
			case when a.modeAssessment = 0 then 
				ag.credit 
			else 
				case when a.modeAssessment = 2 then 
					case when sa.score >= aga.min_score then 
						aga.credit 
					else 
						case when sa.score >= agb.min_score then 
							agb.credit 
						else 
							case when sa.score >= agc.min_score then
								agc.credit
							else 0 
							end
						end  
					end
				end
			end
		end) as score
		from tblAssessment a 
		inner join tblAssessmentGrade aga on a.idAssessment = aga.idAssessment AND aga.grade = 'A'
		inner join tblAssessmentGrade agb on a.idAssessment = agb.idAssessment AND agb.grade = 'B'
		inner join tblAssessmentGrade agc on a.idAssessment = agc.idAssessment AND agc.grade = 'C'
		inner join tblStudentAssessment sa on a.idAssessment = sa.idAssessment
		inner join tblStudent s on s.idStudent = sa.idStudent and ((@term = 1 AND flgTerm1 = 1) OR (@term = 2 AND flgTerm2 = 1))
		inner join tblClass c on s.class = c.class
		left join tblAssessmentGrade ag on a.idAssessment = ag.idAssessment AND ag.grade = sa.grade
		where a.flgComplete = 1 and modeAssessment in (0, 2)
		group by s.idStudent, c.form, a.idPaper
	) r1
	inner join (
		select cast(left(classRemark, 1) as tinyint) as form, idPaper, sum(a.maxCredit) as score
		from tblAssessment a
		where a.flgComplete = 1 and modeAssessment in (0, 2)
		group by cast(left(classRemark, 1) as tinyint) , idPaper
	) r2 on r1.form = r2.form and r1.idPaper = r2.idPaper
	group by r1.form, r1.idPaper, floor(r1.score * 10.0 / r2.score) / 10.0
) r2 on r1.lbound = r2.lbound and r1.form = r2.form and r1.idPaper = r2.idPaper
order by r1.form, r1.keyOrder, r1.lbound desc
