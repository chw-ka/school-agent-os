---------------------------------------------
--Class Rank  2015_03_10_S6
--S1, S2, S3, S4, S5, s6 學業成績優異獎 (班頭三名)
select s.form, rankClass, s.class, s.numberClass, s.nameChinese,s.idStudent, '', score / 100.0 as score
from vwStudent s
inner join tblZStudentRank2 zsr on s.idStudent = zsr.idStudent and zsr.idPaper = '' and zsr.flgStandard = 0 and zsr.section = 'O' and zsr.term = 0
where zsr.rankClass < 4 and s.form in (6)
order by s.class, rankClass

---------------------------------------------
--Paper Rank (科獎)  2015_03_10_S6
select f.form, p.idPaper, s.class, s.numberClass, s.nameChinese, s.idStudent, '', score / 100.0 as score, p.nameChinese + N'科科獎'
from tblStudent s
inner join tblClass c on s.class = c.class
inner join tblForm f on c.form = f.form
inner join tblZStudentRank2 zsr on s.idStudent = zsr.idStudent and zsr.flgStandard = 0 and zsr.section = 'O' and zsr.term = 0
inner join tblPaper p on zsr.idPaper = p.idPaper and f.formGroup = p.formGroup and (p.idSubject = p.idPaper OR p.idSubject is null)
where rankForm < 2 and f.form in  (6)
order by f.form, keyOrder, rankForm

----------------------------------------------
--S6 Form-Best (獎學金) updated by CM  2015_03_10 按標準分排名次
select top 10 r.form, zsr2.rankForm as StandardScoreRank, r.class, r.numberClass, r.nameChinese, r.idStudent, '',
zsr2.score, 
sum(r.rankForm * 1.0 / r.num) / r1.num as rankF,
zsr1.score / 100 as scoreAvg,
numDemeritDS_2 + numDemeritHW_2 as numDemerit,
case when r2.num is null then 0 else r2.num end as numBadAttitude
from (
	select s.idStudent, s.form, s.class, s.numberClass, s.nameChinese, zsr.idPaper, zsr.rankForm, r.num
	from vwStudent s
	inner join tblZStudentRank2 zsr on s.idStudent = zsr.idStudent and zsr.flgStandard = 0 and zsr.idPaper <> '' and zsr.section = 'O' and zsr.term = 0
	inner join (
		select s.class, zsr.idPaper, count(*) as num
		from tblStudent s
		INNER JOIN tblZStudentRank2 zsr ON s.idStudent = zsr.idStudent and zsr.flgStandard = 0 and zsr.idPaper <> '' and zsr.section = 'O' and zsr.term = 0
		where zsr.idPaper <> 'BBS'
		group by class, zsr.idPaper
	) r on s.class = r.class and zsr.idPaper = r.idPaper
	where s.form = 6
) r
inner join (
	select idStudent, count(*) as num
	from tblZStudentRank2
	where flgStandard = 0 and idPaper <> '' and section = 'O' and term = 0 and idPaper <> 'BBS'
	group by idStudent
) r1 on r.idStudent =  r1.idStudent
inner join tblZStudentRank2 zsr1 on r.idStudent = zsr1.idStudent and zsr1.flgStandard = 0 and zsr1.idPaper = '' and zsr1.section = 'O' and zsr1.term = 0
inner join tblZStudentRank2 zsr2 on r.idStudent = zsr2.idStudent and zsr2.flgStandard = 1 and zsr2.idPaper = '' and zsr2.section = 'O' and zsr2.term = 0
left join tblStudentDiscipline sd on r.idStudent = sd.idStudent
left join (
	select idStudent, sum(num) as num
	from (
		select idStudent, count(*) as num
		from tblStudentAttitude
		where lesson_2 in ('C', 'D')
		group by idStudent
		union
		select idStudent, count(*)
		from tblStudentAttitude
		where assessment_2 in ('C', 'D')
		group by idStudent
	) r
	group by idStudent
) r2 on r.idStudent = r2.idStudent
group by r.form, r.class, r.numberClass, r.nameChinese, r.idStudent, r1.num, zsr1.rankForm, zsr1.score / 100, zsr2.score, zsr2.rankForm, numDemeritDS_2, numDemeritHW_2, r2.num
order by score desc


----------------------------------------------
-- 獎學金最新查詢位於檔案最尾 (2013)


----------------------------------------------
--S6, S7 (Option)
select r.form, zsr2.rankClass, r.class, r.numberClass, r.nameChinese, zsr2.score, sum(r.rankClass * 1.0 / r.num) / r1.num as rankC,
zsr1.score / 100
from (
	select s.idStudent, s.form, s.class, s.numberClass, s.nameChinese, zsr.idPaper, zsr.rankClass, r.num
	from vwStudent s
	inner join tblZStudentRank2 zsr on s.idStudent = zsr.idStudent and zsr.flgStandard = 0 and zsr.idPaper <> '' and zsr.section = 'O' and zsr.term = 0
	inner join (
		select s.class, zsr.idPaper, count(*) as num
		from tblStudent s
		INNER JOIN tblZStudentRank2 zsr ON s.idStudent = zsr.idStudent and zsr.flgStandard = 0 and zsr.idPaper <> '' and zsr.section = 'O' and zsr.term = 0
		where zsr.idPaper <> 'BBS'
		group by class, zsr.idPaper
	) r on s.class = r.class and zsr.idPaper = r.idPaper
	where s.form in(6)
) r
inner join (
	select idStudent, count(*) as num
	from tblZStudentRank2
	where flgStandard = 0 and idPaper <> '' and section = 'O' and term = 0 and idPaper <> 'BBS' 
	group by idStudent
) r1 on r.idStudent =  r1.idStudent
inner join tblZStudentRank2 zsr1 on r.idStudent = zsr1.idStudent and zsr1.flgStandard = 0 and zsr1.idPaper = '' and zsr1.section = 'O' and zsr1.term = 0
inner join tblZStudentRank2 zsr2 on r.idStudent = zsr2.idStudent and zsr2.flgStandard = 1 and zsr2.idPaper = '' and zsr2.section = 'O' and zsr2.term = 0
where zsr2.rankClass < 4
group by r.form, r.class, r.numberClass, r.nameChinese, r1.num, zsr1.rankClass, zsr1.score / 100, zsr2.score, zsr2.rankClass
order by r.class, zsr2.rankClass


--S1-3 Form-Best (獎學金)

select f.form, rankForm, s.class, s.numberClass, s.nameChinese, score / 100.0 as score
from tblStudent s
inner join tblClass c on s.class = c.class
inner join tblForm f on c.form = f.form
inner join tblZStudentRank2 zsr on s.idStudent = zsr.idStudent and zsr.flgStandard = 0 and zsr.section = 'O' and zsr.term = 0 and zsr.idPaper = ''
where rankForm <= 5 and f.form < 4
order by f.form, rankForm

----------------------------------------------
--S4 Form-Best (獎學金)

