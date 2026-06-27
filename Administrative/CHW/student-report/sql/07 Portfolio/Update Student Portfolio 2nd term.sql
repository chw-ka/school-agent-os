
-- 1. Student Score
--------------------------------------------------
--------------------------------------------------
-- 開始前先 check database 名：					--
-- 上面標籤 e.g.  db13_14						--
-- SQL command 有 db13_14 字樣					--
-- 一般上下學期唔駛再改，已經分開了 file 做		--
-- 只需注意要改 yearSchool, form #				--
--------------------------------------------------
--------------------------------------------------
-- 目前 tblZStudentRank2 所記的數字是			--
-- Term 1 有 3 位數								--
-- Term 2 有 4 位數								--
-- 再加上 12-13 年度的中六曾出現分數調整		--
-- 因此，如要覆寫 12_13 record，務必小必處理	--
--------------------------------------------------
--------------------------------------------------


--update tblYStudentScore
--set score = zsr.score, rankClass = zsr.rank_class, rankForm = zsr.rank_form
--from tblYStudentScore yss
--inner join tblZStudentRank zsr ON yss.idStudent = zsr.idStudent
--where yss.yearSchool = 2012 and yss.term = 2


-- 1a 下學期總分    (score 要 3 位數, 因 display 有 1 個 d.p. )
	INSERT tblYStudentScore(idStudent, yearSchool, term, score, rankClass, rankForm) 
	SELECT idStudent, 2024, 2, round(score / 10,0) , rankClass, rankForm
	FROM tblZStudentRank2
	WHERE idPaper = '' and flgStandard = 0 and section = 'O' and term = 2 and form in (1,2,3,4,5)


-- 1b 全年總成績    (score 要 3 位數, 因 display 有 1 個 d.p. )
	INSERT tblYStudentScore(idStudent, yearSchool, term, score, rankClass, rankForm) 
	SELECT idStudent, 2024, 0, round(score / 10,0), rankClass, rankForm
	FROM tblZStudentRank2
	WHERE idPaper = '' and flgStandard = 0 and section = 'O' and term = 0 and form in (1,2,3,4,5)



--2 Sutdent 下學期 conduct

--update tblYStudentConduct
--set conduct1 = conduct_1_2, conduct2 = conduct_2_2, conduct3 = conduct_3_2, conduct4 = conduct_4_2, conduct5 = conduct_5_2
--from tblYStudentConduct ysc
--inner join tblStudentConduct sc ON ysc.idStudent = sc.idStudent
--where ysc.yearSchool = 2012 and ysc.term = 2

	INSERT tblYStudentConduct(idStudent, yearSchool, term, conduct1, conduct2, conduct3, conduct4, conduct5) 
	SELECT s.idStudent, 2024, 0, conduct_1_2, conduct_2_2, conduct_3_2, conduct_4_2, conduct_5_2 
	FROM tblStudentConduct sc 
	INNER JOIN vwStudent s ON sc.idStudent = s.idStudent 
	WHERE form IN (1,2,3,4,5)

-- 3 Student 下學期 comment
--update tblYStudentComment
--set idComment1 = comment_1_2, idComment2 = comment_2_2, idComment3 = comment_3_2, idComment4 = comment_4_2, custom1 = custom_1_2, custom2 = custom_2_2, custom3 = custom_3_2, custom4 = custom_4_2
--from tblYStudentComment ysc
--inner join tblStudentComment sc ON ysc.idStudent = sc.idStudent
--where ysc.yearSchool = 2012 and ysc.term = 2

		INSERT tblYStudentComment(idStudent, yearSchool, term, idComment1, idComment2, idComment3, idComment4, custom1, custom2, custom3, custom4) 
		SELECT s.idStudent, 2024, 0, comment_1_2, comment_2_2, comment_3_2, comment_4_2, custom_1_2, custom_2_2, custom_3_2, custom_4_2 
		FROM tblStudentComment sc 
		INNER JOIN vwStudent s ON sc.idStudent = s.idStudent 
		WHERE form IN (1,2,3,4,5)

