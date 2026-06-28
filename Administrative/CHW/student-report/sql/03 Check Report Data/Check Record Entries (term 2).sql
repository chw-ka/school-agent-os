-- Check Possible Weight Mistakes According to Weights
SELECT *
from tblFormPaperWeight 
WHERE weight_test_2 + weight_regular_2 + weight_exam_2 not in (0, 100)

-- Check Full Scores According to Weights
SELECT fpw.form, fpw.idPaper, weight_test_2, weight_regular_2, weight_exam_2, score_test_2, score_regular_2, score_exam_2
from tblFormPaperWeight fpw 
inner join tblFormPaperScore sps on sps.form = fpw.form and sps.idPaper = fpw.idPaper 
WHERE fpw.form in (1,2,3,4,5)
and (
	(weight_test_2 > 0 and (score_test_2 is null or score_test_2 = 0)) or
	(weight_regular_2 > 0 and (score_regular_2 is null or score_regular_2 = 0)) or
	(weight_exam_2 > 0 and (score_exam_2 is null or score_exam_2 = 0))
)
order by fpw.form, fpw.idPaper

-- Check Students Who Have NO Scores (0 or null)
SELECT distinct ss.idStaff, sp.class as auxiliaryClass, sps.idPaper, s.idStudent, s.class, s.numberClass, s.nameChinese, s.gender, sps.score_test_2, sps.score_regular_2, sps.score_exam_2
FROM tblStudent s 
INNER JOIN tblStudentPaperScore sps ON s.idStudent = sps.idStudent 
INNER JOIN vwStudentPaper sp on sps.idStudent = sp.idStudent AND sps.idPaper = sp.idPaper
INNER JOIN tblFormPaperScore fps ON sp.form = fps.form AND sp.idPaper = fps.idPaper 
INNER JOIN tblPaper p ON sp.idPaper = sps.idPaper AND p.formGroup = sp.formGroup 
INNER JOIN vwStaffSubject ss ON sp.idSubject = ss.idSubject AND sp.class = ss.class AND ss.flgTeach = 1
WHERE ((fps.score_test_2 is NOT null AND (sps.score_test_2 = 0 OR sps.score_test_2 is null)) OR (fps.score_regular_2 is NOT null AND (sps.score_regular_2 = 0 OR sps.score_regular_2 is null)) OR (fps.score_exam_2 is NOT null AND (sps.score_exam_2 = 0 OR sps.score_exam_2 is null)) )
AND sp.form in (1,2,3,4,5) AND sp.flgTerm2 = 1 and sps.flgIgnore_2 = 0 and sps.flgAbsent_2 = 0
--ORDER BY ss.idStaff, sp.class, sps.idPaper, s.class, s.numberClass
union
select distinct ss.idStaff, sp.class as auxiliaryClass, sps.idPaper, s.idStudent, s.class, s.numberClass, s.nameChinese, s.gender, NULL, NULL, sps.grade_exam_2 from tblStudent s
INNER JOIN tblStudentPaperScore sps ON s.idStudent = sps.idStudent
INNER JOIN vwStudentPaper sp on sps.idStudent = sp.idStudent AND sps.idPaper = sp.idPaper
INNER JOIN tblPaper p ON sp.idPaper = sps.idPaper AND p.formGroup = sp.formGroup 
INNER JOIN vwStaffSubject ss ON sp.idSubject = ss.idSubject AND sp.class = ss.class AND ss.flgTeach = 1
where sps.idPaper in ('PED','MUS') and sps.grade_exam_2 is NULL and sp.form in (1,2,3,4,5) and sp.flgTerm2 = 1 and sps.flgIgnore_2 = 0 and sps.flgAbsent_2 = 0
order by ss.idStaff, sp.class, sps.idPaper, s.class, s.numberClass

-- Check Students Who Have Scores Larger Than Full Marks
SELECT distinct ss.idStaff, sp.class as auxiliaryClass, sps.idPaper, s.idStudent, s.class, s.numberClass, s.nameChinese, s.gender, sps.score_test_2, fps.score_test_2 as form_score_test_2, sps.score_regular_2, fps.score_regular_2 as form_score_regular_2, sps.score_exam_2, fps.score_exam_2 as form_score_exam_2
FROM tblStudent s 
INNER JOIN tblStudentPaperScore sps ON s.idStudent = sps.idStudent 
INNER JOIN vwStudentPaper sp on sps.idStudent = sp.idStudent AND sps.idPaper = sp.idPaper
INNER JOIN tblFormPaperScore fps ON sp.form = fps.form AND sp.idPaper = fps.idPaper 
INNER JOIN tblPaper p ON sp.idPaper = sps.idPaper AND p.formGroup = sp.formGroup 
INNER JOIN vwStaffSubject ss ON sp.idSubject = ss.idSubject AND sp.class = ss.class AND ss.flgTeach = 1
WHERE ((fps.score_test_2 is NOT null AND (sps.score_test_2 > fps.score_test_2)) OR (fps.score_regular_2 is NOT null AND (sps.score_regular_2 > fps.score_regular_2)) OR (fps.score_exam_2 is NOT null AND (sps.score_exam_2 > fps.score_exam_2)) )
AND sp.form in (1,2,3,4,5) AND sp.flgTerm1 = 1 and sps.flgIgnore_2 = 0
ORDER BY ss.idStaff, sp.class, sps.idPaper, s.class, s.numberClass

