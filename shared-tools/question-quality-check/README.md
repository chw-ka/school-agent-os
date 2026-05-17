# question-quality-check

題目品質檢查：撞題、考核概念、答案鍵分佈與隨機性。

## 檢查項目

| 檢查 | 說明 |
|------|------|
| **Duplicates** | 與原稿／過往試卷比對；相似度 **> 60%** 視為同一題 |
| **Concepts** | 與原稿 spec 比對 `concepts`；`meta.concept_targets` 分佈 |
| **MCQ balance** | 甲部 A–D 分佈均勻 |
| **Answer patterns** | MCQ／配對／T-F／供詞填充答案不可有規律（一般 MCQ 打亂選項；**組合選項題**按 (1)→(1)(2)→…→「皆是」排 A→D，唔 random shuffle） |

## 用法

```bash
# Spec（出卷前）
.venv/bin/python shared-tools/question-quality-check/check_spec_cli.py \
  --candidate "路徑/新卷.spec.json" \
  --template "路徑/原稿.docx"

# DOCX（題目內容）
.venv/bin/python shared-tools/question-quality-check/check_docx.py \
  --candidate "路徑/新卷.docx" \
  --candidate-spec "路徑/新卷.spec.json" \
  --template "路徑/原稿.docx"
```

## Spec 格式

與 `exam_spec.py` 的 version 1 相同；`meta.mcq_answers`、`matching_answers`、`tf_answers`、`fill_answers` 等見 `answer_pattern_check.py`。

## 相關工具

- **`../paper-quality-check/`** — 頁尾、封面等試卷版面檢查
- **`../paper-generator/`** — 出卷後自動執行兩套檢查
