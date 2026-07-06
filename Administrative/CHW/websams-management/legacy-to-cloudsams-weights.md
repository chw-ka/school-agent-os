# Legacy MSSQL → CloudSAMS mapping

Source: `db25_26` via `T:\25-26\ITAdmin_13_StudentReport\_Program\Summaries\connection.txt`

## Two screens — do not mix them

| Screen | What it controls | CES example |
|--------|------------------|---------------|
| **科目滿分及比重** (Subject Full Score) | 滿分 + 科目比重 per period | 滿分 **100**, 科目比重 **50** on every assessed period |
| **學期及考績** (Term & Assessment) | Weight ratio across T1/T2/T1A1/T1A2/T2A1/T2A2 | **`1, 1, 3, 7, 3, 7`** (T1A1:T1A2 = 3:7 = legacy 30:70) |

**CES has no 分卷 (paper components).** Only 中文 and 英文 have component rows. The legacy 30/70 regular:exam split is **not** entered in Subject Full Score — it is the **T1A1:T1A2 ratio**, entered as **3/7** in Term & Assessment.

## Blocked subjects (2026-07-06)

| CloudSAMS name | Legacy `idPaper` | Forms | Subject Full Score | Term & Assessment |
|---|---|---|---|---|
| 公民、經濟與社會 | CES | S1, S2 | 滿分 **100**, 科目比重 **50** on all assessed periods | `1, 1, 3, 7, 3, 7` |
| 普通電腦科 | CMP | S1, S2, S3 | Term-total only — see archetype A | `1, 1, 0, 1, 0, 1` (grade-only pattern) or term-only as per subject |

## CloudSAMS period ↔ legacy MSSQL mapping

| CloudSAMS 考績/學期 | Code | Legacy columns |
|---------------------|------|----------------|
| T1A1 上學期平時 | 1101 | `score_regular_1`, `weight_regular_1` |
| T1A2 上學期考試 | 1102 | `score_exam_1`, `weight_exam_1` |
| T1 上學期總分 | 1100 | 滿分 **100**, 科目比重 **`weight`** (50) |
| T2A1 下學期平時 | 1201 | `score_regular_2`, `weight_regular_2` |
| T2A2 下學期考試 | 1202 | `score_exam_2`, `weight_exam_2` |
| T2 下學期總分 | 1200 | 滿分 **100**, 科目比重 **`weight`** (50) |
| 年終 | 1000 | 滿分 **100**, 科目比重 **50**, plus **列印次序** |

## Assessment archetypes (report-driven)

Configure from **what the report card shows**, not by blindly copying legacy MSSQL columns into the wrong CloudSAMS screen.

### A. Term-total only (no 平時/考試 on report)

**Subjects:** 普通電腦科 (CMP), 聖經 (BBS), 視覺藝術 (ART), 音樂 (MUS), 體育 (PED)

| Period | Subject Full Score: 考核 | 滿分 | 科目比重 |
|--------|--------------------------|------|----------|
| T1A1, T1A2, T2A1, T2A2 | **N** | blank | 0 |
| T1, T2, 年終 | **Y** | **100** | legacy `weight` (CMP = 50) |

### B. Regular + exam split (平時分 + 考試分 on report)

**Subjects:** CES (S1/S2), most numeric subjects.

**Subject Full Score** — same on every assessed period (no 分卷 rows for CES):

| Period | 考核 | 滿分 | 科目比重 |
|--------|------|------|----------|
| T1A1, T1A2, T2A1, T2A2, T1, T2, 年終 | Y (where assessed) | **100** | **50** (CES) |

**Term & Assessment** — carries the T1A1:T1A2 regular:exam ratio:

| Columns | CES value | Meaning |
|---------|-----------|---------|
| T1, T2, T1A1, T1A2, T2A1, T2A2 | `1, 1, 3, 7, 3, 7` | Legacy 30:70 → **3:7** between T1A1 and T1A2 (and T2A1:T2A2) |

### C. Paper components (分卷) — 中文 / 英文 only

Only Chinese and English subjects have **分卷** rows in Subject Full Score. CES does **not**.

### D. Term-exclusive history (S3)

| Subject | T1 (1101/1102/1100) | T2 (1201/1202/1200) |
|---------|---------------------|----------------------|
| **中國歷史 CHT** | 平時+考試 **Y** | **考核 N** on all T2 periods |
| **歷史 HST** | **考核 N** on all T1 periods | 平時+考試 **Y** |

## Legacy detail (from `db25_26`, 2026-07-06)

```
form  idPaper  weight  w_reg  w_exam  max_reg_t1  max_exam_t1  max_reg_t2  max_exam_t2
1     CES      50      30     70      30          40           30          48
1     CMP      50      100    0       100         NULL         100         NULL
2     CES      50      30     70      30          44           30          48
2     CMP      50      100    0       100         NULL         100         NULL
3     CMP      50      100    0       100         NULL         100         NULL
```

- `weight` (50) → CloudSAMS **科目比重** on Subject Full Score
- `w_reg` / `w_exam` (30/70) → CloudSAMS **學期及考績** as **3/7**, not Subject Full Score

**年終 列印次序 (user set):** CES **31**, CMP **90** (S1–S3).

Machine-readable fill spec: `_generation/ces-cmp-cloudsams-period-map.json`.

Reference (passing validation): 數學 MTH → 滿分 100 and 科目比重 = legacy `weight` (300) on every period.

## CloudSAMS UI paths

| Screen | Path |
|--------|------|
| Subject Full Score | `學生成績 → 設定 → 科目滿分及比重` |
| Term & Assessment | `學生成績 → 設定 → 學期及考績` |

### Subject Full Score fields (CES — single subject row, no 分卷)

| Column | UI field | CES rule |
|--------|----------|----------|
| 滿分 | `j_idt175` | **100** when 考核 Y |
| 科目比重 | `j_idt184` | **50** on every assessed period |
| 積分/等級互換表 | `j_idt178` | Global Grade Table (38) — **not** Conduct (40) |
| 列印次序 | 年終 only | CES = **31** |

### Term & Assessment fields (CES)

Grid columns T1, T2, T1A1, T1A2, T2A1, T2A2 → enter **`1, 1, 3, 7, 3, 7`**.

**All 7 periods** must be filled per class on Subject Full Score. **Do not use 複製紀錄** across forms.

## Save gotcha

**儲存 opens PrimeFaces confirm dialog** (`確定儲存紀錄?`). Must click **Confirm** and see **“Record saved successfully.”** — red `E-46xxx` banner means nothing persisted.

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
