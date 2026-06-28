-- Photo
--select 'ren ' + class + '-' + dbo.fnLeadingZero(numberClass, 3) + '.JPG ' + idUser + '.jpg'
--from tblStudent
--order by class, numberClass

if exists (select * from dbo.sysobjects where id = object_id(N'[dbo].[stpUpdatePortfolioBasicInfo]') and OBJECTPROPERTY(id, N'IsProcedure') = 1)
drop procedure [dbo].[stpUpdatePortfolioBasicInfo]
GO

CREATE PROCEDURE dbo.stpUpdatePortfolioBasicInfo
@yearSchool int
AS

-- Form
INSERT tblYForm(yearSchool, form, nameChinese, nameEnglish)
SELECT @yearSchool, f.form, f.nameChinese, f.nameEnglish 
FROM tblForm f 
LEFT JOIN tblYForm yf ON yf.yearSchool = @yearSchool AND f.form = yf.form 
WHERE yf.yearSchool is null

-- Class
INSERT tblYClass(yearSchool, class, form) 
SELECT @yearSchool, c.class, c.form 
FROM tblClass c 
LEFT JOIN tblYClass yc ON yc.yearSchool = @yearSchool AND c.class = yc.class 
WHERE flgAuxiliary = 0 AND yc.yearSchool is null

-- Staff
INSERT tblYStaff(idStaff, yearSchool, nameChinese, nameEnglish, nameGiven) 
SELECT s.idStaff, @yearSchool, s.nameChinese, s.nameEnglish, s.nameGiven 
FROM tblStaff s 
LEFT JOIN tblYStaff ys ON ys.yearSchool = @yearSchool AND s.idStaff = ys.idStaff 
WHERE ys.yearSchool is null

-- StaffClass
INSERT tblYStaffClass(idStaff, yearSchool, class, flgHead) 
SELECT sc.idStaff, @yearSchool, sc.class, sc.flgHead 
FROM tblStaffClass sc 
LEFT JOIN tblYStaffClass ysc ON ysc.yearSchool = @yearSchool AND sc.idStaff = ysc.idStaff AND sc.class = ysc.class 
WHERE ysc.yearSchool is null

-- Paper
INSERT tblYPaper(yearSchool, form, idPaper, keyOrder, idSubject, nameChinese, nameEnglish, remarkChinese, remarkEnglish, flgScore, typePaper) 
SELECT distinct @yearSchool, sp.form, p.idPaper, p.keyOrder, p.idSubject, p.nameChinese, p.nameEnglish, p.remarkChinese, p.remarkEnglish, sp.flgScore, p.typePaper 
FROM vwStudentPaper sp 
INNER JOIN tblPaper p ON sp.formGroup = p.formGroup AND sp.idPaper = p.idPaper 
LEFT JOIN tblYPaper yp ON yp.yearSchool = @yearSchool AND yp.form = sp.form AND yp.idPaper = p.idPaper 
WHERE sp.idSubject <> 'OTH' AND yp.yearSchool is null

-- UnitGroup
INSERT tblYUnitGroup(yearSchool, idUnitGroup, nameChinese, nameEnglish, flgStudent, flgGrade, flgHouse) 
SELECT @yearSchool, ug.idUnitGroup, ug.nameChinese, ug.nameEnglish, ug.flgStudent, ug.flgGrade, ug.flgHouse 
FROM tblUnitGroup ug 
LEFT JOIN tblYUnitGroup yug ON yug.yearSchool = @yearSchool AND yug.idUnitGroup = ug.idUnitGroup 
WHERE yug.yearSchool is null

-- Unit
INSERT tblYUnit(yearSchool, idUnit, idUnitGroup, nameChinese, nameEnglish) 
SELECT @yearSchool, u.idUnit, u.idUnitGroup, u.nameChinese, u.nameEnglish 
FROM tblUnit u 
LEFT JOIN tblYUnit yu ON yu.yearSchool = @yearSchool AND u.idUnit = yu.idUnit 
WHERE yu.yearSchool is null

