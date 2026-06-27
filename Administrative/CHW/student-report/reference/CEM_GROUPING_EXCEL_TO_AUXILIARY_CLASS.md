# 中一至中六：中英數分組名單 ↔ `auxiliaryClass` 對照

本文件記錄 **2525–26（db25_26）** 由 Excel 分組名單與 legacy `tblStudentSubject.auxiliaryClass` 對照後推斷嘅映射。用於步驟 1 核對修讀／分組。

**重要**：分組唔止中四英文／中五中文／中六數學——**中一、中四、中五**都有；而且 **中五、中六** 在 DB 內往往 **中/英/數三科共用同一套輔助班碼**（如 `5W`），但 **各科對應嘅 Excel 組別名單未必相同**。

技術背景：[`STUDENT_REPORT_SQL_TABLE_RELATIONSHIPS.md`](./STUDENT_REPORT_SQL_TABLE_RELATIONSHIPS.md)

---

## 按級別：邊科有分組？

| 級別 | Excel 名單（校內 T: Datafile） | DB `auxiliaryClass`（`flgTerm2=1`） |
|------|---------------------------|-------------------------------------|
| **中一** | 中文 + 英文（`2526_ 各級分組名單(下學期).xlsx`：`1A`–`1D`、`中一級`） | **CHI**、**ENG**（`1U`–`1Z`） |
| **中四** | **英文**（同上：`4A`–`4D`、`中四級`）；**數學** 進階／基礎（`2526_S4_數學分組_進階基礎.xlsx`） | **ENG**（`4U`–`4Z`）；**MTH**（`4U`–`4X`，按課室 501–504） |
| **中五** | **中文**（`2526_S5_中文分組_4月至期末分組名單_To MC.xlsx`）；**數學**（`2526_S5_數學分組_Term2.xlsx`） | **CHI**、**ENG**、**MTH**（`5V`–`5Z`） |
| **中六** | **數學** 進階／基礎（總表 `6A、6B`/`6C、6D`、`中六級`） | **CHI**、**ENG**、**MTH**（`6W`–`6Z`） |

---

## 對照表（Excel 組別 → DB 碼）

### 中一：中文

