# paper-quality-check

試卷版面／元資料品質檢查（已渲染 DOCX）。

## 檢查項目

| 檢查 | 說明 |
|------|------|
| **Footer** | 頁尾橫幅（學年、級別、科目）與 `meta.footer` 或檔名一致 |
| **Cover** | 封面（學年、級別、試題簿）與檔名推算一致 |
| **Written sections** | 乙部／丙部短答及長答：分題縮排、作答空白行、markdown 殘留、與範本 tab 深度 |

## 用法

```bash
.venv/bin/python shared-tools/paper-quality-check/check_docx.py \
  --candidate "路徑/新卷.docx" \
  --candidate-spec "路徑/新卷.spec.json"

# 或 spec + docx 一併
.venv/bin/python shared-tools/paper-quality-check/check_spec_cli.py \
  --candidate-spec "路徑/新卷.spec.json" \
  --candidate-docx "路徑/新卷.docx"
```

## 檔名推算

`25_26_S3_CMP_Term02_Exam.docx` → 2025–2026、中三級、下學期考試、電腦認知（見 `filename_meta.py`）。

## 相關工具

- **`../question-quality-check/`** — 撞題、概念、答案鍵
- **`../paper-generator/post_check.py`** — 合併執行兩套檢查
