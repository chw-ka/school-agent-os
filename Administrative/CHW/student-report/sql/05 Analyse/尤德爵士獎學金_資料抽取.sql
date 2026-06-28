-- 尤德爵士獎學金
select s.idStudent, s.class, s.numberClass, s.nameChinese, a.rankForm, b.rankForm, d.conduct_1_1, d.conduct_2_1, d.conduct_3_1, d.conduct_4_1, d.conduct_1_2, d.conduct_2_2, d.conduct_3_2, d.conduct_4_2 from tblStudent s
left join db19_20.dbo.tblZStudentRank2 a on s.idStudent = a.idStudent and a.term = 0 and a.section = 'O' and a.flgStandard = 0 and a.idPaper = ''
left join db19_20.dbo.tblZStudentRank2 b on s.idStudent = b.idStudent and b.term = 0 and b.section = 'O' and b.flgStandard = 1 and b.idPaper = ''
left join db19_20.dbo.tblStudentConduct c on s.idStudent = c.idStudent
left join db19_20.dbo.tblStudentConduct d on d.idStudent = s.idStudent
where (s.class = '6A' and s.numberClass in (23, 3)) or
      (s.class = '6B' and s.numberClass in (23,20)) or 
	  (s.class = '6C' and s.numberClass in (6,4)) or
	  (s.class = '6D' and s.numberClass in (19,14))
order by s.class, s.numberClass desc


-- 明日之星獎學金
select s.idStudent, s.class, s.numberClass, s.nameChinese, a.score / 100.0, b.conduct_1_1, conduct_2_1, conduct_3_1, conduct_4_1 from tblStudent s
left join tblZStudentRank2 a on a.idStudent = s.idStudent and a.term = 1 and a.section = 'O' and a.flgStandard = 0 and a.idPaper = ''
left join tblStudentConduct b on b.idStudent = s.idStudent
where (s.class = '2B' and s.numberClass = 11) or
      (s.class = '2C' and s.numberClass = 12) or
      (s.class = '3B' and s.numberClass = 24) or
      (s.class = '3D' and s.numberClass = 2) or
      (s.class = '3E' and s.numberClass = 1)      
order by s.class, s.numberClass


-- 操行全 A, 參考上課表現評級
select s.idStudent, s.class, s.numberClass, s.nameChinese, x.conduct_1_2, x.conduct_2_2, x.conduct_3_2, x.conduct_4_2, a.CountA, b.CountB, c.CountC, d.CountD from tblStudent s
left join db19_20.dbo.tblStudentConduct x on s.idStudent = x.idStudent
left join (select idStudent, count(*) as CountA from db19_20.dbo.tblStudentAttitude where lesson_2 = 'A' group by idStudent) a on s.idStudent = a.idStudent 
left join (select idStudent, count(*) as CountB from db19_20.dbo.tblStudentAttitude where lesson_2 = 'B' group by idStudent) b on s.idStudent = b.idStudent 
left join (select idStudent, count(*) as CountC from db19_20.dbo.tblStudentAttitude where lesson_2 = 'C' group by idStudent) c on s.idStudent = c.idStudent 
left join (select idStudent, count(*) as CountD from db19_20.dbo.tblStudentAttitude where lesson_2 = 'D' group by idStudent) d on s.idStudent = d.idStudent 
where x.conduct_1_2 = 'A' and x.conduct_2_2 = 'A' and x.conduct_3_2 = 'A' and x.conduct_4_2 = 'A'
order by s.class, s.numberClass


