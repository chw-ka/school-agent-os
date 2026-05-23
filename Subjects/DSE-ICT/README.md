# DSE-ICT

DSE 資訊及通訊科技（ICT）共用參考庫 — 適用於 F4–F6（S4–S6）出卷與備課。

此資料夾存放**考評局／教育局官方文件**，不屬於任何單一級別。校內試卷、Mock、教學筆記請放在各級別工作區（`S4-ICT/`、`S5-ICT/`、`S6-ICT/`）。

## 結構

- `past-papers/`：DSE 官方歷屆卷 PDF（按年份子資料夾；描述性檔名）
  - 2012–2023：`DSE_ICT_{year}_Paper1_MultipleChoice.pdf`、卷二 `Paper2A`–`Paper2D` 各選修冊
  - 2024+：`Paper1A_MultipleChoice`、`Paper1B_CompulsoryStructured`
  - 2025+：另加 `Paper2_Elective.pdf`（選修三選一合冊；舊制 2A–2D 分冊已停用）
  - 整理工具：`python shared-tools/pdf-engine/build_dse_ict_question_bank.py --rename-only`
- `gemini-output/`：Gemini 人手／半自動提取的原始 JSON（**文字版**，通常無圖片；匯入前的工作區）
- `question-bank/`：結構化題目 JSON（**出卷參考時讀這裡，毋須每次 OCR**）
  - `curriculum_concepts.json`：概念 tag 及新課程單元對照（依 `edb/ICT_C&A Guide_c_final.pdf`）
  - `concept_map.json`（目標，tree）：C&A + bank 統計 — 見 `F5_ICT_CONCEPT_GENERATE_FLOW.md` 🔲
  - `style_patterns.json`（目標）：問法／語法／專有名詞 patterns（唔係題目原文）🔲
  - `index.json`：各年份／試卷目錄
- `edb/`：教育局課程及評估指引等官方文件

## 建立題庫

### 方法 A — PDF OCR（掃描卷）

```bash
pip install -r requirements-ocr.txt
python shared-tools/pdf-engine/build_dse_ict_question_bank.py
```

預設使用 **PaddleOCR**（適合掃描卷、繁體中文準確度優於 Tesseract）。詳見 `shared-tools/pdf-engine/README.md`。

### 方法 B — Gemini JSON 匯入（文字提取）

若已用 Gemini 將試卷轉為 JSON（放在 `gemini-output/`），可一次匯入 question-bank：

```bash
python shared-tools/pdf-engine/import_gemini_question_bank.py
# 覆寫既有 gemini 匯入：
python shared-tools/pdf-engine/import_gemini_question_bank.py --force
# 只處理指定年份：
python shared-tools/pdf-engine/import_gemini_question_bank.py --years 2024 --force
```

**檔名對應：**

| `gemini-output/` 檔名 | question-bank slug |
|----------------------|-------------------|
| `{year}-p1.json` / `{year}-p1a.json` | `Paper1_MultipleChoice`（甲部 MCQ） |
| `{year}-p1b.json` | `Paper1B_CompulsoryStructured`（乙丙部） |
| `{year}-p2.json` | `Paper2_Elective`（2025+ 甲／乙／丙部合冊） |
| `{year}-p2a.json` | `Paper2A_Database` |
| `{year}-p2d.json` | `Paper2D_SoftwareDevelopment` |
| `{year}-ans.json` | `MarkingScheme` |

**合併卷分割規則（2021–2023 的 `p1.json`）：**

- `SectionA_Q*` 或純數字 MCQ → `Paper1_MultipleChoice`
- `SectionB_Q*` / `SectionC_Q*` / `1B-*` → `Paper1B_CompulsoryStructured`

**匯入原則（零資料遺失）：**

- 每題保留完整 `gemini_raw`（原始 Gemini 物件）
- 缺圖時在 `text` 加入 `[圖片描述] …`，並設 `image_description` / `has_image`
- **`support_content`**：匯入時自動補中間內容（偽代碼、`algorithm_code`、ASCII 表／示意）；見下方
- 短題、長題、`statements`、`answer_details`、`marking_notes` 等全部 migrate
- 自動加上 `concepts`、`curriculum_part`（必修／選修）、`curriculum_unit` tag
- **`syllabus_status`**：`current` / `out_of_syllabus`（依 2021 修訂課程；舊卷文書／簡報／OLE 等會標為 out）
- MCQ 答案從 `-ans.json` 合併至 `Paper1_MultipleChoice`

**重新標記題庫（syllabus + concepts）：**

```bash
python shared-tools/pdf-engine/retag_dse_ict_question_bank.py
```

**補中間內容（算法／試算表／示意，`support_content`）：**

Gemini JSON 常只留題幹同 options，中間嘅流程圖、試算表、偽代碼會漏。匯入時會自動嘗試補返；亦可手動跑：

```bash
# 現有 question-bank 一次過補（已 mark support_content）
python shared-tools/pdf-engine/enrich_dse_ict_support_content.py

# 只處理指定年份；強制重算
python shared-tools/pdf-engine/enrich_dse_ict_support_content.py --years 2024 2025 --force
```

每題若有補充，會有：

```json
"support_content": {
  "lines": ["偽代碼或 ASCII 表…"],
  "sources": ["gemini_raw.algorithm_code", "static_template:…"],
  "status": "auto",
  "supplemented_at": "…",
  "note": "Verify against PDF before publishing."
}
```

`status: needs_review` 表示只有 `[表格式意] …` 等粗略描述，建議對照 PDF 人手改。邏輯在 `shared-tools/pdf-engine/dse_ict_support_content.py`；出卷時 `f5_ict_from_dse.py` 會讀 `support_content.lines`。

**課程對照（2025–26 新課程）：**

- 概念 tag 依 `edb/ICT_C&A Guide_c_final.pdf`（必修 A–E、選修 A–C）
- 舊卷 Paper 2 對應：2A→選修數據庫、2D→算法與程式編寫；2B/2C→網絡應用程式開發相關

**後續補圖：** 帶 `[圖片描述]` 的題目可 copy 至 Banana Nano 等工具處理；處理完更新 `question-bank/` 即可，無須改 `gemini-output/`。

### 方法 C — LLM 修正 OCR（可選）

若 OCR 題目結構仍唔準（常見於雙欄 MCQ 掃描），可以 **一次性** 用 LLM 修正並快取：

```bash
set GOOGLE_API_KEY=your-key-from-aistudio
python shared-tools/pdf-engine/refine_dse_ict_question_bank.py --years 2019 --slugs Paper1_MultipleChoice --provider gemini --mode vision
```

輸出 `questions_refined.json`；`needs_review=true` 的題目建議人手覆核後先用作出卷參考。

## 出卷用途

結構化 JSON 係 **DSE 藍本抽題** 嘅來源（見 `shared-tools/paper-generator/F5_ICT_DSE_BLUEPRINT_FLOW.md`）。

**現況（2026-05）：**

| 來源 | 已建立 `questions.json` |
|------|-------------------------|
| Gemini 匯入 | 2021–2024：Paper1 MCQ、Paper1B、Paper2A/2D（視年份）、MarkingScheme |
| Gemini 匯入 | **2025–2026**：Paper1A MCQ、Paper1B、Paper2_Elective（含甲／乙／丙部細分題） |
| OCR | 2019 Paper1 MCQ；2024 部分試卷（已被 Gemini 匯入覆蓋） |

**仍待 Gemini JSON／OCR：** 各年 Paper2B、Paper2C；2023 Paper2D 等（見 `gemini-output/` 有無對應檔）。
