# pdf-engine

HKDSE / school PDF tools: OCR once, store structured questions for reuse.

## DSE ICT question bank

Official scanned papers live in `Subjects/DSE-ICT/past-papers/`.  
Structured output goes to `Subjects/DSE-ICT/question-bank/`.

### One-time setup (scanned PDFs)

For **scanned** DSE papers, use PaddleOCR (much better than Tesseract for Traditional Chinese):

```bash
pip install -r requirements-ocr.txt
```

This pins `paddlepaddle==2.6.2`, `paddleocr==2.7.3`, and `numpy<2` (required on Windows).

Optional fallback: install [Tesseract](https://github.com/tesseract-ocr/tesseract) with `chi_tra+eng` and pass `--ocr tesseract`.

Base deps: `pip install pymupdf` (see repo `requirements.txt`).

### Build the bank (OCR once)

```bash
# Rename legacy p1.pdf / p2a.pdf … if needed
python shared-tools/pdf-engine/build_dse_ict_question_bank.py --rename-only

# OCR all papers → question-bank/{year}/{slug}/questions.json + ocr.txt
python shared-tools/pdf-engine/build_dse_ict_question_bank.py

# Default engine is PaddleOCR with scan preprocessing (denoise + contrast)
python shared-tools/pdf-engine/build_dse_ict_question_bank.py --years 2019 --slugs Paper1_MultipleChoice --force

# Subset
python shared-tools/pdf-engine/build_dse_ict_question_bank.py --years 2019 2020 --slugs Paper1_MultipleChoice
```

### PDF naming

| Legacy | New name | HKEAA title (2012–2024) |
|--------|----------|-------------------------|
| `p1.pdf` | `DSE_ICT_{year}_Paper1_MultipleChoice.pdf` | 卷一 必修部分 |
| `p2a.pdf` | `DSE_ICT_{year}_Paper2A_Database.pdf` | 卷二甲 數據庫 |
| `p2b.pdf` | `DSE_ICT_{year}_Paper2B_DataCommunicationsNetworking.pdf` | 卷二乙 數據通訊及建網 |
| `p2c.pdf` | `DSE_ICT_{year}_Paper2C_MultimediaWebsiteConstruction.pdf` | 卷二丙 多媒體製作及網站建構 |
| `p2d.pdf` | `DSE_ICT_{year}_Paper2D_SoftwareDevelopment.pdf` | 卷二丁 軟件開發 |
| `ans.pdf` | `DSE_ICT_{year}_MarkingScheme.pdf` | 評卷參考 |
| `per.pdf` | `DSE_ICT_{year}_PerformanceReport.pdf` | 考生表現 |

Paper 2A–2D are the **old elective booklets** (one per option), not compulsory modules A–E.
From 2025 DSE onwards, Paper 2 is a single paper with three elective sections (數據庫 / 網絡應用程式開發 / 算法與程式編寫); see EDB C&A Guide §5.5.2. Store as `DSE_ICT_{year}_Paper2_Elective.pdf`.

Loose downloads named `2025-1A.pdf`, `2025-1B.pdf`, `2025-2.pdf` at the `past-papers/` root are moved into `{year}/` with descriptive names when you run `--rename-only`.

### Question bank layout

```
question-bank/
├── index.json
├── 2019/
│   ├── Paper1_MultipleChoice/
│   │   ├── ocr.txt           # cached OCR (reuse)
│   │   └── questions.json    # typed questions + exam_spec items
│   ├── Paper2A_Database/
│   └── MarkingScheme/
└── ...
```

Question `type` values: `mcq`, `structured`, `short_answer`, `long_answer`, `matching`, `true_false`, `fill_in`.

### LLM refinement (recommended for scanned papers)

Setup (macOS / Windows / `.env`): **[docs/GOOGLE_API_KEY.md](../../docs/GOOGLE_API_KEY.md)**.

OCR + rule parser gives a **draft** (`questions.json`). For usable reference text, run an LLM pass once and cache `questions_refined.json`:

```bash
# Needs OPENAI_API_KEY (or compatible endpoint via OPENAI_BASE_URL)
python shared-tools/pdf-engine/refine_dse_ict_question_bank.py --years 2019 --slugs Paper1_MultipleChoice

# Hong Kong / free tier: Gemini API key from https://aistudio.google.com/apikey
set GOOGLE_API_KEY=your-key
python shared-tools/pdf-engine/refine_dse_ict_question_bank.py --years 2019 --slugs Paper1_MultipleChoice --provider gemini

# Best accuracy on 2-column MCQ scans (more tokens; uses page images)
python shared-tools/pdf-engine/refine_dse_ict_question_bank.py --years 2019 --slugs Paper1_MultipleChoice --mode vision --provider gemini
```

Each refined item includes `confidence` and `needs_review` — spot-check those before using in出卷. Load with `load_paper_spec(..., prefer_refined=True)`.

### Import Gemini JSON (`gemini-output/`)

If papers were extracted to JSON elsewhere (text-only, often no images), import into the bank:

```bash
python shared-tools/pdf-engine/import_gemini_question_bank.py
python shared-tools/pdf-engine/import_gemini_question_bank.py --years 2024 --force
```

Preserves full `gemini_raw`, adds concept/curriculum tags, merges marking-scheme answers, and writes `[圖片描述]` placeholders where diagrams are missing. **Also runs `apply_support_to_item()`** to embed `support_content` (pseudocode from `algorithm_code`, ASCII tables/diagrams) into `text`/`stem`.

Back-fill existing bank: `python shared-tools/pdf-engine/enrich_dse_ict_support_content.py`  
Logic: `dse_ict_support_content.py` (shared with `f5_ict_from_dse.py` paper generator).

Full workflow, file naming, split rules, and coverage status: **`Subjects/DSE-ICT/README.md`** (方法 B).

### Reuse without re-OCR

```python
from dse_ict_question_bank import load_paper_spec, collect_bank_text
spec = load_paper_spec("2019", "Paper1_MultipleChoice")
```

Or regenerate style hints:

```bash
python shared-tools/paper-generator/extract_dse_ict_ocr.py
```

Reads cached `ocr.txt` from the question bank by default.
