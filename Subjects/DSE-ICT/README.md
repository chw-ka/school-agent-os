# DSE-ICT

DSE 資訊及通訊科技（ICT）共用參考庫 — 適用於 F4–F6（S4–S6）出卷與備課。

此資料夾存放**考評局／教育局官方文件**，不屬於任何單一級別。校內試卷、Mock、教學筆記請放在各級別工作區（`S4-ICT/`、`S5-ICT/`、`S6-ICT/`）。

## 結構

- `past-papers/`：DSE 官方歷屆卷 PDF（描述性檔名，例如 `DSE_ICT_2019_Paper2A_Database.pdf` = 卷二甲 數據庫）
- `question-bank/`：OCR 及結構化題目 JSON（**出卷參考時讀這裡，毋須每次 OCR**）
- `edb/`：教育局課程及評估指引等官方文件

## 建立題庫（一次性）

```bash
pip install -r requirements-ocr.txt
python shared-tools/pdf-engine/build_dse_ict_question_bank.py
```

預設使用 **PaddleOCR**（適合掃描卷、繁體中文準確度優於 Tesseract）。詳見 `shared-tools/pdf-engine/README.md`。

## 出卷用途

結構化 JSON 係 **DSE 藍本抽題** 嘅來源（見 `shared-tools/paper-generator/F5_ICT_DSE_BLUEPRINT_FLOW.md`）。

**現況（2026-05）：** 只有 `2019/Paper1_MultipleChoice/questions.json`；Paper2A Database 及其他年份仍待建立。

若題目結構仍唔準（常見於雙欄 MCQ 掃描），可以 **一次性** 用 LLM 修正並快取：

```bash
set GOOGLE_API_KEY=your-key-from-aistudio
python shared-tools/pdf-engine/refine_dse_ict_question_bank.py --years 2019 --slugs Paper1_MultipleChoice --provider gemini --mode vision
```

輸出 `questions_refined.json`；`needs_review=true` 的題目建議人手覆核後先用作出卷參考。