select top 10 r.form, zsr2.rankForm, r.class, r.numberClass, r.nameChinese, 
zsr2.score, 
sum(r.rankForm * 1.0 / r.num) / r1.num as rankF,
zsr1.score / 10 as scoreAvg,
numDemeritDS_2 + numDemeritHW_2 as numDemerit,
case when r2.num is null then 0 else r2.num end as numBadAttitude
from (
	select s.idStudent, s.form, s.class, s.numberClass, s.nameChinese, zsr.idPaper, zsr.rankForm, r.num
	from vwStudent s
	inner join tblZStudentRank2 zsr on s.idStudent = zsr.idStudent and zsr.flgStandard = 0 and zsr.idPaper <> '' and zsr.section = 'O' and zsr.term = 0
	inner join (
		select s.class, zsr.idPaper, count(*) as num
		from tblStudent s
		INNER JOIN tblZStudentRank2 zsr ON s.idStudent = zsr.idStudent and zsr.flgStandard = 0 and zsr.idPaper <> '' and zsr.section = 'O' and zsr.term = 0
		where zsr.idPaper <> 'BBS'
		group by class, zsr.idPaper
	) r on s.class = r.class and zsr.idPaper = r.idPaper
	where s.form = 4
) r
inner join (
	select idStudent, count(*) as num
	from tblZStudentRank2
	where flgStandard = 0 and idPaper <> '' and section = 'O' and term = 0 and idPaper <> 'BBS'
	group by idStudent
) r1 on r.idStudent =  r1.idStudent
inner join tblZStudentRank2 zsr1 on r.idStudent = zsr1.idStudent and zsr1.flgStandard = 0 and zsr1.idPaper = '' and zsr1.section = 'O' and zsr1.term = 0
inner join tblZStudentRank2 zsr2 on r.idStudent = zsr2.idStudent and zsr2.flgStandard = 1 and zsr2.idPaper = '' and zsr2.section = 'O' and zsr2.term = 0
left join tblStudentDiscipline sd on r.idStudent = sd.idStudent
left join (
	select idStudent, sum(num) as num
	from (
		select idStudent, count(*) as num
		from tblStudentAttitude
		where lesson_2 in ('C', 'D')
		group by idStudent
		union
		select idStudent, count(*)
		from tblStudentAttitude
		where assessment_2 in ('C', 'D')
		group by idStudent
	) r
	group by idStudent
) r2 on r.idStudent = r2.idStudent
group by r.form, r.class, r.numberClass, r.nameChinese, r1.num, zsr1.rankForm, zsr1.score / 10, zsr2.score, zsr2.rankForm, numDemeritDS_2, numDemeritHW_2, r2.num
order by rankF



----S6 Form-Best (獎學金)
--
--select top 10 r.form, zsr2.rankForm, r.class, r.numberClass, r.nameChinese, 
--zsr2.score, 
--sum(r.rankForm * 1.0 / r.num) / r1.num as rankF,
--zsr1.score / 10 as scoreAvg,
--numDemeritDS_2 + numDemeritHW_2 as numDemerit,
--case when r2.num is null then 0 else r2.num end as numBadAttitude
--from (
--	select s.idStudent, s.form, s.class, s.numberClass, s.nameChinese, zsr.idPaper, zsr.rankForm, r.num
--	from vwStudent s
--	inner join tblZStudentRank2 zsr on s.idStudent = zsr.idStudent and zsr.flgStandard = 0 and zsr.idPaper <> '' and zsr.section = 'O' and zsr.term = 0
--	inner join (
--		select s.class, zsr.idPaper, count(*) as num
--		from tblStudent s
--		INNER JOIN tblZStudentRank2 zsr ON s.idStudent = zsr.idStudent and zsr.flgStandard = 0 and zsr.idPaper <> '' and zsr.section = 'O' and zsr.term = 0
--		where zsr.idPaper <> 'CES'
--		group by class, zsr.idPaper
--	) r on s.class = r.class and zsr.idPaper = r.idPaper
--	where s.form = 6
--) r
--inner join (
--	select idStudent, count(*) as num
--	from tblZStudentRank2
--	where flgStandard = 0 and idPaper <> '' and section = 'O' and term = 0 and idPaper <> 'CES'
--	group by idStudent
--) r1 on r.idStudent =  r1.idStudent
--inner join tblZStudentRank2 zsr1 on r.idStudent = zsr1.idStudent and zsr1.flgStandard = 0 and zsr1.idPaper = '' and zsr1.section = 'O' and zsr1.term = 0
--inner join tblZStudentRank2 zsr2 on r.idStudent = zsr2.idStudent and zsr2.flgStandard = 1 and zsr2.idPaper = '' and zsr2.section = 'O' and zsr2.term = 0
--left join tblStudentDiscipline sd on r.idStudent = sd.idStudent
--left join (
--	select idStudent, sum(num) as num
--	from (
--		select idStudent, count(*) as num
--		from tblStudentAttitude
--		where lesson_2 in ('C', 'D')
--		group by idStudent
--		union
--		select idStudent, count(*)
--		from tblStudentAttitude
--		where assessment_2 in ('C', 'D')
--		group by idStudent
--	) r
--	group by idStudent
--) r2 on r.idStudent = r2.idStudent
--group by r.form, r.class, r.numberClass, r.nameChinese, r1.num, zsr1.rankForm, zsr1.score / 10, zsr2.score, zsr2.rankForm, numDemeritDS_2, numDemeritHW_2, r2.num
--order by rankF
----------------------------------------------
--S5 Form-Best (獎學金)

select top 10 r.form, zsr2.rankForm, r.class, r.numberClass, r.nameChinese, 
zsr2.score, 
sum(r.rankForm * 1.0 / r.num) / r1.num as rankF,
zsr1.score / 10 as scoreAvg,
numDemeritDS_2 + numDemeritHW_2 as numDemerit,
case when r2.num is null then 0 else r2.num end as numBadAttitude
from (
	select s.idStudent, s.form, s.class, s.numberClass, s.nameChinese, zsr.idPaper, zsr.rankForm, r.num
	from vwStudent s
	inner join tblZStudentRank2 zsr on s.idStudent = zsr.idStudent and zsr.flgStandard = 0 and zsr.idPaper <> '' and zsr.section = 'O' and zsr.term = 0
	inner join (
		select s.class, zsr.idPaper, count(*) as num
		from tblStudent s
		INNER JOIN tblZStudentRank2 zsr ON s.idStudent = zsr.idStudent and zsr.flgStandard = 0 and zsr.idPaper <> '' and zsr.section = 'O' and zsr.term = 0
		where zsr.idPaper <> 'CES'
		group by class, zsr.idPaper
	) r on s.class = r.class and zsr.idPaper = r.idPaper
	where s.form = 5
) r
inner join (
	select idStudent, count(*) as num
	from tblZStudentRank2
	where flgStandard = 0 and idPaper <> '' and section = 'O' and term = 0 and idPaper <> 'CES'
	group by idStudent
) r1 on r.idStudent =  r1.idStudent
inner join tblZStudentRank2 zsr1 on r.idStudent = zsr1.idStudent and zsr1.flgStandard = 0 and zsr1.idPaper = '' and zsr1.section = 'O' and zsr1.term = 0
inner join tblZStudentRank2 zsr2 on r.idStudent = zsr2.idStudent and zsr2.flgStandard = 1 and zsr2.idPaper = '' and zsr2.section = 'O' and zsr2.term = 0
left join tblStudentDiscipline sd on r.idStudent = sd.idStudent
left join (
	select idStudent, sum(num) as num
	from (
		select idStudent, count(*) as num
		from tblStudentAttitude
		where lesson_2 in ('C', 'D')
		group by idStudent
		union
		select idStudent, count(*)
		from tblStudentAttitude
		where assessment_2 in ('C', 'D')
		group by idStudent
	) r
	group by idStudent
) r2 on r.idStudent = r2.idStudent
group by r.form, r.class, r.numberClass, r.nameChinese, r1.num, zsr1.rankForm, zsr1.score / 10, zsr2.score, zsr2.rankForm, numDemeritDS_2, numDemeritHW_2, r2.num
order by zsr2.score DESC

----------------------------------------------
--S7 Form-Best (獎學金)