--4 下學期 遲到 缺席 缺點
-- Student Discipline
--update tblYStudentDiscipline
--set dayAbsent = sd.dayAbsent_2, numLate = sd.numLate_2, numDemeritDS = sd.numDemeritDS_2, numDemeritHW = sd.numDemeritHW_2, flgHW = sd.flgHW_2
--from tblYStudentDiscipline ysd
--inner join tblStudentDiscipline sd ON ysd.idStudent = sd.idStudent
--where ysd.yearSchool = 2012 and ysd.term = 2

	INSERT tblYStudentDiscipline(idStudent, yearSchool, term, dayAbsent, numLate, numDemeritDS, numDemeritHW, flgHW) 
	SELECT sd.idStudent, 2024, 2, dayAbsent_2, numLate_2, numDemeritDS_2, numDemeritHW_2, flgHW_2
	FROM tblStudentDiscipline sd 
	INNER JOIN vwStudent s ON sd.idStudent = s.idStudent 
	WHERE form IN (1,2,3,4,5)

-- 5. 下學期獎項 Student Award
--delete
--from tblYStudentAward
--where yearSchool = 2012

INSERT tblYStudentAward(idStudent, yearSchool, idRow, nameChinese, dateAward) 
SELECT sa.idStudent, 2024, idRow, sa.nameChinese, dateAward 
FROM tblStudentAward sa 
INNER JOIN vwStudent s ON sa.idStudent = s.idStudent 
WHERE form IN (1,2,3,4,5)

-- 6.  Student Report Remark
--delete
--from tblYStudentRemark
--where yearSchool = 2012

INSERT tblYStudentRemark(idStudent, yearSchool, term, row, nameChinese)
SELECT srr.idStudent, 2024, CASE WHEN term = 2 THEN 0 ELSE 1 END, row, srr.nameChinese 
FROM tblStudentReportRemark srr 
INNER JOIN vwStudent s ON srr.idStudent = s.idStudent 
WHERE form IN (1,2,3,4,5)

-- 7.  Student Paper Term

-- 上次試就咁 delete tblYStudentPaperTerm 是不成功的，
-- 若真的要做，可能要先清 tblYStudentSubjectPost, tblYStudentPaperScore, 如下
	-- delete from tblYStudentSubjectPost where yearSchool = 2012
	-- delete from tblYStudentPaperScore  where yearSchool = 2012
	-- delete from tblYStudentPaperTerm   where yearSchool = 2012

	-- select * from tblYStudentPaperTerm where yearSchool = 2024 and term in (2,0) and form in (1,2,3,4,5)
	

    -- 7.1 第二學期
	INSERT tblYStudentPaperTerm(idStudent, yearSchool, form, idPaper, term) 
	SELECT idStudent, 2024, form, idPaper, 2
	FROM vwStudentPaper 
	WHERE flgTerm2 = 1 AND form IN (1,2,3,4,5) 
	UNION 
	SELECT idStudent, 2024, form, idSubject, 2
	FROM vwStudentPaper 
	WHERE flgTerm2 = 1 AND idPaper <> idSubject AND form IN (1,2,3,4,5)
	order by idPaper
	
	-- 7.2 全年
	INSERT tblYStudentPaperTerm(idStudent, yearSchool, form, idPaper, term) 
	SELECT idStudent, 2024, form, idPaper, 0
	FROM vwStudentPaper 
	WHERE (flgTerm1 = 1 or flgTerm2 = 1) AND form IN (1,2,3,4,5) 
	UNION 
	SELECT idStudent, 2024, form, idSubject, 0
	FROM vwStudentPaper  
	WHERE (flgTerm1 = 1 or flgTerm2 = 1) AND idPaper <> idSubject AND form IN (1,2,3,4,5)



