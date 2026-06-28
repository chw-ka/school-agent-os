--select idStudent
--from tblStudent
--where idStudent not in (select idStudent from tblYStudentInfo)

-- Student Score

--update tblYStudentScore
--set score = zsr.score_1, rankClass = zsr.rank_class_1, rankForm = zsr.rank_form_1
--from tblYStudentScore yss
--inner join tblZStudentRank zsr ON yss.idStudent = zsr.idStudent
--where yss.yearSchool = 2008 and yss.term = 1

-- 1 上學期分數
	INSERT tblYStudentScore(idStudent, yearSchool, term, score, rankClass, rankForm) 
	SELECT idStudent, 2024, 1, score / 10, rankClass, rankForm
	FROM tblZStudentRank2
	WHERE idPaper = '' and flgStandard = 0 and section = 'O' and term = 1 and form in (1,2,3,4,5)


-- 總成績 （上學期應毋須加入此項資料）
--	INSERT tblYStudentScore(idStudent, yearSchool, term, score, rankClass, rankForm) 
--	SELECT idStudent, 2013, 0, score / 10, rankClass, rankForm
--	FROM tblZStudentRank2
--	WHERE idPaper = '' and flgStandard = 0 and section = 'O' and term = 0 and form in (1,2,3,4,5)

-- Student Conduct

--update tblYStudentConduct
--set conduct1 = conduct_1_1, conduct2 = conduct_2_1, conduct3 = conduct_3_1, conduct4 = conduct_4_1, conduct5 = conduct_5_1
--from tblYStudentConduct ysc
--inner join tblStudentConduct sc ON ysc.idStudent = sc.idStudent
--where ysc.yearSchool = 2008 and ysc.term = 1


--2 上學期conduct
	INSERT tblYStudentConduct(idStudent, yearSchool, term, conduct1, conduct2, conduct3, conduct4, conduct5) 
	SELECT s.idStudent, 2024, 1, conduct_1_1, conduct_2_1, conduct_3_1, conduct_4_1, conduct_5_1 
	FROM tblStudentConduct sc 
	INNER JOIN vwStudent s ON sc.idStudent = s.idStudent 
	WHERE form IN (1,2,3,4,5)

-- Student Comment
--update tblYStudentComment
--set idComment1 = comment_1_1, idComment2 = comment_2_1, idComment3 = comment_3_1, idComment4 = comment_4_1, custom1 = custom_1_1, custom2 = custom_2_1, custom3 = custom_3_1, custom4 = custom_4_1
--from tblYStudentComment ysc
--inner join tblStudentComment sc ON ysc.idStudent = sc.idStudent
--where ysc.yearSchool = 2008 and ysc.term = 1

--3 上學期comment

	Insert into tblYComment
	Select 2024, idComment, idCommentGroup, comment from tblComment

		INSERT tblYStudentComment(idStudent, yearSchool, term, idComment1, idComment2, idComment3, idComment4, custom1, custom2, custom3, custom4) 
		SELECT s.idStudent, 2024, 1, comment_1_1, comment_2_1, comment_3_1, comment_4_1, custom_1_1, custom_2_1, custom_3_1, custom_4_1 
		FROM tblStudentComment sc 
		INNER JOIN vwStudent s ON sc.idStudent = s.idStudent 
		WHERE form IN (1,2,3,4,5)

-- Student Discipline
--update tblYStudentDiscipline
--set dayAbsent = sd.dayAbsent_1, numLate = sd.numLate_1, numDemeritDS = sd.numDemeritDS_1, numDemeritHW = sd.numDemeritHW_1, flgHW = sd.flgHW_1
--from tblYStudentDiscipline ysd
--inner join tblStudentDiscipline sd ON ysd.idStudent = sd.idStudent
--where ysd.yearSchool = 2008 and ysd.term = 1

