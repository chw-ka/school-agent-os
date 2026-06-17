# Exam marking tools

批改掃描答題紙 — 與 `assessments/…/WrittenExam/` 配合使用。

## S3 CMP Term02

### 1. 從教師定稿 DOCX 提取答案 spec

**必須用** `assessments/…/WrittenExam/25_26_S3_CMP_Term02_Exam.docx`（人手定稿），唔好用 `_generation/` 或 `past-papers/` 舊版。

```bash
python shared-tools/exam-marking/extract_s3_cmp_spec_from_docx.py \
  "Subjects/S3-CMP/assessments/2025-2026/Term 02/WrittenExam/25_26_S3_CMP_Term02_Exam.docx" \
  -o "Subjects/S3-CMP/assessments/2025-2026/Term 02/WrittenExam/25_26_S3_CMP_Term02_Exam.spec.json"
```

甲部 MCQ 答案可後補：`--mcq-answers DACDBBACBBDABACDCADC`

### 2. 拆格 crop + PaddleOCR（乙丙丁；戊部 crop/OCR）

**依賴**（與 `requirements-ocr.txt` 相同 — PaddleOCR 2.7 + numpy 1.x）：

```bash
pip install -r requirements-ocr.txt
```

座標：**唔使人手逐版 crop**。每頁用 ZipGrade 四角黑格做基準，再喺 MC 底邊以下自動搵乙/丙表格橫線（`find_bc_table_regions`），適應掃描走位。

```bash
# 對照 overlay（紅框=乙部兩行，藍框=丙部）
python shared-tools/exam-marking/preview_alignment.py \
  ".../SKM_C750i26061513350_reordered.pdf" \
  -o output/align_preview --student 0
```

```bash
# 只 crop（戊部 sa_q1_*.png 留俾你試 OCR）
python shared-tools/exam-marking/grade_s3_cmp_scans.py \
  "_student_submissions/scans/SKM_C750i26061513350_reordered.pdf" \
  --spec "25_26_S3_CMP_Term02_Exam.spec.json" \
  --crop-dir "_student_submissions/crops" \
  --crops-only

# PaddleOCR + 乙丙丁自動計分
python shared-tools/exam-marking/grade_s3_cmp_scans.py \
  "_student_submissions/scans/SKM_C750i26061513350_reordered.pdf" \
  --spec "25_26_S3_CMP_Term02_Exam.spec.json" \
  -o "_student_submissions/marking_bcd.json" \
  --crop-dir "_student_submissions/crops"
```

> WinRT 對單字元格子效果差，已改用 **PaddleOCR 2.7**（`paddle_cell_ocr.py`）。手寫單字母仍有誤讀，建議用 `--crop-dir` 抽查後再信分數。戊部中文用 `chinese_cht` 模型，準確度視手寫而定。