select top 10 r.form, zsr2.rankForm, r.class, r.numberClass, r.nameChinese, 
zsr2.score, 
sum(r.rankForm * 1.0 / r.num) / r1.num as rankF,
zsr1.score / 10 as scoreAvg,
numDemeritDS_2 + numDemeritHW_2 as numDemerit,
case when r2.num is null then 0 else r2.num end as numBadAttitude
from (
	select s.idStudent, s.form, s.class, s.numberClass, s.nameChinese, zsr.idPaper, zsr.rankForm, r.num
	from vwStudent s
	inner join tblZStudentRank2 zsr on s.idStudent = zsr.idStudent and zsr.flgStandard = 0 and zsr.idPaper <> '' and zsr.section = 'O' and zsr.term = 0
	inner join (
		select s.class, zsr.idPaper, count(*) as num
		from tblStudent s
		INNER JOIN tblZStudentRank2 zsr ON s.idStudent = zsr.idStudent and zsr.flgStandard = 0 and zsr.idPaper <> '' and zsr.section = 'O' and zsr.term = 0
		where zsr.idPaper <> 'CES'
		group by class, zsr.idPaper
	) r on s.class = r.class and zsr.idPaper = r.idPaper
	where s.form = 7
) r
inner join (
	select idStudent, count(*) as num
	from tblZStudentRank2
	where flgStandard = 0 and idPaper <> '' and section = 'O' and term = 0 and idPaper <> 'CES'
	group by idStudent
) r1 on r.idStudent =  r1.idStudent
inner join tblZStudentRank2 zsr1 on r.idStudent = zsr1.idStudent and zsr1.flgStandard = 0 and zsr1.idPaper = '' and zsr1.section = 'O' and zsr1.term = 0
inner join tblZStudentRank2 zsr2 on r.idStudent = zsr2.idStudent and zsr2.flgStandard = 1 and zsr2.idPaper = '' and zsr2.section = 'O' and zsr2.term = 0
left join tblStudentDiscipline sd on r.idStudent = sd.idStudent
left join (
	select idStudent, sum(num) as num
	from (
		select idStudent, count(*) as num
		from tblStudentAttitude
		where lesson_2 in ('C', 'D')
		group by idStudent
		union
		select idStudent, count(*)
		from tblStudentAttitude
		where assessment_2 in ('C', 'D')
		group by idStudent
	) r
	group by idStudent
) r2 on r.idStudent = r2.idStudent
group by r.form, r.class, r.numberClass, r.nameChinese, r1.num, zsr1.rankForm, zsr1.score / 10, zsr2.score, zsr2.rankForm, numDemeritDS_2, numDemeritHW_2, r2.num
order by zsr2.score DESC

------------------------------------------
------------------------------------------
------------------------------------------
------------------------------------------
------------------------------------------
--Reference SQL Only (Optional)

--select top 10 r.idStudent, r.form, r.class, r.numberClass, r.nameChinese, sum(r.rankClass * 1.0 / r.num) / r1.num as rankC,
--zsr1.rankClass, zsr1.score / 10, zsr2.score
--from (
--	select s.idStudent, s.form, s.class, s.numberClass, s.nameChinese, zsr.idPaper, zsr.rankClass, r.num
--	from vwStudent s
--	inner join tblZStudentRank2 zsr on s.idStudent = zsr.idStudent and zsr.flgStandard = 0 and zsr.idPaper <> '' and zsr.section = 'O' and zsr.term = 0
--	inner join (
--		select s.class, zsr.idPaper, count(*) as num
--		from tblStudent s
--		INNER JOIN tblZStudentRank2 zsr ON s.idStudent = zsr.idStudent and zsr.flgStandard = 0 and zsr.idPaper <> '' and zsr.section = 'O' and zsr.term = 0
--		group by class, zsr.idPaper
--	) r on s.class = r.class and zsr.idPaper = r.idPaper
--	where s.class = '4A' and zsr.idPaper <> 'CES'
--) r
--inner join (
--	select idStudent, count(*) as num
--	from tblZStudentRank2
--	where flgStandard = 0 and idPaper <> '' and section = 'O' and term = 0
--	group by idStudent
--) r1 on r.idStudent =  r1.idStudent
--inner join tblZStudentRank2 zsr1 on r.idStudent = zsr1.idStudent and zsr1.flgStandard = 0 and zsr1.idPaper = '' and zsr1.section = 'O' and zsr1.term = 0
--inner join tblZStudentRank2 zsr2 on r.idStudent = zsr2.idStudent and zsr2.flgStandard = 1 and zsr2.idPaper = '' and zsr2.section = 'O' and zsr2.term = 0
--group by r.idStudent, r.form, r.class, r.numberClass, r.nameChinese, r1.num, zsr1.rankClass, zsr1.score / 10, zsr2.score
--order by rankC

select top 10 r.idStudent, r.form, r.class, r.numberClass, r.nameChinese, sum(r.rankForm * 1.0 / r.num) / r1.num as rankF,
zsr1.rankForm, zsr1.score / 10, zsr2.score
from (
	select s.idStudent, s.form, s.class, s.numberClass, s.nameChinese, zsr.idPaper, zsr.rankForm, r.num
	from vwStudent s
	inner join tblZStudentRank2 zsr on s.idStudent = zsr.idStudent and zsr.flgStandard = 0 and zsr.idPaper <> '' and zsr.section = 'O' and zsr.term = 0
	inner join (
		select s.class, zsr.idPaper, count(*) as num
		from tblStudent s
		INNER JOIN tblZStudentRank2 zsr ON s.idStudent = zsr.idStudent and zsr.flgStandard = 0 and zsr.idPaper <> '' and zsr.section = 'O' and zsr.term = 0
		where zsr.idPaper <> 'CES'
		group by class, zsr.idPaper
	) r on s.class = r.class and zsr.idPaper = r.idPaper
	where s.form = 7
) r
inner join (
	select idStudent, count(*) as num
	from tblZStudentRank2
	where flgStandard = 0 and idPaper <> '' and section = 'O' and term = 0 and idPaper <> 'CES' 
	group by idStudent
) r1 on r.idStudent =  r1.idStudent
inner join tblZStudentRank2 zsr1 on r.idStudent = zsr1.idStudent and zsr1.flgStandard = 0 and zsr1.idPaper = '' and zsr1.section = 'O' and zsr1.term = 0
inner join tblZStudentRank2 zsr2 on r.idStudent = zsr2.idStudent and zsr2.flgStandard = 1 and zsr2.idPaper = '' and zsr2.section = 'O' and zsr2.term = 0
group by r.idStudent, r.form, r.class, r.numberClass, r.nameChinese, r1.num, zsr1.rankForm, zsr1.score / 10, zsr2.score
order by rankF

--select s.form, zsr.rankClass, s.class, s.numberClass, s.nameChinese, zsr.rankClass, zsr.score, zsr1.rankClass, zsr1.score / 10.0 as score
--from vwStudent s
--inner join tblZStudentRank2 zsr on s.idStudent = zsr.idStudent and zsr.idPaper = '' and zsr.flgStandard = 1 and zsr.section = 'O' and zsr.term = 0
--inner join tblZStudentRank2 zsr1 on s.idStudent = zsr1.idStudent and zsr1.idPaper = '' and zsr1.flgStandard = 0 and zsr1.section = 'O' and zsr1.term = 0
--where zsr.rankClass < 4 and s.form in (4, 6) 
--order by s.class, zsr.rankClass


SELECT top 5 s
select top 5 s.class, s.numberClass, s.nameChinese, avg(((score_final / 10.0) - mean) / sd) as score, count( * ) as numSubject, sc.idStaff 
from tblStudent s
inner join tblClass c on s.class = c.class
inner join tblForm f on c.form = f.form
inner join tblZStudentPaperRank zspr on s.idStudent = zspr.idStudent
INNER JOIN tblPaper p ON zspr.idPaper = p.idPaper AND f.formGroup = p.formGroup AND (p.idSubject = p.idPaper OR p.idSubject is null) 
INNER JOIN tblStaffClass sc ON sc.class = s.class AND flgHead = 1 
INNER JOIN (
select f.form, p.idPaper, avg(score_final / 10.0) as mean, stdev(score_final / 10.0) as sd
from tblStudent s
inner join tblClass c on s.class = c.class
inner join tblForm f on c.form = f.form
inner join tblZStudentPaperRank zspr on s.idStudent = zspr.idStudent
INNER JOIN tblPaper p ON zspr.idPaper = p.idPaper AND f.formGroup = p.formGroup AND (p.idSubject = p.idPaper OR p.idSubject is null) 
group by f.form, p.idPaper
) r on f.form = r.form and p.idPaper = r.idPaper 
where s.class = @class and p.idPaper <> 'CES'
group by f.form, s.class, s.numberClass, s.nameEnglish, s.nameChinese, sc.idStaff 
order by score desc





----------------------------------------------
--S4-7 Form-Best 
--w/ Standard Score

