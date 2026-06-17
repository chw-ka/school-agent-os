# S3-CMP — 評核工作區（assessments）

本資料夾存放進行中之出卷、實作評估答案腳本、批改暫存及輸入規格。

## 結構

```
assessments/
├── exam-input/          # 題目 JSON 輸入
└── {YYYY-YYYY}/Term {01|02}/
    ├── _generation/
    ├── _assets/
    ├── WrittenExam/
    ├── PracticalAssessment/
    │   └── _student_submissions/   # 批改暫存（避免大量具名作品入 git）
    └── PracticalMock/
```

終稿請存放於 `../past-papers/`（**僅教師人手定稿**；generator 產出留 `_generation/`）。參考卷請見 `../resources/reference/`。
