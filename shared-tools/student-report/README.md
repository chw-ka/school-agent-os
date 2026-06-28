# Student report tools

成績表相關 CLI 工具。流程指引見 `Administrative/CHW/student-report/guides/`。

## 依賴

```powershell
pip install -r requirements-student-report.txt
```

Windows 上 `generate_class_score_summary_term2.py` 另需 Excel COM（`pywin32`）。

## 常用命令

### 遲缺／考試缺席 Excel → SQL

```powershell
python shared-tools/student-report/generate_term2_discipline_absent_sql.py
```

預設讀 `T:\25-26\ITAdmin_13_StudentReport\Datafile\25_26_Term2\Datafile\` 內 Excel，輸出 SQL 至同層 `SQL\`。
卷名 → `idPaper` 對照表：`shared-tools/student-report/data/exam_subject_label_to_idpaper_2526.csv`

### 缺席 UPDATE 前檢查

```powershell
python shared-tools/student-report/check_term2_absent_before_update.py
python shared-tools/student-report/check_term2_absent_batches.py
```

### 執行 T: 上已產生嘅 SQL 檔

```powershell
python shared-tools/student-report/run_term2_sql_files.py
```

## 資料位置

- **輸入 Excel**：`T:\25-26\ITAdmin_13_StudentReport\Datafile\25_26_Term2\Datafile\`
- **輸出 SQL**：`T:\25-26\ITAdmin_13_StudentReport\Datafile\25_26_Term2\SQL\`
- DB 連線讀 `T:\25-26\...\Summaries\connection.txt`（見 `_mssql_conn.py`）
- 所有路徑可用 CLI 參數覆寫；詳見各腳本 `--help` 或 docstring。