select top 10 r.form, zsr2.rankForm, r.class, r.numberClass, r.nameChinese, 
zsr2.score, 
sum(r.rankForm * 1.0 / r.num) / r1.num as rankF,
zsr1.score / 10 as scoreAvg,
numDemeritDS_2 + numDemeritHW_2 as numDemerit,
case when r2.num is null then 0 else r2.num end as numBadAttitude
from (
	select s.idStudent, s.form, s.class, s.numberClass, s.nameChinese, zsr.idPaper, zsr.rankForm, r.num
	from vwStudent s
	inner join tblZStudentRank2 zsr on s.idStudent = zsr.idStudent and zsr.flgStandard = 0 and zsr.idPaper <> '' and zsr.section = 'O' and zsr.term = 0
	inner join (
		select s.class, zsr.idPaper, count(*) as num
		from tblStudent s
		INNER JOIN tblZStudentRank2 zsr ON s.idStudent = zsr.idStudent and zsr.flgStandard = 0 and zsr.idPaper <> '' and zsr.section = 'O' and zsr.term = 0
		where zsr.idPaper <> 'BBS'
		group by class, zsr.idPaper
	) r on s.class = r.class and zsr.idPaper = r.idPaper
	where s.form = 4
) r
inner join (
	select idStudent, count(*) as num
	from tblZStudentRank2
	where flgStandard = 0 and idPaper <> '' and section = 'O' and term = 0 and idPaper <> 'BBS'
	group by idStudent
) r1 on r.idStudent =  r1.idStudent
inner join tblZStudentRank2 zsr1 on r.idStudent = zsr1.idStudent and zsr1.flgStandard = 0 and zsr1.idPaper = '' and zsr1.section = 'O' and zsr1.term = 0
inner join tblZStudentRank2 zsr2 on r.idStudent = zsr2.idStudent and zsr2.flgStandard = 1 and zsr2.idPaper = '' and zsr2.section = 'O' and zsr2.term = 0
left join tblStudentDiscipline sd on r.idStudent = sd.idStudent
left join (
	select idStudent, sum(num) as num
	from (
		select idStudent, count(*) as num
		from tblStudentAttitude
		where lesson_2 in ('C', 'D')
		group by idStudent
		union
		select idStudent, count(*)
		from tblStudentAttitude
		where assessment_2 in ('C', 'D')
		group by idStudent
	) r
	group by idStudent
) r2 on r.idStudent = r2.idStudent
group by r.form, r.class, r.numberClass, r.nameChinese, r1.num, zsr1.rankForm, zsr1.score / 10, zsr2.score, zsr2.rankForm, numDemeritDS_2, numDemeritHW_2, r2.num
order by zsr2.rankForm

-- Poor   ( 吳、陳)
--update yearSchool
--select top 10 s.form, rankForm, s.class, s.numberClass, s.nameChinese, score / 100.0 as score
--from vwStudent s
--inner join tblZStudentRank2 zsr on s.idStudent = zsr.idStudent and zsr.flgStandard = 0 and zsr.section = 'O' and zsr.term = 0 and zsr.idPaper = ''
--inner join tblYStudentInfo2 ysi1 on s.idStudent = ysi1.idStudent and ysi1.yearSchool = 2019 and ysi1.grantRange in ('H', 'F', 'E')
--where s.form in (1,2,3)
--order by score desc

-- 吳柏炎先生紀念獎學金、吳冼佩英夫人紀念獎學金   2019-2020
--update yearSchool
select top 10 r.form, zsr2.rankForm, r.class, r.numberClass, r.nameChinese, r.idStudent,
zsr2.score, 
sum(r.rankForm * 1.0 / r.num) / r1.num as rankF,
zsr1.score / 100 as scoreAvg,
numDemeritDS_2 + numDemeritHW_2 as numDemerit,
case when r2.num is null then 0 else r2.num end as numBadAttitude
from (
	select s.idStudent, s.form, s.class, s.numberClass, s.nameChinese, zsr.idPaper, zsr.rankForm, r.num
	from vwStudent s
	inner join tblZStudentRank2 zsr on s.idStudent = zsr.idStudent and zsr.flgStandard = 0 and zsr.idPaper <> '' and zsr.section = 'O' and zsr.term = 0
	inner join (
		select s.class, zsr.idPaper, count(*) as num
		from tblStudent s
		INNER JOIN tblZStudentRank2 zsr ON s.idStudent = zsr.idStudent and zsr.flgStandard = 0 and zsr.idPaper <> '' and zsr.section = 'O' and zsr.term = 0
		where zsr.idPaper <> 'BBS'
		group by class, zsr.idPaper
	) r on s.class = r.class and zsr.idPaper = r.idPaper
	where s.form in (1,2,3)
) r
inner join tblYStudentInfo2 ysi1 on r.idStudent = ysi1.idStudent and ysi1.yearSchool = 2019 and ysi1.grantRange in ('H', 'F', 'E')
inner join (
	select idStudent, count(*) as num
	from tblZStudentRank2
	where flgStandard = 0 and idPaper <> '' and section = 'O' and term = 0 and idPaper <> 'BBS'
	group by idStudent
) r1 on r.idStudent =  r1.idStudent
inner join tblZStudentRank2 zsr1 on r.idStudent = zsr1.idStudent and zsr1.flgStandard = 0 and zsr1.idPaper = '' and zsr1.section = 'O' and zsr1.term = 0
inner join tblZStudentRank2 zsr2 on r.idStudent = zsr2.idStudent and zsr2.flgStandard = 1 and zsr2.idPaper = '' and zsr2.section = 'O' and zsr2.term = 0
left join tblStudentDiscipline sd on r.idStudent = sd.idStudent
left join (
	select idStudent, sum(num) as num
	from (
		select idStudent, count(*) as num
		from tblStudentAttitude
		where lesson_2 in ('C', 'D')
		group by idStudent
		union
		select idStudent, count(*)
		from tblStudentAttitude
		where assessment_2 in ('C', 'D')
		group by idStudent
	) r
	group by idStudent
) r2 on r.idStudent = r2.idStudent
group by r.form, r.class, r.numberClass, r.nameChinese, r.idStudent, r1.num, zsr1.rankForm, zsr1.score / 100, zsr2.score, zsr2.rankForm, numDemeritDS_2, numDemeritHW_2, r2.num
order by rankF

-- 陳學文先生紀念獎學金、陳容超巾夫人紀念獎學金   
-- ****** 執行前須 update yearSchool
select top 10 r.form, zsr2.rankForm, r.class, r.numberClass, r.nameChinese, r.idStudent, '',
zsr2.score, '',
sum(r.rankForm * 1.0 / r.num) / r1.num as rankF,
zsr1.score / 100 as scoreAvg,
numDemeritDS_2 + numDemeritHW_2 as numDemerit,
case when r2.num is null then 0 else r2.num end as numBadAttitude
from (
	select s.idStudent, s.form, s.class, s.numberClass, s.nameChinese, zsr.idPaper, zsr.rankForm, r.num
	from vwStudent s
	inner join tblZStudentRank2 zsr on s.idStudent = zsr.idStudent and zsr.flgStandard = 0 and zsr.idPaper <> '' and zsr.section = 'O' and zsr.term = 0
	inner join (
		select s.class, zsr.idPaper, count(*) as num
		from tblStudent s
		INNER JOIN tblZStudentRank2 zsr ON s.idStudent = zsr.idStudent and zsr.flgStandard = 0 and zsr.idPaper <> '' and zsr.section = 'O' and zsr.term = 0
		where zsr.idPaper <> 'BBS'
		group by class, zsr.idPaper
	) r on s.class = r.class and zsr.idPaper = r.idPaper
	where s.form in (6)
) r
inner join tblYStudentInfo2 ysi1 on r.idStudent = ysi1.idStudent and ysi1.yearSchool = 2024 and ysi1.grantRange in ('H', 'F', 'E')
inner join (
	select idStudent, count(*) as num
	from tblZStudentRank2
	where flgStandard = 0 and idPaper <> '' and section = 'O' and term = 0 and idPaper <> 'BBS'
	group by idStudent
) r1 on r.idStudent =  r1.idStudent
inner join tblZStudentRank2 zsr1 on r.idStudent = zsr1.idStudent and zsr1.flgStandard = 0 and zsr1.idPaper = '' and zsr1.section = 'O' and zsr1.term = 0
inner join tblZStudentRank2 zsr2 on r.idStudent = zsr2.idStudent and zsr2.flgStandard = 1 and zsr2.idPaper = '' and zsr2.section = 'O' and zsr2.term = 0
left join tblStudentDiscipline sd on r.idStudent = sd.idStudent
left join (
	select idStudent, sum(num) as num
	from (
		select idStudent, count(*) as num
		from tblStudentAttitude
		where lesson_2 in ('C', 'D')
		group by idStudent
		union
		select idStudent, count(*)
		from tblStudentAttitude
		where assessment_2 in ('C', 'D')
		group by idStudent
	) r
	group by idStudent
) r2 on r.idStudent = r2.idStudent
group by r.form, r.class, r.numberClass, r.nameChinese, r.idStudent, r1.num, zsr1.rankForm, zsr1.score / 100, zsr2.score, zsr2.rankForm, numDemeritDS_2, numDemeritHW_2, r2.num
order by score desc

