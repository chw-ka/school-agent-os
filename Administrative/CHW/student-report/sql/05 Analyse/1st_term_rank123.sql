-- Overall Class Rank --
select s.form, rankClass as place, s.class, s.numberClass, s.nameChinese, score / 10.0 as score
from vwStudent s
inner join tblZStudentRank2 zsr on s.idStudent = zsr.idStudent   
	and zsr.flgStandard = 0 
	and zsr.section = 'O' 
	and zsr.term = 1
	and zsr.idPaper = ''
where zsr.rankClass <= 3 and s.form in (1,2,3,4,5)
order by form, s.class, place


-- Subject Form Rank
select s.form, p.nameChinese, rankForm as place, s.class, s.numberClass, s.nameChinese, score / 10.0 as score,  p.keyorder
from vwStudent s
inner join tblZStudentRank2 zsr on s.idStudent = zsr.idStudent   
	and zsr.flgStandard = 0 
	and zsr.section = 'E' 
	and zsr.term = 1
	and idPaper <> ''

inner join tblPaper p on p.idPaper = zsr.idPaper 
	and (p.idPaper = p.idSubject or p.idSubject is NULL) 
	and p.formgroup = zsr.form
where zsr.rankForm = 1 and s.form in (1,2,3,4,5,6)


order by form, p.keyorder, place, s.class




















--select * from tblZStudentRank2 where idPaper = ''
--select * from tblPaper

-- class rank ----
select s.form, p.nameChinese, rankClass as place, s.class, s.numberClass, s.nameChinese, score / 10.0 as score,  p.keyorder, 0 as form_rank
from vwStudent s
inner join tblZStudentRank2 zsr on s.idStudent = zsr.idStudent and idPaper <> ''  and zsr.flgStandard = 0 and zsr.section = 'E' and zsr.term = 1
inner join tblPaper p on p.idPaper = zsr.idPaper and (p.idPaper = p.idSubject or p.idSubject is NULL) and p.formgroup = zsr.form
where zsr.rankClass < 4 and s.form in (1,2,3)


Union


-- class rank ----
select s.form, p.nameChinese, rankClass  as place, s.class, s.numberClass, s.nameChinese, score / 10.0 as score,  p.keyorder, 0 as form_rank
from vwStudent s
inner join tblZStudentRank2 zsr on s.idStudent = zsr.idStudent and idPaper = 'CMP'  and zsr.flgStandard = 0 and zsr.section = 'R' and zsr.term = 1
inner join tblPaper p on p.idPaper = zsr.idPaper and (p.idPaper = p.idSubject or p.idSubject is NULL) and p.formgroup = zsr.form
where zsr.rankClass < 4 and s.form in (1,2,3)

Union
-- class rank ----

select s.form, p.nameChinese, rankClass as place, s.class, s.numberClass, s.nameChinese, score / 10.0 as score,  p.keyorder, 0 as form_rank
from vwStudent s
inner join tblZStudentRank2 zsr on s.idStudent = zsr.idStudent   and zsr.flgStandard = 0 and zsr.section = 'E' and zsr.term = 1
and idPaper <> ''
and idPaper in ('CHI', 'ENG', 'MTH','LST')
inner join tblPaper p on p.idPaper = zsr.idPaper and (p.idPaper = p.idSubject or p.idSubject is NULL) and p.formgroup = zsr.form
where zsr.rankClass < 4 and s.form in (4,5,6)

Union

-- form rank ----


select s.form, p.nameChinese, rankForm as place, s.class, s.numberClass, s.nameChinese, score / 10.0 as score,  p.keyorder, rankForm as form_rank
from vwStudent s
inner join tblZStudentRank2 zsr on s.idStudent = zsr.idStudent   and zsr.flgStandard = 0 and zsr.section = 'E' and zsr.term = 1
and idPaper <> ''
and idPaper not in ('CHI', 'ENG', 'MTH','LST')
inner join tblPaper p on p.idPaper = zsr.idPaper and (p.idPaper = p.idSubject or p.idSubject is NULL) and p.formgroup = zsr.form
where zsr.rankForm < 4 and s.form in (4,5,6)


order by form, p.keyorder, form_rank,  s.class, place 

