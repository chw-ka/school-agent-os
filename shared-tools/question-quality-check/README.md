# question-quality-check

題目品質檢查：撞題、考核概念、答案鍵分佈與隨機性。

> **出卷流程命名（2026-05）：** 在 F5 ICT skill 中稱 **question_review**（本目錄程式名暫不改）。  
> **concept_review** / **paper_review** 見 `.cursor/skills/generate-f5-ict-exam/SKILL.md` 與 `F5_ICT_CONCEPT_GENERATE_FLOW.md`。  
> 目標：bank 唔抄題 → generate spec → 本工具做 question_review；pick-time similarity gate 將移除。

## 檢查項目

| 檢查 | 說明 |
|------|------|
| **Duplicates** | 與原稿／過往試卷比對；甲部 MCQ **> 60%** 視為同一題 |
| **Written (乙／丙)** | 整條 **> 60%**；子題 `(a)(b)(i)…` **> 85%**（見 `written_similarity.py`） |
| **Concepts** | 與原稿 spec 比對 `concepts`；`meta.concept_targets` 分佈 |
| **MCQ balance** | 甲部 A–D 分佈均勻 |
| **Answer patterns** | MCQ／配對／T-F／供詞填充答案不可有規律（一般 MCQ 打亂選項；**組合選項題**按 (1)→(1)(2)→…→「皆是」排 A→D，唔 random shuffle） |
| **Coherence（通順）** | 禁止改編橋接句、主題硬拼（SQL+多媒體）、子題順序錯亂、孤兒 (ii) 等 |
| **Written spec ↔ DOCX** | 乙／丙每 slot：spec `text` 與 DOCX 段落 span 相似度 **≥ 92%**（`written_spec_docx_check.py`） |
| **Answer verify** | 甲部有答案；有 `dse_source` 時對照 bank（改寫題標「與原題不同」供人工確認）；乙丙標示缺 model answer 的來源 |

說明圖解見 [`../paper-generator/EXAM_SPEC_AND_DOCX.md`](../paper-generator/EXAM_SPEC_AND_DOCX.md)。

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
