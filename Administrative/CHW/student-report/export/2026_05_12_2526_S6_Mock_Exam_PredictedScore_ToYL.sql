SELECT
  st.class AS Class,
  st.numberClass AS ClassNo,
  st.idStudent AS StudentID,
  st.nameChinese AS ChineseName,
  st.nameEnglish AS EnglishName,
  MAX(CASE WHEN zr.idPaper = 'ENG' THEN ROUND(zr.score / 100.0, 2) END) AS ENG,
  MAX(CASE WHEN zr.idPaper = 'CHI' THEN ROUND(zr.score / 100.0, 2) END) AS CHI,
  MAX(CASE WHEN zr.idPaper = 'MTH' THEN ROUND(zr.score / 100.0, 2) END) AS MTH,
  MAX(CASE WHEN zr.idPaper = 'CSD' THEN ROUND(zr.score / 100.0, 2) END) AS CSD,
  MAX(CASE WHEN zr.idPaper = 'MM2' THEN ROUND(zr.score / 100.0, 2) END) AS MM2,
  MAX(CASE WHEN zr.idPaper = 'ICT' THEN ROUND(zr.score / 100.0, 2) END) AS ICT,
  MAX(CASE WHEN zr.idPaper = 'THS' THEN ROUND(zr.score / 100.0, 2) END) AS THS,
  MAX(CASE WHEN zr.idPaper = 'PHY' THEN ROUND(zr.score / 100.0, 2) END) AS PHY,
  MAX(CASE WHEN zr.idPaper = 'CHM' THEN ROUND(zr.score / 100.0, 2) END) AS CHM,
  MAX(CASE WHEN zr.idPaper = 'BIO' THEN ROUND(zr.score / 100.0, 2) END) AS BIO,
  MAX(CASE WHEN zr.idPaper = 'CHT' THEN ROUND(zr.score / 100.0, 2) END) AS CHT,
  MAX(CASE WHEN zr.idPaper = 'CLT' THEN ROUND(zr.score / 100.0, 2) END) AS CLT,
  MAX(CASE WHEN zr.idPaper = 'HST' THEN ROUND(zr.score / 100.0, 2) END) AS HST,
  MAX(CASE WHEN zr.idPaper = 'GEO' THEN ROUND(zr.score / 100.0, 2) END) AS GEO,
  MAX(CASE WHEN zr.idPaper = 'ECO' THEN ROUND(zr.score / 100.0, 2) END) AS ECO,
  MAX(CASE WHEN zr.idPaper = 'BAF' THEN ROUND(zr.score / 100.0, 2) END) AS BAF,
  MAX(CASE WHEN zr.idPaper = 'ART' THEN ROUND(zr.score / 100.0, 2) END) AS ART
FROM dbo.tblStudent st
INNER JOIN dbo.tblZStudentRank2 zr ON zr.idStudent = st.idStudent
INNER JOIN dbo.tblSubject subj ON subj.idSubject = zr.idPaper
WHERE st.class LIKE '6%'
  AND zr.term = 2
  AND zr.section = 'E'
  AND zr.flgStandard = 0
  AND zr.idPaper <> ''
GROUP BY st.class, st.numberClass, st.idStudent, st.nameChinese, st.nameEnglish
ORDER BY st.class, st.numberClass;