select class, numberClass, nameEnglish, nameChinese, z1.score_final / 10.0, z2.score_final / 10.0, (z2.score_final - z1.score_final) / 10.0 as score_diff
from tblZStudentRank z2
inner join db04_05..tblZStudentRank z1 on z1.idStudent = z2.idStudent and z2.score_final > 0
inner join tblStudent s on z2.idStudent = s.idStudent
order by score_diff desc