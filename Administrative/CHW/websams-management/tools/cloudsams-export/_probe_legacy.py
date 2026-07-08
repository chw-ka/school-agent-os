import pyodbc

CONN = (
    "DRIVER={ODBC Driver 13 for SQL Server};"
    "SERVER=10.103.16.21;DATABASE=db25_26;UID=sa;PWD=sql2admin"
)
sql = """
SELECT s.numberClass, sps.idPaper, sps.score_exam_1, sps.grade_exam_1,
       sps.flgIgnore_1, sps.flgAbsent_1
FROM dbo.tblStudent s
JOIN dbo.tblStudentPaperScore sps ON sps.idStudent = s.idStudent
WHERE s.class = ? AND sps.idPaper IN ('CHI','ENG','MTH','CES')
ORDER BY s.numberClass, sps.idPaper
"""
with pyodbc.connect(CONN) as conn:
    cur = conn.cursor()
    cur.execute(sql, ("1A",))
    for row in cur.fetchall():
        if row[0] <= 5 or row[5] or row[4] or str(row[2]) == "AB":
            print(row)