-- Check Students Who Have NO Attitudes
SELECT ss2.idStaff, ss.class as auxiliaryClass, ss.idSubject, s.idStudent, s.class, s.numberClass, s.nameChinese, lesson_2, assessment_2
FROM vwStudent s 
INNER JOIN vwStudentSubject ss on s.idStudent = ss.idStudent
INNER JOIN tblStaffSubject ss2 ON ss.idSubject = ss2.idSubject AND ss2.class = s.class 
LEFT JOIN tblStudentAttitude sa on s.idStudent = sa.idStudent AND sa.idSubject = ss.idSubject
WHERE s.form in (1,2,3,4,5) and s.flgTerm1 = 1 and ss.flgTerm2 = 1 and 
	(
		lesson_2 is null 
		OR 
		(
			assessment_2 is null 
			and 
			(
				(
					s.form < 6 and ss.idSubject not in ('PED', 'MUS', 'PBL')
				) 
				or 
				(
					s.form > 5 and ss.idSubject not in ('PED', 'MUS', 'PBL', 'BBS')
				)
			)
		)
		OR 
		sa.idStudent is null
	) 
ORDER BY ss2.idStaff, ss.class, ss.idSubject, s.class, s.numberClass

-- Check Possible Weight Mistakes According to Students' Scores
SELECT ss.idStaff, sp.class as auxiliaryClass, sp.idPaper, s.idStudent, s.class, s.numberClass, s.nameChinese, s.gender, sp.idPaper, weight_test_2, weight_regular_2, weight_exam_2, score_test_2, score_regular_2, score_exam_2
from tblStudent s
inner join vwStudentPaper sp on s.idStudent = sp.idStudent and sp.flgTerm1 = 1
inner join tblFormPaperWeight fpw on sp.form = fpw.form and sp.idPaper = fpw.idPaper 
inner join tblStaffSubject ss on sp.class = ss.class and ss.idSubject = sp.idSubject 
left join tblStudentPaperScore sps on sps.idStudent = s.idStudent and sps.idPaper = sp.idPaper
WHERE sp.form in (1, 2, 3, 4, 5)
and (
--	(weight_test_2 = 0 and weight_regular_2 = 0 and weight_exam_2 = 0 and grade_exam_2 is null) or
	(weight_test_2 > 0 and score_test_2 is null) or
	(weight_regular_2 > 0 and score_regular_2 is null) or
	(weight_exam_2 > 0 and score_exam_2 is null)
) and flgIgnore_2 = 0
order by ss.idStaff, sp.class, sp.idPaper, s.class, s.numberClass

-- Check Conducts
select s.idStudent, s.class, s.numberClass, s.nameChinese, 
sd.numDemeritDS_2 as numDemeritDP_2, 
case when numBadLesson is null then 0 else numBadLesson end as numBadLesson, 
case when numBadAssessment is null then 0 else numBadAssessment end as numBadAssessment, 
sc.conduct_1_2, numDemeritHW_2, flgHW_2, sc.conduct_3_2, 
sc2.idStaff
from vwStudent s
inner join tblStudentDiscipline sd on s.idStudent = sd.idStudent
inner join tblStudentConduct sc on s.idStudent = sc.idStudent
inner join tblStaffClass sc2 on s.class = sc2.class and flgHead = 1
left join (
	select idStudent, count(*) as numBadLesson
	from tblStudentAttitude
	where lesson_2 in ('C', 'D')
	group by idStudent
) r on r.idStudent = s.idStudent
left join (
	select idStudent, count(*) as numBadAssessment
	from tblStudentAttitude
	where assessment_2 in ('C', 'D')
	group by idStudent
) r2 on r2.idStudent = s.idStudent
where s.form in (1, 2, 3, 4, 5) and (
	(numDemeritDS_2 between 1 and 8 and conduct_1_2 in ('A', 'B')) or 
	(numDemeritDS_2 >= 9 and conduct_1_2 in ('A', 'B', 'C')) or 
	(numBadLesson > 0 and conduct_1_2 in ('A')) or
	(numDemeritHW_2 > 0 and conduct_3_2 in ('A', 'B')) or
	(flgHW_2 = 1 and conduct_3_2 in ('A')) or 
	(numBadAssessment > 0 and conduct_3_2 in ('A'))
)
order by s.class, s.numberClass
