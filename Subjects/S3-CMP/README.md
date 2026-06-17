# S3-CMP

中三電腦科（CMP）工作區 — 出卷、歷屆試卷、教學素材集中於此。

## 建議結構

- `assessments/`：出卷與批改工作區
  - `exam-input/`：題目 JSON（Markdown 內容）
  - `{YYYY-YYYY}/Term {01|02}/`：`_generation/`、答案腳本、`_student_submissions/`
- `past-papers/`：終稿庫（依學年 → 學期 → 類型）
  - `{YYYY-YYYY}/Term {01|02}/WrittenExam/`
  - `{YYYY-YYYY}/Term {01|02}/PracticalAssessment/`
  - `{YYYY-YYYY}/Term {01|02}/PracticalMock/`
- `resources/reference/`：樣本卷、參考答案
- `notes/`：教學筆記、課堂程式、worksheet（例如 `Python & AI/Lesson 1/`）

## 檔名規範

檔名維持 `{YY}_{YY}_S3_CMP_...` 格式，方便工具辨識。
