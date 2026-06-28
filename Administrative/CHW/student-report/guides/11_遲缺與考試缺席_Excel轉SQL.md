# 11. 遲缺與考試缺席：Excel → SQL（25-26 起）

**資料夾**

| 學年 | 來源 Excel | 去年 Excel Generate SQL（參考） |
|------|------------|--------------------------------|
| 24-25 | `T:\24-25\...\Datafile\24_25_Term2\Datafile\` | `T:\24-25\...\24_25_Term2\A_Done_SQL_Term2_DisciplineRecord.xls`、`A_Done_SQL_Term2_Exempt_Absent.xlsx` |
| 25-26 | `T:\25-26\...\Datafile\25_26_Term2\Datafile\` | **改為** 專案腳本直接出 `.sql`（見下） |

---

## 24-25 實際做法（對照）

### A. 遲缺、缺點、缺席日數、功課欠交

| 步驟 | 說明 |
|------|------|
| 1 | PY／PC 提供 `2024-25_S1_S5_2nd Term.xlsx`（在 `Datafile\`） |
| 2 | 複製到 `A_Done_SQL_Term2_DisciplineRecord.xls` 的 `S1-5_DisciplineRecord` 工作表（或公式自動帶） |
| 3 | 用 `StudentList` 工作表 VLOOKUP `idStudent` |
| 4 | 公式欄 **SQL** 產生每行 `UPDATE` |

**寫入目標**：`tblStudentDiscipline`（下學期欄位）

| Excel 欄（24-25 來源列） | DB 欄位 | 備註 |
|--------------------------|---------|------|
| 缺席下學期 | `dayAbsent_2` | `real`，可有小數 |
| 遲到下學期 | `numLate_2` | `smallint` |
| 因紀律／遲到 | `numDemeritDS_2` | |
| 因功課 | `numDemeritHW_2` | |
| 因欠交功課而被警告 `Y` | `flgHW_2` | `1`／`0` |
| 學生證號碼 | `WHERE idStudent = …` | |

**去年 SQL 範例**：

```sql
UPDATE tblStudentDiscipline
SET dayAbsent_2 = 1, numLate_2 = 1, numDemeritDS_2 = 0, numDemeritHW_2 = 0, flgHW_2 = 0
WHERE idStudent = 24147;
```

25-26 來源檔 `2025-26_S1_S5_2nd Term_V2.xlsx` 欄位與去年相同，只是欄位位置略調（缺席 col 16、遲到 col 15、`idStudent` col 17）。

---

### B. 考試缺席／豁免

| 步驟 | 說明 |
|------|------|
| 1 | 教務提供 `24-25_下學期考試缺席學生名單.xlsx` |
| 2 | **人工**把每科「考試卷名稱」對應為 `idPaper`（如 `EG1`、`CH4`），輸入 `A_Done_SQL_Term2_Exempt_Absent.xlsx` |
| 3 | `StudentList` VLOOKUP `idStudent`；欄 **缺席** `1` → `flgAbsent_2`；欄 **免考** `1` → `flgIgnore_2` |
| 4 | 公式產生 SQL |

**寫入目標**：`tblStudentPaperScore`

| 情況 | SQL 效果 |
|------|----------|
| 缺席 | `score_exam_2 = 0, flgAbsent_2 = 1` |
| 免考／豁免 | `score_exam_2 = 0, flgIgnore_2 = 1` |

**去年 SQL 範例**：

```sql
UPDATE tblStudentPaperScore
SET score_exam_2 = 0, flgAbsent_2 = 1
WHERE idStudent = 19100 AND idPaper = 'EG1';
```

去年約 **105** 條（缺席 100、豁免 5）。同一行 col「沒有考／遲到」col 7、col 8 可對應**兩個** `idPaper`。

---

## 25-26 計劃（唔再用 Excel Generate SQL）

### 工具位置

```
shared-tools/student-report/generate_term2_discipline_absent_sql.py
shared-tools/student-report/data/exam_subject_label_to_idpaper_2526.csv   ← 考試卷名 → idPaper 對照（可逐年複製修改）
```

### 執行

```powershell
cd c:\Users\localadmin\Projects\school-agent-os
python shared-tools/student-report/generate_term2_discipline_absent_sql.py
```

預設讀取：

- `T:\25-26\ITAdmin_13_StudentReport\Datafile\25_26_Term2\Datafile\2025-26_S1_S5_2nd Term_V2.xlsx`
- `T:\25-26\ITAdmin_13_StudentReport\Datafile\25_26_Term2\Datafile\25-26_下學期考試缺席學生名單.xlsx`

輸出至：

- `T:\25-26\ITAdmin_13_StudentReport\Datafile\25_26_Term2\SQL\01_Update_tblStudentDiscipline_term2.sql`
- `T:\25-26\ITAdmin_13_StudentReport\Datafile\25_26_Term2\SQL\02_Update_tblStudentPaperScore_exam_absent_term2.sql`
- `...\SQL\02_unmapped_exam_labels.txt`（如有對唔到嘅卷名）

### 建議執行順序（SSMS）

1. **備份**（可選）：`SELECT * INTO _bak_tblStudentDiscipline_YYYYMMDD FROM tblStudentDiscipline`
2. 執行 `01_Update_tblStudentDiscipline_term2.sql`
3. 抽查：`Check Record Entries (term 2).sql` 操行矛盾段（遲缺寫入後、操行入之前）
4. 確認 `02_unmapped_exam_labels.txt` 為空或已人手處理
5. 執行 `02_Update_tblStudentPaperScore_exam_absent_term2.sql`
6. 抽查：缺席生是否 `flgAbsent_2=1` 且 `score_exam_2=0`；有分數者不應誤標缺席

### 考試缺席注意（25-26 檔較複雜）

`25-26_下學期考試缺席學生名單.xlsx` 除左每行 **主區塊**（date + 班別 + 學號 + col7／col8 卷名）外，闊欄 **14–39** 會為**長缺**學生列出多科缺席；腳本會一併掃描。

**卷名 → `idPaper` 必須按班別（form）對應**（例：S1–3 的 `Eng 1 (GE)` → `EG1`；S4+ 的 `Eng 1 (Reading)` → `EG1`）。對照表在 `shared-tools/student-report/data/exam_subject_label_to_idpaper_2526.csv`；對唔到會寫入 `02_unmapped_exam_labels.txt` 俾教務補完再 rerun。

**長缺日數**（col 45「下學期缺席日數」）屬 `tblStudentDiscipline.dayAbsent_2`，在 **遲缺檔** 處理，唔喺考試缺席 SQL 重複寫。

**考試遲到**（col 5 `late`）：去年多數唔寫入 `tblStudentPaperScore`；若教務有特別顯示要求，再另議（或寫入 SpecialCases）。

---

## 與整體 Workflow 的關係

見 `10_行政分工_下學期時序與聯絡.md` 階段 **A2／A2b／A5**：

- 本指引 = **A2 + A5 的 IT 落地**
- 執行時機：與老師核對分數並行；**計分（步驟 5）之前**必須完成
- 完成後才可跑 `_獎項計算.sql` 同正式計分

---

*建立：2026-06*