| Excel 組別 | `auxiliaryClass`（`CHI`） | 備註 |
|------------|---------------------------|------|
| 中文A組 | **1U** | |
| 中文B組 | **1V** | |
| 中文C組 | **1X** | 少數 **1Z** |
| 中文D組 | **1Y** | 少數 **1Z** |
| 中文X組 | **1W** | 跨班 X 組 |
| 中文Y組 | **1Z** | 跨 1C/1D Y 組；亦見 **1X**/**1Y** |

### 中一：英文

| Excel 組別 | `auxiliaryClass`（`ENG`） |
|------------|---------------------------|
| 英文A組 | **1U** |
| 英文B組 | **1V** |
| 英文C組 | **1X** |
| 英文X組 | **1W** |
| 英文Y組 | **1Z** |

中一英文：有出現在分組名單嘅學生，與 DB 對照 **一致**（2026-04 核對）。

### 中四：英文

| Excel 組別 | `auxiliaryClass`（`ENG`） |
|------------|---------------------------|
| 英文A組 | **4U** |
| 英文B組 | **4V** |
| 英文C組 | **4X** |
| 英文D組 | **4Y** |
| 英文X組 | **4W** |
| 英文Y組 | **4Z** |

中四英文：名單有列出嘅學生與 DB **100% 一致**（2026-04 核對）。

### 中四：數學

| Excel 組別（課室） | `auxiliaryClass`（`MTH`） |
|--------------------|---------------------------|
| 進階（501 室） | **4U** |
| 基礎（502 室） | **4V** |
| 進階（503 室） | **4W** |
| 基礎（504 室） | **4X** |

來源：`2526_S4_數學分組_進階基礎.xlsx`（數學科 2026-06 提供）。

### 中五：中文

| Excel 組別（4 月中文表） | `auxiliaryClass`（`CHI`） |
|--------------------------|---------------------------|
| 5AB一組 | **5W** |
| 5AB二組 | **5V** |
| 5C | **5X** |
| 5D | **5Y** |
| 5Y | **5Z**（部分 DB 仍為 **5Y**） |

約 30 人個別記錄不符多數規則 → 用下方「查 DB」SQL 逐班核對 `CHI` + `auxiliaryClass`。

### 中五：數學

| Excel 組別 | `auxiliaryClass`（`MTH`） |
|------------|---------------------------|
| 5AB 進階班 | **5W** |
| 5AB 基礎班 | **5X** |
| 5CD 進階班 | **5Y** |
| 5CD 基礎班 | **5Z** |

來源：`2526_S5_數學分組_Term2.xlsx`（數學科 2026-06 提供）。**勿**用中文分組表標籤推 MTH 碼。

### 中五：英文、數學（僅 DB 碼 — 舊備註）

校內英文分組 Excel 仍缺時以 DB 為準；數學已見上表。

| 科目 | 可能嘅 `auxiliaryClass` |
|------|-------------------------|
| ENG | **5W**、**5X**、**5Y**、**5Z** |
| MTH | **5W**、**5X**、**5Y**、**5Z** |

**勿**用中五**中文**表嘅「5AB一組」等標籤直接推英文／數學碼——同一學生三科碼可以唔同（例：CHI=`5V`、ENG=`5W`、MTH=`5W`）。要核對 ENG/MTH 須另有教務名單或逐人查 DB。

### 中六：數學

| Excel 組別 | `auxiliaryClass`（`MTH`） |
|------------|---------------------------|
| 6AB 進階班 | **6W** |
| 6AB 基礎班 | **6X** |
| 6CD 進階班 | **6Y** |
| 6CD 基礎班 | **6Z** |

### 中六：中文、英文（僅 DB 碼）

DB 亦有 **CHI**、**ENG** 的 `6W`–`6Z`；Excel 總表以**數學**分組為主，中/英要查 DB 或另備名單。

---

## 資料來源與產物

Excel 名單存放於校內 `T:\25-26\ITAdmin_13_StudentReport\Datafile\`（或科組提供嘅分組 Excel）。逐人比對可即場用下方 SQL 查 DB，唔需要保留 CSV 快照。

| 用途 | 做法 |
|------|------|
| 完整對照表 | 見本文各級表格；必要時由 Excel + MCP 查 DB 重新核對 |
| 中四至六逐人比對 | MCP 執行下方「查 DB」SQL，與 Excel 人手或腳本比對 |
| 選修科 | 查 `tblStudentSubject` 或 CHW API |

### Excel 名單建議

| 級別 | 檔案 | Sheet |
|------|------|-------|
| 中一 中/英 | `2526_ 各級分組名單(下學期).xlsx` | `1A`–`1D`、`中一級` |
| 中四 英文 | 同上 | `4A`–`4D`、`中四級` |
| 中五 中文 | `2526_S5_中文分組_4月至期末分組名單_To MC.xlsx` | （優先） |
| 中六 數學 | `2526_ 各級分組名單(下學期).xlsx` | `6A、6B`、`6C、6D`、`中六級` |

選修科對照：查 DB 或 CHW API（見步驟 1 指引）

---

## 查 DB（只讀）

```sql
SELECT s.class, s.numberClass, s.nameChinese,
  MAX(CASE WHEN tss.idSubject = N'ENG' THEN RTRIM(tss.auxiliaryClass) END) AS eng_aux,
  MAX(CASE WHEN tss.idSubject = N'CHI' THEN RTRIM(tss.auxiliaryClass) END) AS chi_aux,
  MAX(CASE WHEN tss.idSubject = N'MTH' THEN RTRIM(tss.auxiliaryClass) END) AS mth_aux
FROM dbo.tblStudent s
JOIN dbo.tblStudentSubject tss ON tss.idStudent = s.idStudent
WHERE LEFT(s.class, 1) IN (N'1', N'4', N'5', N'6')
  AND tss.idSubject IN (N'ENG', N'CHI', N'MTH')
  AND tss.flgTerm2 = 1
GROUP BY s.class, s.numberClass, s.nameChinese
ORDER BY s.class, s.numberClass;
```

---

## 修訂記錄

| 日期 | 說明 |
|------|------|
| 2026-04 | 初版（中四英／中五中／中六數） |
| 2026-04 | **補中一英中、中五英數 DB 碼、各級覆蓋表**；澄清中五勿用中文表推 ENG/MTH |

學年或分組改動後，請更新本文件與 `cem_excel_to_db_mapping.csv`；中四至六可重跑 `compare_cem_mssql.py`。