--4 上學期 遲到 缺席 缺點
	INSERT tblYStudentDiscipline(idStudent, yearSchool, term, dayAbsent, numLate, numDemeritDS, numDemeritHW, flgHW) 
	SELECT sd.idStudent, 2024, 1, dayAbsent_1, numLate_1, numDemeritDS_1, numDemeritHW_1, flgHW_1 
	FROM tblStudentDiscipline sd 
	INNER JOIN vwStudent s ON sd.idStudent = s.idStudent 
	WHERE form IN (1,2,3,4,5)

-- Student Award
--delete
--from tblYStudentAward
--where yearSchool = 2008

--下學期才需要
--INSERT tblYStudentAward(idStudent, yearSchool, idRow, nameChinese, dateAward) 
--SELECT sa.idStudent, 2013, idRow, sa.nameChinese, dateAward 
--FROM tblStudentAward sa 
--INNER JOIN vwStudent s ON sa.idStudent = s.idStudent 
--WHERE form IN (1,2,3,4,5)

-- Student Remark
--delete
--from tblYStudentRemark
--where yearSchool = 2008

--下學期才需要
--INSERT tblYStudentRemark(idStudent, yearSchool, term, row, nameChinese)
--SELECT srr.idStudent, 2013, CASE WHEN term = 2 THEN 0 ELSE 1 END, row, srr.nameChinese 
--FROM tblStudentReportRemark srr 
--INNER JOIN vwStudent s ON srr.idStudent = s.idStudent 
--WHERE form IN (1,2,3,4,5)

-- Student Paper Term
--delete
--from tblYStudentSubjectPost
--where yearSchool = 2008
--
--delete
--from tblYStudentPaperScore
--where yearSchool = 2008
--
--delete
--from tblYStudentPaperTerm
--where yearSchool = 2008

--insert tblYStudentPaperTerm(idStudent,yearSchool,form,idPaper,term)
--select idStudent,2008,form,idPaper,1
--from vwStudentPaper
--where flgTerm1 = 1
--union
--select idStudent,2008,form,idSubject,1
--from vwStudentPaper
--where flgTerm1 = 1 and idPaper <> idSubject


--5 paper  
	INSERT tblYPaper(yearSchool,form,idPaper,keyOrder,idSubject,nameChinese,nameEnglish,remarkChinese,remarkEnglish,flgScore,typePaper)
	SELECT 2024, r.form, r.idPaper, p.keyOrder, p.idSubject, p.nameChinese, p.nameEnglish, p.remarkChinese, p.remarkEnglish, p.flgScore, p.typePaper
	FROM (
	SELECT form, idPaper
	FROM dbo.vwStudentPaper 
	WHERE (flgTerm1 = 1 or flgTerm2 = 1) AND form IN (1,2,3,4,5) 
	UNION 
	SELECT form, idSubject
	FROM dbo.vwStudentPaper 
	WHERE (flgTerm1 = 1 or flgTerm2 = 1) AND idPaper <> idSubject AND form IN (1,2,3,4,5)
	) r 
	INNER JOIN tblPaper p ON p.formGroup = r.form and p.idPaper = r.idPaper
	LEFT JOIN tblYPaper yp on r.form = yp.form and r.idPaper = yp.idPaper and yp.yearSchool = 2024
	where yp.idPaper is null

	INSERT tblYStudentPaperTerm(idStudent, yearSchool, form, idPaper, term) 
	SELECT idStudent, 2024, form, idPaper, 1 
	FROM vwStudentPaper 
	WHERE flgTerm1 = 1 AND form IN (1,2,3,4,5) 
	UNION 
	SELECT idStudent, 2024, form, idSubject, 1
	FROM vwStudentPaper 
	WHERE flgTerm1 = 1 AND idPaper <> idSubject AND form IN (1,2,3,4,5)

