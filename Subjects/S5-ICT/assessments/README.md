# S5-ICT — 評核工作區（assessments）

本資料夾存放進行中之出卷、審核與生成產物，**不應**作為派發予學生之終稿。

## 結構

```
assessments/
└── {YYYY-YYYY}/Term {01|02}/
    ├── _generation/     # spec、blueprint、審計 JSON
    ├── _reference/      # 出卷參考卷
    └── WrittenExam/     # 進行中之書面試卷 spec（如有）
```

終稿（可派發 `.pdf` / `.docx`）請存放於 `../past-papers/` 對應學期路徑。