--select top 15 r.form, zsr2.rankForm, r.class, r.numberClass, r.nameChinese, 
--zsr2.score, 
--sum(r.rankForm * 1.0 / r.num) / r1.num as rankF,
--zsr1.score / 10
--from (
--	select s.idStudent, s.form, s.class, s.numberClass, s.nameChinese, zsr.idPaper, zsr.rankForm, r.num
--	from vwStudent s
--	inner join tblZStudentRank2 zsr on s.idStudent = zsr.idStudent and zsr.flgStandard = 0 and zsr.idPaper <> '' and zsr.section = 'O' and zsr.term = 0
--	inner join (
--		select s.class, zsr.idPaper, count(*) as num
--		from tblStudent s
--		INNER JOIN tblZStudentRank2 zsr ON s.idStudent = zsr.idStudent and zsr.flgStandard = 0 and zsr.idPaper <> '' and zsr.section = 'O' and zsr.term = 0
--		where zsr.idPaper <> 'CES'
--		group by class, zsr.idPaper
--	) r on s.class = r.class and zsr.idPaper = r.idPaper
--	where s.form in (4,5)
--) r
--inner join (
--	select idStudent, count(*) as num
--	from tblZStudentRank2
--	where flgStandard = 0 and idPaper <> '' and section = 'O' and term = 0 and idPaper <> 'BBS' 
--	group by idStudent
--) r1 on r.idStudent = r1.idStudent
--inner join tblZStudentRank2 zsr1 on r.idStudent = zsr1.idStudent and zsr1.flgStandard = 0 and zsr1.idPaper = '' and zsr1.section = 'O' and zsr1.term = 0
--inner join tblZStudentRank2 zsr2 on r.idStudent = zsr2.idStudent and zsr2.flgStandard = 1 and zsr2.idPaper = '' and zsr2.section = 'O' and zsr2.term = 0
--inner join tblYStudentInfo2 ysi1 on r.idStudent = ysi1.idStudent and ysi1.yearSchool = 2011 and ysi1.grantRange in ('H', 'F', 'E')
--group by r.form, r.class, r.numberClass, r.nameChinese, r1.num, zsr1.rankForm, zsr1.score / 10, zsr2.score, zsr2.rankForm
--order by zsr2.score desc

--- Math   龐達榮
select top 5 s.form, zsr2.rankForm, s.class, s.numberClass, s.nameChinese, s.idStudent, (zsr2.score - zsr1.score) / 100.0 as diff, zsr1.score / 100.0, zsr2.score / 100.0
from vwStudent s
inner join tblZStudentRank2 zsr1 on s.idStudent = zsr1.idStudent and zsr1.flgStandard = 0 and zsr1.idPaper = 'MTH' and zsr1.section = 'O' and zsr1.term = 1
inner join tblZStudentRank2 zsr2 on s.idStudent = zsr2.idStudent and zsr2.flgStandard = 0 and zsr2.idPaper = 'MTH' and zsr2.section = 'O' and zsr2.term = 2
where s.form in (1) and zsr2.score >= 500
order by diff desc

select top 5 s.form, zsr2.rankForm, s.class, s.numberClass, s.nameChinese, s.idStudent, (zsr2.score - zsr1.score) / 100.0 as diff, zsr1.score / 100.0, zsr2.score / 100.0
from vwStudent s
inner join tblZStudentRank2 zsr1 on s.idStudent = zsr1.idStudent and zsr1.flgStandard = 0 and zsr1.idPaper = 'MTH' and zsr1.section = 'O' and zsr1.term = 1
inner join tblZStudentRank2 zsr2 on s.idStudent = zsr2.idStudent and zsr2.flgStandard = 0 and zsr2.idPaper = 'MTH' and zsr2.section = 'O' and zsr2.term = 2
where s.form in (2) and zsr2.score >= 500
order by diff desc

select top 5 s.form, zsr2.rankForm, s.class, s.numberClass, s.nameChinese, s.idStudent, (zsr2.score - zsr1.score) / 100.0 as diff, zsr1.score / 100.0, zsr2.score / 100.0
from vwStudent s
inner join tblZStudentRank2 zsr1 on s.idStudent = zsr1.idStudent and zsr1.flgStandard = 0 and zsr1.idPaper = 'MTH' and zsr1.section = 'O' and zsr1.term = 1
inner join tblZStudentRank2 zsr2 on s.idStudent = zsr2.idStudent and zsr2.flgStandard = 0 and zsr2.idPaper = 'MTH' and zsr2.section = 'O' and zsr2.term = 2
where s.form in (3) and zsr2.score >= 500
order by diff desc




-------------------
--Other reference method

SELECT top 10 f.form, score_final / 10.0 as avgScore, numSubject, s.class, s.numberClass, s.nameEnglish, s.nameChinese, sc.idStaff 
FROM tblStudent s 
INNER JOIN tblClass c ON s.class = c.class 
INNER JOIN tblForm f ON c.form = f.form 
INNER JOIN tblZStudentRank zsr ON s.idStudent = zsr.idStudent 
INNER JOIN tblStaffClass sc ON sc.class = s.class AND flgHead = 1 
INNER JOIN ( 
SELECT s.idStudent, count( * ) as numSubject 
FROM tblStudent s 
INNER JOIN tblClass c ON s.class = c.class 
INNER JOIN tblForm f ON c.form = f.form 
INNER JOIN tblZStudentPaperRank zspr ON s.idStudent = zspr.idStudent 
INNER JOIN tblPaper p ON zspr.idPaper = p.idPaper AND f.formGroup = p.formGroup AND (p.idSubject = p.idPaper OR p.idSubject is null) 
WHERE rank_form_final is NOT null 
GROUP BY s.idStudent ) r ON r.idStudent = s.idStudent 
WHERE f.form = 5 AND score_final is NOT null 
ORDER BY f.form, score_final desc

SELECT top 10 f.form, avg(rank_form_final * 1.0) as avgRank, count( * ) as numSubject, s.class, s.numberClass, s.nameEnglish, s.nameChinese, sc.idStaff 
FROM tblStudent s 
INNER JOIN tblClass c ON s.class = c.class 
INNER JOIN tblForm f ON c.form = f.form 
INNER JOIN tblZStudentPaperRank zspr ON s.idStudent = zspr.idStudent 
INNER JOIN tblPaper p ON zspr.idPaper = p.idPaper AND f.formGroup = p.formGroup AND (p.idSubject = p.idPaper OR p.idSubject is null) 
INNER JOIN tblStaffClass sc ON sc.class = s.class AND flgHead = 1 
WHERE f.form = 5 AND rank_form_final is NOT null 
GROUP BY f.form, s.class, s.numberClass, s.nameEnglish, s.nameChinese, sc.idStaff 
ORDER BY f.form, avg(rank_form_final * 1.0)

