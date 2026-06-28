select b.idStudent, b.class, b.numberClass, b.nameChinese, a.score, a.rankForm, round(c.score / 100.0,0) as CHI, round(d.score / 100.0,0) as ENG, round(e.score / 100.0,0) as MTH, round(f.score / 100.0,0) as LST from tblZStudentRank2 a
left join tblStudent b on a.idStudent = b.idStudent
left join tblZStudentRank2 c on c.idStudent = a.idStudent and c.flgStandard = 0 and c.idPaper = 'CHI' and c.section = 'O' and c.term = 0
left join tblZStudentRank2 d on d.idStudent = a.idStudent and d.flgStandard = 0 and d.idPaper = 'ENG' and d.section = 'O' and d.term = 0
left join tblZStudentRank2 e on e.idStudent = a.idStudent and e.flgStandard = 0 and e.idPaper = 'MTH' and e.section = 'O' and e.term = 0
left join tblZStudentRank2 f on f.idStudent = a.idStudent and f.flgStandard = 0 and f.idPaper = 'LST' and f.section = 'O' and f.term = 0
where a.idStudent in (select idStudent from tblStudent where left(class,1) = 6) and a.flgStandard = 1 and a.idPaper = '' and a.section = 'O' and a.term = 0 and a.rankForm <= 10
order by a.rankForm