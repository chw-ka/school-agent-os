-- 各科總分連術科合格 >= 50, C 或以上
-- 平均分 >= 60
-- 操行、上課表現及功課考勤 C 或以上

select s.idStudent, s.class, s.numberClass, s.nameChinese, round(zsr2.score / 100,1) as average, zsr2.rankClass,
       x.countA1, x.countA2, x.countB1, x.countB2, x.countC1, x.countC2, x.countD1, x.countD2, 
       subjectFail.subjectFailCount, cSubjectFail.cSubjectFailCount, conductFail.numConductFail
from tblZStudentRank2 zsr2
inner join tblStudent s on zsr2.idStudent = s.idStudent
left join
(select * from 
(select a1.idStudent as idStudentA, 'A' as gradeA,
(select count(*) from tblStudentAttitude
where lesson_2 = 'A' and idStudent = a1.idStudent
group by idStudent) as countA1,
(select count(*) from tblStudentAttitude
where assessment_2 = 'A' and idStudent = a1.idStudent
group by idStudent) as countA2
from tblStudentAttitude a1
where a1.idStudent in (select idStudent from tblStudent where left(class,1) = 6)
group by idStudent) a
left join 
(select b1.idStudent as idStudentB, 'B' as gradeB,
(select count(*) from tblStudentAttitude
where lesson_2 = 'B' and idStudent = b1.idStudent
group by idStudent) as countB1,
(select count(*) from tblStudentAttitude
where assessment_2 = 'B' and idStudent = b1.idStudent
group by idStudent) as countB2
from tblStudentAttitude b1
where b1.idStudent in (select idStudent from tblStudent where left(class,1) = 6)
group by idStudent) b on a.idStudentA = b.idStudentB
left join
(select c1.idStudent as idStudentC, 'C' as gradeC,
(select count(*) from tblStudentAttitude
where lesson_2 = 'C' and idStudent = c1.idStudent
group by idStudent) as countC1,
(select count(*) from tblStudentAttitude
where assessment_2 = 'C' and idStudent = c1.idStudent
group by idStudent) as countC2
from tblStudentAttitude c1
where c1.idStudent in (select idStudent from tblStudent where left(class,1) = 6)
group by idStudent) c on a.idStudentA = c.idStudentC
left join
(select d1.idStudent as idStudentD, 'D' as gradeD,
(select count(*) from tblStudentAttitude
where lesson_2 = 'D' and idStudent = d1.idStudent
group by idStudent) as countD1,
(select count(*) from tblStudentAttitude
where assessment_2 = 'D' and idStudent = d1.idStudent
group by idStudent) as countD2
from tblStudentAttitude d1
where d1.idStudent in (select idStudent from tblStudent where left(class,1) = 6)
group by idStudent) d on a.idStudentA = d.idStudentD) x on zsr2.idStudent = x.idStudentA
left join
(select idStudent, count(*) as subjectFailCount from tblZStudentRank2
where section = 'O' and flgStandard = 0 and term = 2 and round(score/100,0) < 50 and idPaper <> ''
group by idStudent) subjectFail on zsr2.idStudent = subjectFail.idStudent
left join
(select idStudent, count(*) as cSubjectFailCount from tblStudentPaperScore
where idStudent in (select idStudent from tblStudent where left(class,1) = 6) and
	  grade_exam_2 <> '' and grade_exam_2 = 'D'
group by idStudent) cSubjectFail on zsr2.idStudent = cSubjectFail.idStudent
left join 
(select sc.idStudent, 
((select count(*) from tblStudentConduct sc1 where sc1.idStudent = sc.idStudent and conduct_1_2 in ('C+', 'C', 'C-', 'D')) +
(select count(*) from tblStudentConduct sc1 where sc1.idStudent = sc.idStudent and conduct_2_2 in ('C+', 'C', 'C-', 'D')) +
(select count(*) from tblStudentConduct sc1 where sc1.idStudent = sc.idStudent and conduct_3_2 in ('C+', 'C', 'C-', 'D')) +
(select count(*) from tblStudentConduct sc1 where sc1.idStudent = sc.idStudent and conduct_4_2 in ('C+', 'C', 'C-', 'D'))) as numConductFail
from tblStudentConduct sc
) conductFail on zsr2.idStudent = conductFail.idStudent
where zsr2.term = 2 and zsr2.flgStandard = 0 and zsr2.idPaper = '' and zsr2.section = 'O' and 
       round(score/100, 1) >= 60 and left(class,1) = 6 and x.countD1 is NULL and x.countD2 is NULL and subjectFail.subjectFailCount is Null
order by s.class, s.numberClass

 