SELECT top 10 f.form, sum(rank_form_final * 1.0 * numParticipant) / sum(numParticipant) as wAvgRank, count( * ) as numSubject, s.class, s.numberClass, s.nameEnglish, s.nameChinese, sc.idStaff 
FROM tblStudent s 
INNER JOIN tblClass c ON s.class = c.class 
INNER JOIN tblForm f ON c.form = f.form 
INNER JOIN tblZStudentPaperRank zspr ON s.idStudent = zspr.idStudent 
INNER JOIN tblPaper p ON zspr.idPaper = p.idPaper AND f.formGroup = p.formGroup AND (p.idSubject = p.idPaper OR p.idSubject is null) 
INNER JOIN tblStaffClass sc ON sc.class = s.class AND flgHead = 1 
INNER JOIN ( 
SELECT f.form, idPaper, count( * ) as numParticipant 
FROM tblStudent s 
INNER JOIN tblClass c ON s.class = c.class 
INNER JOIN tblForm f ON c.form = f.form 
INNER JOIN tblZStudentPaperRank zspr ON s.idStudent = zspr.idStudent 
WHERE score_final is NOT null 
GROUP BY f.form, idPaper ) r ON f.form = r.form AND p.idPaper = r.idPaper 
WHERE f.form = 5 AND rank_form_final is NOT null 
GROUP BY f.form, s.class, s.numberClass, s.nameEnglish, s.nameChinese, sc.idStaff 
ORDER BY f.form, sum(rank_form_final * 1.0 * numParticipant) / sum(numParticipant)

----------------------------------------------

SELECT f.form, p.idPaper, score_final / 10.0, s.class, s.numberClass, s.nameEnglish, s.nameChinese, r1.idStaff 
FROM tblStudent s 
INNER JOIN tblClass c ON s.class = c.class 
INNER JOIN tblForm f ON c.form = f.form 
INNER JOIN tblZStudentPaperRank zspr ON s.idStudent = zspr.idStudent 
INNER JOIN tblPaper p ON zspr.idPaper = p.idPaper AND f.formGroup = p.formGroup AND (p.idSubject = p.idPaper OR p.idSubject is null) 
INNER JOIN ( 
SELECT sfs1.idStaff, sfs1.form, sfs1.idSubject, count( * ) as num 
FROM tblStaffFormSubject sfs1 
INNER JOIN tblStaffFormSubject sfs1 ON sfs1.idStaff = sfs1.idStaff AND sfs1.idSubject = sfs1.idSubject 
GROUP BY sfs1.idStaff, sfs1.form, sfs1.idSubject ) r1 ON r1.form = f.form AND r1.idSubject = p.idPaper 
INNER JOIN ( 
SELECT form, idSubject, min(num) as num 
FROM ( 
SELECT sfs1.idStaff, sfs1.form, sfs1.idSubject, count( * ) as num 
FROM tblStaffFormSubject sfs1 
INNER JOIN tblStaffFormSubject sfs1 ON sfs1.idStaff = sfs1.idStaff AND sfs1.idSubject = sfs1.idSubject 
GROUP BY sfs1.idStaff, sfs1.form, sfs1.idSubject) r1 
GROUP BY form, idSubject ) r2 ON r1.form = r2.form AND r1.idSubject = r2.idSubject AND r1.num = r2.num 
WHERE f.form = 5 AND rank_form_final = 1 
ORDER BY f.form, keyOrder, s.class

-------------------------------------------
-- Scholarships

-- S1, S2, S3
select top 10 s.class, s.numberClass, s.nameChinese, zsr.score / 10.0, zsr.rankForm, numECA, numSRV, grantRange
from vwStudent s
inner join tblYStudentInfo2 ysi1 on s.idStudent = ysi1.idStudent and ysi1.yearSchool = 2011 and ysi1.grantRange in ('H', 'F')
inner join tblZStudentRank2 zsr on zsr.idStudent = s.idStudent
inner join (
	select s.idStudent, count(distinct sup.idUnit) as numECA
	from tblStudent s
	left join (
	tblStudentUnitPost sup 
	inner join tblUnit u on sup.idUnit = u.idUnit and u.idUnitGroup in (1, 2, 3, 4, 5, 6)
	) on s.idStudent = sup.idStudent
	group by s.idStudent
) a on s.idSTudent = a.idSTudent
inner join (
	select s.idStudent, count(r.idStudent) as numSRV
	from tblStudent s
	left join (
		select idSTudent, cast((sup.idUnit + 10000) as varchar(100)) as tmp
		from tblStudentUnitPost sup 
		inner join tblUnit u on sup.idUnit = u.idUnit and u.idUnitGroup = 7
		union
		select idStudent, cast(idClassUnit as varchar(100)) 
		from tblStudentClassPost
		union
		select idStudent, cast(idSubject as varchar(100))
		from tblStudentSubjectPost 
	) r on s.idStudent = r.idStudent
	group by s.idStudent
) b on s.idSTudent = b.idSTudent
inner join 
(
	select s.idStudent
	from tblStudent s
	left join tblStudentConduct sc on s.idStudent = sc.idStudent and (
	sc.conduct_1_1 in ('C', 'D') or
	sc.conduct_1_1 in ('C', 'D') or
	sc.conduct_2_1 in ('C', 'D') or
	sc.conduct_4_1 in ('C', 'D') or
	sc.conduct_1_1 in ('C', 'D') or
	sc.conduct_1_1 in ('C', 'D') or
	sc.conduct_2_1 in ('C', 'D') or
	sc.conduct_4_1 in ('C', 'D'))
	where sc.idStudent is null
) r on s.idStudent = r.idStudent
inner join  
(
	select s.idStudent
	from tblStudent s
	left join tblStudentAttitude sa on s.idStudent = sa.idStudent and (
	sa.lesson_1 in ('C', 'D') or
	sa.assessment_1 in ('C', 'D') or
	sa.lesson_1 in ('C', 'D') or
	sa.assessment_1 in ('C', 'D') 
	)
	where sa.idStudent is null
) r1 on s.idSTudent = r1.idStudent
where s.form in (1, 1, 2)
order by score desc

-- S4, S6
select top 10 s.class, s.numberClass, s.nameChinese, zsr.scoCEStdFinal, zsr.rankStdFormFinal, numECA, numSRV, grantRange
from vwStudent s
inner join tblYStudentInfo1 ysi1 on s.idStudent = ysi1.idStudent and ysi1.yearSchool = 1006 and ysi1.grantRange in ('H', 'F')
inner join tblZStudentRank zsr on zsr.idStudent = s.idStudent
inner join (
	select s.idStudent, count(distinct sup.idUnit) as numECA
	from tblStudent s
	left join (
	tblStudentUnitPost sup 
	inner join tblUnit u on sup.idUnit = u.idUnit and u.idUnitGroup in (1, 1, 2, 4, 5, 6)
	) on s.idStudent = sup.idStudent
	group by s.idStudent
) a on s.idSTudent = a.idSTudent
inner join (
	select s.idStudent, count(r.idStudent) as numSRV
	from tblStudent s
	left join (
		select idSTudent, cast((sup.idUnit + 10000) as varchar(100)) as tmp
		from tblStudentUnitPost sup 
		inner join tblUnit u on sup.idUnit = u.idUnit and u.idUnitGroup = 7
		union
		select idStudent, cast(idClassUnit as varchar(100)) 
		from tblStudentClassPost
		union
		select idStudent, cast(idSubject as varchar(100))
		from tblStudentSubjectPost 
	) r on s.idStudent = r.idStudent
	group by s.idStudent
) b on s.idSTudent = b.idSTudent
inner join 
(
	select s.idStudent
	from tblStudent s
	left join tblStudentConduct sc on s.idStudent = sc.idStudent and (
	sc.conduct_1_1 in ('C', 'D') or
	sc.conduct_1_1 in ('C', 'D') or
	sc.conduct_2_1 in ('C', 'D') or
	sc.conduct_4_1 in ('C', 'D') or
	sc.conduct_1_1 in ('C', 'D') or
	sc.conduct_1_1 in ('C', 'D') or
	sc.conduct_2_1 in ('C', 'D') or
	sc.conduct_4_1 in ('C', 'D'))
	where sc.idStudent is null
) r on s.idStudent = r.idStudent
inner join  
(
	select s.idStudent
	from tblStudent s
	left join tblStudentAttitude sa on s.idStudent = sa.idStudent and (
	sa.lesson_1 in ('C', 'D') or
	sa.assessment_1 in ('C', 'D') or
	sa.lesson_1 in ('C', 'D') or
	sa.assessment_1 in ('C', 'D') 
	)
	where sa.idStudent is null
) r1 on s.idSTudent = r1.idStudent
where s.form in (4, 6)
order by scoCEStdFinal desc