--8 paper name

	-- 這段已 CHECK 埋若有重覆的話不用再覆寫
	INSERT tblYPaper(yearSchool,form,idPaper,keyOrder,idSubject,nameChinese,nameEnglish,remarkChinese,remarkEnglish,flgScore,typePaper)
	SELECT 2024, r.form, r.idPaper, p.keyOrder, p.idSubject, p.nameChinese, p.nameEnglish, p.remarkChinese, p.remarkEnglish, p.flgScore, p.typePaper
	FROM (
	SELECT form, idPaper
	FROM vwStudentPaper 
	WHERE (flgTerm1 = 1 or flgTerm2 = 1) AND form IN (1,2,3,4,5) 
	UNION 
	SELECT form, idSubject
	FROM vwStudentPaper 
	WHERE (flgTerm1 = 1 or flgTerm2 = 1) AND idPaper <> idSubject AND form IN (1,2,3,4,5)
	) r 
	INNER JOIN tblPaper p ON p.formGroup = r.form and p.idPaper = r.idPaper
	LEFT JOIN tblYPaper yp on r.form = yp.form and r.idPaper = yp.idPaper and yp.yearSchool = 2024
	where yp.idPaper is null


-- 9. 下學期功課考勤 StudentSubjectAttitude
--delete from tblYStudentSubjectAttitude where yearSchool = 2012

	INSERT tblYStudentSubjectAttitude(idStudent, yearSchool, form, idSubject, term, lesson, assessment, comment1, comment2, comment3, comment4, custom1, custom2, custom3, custom4) 
	SELECT sa.idStudent, 2024, ss.form, sa.idSubject, 0, lesson_2, assessment_2, comment_1_2, comment_2_2, comment_3_2, comment_4_2, custom_1_2, custom_2_2, custom_3_2, custom_4_2 
	FROM tblStudentAttitude sa 
	INNER JOIN vwStudentSubject ss ON sa.idStudent = ss.idStudent AND sa.idSubject = ss.idSubject AND flgTerm2 = 1 
	WHERE form IN (1,2,3,4,5)


-- 10 分數 StudentPaperScore  (score 要 2 位數) (2014-09-12 Log  Not Success from here)

	-- 10.1 第二學期
	INSERT tblYStudentPaperScore (idStudent, yearSchool, form, idPaper, term, score, grade, flgAssess, flgIgnore, rankClass, rankForm) 
	SELECT zsr.idStudent, yspt.yearSchool, zsr.form, zsr.idPaper, zsr.term, floor((score + 50.0) / 100.0), null, 0, flgIgnore, rankClass, rankForm
	FROM tblZStudentRank2 zsr 
	INNER JOIN tblYStudentPaperTerm yspt ON zsr.idStudent = yspt.idStudent AND zsr.idPaper = yspt.idPaper AND yspt.yearSchool = 2024 AND yspt.term = zsr.term and zsr.section = 'O' and zsr.flgStandard = 0 
	WHERE zsr.term in (2) and zsr.form in (1,2,3,4,5)
	UNION 
	SELECT sps.idStudent, yearSchool, form, sps.idPaper, 2, null, grade_exam_2, 0, flgIgnore_2, null, null 
	FROM tblStudentPaperScore sps 
	INNER JOIN tblYStudentPaperTerm yspt ON sps.idStudent = yspt.idStudent AND sps.idPaper = yspt.idPaper AND yspt.yearSchool = 2024 AND yspt.term = 2
	where yspt.form in (1,2,3,4,5) and grade_exam_2 is NOT null


    -- 10.2 總分
	INSERT tblYStudentPaperScore (idStudent, yearSchool, form, idPaper, term, score, grade, flgAssess, flgIgnore, rankClass, rankForm) 
	SELECT zsr.idStudent, yspt.yearSchool, zsr.form, zsr.idPaper, zsr.term, floor((score + 50.0) / 100.0), null, 0, flgIgnore, rankClass, rankForm
	FROM tblZStudentRank2 zsr 
	INNER JOIN tblYStudentPaperTerm yspt ON zsr.idStudent = yspt.idStudent AND zsr.idPaper = yspt.idPaper AND yspt.yearSchool = 2024 AND yspt.term = zsr.term and zsr.section = 'O' and zsr.flgStandard = 0 
	WHERE zsr.term in (0) and zsr.form in (1,2,3,4,5)
	UNION 
	SELECT sps.idStudent, yearSchool, form, sps.idPaper, 0, null, grade_exam_2, 0, flgIgnore_2, null, null 
	FROM tblStudentPaperScore sps 
	INNER JOIN tblYStudentPaperTerm yspt ON sps.idStudent = yspt.idStudent AND sps.idPaper = yspt.idPaper AND yspt.yearSchool = 2024 AND yspt.term = 2
	where yspt.form in (1,2,3,4,5) and grade_exam_2 is NOT null