-- ClassUnit
INSERT tblYClassUnit(yearSchool, idClassUnit, nameChinese, nameEnglish, flgComment) 
SELECT @yearSchool, cu.idClassUnit, cu.nameChinese, cu.nameEnglish, cu.flgComment 
FROM tblClassUnit cu 
LEFT JOIN tblYClassUnit ycu ON ycu.yearSchool = @yearSchool AND ycu.idClassUnit = cu.idClassUnit 
WHERE ycu.yearSchool is null

-- Post
INSERT tblYPost(yearSchool, idPost, nameChinese, nameEnglish, keyOrder) 
SELECT @yearSchool, p.idPost, p.nameChinese, p.nameEnglish, p.keyOrder 
FROM tblPost p 
LEFT JOIN tblYPost yp ON yp.yearSchool = @yearSchool AND yp.idPost = p.idPost 
WHERE yp.yearSchool is null

-- UnitComment
INSERT tblYUnitComment(yearSchool, idComment, nameChinese, nameEnglish) 
SELECT @yearSchool, ecac.idComment, ecac.nameChinese, ecac.nameEnglish 
FROM tblECAComment ecac 
LEFT JOIN tblYUnitComment yuc ON yuc.yearSchool = @yearSchool AND yuc.idComment = ecac.idComment 
WHERE yuc.yearSchool is null

-- Comment
INSERT tblYComment(yearSchool, idComment, idCommentGroup, comment) 
SELECT @yearSchool, c.idComment, c.idCommentGroup, c.comment 
FROM tblComment c 
LEFT JOIN tblYComment yc ON yc.yearSchool = @yearSchool AND yc.idComment = c.idComment 
WHERE yc.yearSchool is null

-- AttitudeComment
INSERT tblYAttitudeComment(yearSchool, idComment, nameChinese, nameEnglish) 
SELECT @yearSchool, ac.idComment, ac.nameChinese, ac.nameEnglish 
FROM tblAttitudeComment ac 
LEFT JOIN tblYAttitudeComment yac ON yac.yearSchool = @yearSchool AND yac.idComment = ac.idComment 
WHERE yac.yearSchool is null

GO

if exists (select * from dbo.sysobjects where id = object_id(N'[dbo].[stpUpdatePortfolioReport]') and OBJECTPROPERTY(id, N'IsProcedure') = 1)
drop procedure [dbo].[stpUpdatePortfolioReport]
GO

CREATE PROCEDURE dbo.stpUpdatePortfolioReport
@yearSchool int, @term tinyint
AS

-- StudentScore
DELETE 
FROM tblYStudentScore 
WHERE yearSchool = @yearSchool AND ((@term = 1 and term = 1) or (@term = 2 and term in (2, 0)))

INSERT tblYStudentScore(idStudent, yearSchool, term, score, rankClass, rankForm) 
SELECT zsr.idStudent, @yearSchool, zsr.term, zsr.score, zsr.rankClass, zsr.rankForm 
FROM tblZStudentRank2 zsr 
WHERE ((@term = 1 and zsr.term = 1) or (@term = 2 and zsr.term in (2, 0))) AND zsr.idPaper = '' AND zsr.flgStandard = 0 AND zsr.section = 'O'

-- StudentPaperTerm
DELETE
FROM tblYStudentPaperTerm
WHERE yearSchool = @yearSchool AND ((@term = 1 and term = 1) or (@term = 2 and term in (2, 0)))

INSERT tblYStudentPaperTerm(idStudent, yearSchool, form, idPaper, term) 
SELECT idStudent, @yearSchool, form, idPaper, @term
FROM vwStudentPaper 
WHERE ((@term = 1 and flgTerm1 = 1) OR (@term = 2 and flgTerm2 = 1)) AND idSubject = idPaper AND form IN ( 
SELECT form 
FROM tblFormTerm 
WHERE term = @term )
UNION
SELECT idStudent, @yearSchool, form, idPaper, 0
FROM vwStudentPaper 
WHERE (flgTerm1 = 1 OR flgTerm2 = 1) AND idSubject = idPaper AND @term = 2

-- StudentSubjectPost
DELETE
FROM tblYStudentSubjectPost
WHERE yearSchool = @yearSchool AND term = @term