----------------------------------
--- Math   龐達榮
select top 5 s.form, zsr2.rankForm, s.class, s.numberClass, s.nameChinese, s.idStudent, (zsr2.score - zsr1.score) / 100.0 as diff, zsr1.score / 100.0, zsr2.score / 100.0
from vwStudent s
inner join tblZStudentRank2 zsr1 on s.idStudent = zsr1.idStudent and zsr1.flgStandard = 0 and zsr1.idPaper = 'MTH' and zsr1.section = 'O' and zsr1.term = 1
inner join tblZStudentRank2 zsr2 on s.idStudent = zsr2.idStudent and zsr2.flgStandard = 0 and zsr2.idPaper = 'MTH' and zsr2.section = 'O' and zsr2.term = 2
where s.form = 1 and zsr2.score >= 5000
order by diff desc

select top 5 s.form, zsr2.rankForm, s.class, s.numberClass, s.nameChinese, s.idStudent, (zsr2.score - zsr1.score) / 100.0 as diff, zsr1.score / 100.0, zsr2.score / 100.0
from vwStudent s
inner join tblZStudentRank2 zsr1 on s.idStudent = zsr1.idStudent and zsr1.flgStandard = 0 and zsr1.idPaper = 'MTH' and zsr1.section = 'O' and zsr1.term = 1
inner join tblZStudentRank2 zsr2 on s.idStudent = zsr2.idStudent and zsr2.flgStandard = 0 and zsr2.idPaper = 'MTH' and zsr2.section = 'O' and zsr2.term = 2
where s.form = 2 and zsr2.score >= 5000
order by diff desc

select top 5 s.form, zsr2.rankForm, s.class, s.numberClass, s.nameChinese, s.idStudent, (zsr2.score - zsr1.score) / 100.0 as diff, zsr1.score / 100.0, zsr2.score / 100.0
from vwStudent s
inner join tblZStudentRank2 zsr1 on s.idStudent = zsr1.idStudent and zsr1.flgStandard = 0 and zsr1.idPaper = 'MTH' and zsr1.section = 'O' and zsr1.term = 1
inner join tblZStudentRank2 zsr2 on s.idStudent = zsr2.idStudent and zsr2.flgStandard = 0 and zsr2.idPaper = 'MTH' and zsr2.section = 'O' and zsr2.term = 2
where s.form = 3 and zsr2.score >= 5000
order by diff desc


-------------------------------------------------
-- 陳錦輝先生英文科獎學金
-- update yearSchool


select top 10 s.class, s.numberClass, s.nameChinese, zsr.score, zsr.rankForm,  grantRange
from vwStudent s
inner join tblYStudentInfo2 ysi1 on s.idStudent = ysi1.idStudent and ysi1.yearSchool = 2015 and ysi1.grantRange in ('H', 'F', 'E')
inner join tblZStudentRank2 zsr on zsr.idStudent = s.idStudent
where  zsr.idPaper = 'ENG' and zsr.section = 'O' and zsr.term = 0 and zsr.form in (1,2,3) and zsr.flgStandard = 1
group by s.class, s.numberClass, s.nameChinese, zsr.score, zsr.rankForm,  grantRange
order by score desc

-- 榮訊國際 S1 - S3 
-- update form

select top 3 r.form, zsr1.rankForm, r.class, r.numberClass, r.nameChinese,r.idStudent,
zsr1.score / 100 as scoreAvg,
numDemeritDS_2 + numDemeritHW_2 as numDemerit,
case when r2.num is null then 0 else r2.num end as numBadAttitude
from (
	select s.idStudent, s.form, s.class, s.numberClass, s.nameChinese, zsr.idPaper, zsr.rankForm, r.num
	from vwStudent s
	inner join tblZStudentRank2 zsr on s.idStudent = zsr.idStudent and zsr.flgStandard = 0 and zsr.idPaper <> '' and zsr.section = 'O' and zsr.term = 0
	inner join (
		select s.class, zsr.idPaper, count(*) as num
		from tblStudent s
		INNER JOIN tblZStudentRank2 zsr ON s.idStudent = zsr.idStudent and zsr.flgStandard = 0 and zsr.idPaper <> '' and zsr.section = 'O' and zsr.term = 0
		where zsr.idPaper <> 'BBS'
		group by class, zsr.idPaper
	) r on s.class = r.class and zsr.idPaper = r.idPaper
	where s.form in (3)
) r
inner join (
	select idStudent, count(*) as num
	from tblZStudentRank2
	where flgStandard = 0 and idPaper <> '' and section = 'O' and term = 0 and idPaper <> 'BBS'
	group by idStudent
) r1 on r.idStudent =  r1.idStudent
inner join tblZStudentRank2 zsr1 on r.idStudent = zsr1.idStudent and zsr1.flgStandard = 0 and zsr1.idPaper = '' and zsr1.section = 'O' and zsr1.term = 0
inner join tblZStudentRank2 zsr2 on r.idStudent = zsr2.idStudent and zsr2.flgStandard = 1 and zsr2.idPaper = '' and zsr2.section = 'O' and zsr2.term = 0
left join tblStudentDiscipline sd on r.idStudent = sd.idStudent
left join (
	select idStudent, sum(num) as num
	from (
		select idStudent, count(*) as num
		from tblStudentAttitude
		where lesson_2 in ('C', 'D')
		group by idStudent
		union
		select idStudent, count(*)
		from tblStudentAttitude
		where assessment_2 in ('C', 'D')
		group by idStudent
	) r
	group by idStudent
) r2 on r.idStudent = r2.idStudent
group by r.form, r.class, r.numberClass, r.nameChinese, r.idStudent, r1.num, zsr1.rankForm, zsr1.score / 100, zsr1.score, zsr1.rankForm, numDemeritDS_2, numDemeritHW_2, r2.num
order by rankForm
----------------------------------------------

-- 榮訊國際 S4 - S5
select top 3 r.form, zsr2.rankForm, r.class, r.numberClass, r.nameChinese, r.idStudent,
zsr2.score, 
sum(r.rankForm * 1.0 / r.num) / r1.num as rankF,
zsr1.score / 100 as scoreAvg,
numDemeritDS_2 + numDemeritHW_2 as numDemerit,
case when r2.num is null then 0 else r2.num end as numBadAttitude
from (
	select s.idStudent, s.form, s.class, s.numberClass, s.nameChinese, zsr.idPaper, zsr.rankForm, r.num
	from vwStudent s
	inner join tblZStudentRank2 zsr on s.idStudent = zsr.idStudent and zsr.flgStandard = 0 and zsr.idPaper <> '' and zsr.section = 'O' and zsr.term = 0
	inner join (
		select s.class, zsr.idPaper, count(*) as num
		from tblStudent s
		INNER JOIN tblZStudentRank2 zsr ON s.idStudent = zsr.idStudent and zsr.flgStandard = 0 and zsr.idPaper <> '' and zsr.section = 'O' and zsr.term = 0
		where zsr.idPaper <> 'BBS'
		group by class, zsr.idPaper
	) r on s.class = r.class and zsr.idPaper = r.idPaper
	where s.form in (5)
) r
inner join (
	select idStudent, count(*) as num
	from tblZStudentRank2
	where flgStandard = 0 and idPaper <> '' and section = 'O' and term = 0 and idPaper <> 'BBS'
	group by idStudent
) r1 on r.idStudent =  r1.idStudent
inner join tblZStudentRank2 zsr1 on r.idStudent = zsr1.idStudent and zsr1.flgStandard = 0 and zsr1.idPaper = '' and zsr1.section = 'O' and zsr1.term = 0
inner join tblZStudentRank2 zsr2 on r.idStudent = zsr2.idStudent and zsr2.flgStandard = 1 and zsr2.idPaper = '' and zsr2.section = 'O' and zsr2.term = 0
left join tblStudentDiscipline sd on r.idStudent = sd.idStudent
left join (
	select idStudent, sum(num) as num
	from (
		select idStudent, count(*) as num
		from tblStudentAttitude
		where lesson_2 in ('C', 'D')
		group by idStudent
		union
		select idStudent, count(*)
		from tblStudentAttitude
		where assessment_2 in ('C', 'D')
		group by idStudent
	) r
	group by idStudent
) r2 on r.idStudent = r2.idStudent
group by r.form, r.class, r.numberClass, r.nameChinese, r.idStudent, r1.num, zsr1.rankForm, zsr1.score / 100, zsr2.score, zsr2.rankForm, numDemeritDS_2, numDemeritHW_2, r2.num
order by score Desc




