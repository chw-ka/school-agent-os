-- S1-S3
SELECT top 10 s.class, s.numberClass, s.nameChinese, zsr.score_final / 10.0 as score, zsr.rank_form_final as rank 
FROM vwStudent s 
INNER JOIN tblYStudentInfo2 ysi ON ysi.yearSchool = 2005 AND ysi.idStudent = s.idStudent AND grantRange = 'F' 
INNER JOIN tblZStudentRank zsr ON s.idStudent = zsr.idStudent 
INNER JOIN ( 
SELECT idStudent, sum( CASE lesson_2 WHEN 'A' THEN 1 WHEN 'C' THEN - 1 WHEN 'D' THEN - 1000 END) as attitude 
FROM tblStudentAttitude 
GROUP BY idStudent ) r ON r.idStudent = s.idStudent AND attitude >= 0 
WHERE s.form = 3 
ORDER BY rank_form_final, s.class, s.numberClass

-- S4-S7
SELECT top 10 s.class, s.numberClass, s.nameChinese, avg(((zspr.score_final / 10.0) - mean) / sd) as std_score, zsr.score_final / 10.0 as average, count( * ) as numSubject
FROM vwStudent s 
INNER JOIN tblYStudentInfo2 ysi ON ysi.yearSchool = 2005 AND ysi.idStudent = s.idStudent AND grantRange = 'F' 
INNER JOIN ( 
SELECT idStudent, sum( CASE lesson_2 WHEN 'A' THEN 1 WHEN 'C' THEN - 1 WHEN 'D' THEN - 1000 END) as attitude 
FROM tblStudentAttitude 
GROUP BY idStudent ) r ON r.idStudent = s.idStudent AND attitude >= 0 
INNER JOIN tblZStudentRank zsr ON s.idStudent = zsr.idStudent 
INNER JOIN tblZStudentPaperRank zspr ON s.idStudent = zspr.idStudent 
INNER JOIN tblPaper p ON zspr.idPaper = p.idPaper AND s.formGroup = p.formGroup AND (p.idSubject = p.idPaper OR p.idSubject is null) 
INNER JOIN ( 
SELECT s.form, p.idPaper, avg(score_final / 10.0) as mean, stdev(score_final / 10.0) as sd 
FROM vwStudent s 
INNER JOIN tblZStudentPaperRank zspr ON s.idStudent = zspr.idStudent 
INNER JOIN tblPaper p ON zspr.idPaper = p.idPaper AND s.formGroup = p.formGroup AND (p.idSubject = p.idPaper OR p.idSubject is null) 
GROUP BY s.form, p.idPaper ) r2 ON s.form = r2.form AND p.idPaper = r2.idPaper 
WHERE s.form = 6 AND p.idPaper <> 'RES' 
GROUP BY s.class, s.numberClass, s.nameEnglish, s.nameChinese, zsr.score_final
ORDER BY std_score desc
