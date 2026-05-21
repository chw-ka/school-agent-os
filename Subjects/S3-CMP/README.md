# S3-CMP

中三電腦科（CMP）工作區 — 出卷、考古題、教學素材集中於此。

## 建議結構

- `exam-input/`：題目 JSON（Markdown 內容）
- `source/`：原始題庫／規格
- `past-papers/`：歷屆試卷與評估（依學年 → 學期 → 類型）
  - `{YYYY-YYYY}/Term {01|02}/WrittenExam/`
  - `{YYYY-YYYY}/Term {01|02}/PracticalAssessment/`
  - `{YYYY-YYYY}/Term {01|02}/PracticalMock/`
  - `Reference/`：樣本卷、參考答案
- `notes/`：教學筆記、課堂程式、worksheet（例如 `Python & AI/Lesson 1/`）

## past-papers 命名

檔名維持 `{YY}_{YY}_S3_CMP_...` 格式，方便工具辨識。