INSERT tblYStudentSubjectPost(idStudent, yearSchool, form, idSubject, term, idPost, idComment) 
SELECT ssp.idStudent, yearSchool, form, idSubject, @term, idPost, idComment 
FROM tblStudentSubjectPost ssp 
INNER JOIN tblStudent s ON ssp.idStudent = s.idStudent 
INNER JOIN tblYStudentPaperTerm yspt ON ssp.idStudent = yspt.idStudent AND ssp.idSubject = yspt.idPaper AND yspt.yearSchool = @yearSchool AND yspt.term = @term

-- StudentRemark
DELETE
FROM tblYStudentRemark
WHERE yearSchool = @yearSchool AND ((@term = 1 and term = 1) or (@term = 2 and term = 0))

INSERT tblYStudentRemark(idStudent, yearSchool, term, row, nameChinese) 
SELECT idStudent, @yearSchool, CASE @term WHEN 1 THEN 1 ELSE 0 END, row, nameChinese 
FROM tblStudentReportRemark
WHERE term = @term

-- StudentPaperScore
DELETE
FROM tblYStudentPaperScore
WHERE yearSchool = @yearSchool AND ((@term = 1 and term = 1) or (@term = 2 and term in (2, 0)))

INSERT tblYStudentPaperScore (idStudent, yearSchool, form, idPaper, term, score, grade, flgAssess, flgIgnore, rankClass, rankForm) 
SELECT zsr.idStudent, yspt.yearSchool, zsr.form, zsr.idPaper, zsr.term, floor((score + 5.0) / 10.0), null, 0, flgIgnore, rankClass, rankForm
FROM tblZStudentRank2 zsr 
INNER JOIN tblYStudentPaperTerm yspt ON zsr.idStudent = yspt.idStudent AND zsr.idPaper = yspt.idPaper AND yspt.yearSchool = @yearSchool AND yspt.term = zsr.term and zsr.section = 'O' and zsr.flgStandard = 0 
WHERE (@term = 1 and zsr.term = 1) or (@term = 2 and zsr.term in (2, 0))
UNION 
SELECT sps.idStudent, yearSchool, form, sps.idPaper, 1, null, grade_exam_1, 0, flgIgnore_1, null, null 
FROM tblStudentPaperScore sps 
INNER JOIN tblYStudentPaperTerm yspt ON sps.idStudent = yspt.idStudent AND sps.idPaper = yspt.idPaper AND yspt.yearSchool = @yearSchool AND yspt.term = 1
WHERE grade_exam_1 is NOT null and @term = 1
UNION 
SELECT sps.idStudent, yearSchool, form, sps.idPaper, 2, null, grade_exam_2, 0, flgIgnore_2, null, null 
FROM tblStudentPaperScore sps 
INNER JOIN tblYStudentPaperTerm yspt ON sps.idStudent = yspt.idStudent AND sps.idPaper = yspt.idPaper AND yspt.yearSchool = @yearSchool AND yspt.term = 2
WHERE grade_exam_2 is NOT null and @term = 2

-- StudentConduct
DELETE 
FROM tblYStudentConduct 
WHERE yearSchool = @yearSchool AND ((@term = 1 and term = 1) or (@term = 2 and term = 0))

INSERT tblYStudentConduct(idStudent, yearSchool, term, conduct1, conduct2, conduct3, conduct4, conduct5) 
SELECT idStudent, @yearSchool, 1, conduct_1_1, conduct_2_1, conduct_3_1, conduct_4_1, conduct_5_1
FROM tblStudentConduct
WHERE @term = 1 and conduct_1_1 is not null
UNION
SELECT idStudent, @yearSchool, 0, conduct_1_2, conduct_2_2, conduct_3_2, conduct_4_2, conduct_5_2
FROM tblStudentConduct
WHERE @term = 2 and conduct_1_2 is not null
	
-- StudentComment
DELETE
FROM tblYStudentComment
WHERE yearSchool = @yearSchool AND ((@term = 1 and term = 1) or (@term = 2 and term = 0))