--insert tblYStudentPaperScore (idStudent,yearSchool,form,idPaper,term,score,grade,flgAssess,flgIgnore,rankClass,rankForm)
--select zspr.idStudent,yearSchool,form,zspr.idPaper, 0,floor((score_final + 5.0) / 10.0), null, 0, 0,rank_class_final,rank_form_final
--from tblZStudentPaperRank zspr
--inner join tblYStudentPaperTerm yspt on zspr.idStudent = yspt.idStudent and zspr.idPaper = yspt.idPaper and yspt.yearSchool = 2008 and yspt.term = 0 

-- 11 科長   StudentSubjectPost

	insert tblYStudentSubjectPost(idStudent,yearSchool,form,idSubject,term,idPost,idComment)
	select distinct ssp.idStudent,yearSchool,form,idSubject,2,idPost,idComment
	from tblStudentSubjectPost ssp
	inner join tblStudent s on ssp.idStudent = s.idStudent
	inner join tblYStudentPaperTerm yspt on ssp.idStudent = yspt.idStudent and ssp.idSubject = yspt.idPaper and yspt.yearSchool = 2024 and term = 2
	where yspt.form in (1,2,3,4,5)


--12  UNIT POST

	-- 12.1 Unitgroup
	Insert into tblYUnitGroup
	select 2024, idUnitGroup, nameChinese, nameEnglish, flgStudent, flgGrade, flgHouse from tblUnitGroup

	-- 12.2 Unit
	insert tblYUnit (yearSchool,idUnit,idUnitGroup,nameChinese,nameEnglish)
	select 2024, u.idUnit, u.idUnitGroup, u.nameChinese, u.nameEnglish
	from tblUnit u
	left join tblYUnit yu on yu.yearSchool = 2024 and u.idUnit = yu.idUnit
	where yu.idUnit is null

	select * from tblYUnit where yearSchool = 2024

	-- 12.3 Post
	insert tblYPost (yearSchool,idPost,nameChinese,nameEnglish,keyOrder)
	select 2024, p.idPost, p.nameChinese, p.nameEnglish, p.keyOrder
	from tblPost p
	left join tblYPost yp on yp.yearSchool = 2024 and p.idPost = yp.idPost
	where yp.idPost is null

		-- 12.4 Student Unit Post 包括只有參與而沒有職位的學生
	insert tblYStudentUnitPost(idStudent,yearSchool,idUnit,idPost,idComment)
	select sup.idStudent,2024,idUnit,idPost,idComment
	from tblStudentUnitPost sup
	INNER JOIN dbo.vwStudent s on sup.idStudent = s.idStudent
	where form in (1,2,3,4,5)


-- 13 班長 StudentClassPost
	
	-- 13.1 names
	Insert into tblYClassUnit
	select 2020,* from tblClassUnit

	-- 13.2 學生職位 (班會、班長)
	insert tblYStudentClassPost(idStudent,yearSchool,idClassUnit,idPost,idComment)
	select scp.idStudent,2024,idClassUnit,idPost,idComment
	from tblStudentClassPost scp
	INNER JOIN vwStudent s on scp.idStudent = s.idStudent
	where form in (1,2,3,4,5)
