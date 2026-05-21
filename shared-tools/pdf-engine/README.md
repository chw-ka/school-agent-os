# pdf-engine

HKDSE / school PDF tools: OCR once, store structured questions for reuse.

## DSE ICT question bank

Official scanned papers live in `Subjects/DSE-ICT/past-papers/`.  
Structured output goes to `Subjects/DSE-ICT/question-bank/`.

### One-time setup

1. Install [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) with `chi_tra` + `eng` language packs.
2. `pip install pymupdf` (see repo `requirements.txt`).

### Build the bank (OCR once)

```bash
# Rename legacy p1.pdf / p2a.pdf … if needed
python shared-tools/pdf-engine/build_dse_ict_question_bank.py --rename-only

# OCR all papers → question-bank/{year}/{slug}/questions.json + ocr.txt
python shared-tools/pdf-engine/build_dse_ict_question_bank.py

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
From 2025 DSE onwards, Paper 2 is a single paper with three elective sections (數據庫 / 網絡應用程式開發 / 算法與程式編寫); see EDB C&A Guide §5.5.2.

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
