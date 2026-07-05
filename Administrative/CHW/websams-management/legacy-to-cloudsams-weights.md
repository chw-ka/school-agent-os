# Legacy MSSQL → CloudSAMS 科目滿分及比重 mapping

Source: `db25_26` via `T:\25-26\ITAdmin_13_StudentReport\_Program\Summaries\connection.txt`

## Blocked subjects (2026-07-06)

| CloudSAMS name | Legacy `idPaper` | Forms | Legacy `fpw.weight` → CloudSAMS 科目比重 | Legacy max → CloudSAMS 滿分 |
|---|---|---|---|---|
| 公民、經濟與社會 | CES | S1, S2 | **50** | **100** (scale; legacy components 30/70 regular/exam) |
| 普通電腦科 | CMP | S1, S2, S3 | **50** | **100** (legacy 100% regular only) |

## Legacy detail (term 1 & 2 identical weights)

```
form  idPaper  weight  w_reg  w_exam  max_reg_t1  max_exam_t1  max_reg_t2  max_exam_t2
1     CES      50      30     70      30          40           30          48
1     CMP      50      100    0       100         NULL         100         NULL
2     CES      50      30     70      30          44           30          48
2     CMP      50      100    0       100         NULL         100         NULL
3     CMP      50      100    0       100         NULL         100         NULL
```

Reference (passing validation): 數學 MTH → 滿分 100, 科目比重 300 (= legacy `weight`).

## CloudSAMS UI path

`學生成績 → 設定 → 科目滿分及比重 → 搜尋 → [S-ASR03-02 edit grid]`

Fields per subject row:

| Column | Value for CES/CMP |
|--------|-------------------|
| 滿分 | 100 |
| 科目比重 | 50 |
| 積分/等級互換表 | Global Grade Table (38) — **not** Conduct Grade Table (40) for CES |

**All 7 periods** must be filled: T1A1, T1A2, T1, T2A1, T2A2, T2, 年終.

## Save gotcha

**儲存 opens PrimeFaces confirm dialog** (`確定儲存紀錄?`). Must click **Confirm** (`.ui-confirmdialog-yes`) or save is discarded.

## SQL to re-query legacy weights

```sql
SELECT p.formGroup, p.idPaper, p.nameEnglish,
  fpw.weight, fpw.weight_regular_1, fpw.weight_exam_1,
  fpw.weight_regular_2, fpw.weight_exam_2,
  fps.score_regular_1, fps.score_exam_1,
  fps.score_regular_2, fps.score_exam_2
FROM tblPaper p
INNER JOIN tblFormPaperWeight fpw ON fpw.idPaper = p.idPaper AND fpw.form = p.formGroup
INNER JOIN tblFormPaperScore fps ON fps.idPaper = p.idPaper AND fps.form = p.formGroup
WHERE p.formGroup IN (1,2,3) AND p.idPaper IN ('CES','CMP')
ORDER BY p.formGroup, p.idPaper;
```