--	INSERT tblYStudentPaperTerm(idStudent, yearSchool, form, idPaper, term) 
--	SELECT idStudent, 2009, form, idPaper, 1
--	FROM vwStudentPaper 
--	WHERE (flgTerm1 = 1 or flgTerm2 = 1) AND form IN (1,2,3,4,6) 
--	UNION 
--	SELECT idStudent, 2009, form, idSubject, 1
--	FROM vwStudentPaper 
--	WHERE (flgTerm1 = 1 or flgTerm2 = 1) AND idPaper <> idSubject AND form IN (1,2,3,4,6)

-- StudentSubjectAttitude
--delete
--from tblYStudentSubjectAttitude
--where yearSchool = 2008

--insert tblYStudentSubjectAttitude(idStudent,yearSchool,form,idSubject,term,lesson,assessment,comment1,comment2,comment3,comment4,custom1,custom2,custom3,custom4)
--select sa.idStudent, 2008, ss.form, sa.idSubject, 1, lesson_1,assessment_1,comment_1_1,comment_2_1,comment_3_1,comment_4_1,custom_1_1,custom_2_1,custom_3_1,custom_4_1
--from tblStudentAttitude sa
--inner join vwStudentSubject ss on sa.idStudent = ss.idStudent and sa.idSubject = ss.idSubject and flgTerm1 = 1



--6 上學期功課考勤
	Insert tblYAttitudeComment
	Select 2024, idComment, nameChinese, nameEnglish from tblAttitudeComment
	
	INSERT tblYStudentSubjectAttitude(idStudent, yearSchool, form, idSubject, term, lesson, assessment, comment1, comment2, comment3, comment4, custom1, custom2, custom3, custom4) 
	SELECT sa.idStudent, 2024, ss.form, sa.idSubject, 1, lesson_1, assessment_1, comment_1_1, comment_2_1, comment_3_1, comment_4_1, custom_1_1, custom_2_1, custom_3_1, custom_4_1 
	FROM tblStudentAttitude sa 
	INNER JOIN vwStudentSubject ss ON sa.idStudent = ss.idStudent AND sa.idSubject = ss.idSubject AND flgTerm1 = 1 
	WHERE form IN (1,2,3,4,5)

-- StudentPaperScore
--insert tblYStudentPaperScore (idStudent,yearSchool,form,idPaper,term,score,grade,flgAssess,flgIgnore,rankClass,rankForm)
--select zspr.idStudent,yearSchool,form,zspr.idPaper, 1,floor((score_1 + 5.0) / 10.0), null, 0, flgIgnore_1,rank_class_1,rank_form_1
--from tblZStudentPaperRank zspr
--inner join tblYStudentPaperTerm yspt on zspr.idStudent = yspt.idStudent and zspr.idPaper = yspt.idPaper and yspt.yearSchool = 2008 and yspt.term = 1 
--union
--select sps.idStudent, yearSchool, form,sps.idPaper, 1, null, grade_exam_1, 0, flgIgnore_1, null, null
--from tblStudentPaperScore sps
--inner join tblYStudentPaperTerm yspt on sps.idStudent = yspt.idStudent and sps.idPaper = yspt.idPaper and yspt.yearSchool = 2008 and yspt.term = 1 
--where grade_exam_1 is not null


--7 分數
	INSERT tblYStudentPaperScore (idStudent, yearSchool, form, idPaper, term, score, grade, flgAssess, flgIgnore, rankClass, rankForm) 
	SELECT zsr.idStudent, yspt.yearSchool, zsr.form, zsr.idPaper, zsr.term, floor((score / 10 + 5.0) / 10.0), null, 0, flgIgnore, rankClass, rankForm
	FROM tblZStudentRank2 zsr 
	INNER JOIN tblYStudentPaperTerm yspt ON zsr.idStudent = yspt.idStudent AND zsr.idPaper = yspt.idPaper AND yspt.yearSchool = 2024 AND yspt.term = zsr.term and zsr.section = 'O' and zsr.flgStandard = 0 
	WHERE zsr.term in (1) and zsr.form in (1,2,3,4,5)
	UNION 
	SELECT sps.idStudent, yearSchool, form, sps.idPaper, 1, null, grade_exam_1, 0, flgIgnore_1, null, null 
	FROM tblStudentPaperScore sps 
	INNER JOIN tblYStudentPaperTerm yspt ON sps.idStudent = yspt.idStudent AND sps.idPaper = yspt.idPaper AND yspt.yearSchool = 2024 AND yspt.term = 1
	where yspt.form in (1,2,3,4,5) and grade_exam_1 is NOT null

