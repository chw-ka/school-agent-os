-- Check Possible Weight Mistakes According to Weights
SELECT *
from tblFormPaperWeight 
WHERE weight_test_1 + weight_regular_1 + weight_exam_1 not in (0, 100)

-- Check Full Scores According to Weights
SELECT fpw.form, fpw.idPaper, weight_test_1, weight_regular_1, weight_exam_1, score_test_1, score_regular_1, score_exam_1
from tblFormPaperWeight fpw 
inner join tblFormPaperScore sps on sps.form = fpw.form and sps.idPaper = fpw.idPaper 
WHERE fpw.form in (1, 2, 3, 4, 5, 6)
and (
	(weight_test_1 > 0 and (score_test_1 is null or score_test_1 = 0)) or
	(weight_regular_1 > 0 and (score_regular_1 is null or score_regular_1 = 0)) or
	(weight_exam_1 > 0 and (score_exam_1 is null or score_exam_1 = 0) and sps.idPaper not in ('ENG', 'CHI'))
)
order by fpw.form, fpw.idPaper

-- Check Students Who Have NO Scores (0 or null)
SELECT ss.idStaff, ss2.class as auxiliaryClass, sps.idPaper, s.idStudent, s.class, s.numberClass, s.nameChinese, s.gender, sps.score_regular_1, sps.score_exam_1
FROM tblStudent s 
INNER JOIN vwStudentSubject ss2 on s.idStudent = ss2.idStudent
INNER JOIN vwStaffSubject ss ON ss.idSubject = ss2.idSubject AND ss.class = ss2.class AND ss.flgTeach = 1
INNER JOIN tblPaper p ON (ss.idSubject = p.idPaper or ss.idSubject = p.idSubject) AND p.formGroup = ss.formGroup 
INNER JOIN tblFormPaperScore fps ON ss.formGroup = fps.form AND p.idPaper = fps.idPaper 
LEFT JOIN tblStudentPaperScore sps on sps.idStudent = ss2.idStudent AND sps.idPaper = p.idPaper
WHERE (
	(fps.score_regular_1 is NOT null AND (sps.score_regular_1 = 0 OR sps.score_regular_1 is null)) OR 
	(fps.score_exam_1 is NOT null AND (sps.score_exam_1 = 0 OR sps.score_exam_1 is null) and (sps.flgAbsent_1 is null or sps.flgAbsent_1 = 0) )
) AND ss2.form in (1, 2, 3, 4, 5) AND ss2.flgTerm1 = 1 and (sps.flgIgnore_1 is null or sps.flgIgnore_1 = 0) -- and not s.idStudent in (24103, 23101, 23080) -- 處理 25-26 Term1 長缺學生
ORDER BY ss.idStaff, ss2.class, p.keyOrder, s.class, s.numberClass

-- Exempt but have scores
SELECT ss.idStaff, ss2.class as auxiliaryClass, sps.idPaper, s.idStudent, s.class, s.numberClass, s.nameChinese, s.gender, sps.score_exam_1, sps.flgIgnore_1, sps.flgAbsent_1
FROM tblStudent s 
INNER JOIN vwStudentSubject ss2 on s.idStudent = ss2.idStudent
INNER JOIN vwStaffSubject ss ON ss.idSubject = ss2.idSubject AND ss.class = ss2.class AND ss.flgTeach = 1
INNER JOIN tblPaper p ON (ss.idSubject = p.idPaper or ss.idSubject = p.idSubject) AND p.formGroup = ss.formGroup 
INNER JOIN tblFormPaperScore fps ON ss.formGroup = fps.form AND p.idPaper = fps.idPaper 
LEFT JOIN tblStudentPaperScore sps on sps.idStudent = ss2.idStudent AND sps.idPaper = p.idPaper
WHERE (
	(sps.score_exam_1 <> 0) AND (sps.flgAbsent_1 = 1 or sps.flgIgnore_1 = 1)
) AND ss2.form in (1, 2, 3, 4, 5) AND ss2.flgTerm1 = 1 
ORDER BY ss.idStaff, ss2.class, p.keyOrder, s.class, s.numberClass


-- Check Students Who Have Scores Larger Than Full Marks
SELECT distinct ss.idStaff, sp.class as auxiliaryClass, sps.idPaper, s.idStudent, s.class, s.numberClass, s.nameChinese, s.gender, sps.score_test_1, fps.score_test_1 as form_score_test_1, sps.score_regular_1, fps.score_regular_1 as form_score_regular_1, sps.score_exam_1, fps.score_exam_1 as form_score_exam_1
FROM tblStudent s 
INNER JOIN tblStudentPaperScore sps ON s.idStudent = sps.idStudent 
INNER JOIN vwStudentPaper sp on sps.idStudent = sp.idStudent AND sps.idPaper = sp.idPaper
INNER JOIN tblFormPaperScore fps ON sp.form = fps.form AND sp.idPaper = fps.idPaper 
INNER JOIN tblPaper p ON sp.idPaper = sps.idPaper AND p.formGroup = sp.formGroup 
INNER JOIN vwStaffSubject ss ON sp.idSubject = ss.idSubject AND sp.class = ss.class AND ss.flgTeach = 1
WHERE ((fps.score_test_1 is NOT null AND (sps.score_test_1 > fps.score_test_1)) OR (fps.score_regular_1 is NOT null AND (sps.score_regular_1 > fps.score_regular_1)) OR (fps.score_exam_1 is NOT null AND (sps.score_exam_1 > fps.score_exam_1)) )
AND sp.form in (1, 2, 3, 4, 5) AND sp.flgTerm1 = 1 and sps.flgIgnore_1 = 0
ORDER BY ss.idStaff, sp.class, sps.idPaper, s.class, s.numberClass