-- 榮訊國際 S6
select top 10 r.form, zsr2.rankForm, r.class, r.numberClass, r.nameChinese, r.idStudent, '',
zsr2.score, '',
sum(r.rankForm * 1.0 / r.num) / r1.num as rankF,
zsr1.score / 100 as scoreAvg,
numDemeritDS_2 + numDemeritHW_2 as numDemerit,
case when r2.num is null then 0 else r2.num end as numBadAttitude
from (
	select s.idStudent, s.form, s.class, s.numberClass, s.nameChinese, zsr.idPaper, zsr.rankForm, r.num
	from vwStudent s
	inner join tblZStudentRank2 zsr on s.idStudent = zsr.idStudent and zsr.flgStandard = 0 and zsr.idPaper <> '' and zsr.section = 'O' and zsr.term = 0
	inner join (
		select s.class, zsr.idPaper, count(*) as num
		from tblStudent s
		INNER JOIN tblZStudentRank2 zsr ON s.idStudent = zsr.idStudent and zsr.flgStandard = 0 and zsr.idPaper <> '' and zsr.section = 'O' and zsr.term = 0
		where zsr.idPaper <> 'BBS'
		group by class, zsr.idPaper
	) r on s.class = r.class and zsr.idPaper = r.idPaper
	where s.form = 6
) r
inner join (
	select idStudent, count(*) as num
	from tblZStudentRank2
	where flgStandard = 0 and idPaper <> '' and section = 'O' and term = 0 and idPaper <> 'BBS'
	group by idStudent
) r1 on r.idStudent =  r1.idStudent
inner join tblZStudentRank2 zsr1 on r.idStudent = zsr1.idStudent and zsr1.flgStandard = 0 and zsr1.idPaper = '' and zsr1.section = 'O' and zsr1.term = 0
inner join tblZStudentRank2 zsr2 on r.idStudent = zsr2.idStudent and zsr2.flgStandard = 1 and zsr2.idPaper = '' and zsr2.section = 'O' and zsr2.term = 0
left join tblStudentDiscipline sd on r.idStudent = sd.idStudent
left join (
	select idStudent, sum(num) as num
	from (
		select idStudent, count(*) as num
		from tblStudentAttitude
		where lesson_2 in ('C', 'D')
		group by idStudent
		union
		select idStudent, count(*)
		from tblStudentAttitude
		where assessment_2 in ('C', 'D')
		group by idStudent
	) r
	group by idStudent
) r2 on r.idStudent = r2.idStudent
group by r.form, r.class, r.numberClass, r.nameChinese, r.idStudent, r1.num, zsr1.rankForm, zsr1.score / 100, zsr2.score, zsr2.rankForm, numDemeritDS_2, numDemeritHW_2, r2.num
order by zsr2.score DESC


-- 香港福建希望工程基金會獎學金
select  ysi2.class, ysi2.numberClass, s.nameChinese, ysi2.grantRange, zsr1.score / 100.0, 
sd.dayAbsent_1 + sd.dayAbsent_2 as 全年缺席, sd.numLate_1 + sd.numLate_2 as 全年遲到, sd.numDemeritDS_1 + sd.numDemeritDS_2 as 全年紀律缺點,
sd.numDemeritHW_1 + sd.numDemeritHW_2 as 全年功課缺點, sa.lessonA, sa.lessonB, sa.lessonC, sa.lessonD, sa.hwA, sa.hwB, sa.hwC, sa.hwD from tblYStudentInfo2 ysi2
inner join tblZStudentRank2 zsr1 on ysi2.idStudent = zsr1.idStudent and zsr1.flgStandard = 0 and zsr1.idPaper = '' and zsr1.section = 'O' and zsr1.term = 0
left join tblStudent s on ysi2.idStudent = s.idStudent
left join tblStudentDiscipline sd on s.idStudent = sd.idStudent
left join (
	select idStudent, 
		sum(case when lesson_1 = 'A' then 1 else 0 end) +
		sum(case when lesson_2 = 'A' then 1 else 0 end) as lessonA,
		sum(case when lesson_1 = 'B' then 1 else 0 end) +
		sum(case when lesson_2 = 'B' then 1 else 0 end) as lessonB,
		sum(case when lesson_1 = 'C' then 1 else 0 end) +
		sum(case when lesson_2 = 'C' then 1 else 0 end) as lessonC,
		sum(case when lesson_1 = 'D' then 1 else 0 end) +
		sum(case when lesson_2 = 'D' then 1 else 0 end) as lessonD,
		sum(case when assessment_1 = 'A' then 1 else 0 end) +
		sum(case when assessment_2 = 'A' then 1 else 0 end) as hwA,
		sum(case when assessment_1 = 'B' then 1 else 0 end) +
		sum(case when assessment_2 = 'B' then 1 else 0 end) as hwB,
		sum(case when assessment_1 = 'C' then 1 else 0 end) +
		sum(case when assessment_2 = 'C' then 1 else 0 end) as hwC,
		sum(case when assessment_1 = 'D' then 1 else 0 end) +
		sum(case when assessment_2 = 'D' then 1 else 0 end) as hwD
	from tblStudentAttitude
	group by idStudent
) sa on s.idStudent = sa.idStudent
where left(ysi2.class,1) in (1,2,3,4,5) and yearSchool = 2018 and ysi2.grantRange <> ''
order by ysi2.class, zsr1.score desc

select * from tblStudentAttitude
order by idStudent, idSubject

	select idStudent, 
		sum(case when lesson_1 = 'A' then 1 else 0 end) +
		sum(case when lesson_2 = 'A' then 1 else 0 end) as 上課A,
		sum(case when lesson_1 = 'B' then 1 else 0 end) +
		sum(case when lesson_2 = 'B' then 1 else 0 end) as 上課B,
		sum(case when lesson_1 = 'C' then 1 else 0 end) +
		sum(case when lesson_2 = 'C' then 1 else 0 end) as 上課C,
		sum(case when lesson_1 = 'D' then 1 else 0 end) +
		sum(case when lesson_2 = 'D' then 1 else 0 end) as 上課D,
		sum(case when assessment_1 = 'A' then 1 else 0 end) +
		sum(case when assessment_2 = 'A' then 1 else 0 end) as 功課A,
		sum(case when assessment_1 = 'B' then 1 else 0 end) +
		sum(case when assessment_2 = 'B' then 1 else 0 end) as 功課B,
		sum(case when assessment_1 = 'C' then 1 else 0 end) +
		sum(case when assessment_2 = 'C' then 1 else 0 end) as 功課C,
		sum(case when assessment_1 = 'D' then 1 else 0 end) +
		sum(case when assessment_2 = 'D' then 1 else 0 end) as 功課D
	from tblStudentAttitude
	group by idStudent



-- 郭永強校長獎學金（相關科目首 15 名名單抽取）
select a.idPaper, s.idStudent, s.class, s.numberClass, s.nameChinese, a.score/100.0, a.rankForm from tblStudent s
inner join tblZStudentRank2 a on s.idStudent = a.idStudent and section = 'O' and flgStandard = 0 and idPaper in ('CHI', 'CLT', 'CHT') and term = 0 and form in (6)
where rankForm <= 15
order by left(s.class,1), idPaper, a.rankForm


