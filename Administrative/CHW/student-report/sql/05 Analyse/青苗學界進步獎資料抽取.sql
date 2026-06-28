select s.idStudent, s.class, s.numberClass, s.nameEnglish, s.nameChinese, s.gender, sa.conduct_1_1, sa.conduct_2_1, sa.conduct_3_1, sa.conduct_4_1, sa.conduct_1_2, sa.conduct_2_2, sa.conduct_3_2, sa.conduct_4_2, a.score / 100, b.score / 100, b.score/100-a.score/100 from tblStudent s
left join tblStudentConduct sa on s.idStudent = sa.idStudent
left join tblZStudentRank2 a on a.idStudent = s.idStudent and a.idPaper = '' and a.flgStandard = 0 and a.section = 'O' and a.term = 1
left join tblZStudentRank2 b on b.idStudent = s.idStudent and b.idPaper = '' and b.flgStandard = 0 and b.section = 'O' and b.term = 2
where 
	  --(s.class = '1A' and s.numberClass = 17) or
	  --(s.class = '1B' and s.numberClass = 11) or
	  --(s.class = '1C' and s.numberClass = 13) or
	  --(s.class = '1D' and s.numberClass = 29) or
	  --(s.class = '2A' and s.numberClass = 1) or
	  --(s.class = '2B' and s.numberClass = 22) or
	  --(s.class = '2C' and s.numberClass = 13) or
	  --(s.class = '2D' and s.numberClass = 2) or
	  --(s.class = '2E' and s.numberClass = 1) or
	  --(s.class = '3A' and s.numberClass = 3) or
	  --(s.class = '3B' and s.numberClass = 25) or
	  --(s.class = '3C' and s.numberClass = 10) or
	  --(s.class = '3D' and s.numberClass = 20) or
	  --(s.class = '3E' and s.numberClass = 6) or
	  --(s.class = '4A' and s.numberClass = 21) or
	  --(s.class = '4B' and s.numberClass = 3) or
	  --(s.class = '4C' and s.numberClass = 5) or
	  --(s.class = '4D' and s.numberClass = 2) or
	  (s.class = '5A' and s.numberClass = 9) or
	  (s.class = '5B' and s.numberClass = 24) or
	  (s.class = '5C' and s.numberClass = 4) or
	  (s.class = '5D' and s.numberClass = 19) 
order by s.class, s.numberClass


