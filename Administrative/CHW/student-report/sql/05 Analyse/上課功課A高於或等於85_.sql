-- 檢視當前年度 tblStudentAttitude 資料決定獲獎名單
select s.idStudent, s.class as 本年度班別, s.numberClass as 本年度學號, s.nameChinese, a.numA + c.numC as A數量, b.numB + d.numD as 科目總數, round(((a.numA + c.numC) * 1.0) / ((b.numB + d.numD) * 1.0) * 100,2) as A百分比 from tblStudent s
left join 
	(select idStudent, count(lesson_1) as numA from tblStudentAttitude
	where lesson_1 = 'A'
	group by idStudent) a on s.idStudent = a.idStudent
left join 
	(select idStudent, count(lesson_2) as numC from tblStudentAttitude
	where lesson_2 = 'A'
	group by idStudent) c on s.idStudent = c.idStudent
left join
	(select idStudent, count(lesson_1) as numB from tblStudentAttitude
	where not (lesson_1 is NULL)
	group by idStudent) b on s.idStudent = b.idStudent
left join
	(select idStudent, count(lesson_2) as numD from tblStudentAttitude
	where not (lesson_2 is NULL)
	group by idStudent) d on s.idStudent = d.idStudent
where round(((a.numA + c.numC) * 1.0) / ((b.numB + d.numD) * 1.0) * 100,2) >= 85.0
order by s.class, s.numberClass



-- 檢視學生資料冊，找出上年度得獎名單
select s.idStudent, s.class as 本年度班別, s.numberClass as 本年度學號, s.nameChinese, c.class as 上年度班別, c.numberClass as 上年度學號, a.numA as A數量, b.numB as 科目總數, round((a.numA * 1.0) / (b.numB * 1.0) * 100,2) as A百分比 from tblStudent s
left join 
	(select idStudent, count(lesson) as numA from tblYStudentSubjectAttitude
	where yearSchool = 2015 and lesson='A'
	group by idStudent) a on s.idStudent = a.idStudent
left join
	(select idStudent, count(lesson) as numB from tblYStudentSubjectAttitude
	where yearSchool = 2015 and not (lesson is NULL)
	group by idStudent) b on s.idStudent = b.idStudent
left join
	(select idStudent, class, numberClass from tblYStudentInfo2
	where yearSchool = 2015) c on s.idStudent = c.idStudent
where round((a.numA * 1.0) / (b.numB * 1.0) * 100,2) >= 85.0
order by s.class, s.numberClass



select s.idStudent, s.class, s.numberClass, s.nameChinese, sa1.Count1, sa2.Count2, sa3.Count3 from tblStudent s
left join (select idStudent, count(lesson_1) as Count1 from tblStudentAttitude where lesson_1 = 'A' group by idStudent) sa1 on s.idStudent = sa1.idStudent 
left join (select idStudent, count(lesson_2) as Count2 from tblStudentAttitude where lesson_2 = 'A' group by idStudent) sa2 on s.idStudent = sa2.idStudent 
left join (select idStudent, count(lesson_1) * 2 as Count3 from tblStudentAttitude group by idStudent) sa3 on s.idStudent = sa3.idStudent
where left(s.class,1) in (1,2,3,4,5)
order by class, numberClass