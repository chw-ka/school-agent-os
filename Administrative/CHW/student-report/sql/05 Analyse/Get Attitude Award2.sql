select s.form, zspr.idPaper, 
avg(score_final / 10.0)  as mean,
sum (case when score_final >= 495 then 1.0 else 0.0 end) / r.num as numPass
from vwStudent s
inner join tblZStudentPaperRank zspr on s.idStudent = zspr.idStudent
inner join (
select s.form, zspr.idPaper, count(*) as num
from vwStudent s
inner join tblZStudentPaperRank zspr on s.idStudent = zspr.idStudent
where zspr.score_final is not null and zspr.idPaper in ('CHI', 'CLT', 'PTH')
group by s.form, zspr.idPaper
) r  on s.form = r.form and zspr.idPaper = r.idPaper
group by s.form, zspr.idPaper, r.num
order by zspr.idPaper, s.form

select s.class, zspr.idPaper, 
avg(score_final / 10.0)  as mean,
sum (case when score_final >= 495 then 1.0 else 0.0 end) / r.num as numPass
from vwStudent s
inner join tblZStudentPaperRank zspr on s.idStudent = zspr.idStudent
inner join (
select s.class, zspr.idPaper, count(*) as num
from vwStudent s
inner join tblZStudentPaperRank zspr on s.idStudent = zspr.idStudent
where zspr.score_final is not null and zspr.idPaper in ('CHI', 'CLT', 'PTH')
group by s.class, zspr.idPaper
) r  on s.class = r.class and zspr.idPaper = r.idPaper
group by s.class, zspr.idPaper, r.num
order by zspr.idPaper, s.class