SELECT s.idStudent, numberClass, nameChinese, statusPromotion, 
numDemeritDS_1, numDemeritDS_2, numMiss_1, numMiss_2, score_1 / 10.0 as score_1, score_2 / 10.0 as score_2, 
case when zsr.score_final < 500 then 1 else 0 end as problemPromotion,
case when ri1.idStudent is not null then N'ª÷¼ú' else case when ri2.idStudent is not null then N'´¶³q' else '' end end as typeImprovement
FROM tblStudent s 
INNER JOIN tblZStudentRank zsr ON s.idStudent = zsr.idStudent 
INNER JOIN tblStudentDiscipline sd ON s.idStudent = sd.idStudent 
INNER JOIN ( 
SELECT ys1.idStudent, CASE WHEN LEFT(ys1.class, 1) = LEFT(ys2.class, 1) THEN N'¯d¯Å' ELSE CASE WHEN score < 500 THEN N'¸Õ¤É' ELSE null END END as statusPromotion 
FROM tblYStudentInfo2 ys1 
LEFT JOIN tblYStudentInfo2 ys2 ON ys2.yearSchool = 2004 AND ys1.idStudent = ys2.idStudent 
LEFT JOIN tblYStudentScore yss ON yss.yearSchool = 2004 AND ys1.idStudent = yss.idStudent AND yss.term = 0 
WHERE ys1.yearSchool = 2005 ) rp ON s.idStudent = rp.idStudent 
LEFT JOIN ( 
SELECT sm.idStudent, count( * ) as numMiss_1 
FROM tblStudentMistake sm 
INNER JOIN vwStudent s ON sm.idStudent = s.idStudent 
INNER JOIN tblFormTerm ft ON s.form = ft.form 
WHERE ft.term = 1 AND dateRecord between dateStart AND dateEnd 
GROUP BY sm.idStudent ) rm1 ON s.idStudent = rm1.idStudent 
LEFT JOIN ( 
SELECT sm.idStudent, count( * ) as numMiss_2 
FROM tblStudentMistake sm 
INNER JOIN vwStudent s ON sm.idStudent = s.idStudent 
INNER JOIN tblFormTerm ft ON s.form = ft.form 
WHERE ft.term = 2 AND dateRecord between dateStart AND dateEnd 
GROUP BY sm.idStudent ) rm2 ON s.idStudent = rm2.idStudent 
left join (
	select r.idStudent, r.typeImprove, r.score_diff
	from (
		select top 1 s.idStudent, score_2 - score_1 as score_diff, 1 as typeImprove
		from tblStudent s
		INNER JOIN tblZStudentRank zsr ON s.idStudent = zsr.idStudent 
		INNER JOIN (
			select idStudent, 
			sum(
			case lesson_2 
			when 'A' then 1
			when 'C' then -1
			when 'D' then -1000
			end) as attitude
			from tblStudentAttitude
			group by idStudent
		) r on s.idStudent = r.idStudent
		where class = '2B' and score_2 - score_1 >= 50 and attitude >= 0
		order by score_diff desc
	) r
) ri1 on s.idStudent = ri1.idStudent
left join (
	select r2.idStudent
	from (
		select top 5 s.idStudent, score_2 - score_1 as score_diff, 2 as typeImprove
		from tblStudent s
		INNER JOIN tblZStudentRank zsr ON s.idStudent = zsr.idStudent
		INNER JOIN (
			select idStudent, 
			sum(
			case lesson_2 
			when 'A' then 1
			when 'C' then -1
			when 'D' then -1000
			end) as attitude
			from tblStudentAttitude
			group by idStudent
		) r on s.idStudent = r.idStudent
		where class = '2B' and score_2 - score_1 >= 30 and attitude >= 0 and s.idStudent not in (
			select idStudent
			from (
				select top 1 s.idStudent
				from tblStudent s
				INNER JOIN tblZStudentRank zsr ON s.idStudent = zsr.idStudent 
				INNER JOIN (
					select idStudent, 
					sum(
					case lesson_2 
					when 'A' then 1
					when 'C' then -1
					when 'D' then -1000
					end) as attitude
					from tblStudentAttitude
					group by idStudent
				) r on s.idStudent = r.idStudent
				where class = '2B' and score_2 - score_1 >= 50 and attitude >= 0
				order by score_2 - score_1 desc
			) r
		)
		order by score_diff desc
	) r2
) ri2 on s.idStudent = ri2.idStudent
WHERE class = '2B' 
ORDER BY numberClass