--insert tblYStudentPaperScore (idStudent,yearSchool,form,idPaper,term,score,grade,flgAssess,flgIgnore,rankClass,rankForm)
--select zspr.idStudent,yearSchool,form,zspr.idPaper, 0,floor((score_final + 5.0) / 10.0), null, 0, 0,rank_class_final,rank_form_final
--from tblZStudentPaperRank zspr
--inner join tblYStudentPaperTerm yspt on zspr.idStudent = yspt.idStudent and zspr.idPaper = yspt.idPaper and yspt.yearSchool = 2008 and yspt.term = 0 

-- StudentSubjectPost (Remarked at 2015)
--delete
--from tblYStudentSubjectPost
--where yearSchool = 2008 and form in (5,7)



--8 科長
insert tblYPost (yearSchool,idPost,nameChinese,nameEnglish,keyOrder)
select 2024, p.idPost, p.nameChinese, p.nameEnglish, p.keyOrder
from tblPost p
left join tblYPost yp on yp.yearSchool = 2024 and p.idPost = yp.idPost
where yp.idPost is null

Insert tblYUnitComment
Select 2024, idComment, nameChinese, nameEnglish from tblECAComment

insert tblYStudentSubjectPost(idStudent,yearSchool,form,idSubject,term,idPost,idComment)
select distinct ssp.idStudent,yearSchool,form,idSubject,1,idPost,idComment
from tblStudentSubjectPost ssp
inner join tblStudent s on ssp.idStudent = s.idStudent
inner join tblYStudentPaperTerm yspt on ssp.idStudent = yspt.idStudent and ssp.idSubject = yspt.idPaper and yspt.yearSchool = 2024 and term = 1
where yspt.form in (1,2,3,4,5)



--9 UNIT POST
-- StudentUnitPost

Insert tblYUnitGroup
Select 2024, idUnitGroup, nameChinese, nameEnglish, flgStudent, flgGrade, flgHouse from tblUnitGroup

insert tblYUnit (yearSchool,idUnit,idUnitGroup,nameChinese,nameEnglish)
select 2024, u.idUnit, u.idUnitGroup, u.nameChinese, u.nameEnglish
from tblUnit u
left join tblYUnit yu on yu.yearSchool = 2023 and u.idUnit = yu.idUnit
where yu.idUnit is null





----------------------------
--delete
--from tblYStudentUnitPost
--where yearSChool = 2009 and idStudent in (
--select idStudent
--from vwStudent
--where form in (5,7)
--)

insert tblYStudentUnitPost(idStudent,yearSchool,idUnit,idPost,idComment)
select sup.idStudent,2024,idUnit,idPost,idComment
from tblStudentUnitPost sup
INNER JOIN vwStudent s on sup.idStudent = s.idStudent
where form in (1,2,3,4,5)

--OOO
-- StudentClassPost

--delete
--from tblYStudentClassPost
--where yearSChool = 2009 and idStudent in (
--select idStudent
--from vwStudent
--where form in (5,7)
--)

insert tblYClassUnit
select 2024, idClassUnit, nameChinese, nameEnglish, flgComment from tblYClassUnit where yearSchool = 2023

insert tblYStudentClassPost
select scp.idStudent,2024,idClassUnit,idPost,idComment
from tblStudentClassPost scp
INNER JOIN vwStudent s on scp.idStudent = s.idStudent
where form in (1,2,3,4,5)





