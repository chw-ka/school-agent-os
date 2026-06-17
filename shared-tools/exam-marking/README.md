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

座標：**乙/丙人手校準一次**（`answer_p1.calibrated`）；**第 2 頁**用考試 PDF 空白答題紙（page 8–9）ORB + homography 對齊（`alignment.template`）。

**對齊策略：** 第 1 頁 ZipGrade 角格；第 2 頁優先 ORB（無角格）。工具：`calibrate_bc_layout.py`。

**第 1 頁（乙、丙）** — `calibrated.rows`：3 行 × 5 欄 norm box（配對×2 + 是非×1）；表格闊度約 **17%–88% 頁寬**（參考卷已 tune）。  
**第 2 頁（丁、戊）** — 幼 kernel 搵 10 條填空底線；左邊 (a)–(e) label cluster 定位戊部 (a)(b)(c) 答題區。

```bash
# 從參考卷 dump 建議座標（貼入 layout JSON 再微調）
python shared-tools/exam-marking/calibrate_bc_layout.py ref.pdf --dump --table-x 0.168 0.882

# 預覽 calibrated crops
python shared-tools/exam-marking/calibrate_bc_layout.py ref.pdf -o ./_cal_preview --student 0
```

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