INSERT tblYStudentComment(idStudent, yearSchool, term, idComment1, idComment2, idComment3, idComment4, custom1, custom2, custom3, custom4) 
SELECT idStudent, @yearSchool, 1, comment_1_1, comment_2_1, comment_3_1, comment_4_1, custom_1_1, custom_2_1, custom_3_1, custom_4_1
FROM tblStudentComment
WHERE (comment_1_1 is not null OR custom_1_1 is not null) and @term = 1
UNION
SELECT idStudent, @yearSchool, 0, comment_1_2, comment_2_2, comment_3_2, comment_4_2, custom_1_2, custom_2_2, custom_3_2, custom_4_2
FROM tblStudentComment
WHERE (comment_1_2 is not null OR custom_1_2 is not null) and @term = 2

-- StudentDiscipline
DELETE
FROM tblYStudentDiscipline
WHERE yearSchool = @yearSchool AND term = @term

INSERT tblYStudentDiscipline(idStudent, yearSchool, term, dayAbsent, numLate, numDemeritDS, numDemeritHW, flgHW) 
SELECT idStudent, @yearSchool, 1, dayAbsent_1, numLate_1, numDemeritDS_1, numDemeritHW_1, flgHW_1 
FROM tblStudentDiscipline
WHERE dayAbsent_1 is not null and @term = 1
UNION 
SELECT idStudent, @yearSchool, 2, dayAbsent_2, numLate_2, numDemeritDS_2, numDemeritHW_2, flgHW_2 
FROM tblStudentDiscipline
WHERE dayAbsent_2 is not null and @term = 2

-- StudentSubjectAttitude
DELETE
FROM tblYStudentSubjectAttitude
WHERE yearSchool = @yearSchool AND ((@term = 1 and term = 1) or (@term = 2 and term = 0))

INSERT tblYStudentSubjectAttitude(idStudent, yearSchool, form, idSubject, term, lesson, assessment, comment1, comment2, comment3, comment4, custom1, custom2, custom3, custom4) 
SELECT sa.idStudent, @yearSchool, ss.form, sa.idSubject, 1, lesson_1, assessment_1, comment_1_1, comment_2_1, comment_3_1, comment_4_1, custom_1_1, custom_2_1, custom_3_1, custom_4_1
FROM tblStudentAttitude sa 
INNER JOIN vwStudentSubject ss ON sa.idStudent = ss.idStudent AND sa.idSubject = ss.idSubject AND flgTerm1 = 1
WHERE lesson_1 is not null and @term = 1
UNION
SELECT sa.idStudent, @yearSchool, ss.form, sa.idSubject, 0, lesson_2, assessment_2, comment_1_2, comment_2_2, comment_3_2, comment_4_2, custom_1_2, custom_2_2, custom_3_2, custom_4_2
FROM tblStudentAttitude sa 
INNER JOIN vwStudentSubject ss ON sa.idStudent = ss.idStudent AND sa.idSubject = ss.idSubject AND flgTerm2 = 1
WHERE lesson_2 is not null and @term = 2

-- StudentAward
DELETE
FROM tblYStudentAward
WHERE yearSchool = @yearSchool

INSERT tblYStudentAward(idStudent, yearSchool, idRow, nameChinese, dateAward) 
SELECT idStudent, @yearSchool, idRow, nameChinese, dateAward 
FROM tblStudentAward

-- StudentUnitPost
DELETE
FROM tblYStudentUnitPost
WHERE yearSchool = @yearSchool

INSERT tblYStudentUnitPost(idStudent, yearSchool, idUnit, idPost, idComment) 
SELECT idStudent, @yearSchool, idUnit, idPost, idComment 
FROM tblStudentUnitPost

-- StudentClassPost
DELETE
FROM tblYStudentClassPost
WHERE yearSchool = @yearSchool

INSERT tblYStudentClassPost(idStudent, yearSchool, idClassUnit, idPost, idComment) 
SELECT idStudent, @yearSchool, idClassUnit, idPost, idComment 
FROM tblStudentClassPost

GO

exec stpUpdatePortfolioBasicInfo 2012

-----------------------------------------------------------------
-- StudentInfo, StudentInfo2, StudentStudent (Run in Excel Macro)
-----------------------------------------------------------------

exec stpUpdatePortfolioReport 2012,  2