-- Check Students Who Have NO Attitudes
SELECT ss2.idStaff, ss.class as auxiliaryClass, ss.idSubject, s.idStudent, s.class, s.numberClass, s.nameChinese, lesson_1, assessment_1
FROM vwStudent s 
INNER JOIN vwStudentSubject ss on s.idStudent = ss.idStudent
INNER JOIN tblStaffSubject ss2 ON ss.idSubject = ss2.idSubject AND ss2.class = s.class 
LEFT JOIN tblStudentAttitude sa on s.idStudent = sa.idStudent AND sa.idSubject = ss.idSubject
WHERE s.form in (1, 2, 3, 4, 5) and s.flgTerm1 = 1 and ss.flgTerm1 = 1 and 
	(
		lesson_1 is null 
		OR 
		(
			assessment_1 is null 
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


-- Version 2 (Edited by CM at 03/02/2024)
select b.idStaff, s.idStudent, s.class, s.numberClass, s.nameChinese, a.idSubject, a.lesson_1, a.assessment_1 from tblStudentAttitude a
left join tblStudent s on s.idStudent = a.idStudent
left join tblStaffSubject b on s.class = b.class and a.idSubject = b.idSubject
where a.idStudent in (select idStudent from tblStudent where left(class,1) in (1,2,3,4,5)) and (a.lesson_1 is NULL or a.assessment_1 is NULL) and not (a.idSubject in ('MUS', 'PED') and a.assessment_1 is NULL) 
order by b.idStaff, a.idSubject


-- Check Possible Weight Mistakes According to Students' Scores
SELECT ss.idStaff, sp.class as auxiliaryClass, sp.idPaper, s.idStudent, s.class, s.numberClass, s.nameChinese, s.gender, sp.idPaper, weight_test_1, weight_regular_1, weight_exam_1, score_test_1, score_regular_1, score_exam_1
from tblStudent s
inner join vwStudentPaper sp on s.idStudent = sp.idStudent and sp.flgTerm1 = 1
inner join tblFormPaperWeight fpw on sp.form = fpw.form and sp.idPaper = fpw.idPaper 
inner join tblStaffSubject ss on sp.class = ss.class and ss.idSubject = sp.idSubject 
left join tblStudentPaperScore sps on sps.idStudent = s.idStudent and sps.idPaper = sp.idPaper
WHERE sp.form in (1, 2, 3, 4, 5) and not sp.idPaper in ('CHI', 'ENG')
and (
--	(weight_test_1 = 0 and weight_regular_1 = 0 and weight_exam_1 = 0 and grade_exam_1 is null) or
	(weight_test_1 > 0 and score_test_1 is null) or
	(weight_regular_1 > 0 and score_regular_1 is null) or
	(weight_exam_1 > 0 and score_exam_1 is null)
) and flgIgnore_1 = 0
order by ss.idStaff, sp.class, sp.idPaper, s.class, s.numberClass

-- Check Conducts
select s.idStudent, s.class, s.numberClass, s.nameChinese, 
sd.numDemeritDS_1 as numDemeritDP_1, 
case when numBadLesson is null then 0 else numBadLesson end as numBadLesson, 
case when numBadAssessment is null then 0 else numBadAssessment end as numBadAssessment, 
sc.conduct_1_1, numDemeritHW_1, flgHW_1, sc.conduct_3_1, 
sc2.idStaff
from vwStudent s
inner join tblStudentDiscipline sd on s.idStudent = sd.idStudent
inner join tblStudentConduct sc on s.idStudent = sc.idStudent
inner join tblStaffClass sc2 on s.class = sc2.class and flgHead = 1
left join (
	select idStudent, count(*) as numBadLesson
	from tblStudentAttitude
	where lesson_1 in ('C', 'D')
	group by idStudent
) r on r.idStudent = s.idStudent
left join (
	select idStudent, count(*) as numBadAssessment
	from tblStudentAttitude
	where assessment_1 in ('C', 'D')
	group by idStudent
) r2 on r2.idStudent = s.idStudent
where s.form in (1, 2, 3, 4, 6) and (
	(numDemeritDS_1 between 1 and 8 and conduct_1_1 in ('A', 'B')) or 
	(numDemeritDS_1 >= 9 and conduct_1_1 in ('A', 'B', 'C')) or 
	(numBadLesson > 0 and conduct_1_1 in ('A')) or
	(numDemeritHW_1 > 0 and conduct_3_1 in ('A', 'B')) or
	(flgHW_1 = 1 and conduct_3_1 in ('A')) or 
	(numBadAssessment > 0 and conduct_3_1 in ('A'))
)
order by s.class, s.numberClass
