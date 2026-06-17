# 藝術科行政

科組會議議程、紀錄及 AI 輔助產出。

## 路徑慣例

```
Administrative/ART/{學年}/Meeting {NN}/
├── README.md                    # 該次會議說明（可選）
├── 會議紀錄_藝術科_YYYYMMDD.docx  # 覆核後終稿（可發 S: 1_Agenda_Minutes/）
└── _generation/                 # AI／轉寫／草稿 — git only，不發 panel
    ├── agenda.txt
    ├── *.transcript.txt
    ├── meeting-minutes-draft.md
    └── 會議紀錄_*.docx          # AI 草稿（覆核前）
```

- **`_generation/`**：逐字稿、`.md` 草稿、未覆核 `.docx`（同 `Subjects/…/_generation/` 原則一致）
- **上層目錄**：記錄人覆核後嘅正式紀錄
- **勿用** repo 根目錄 `output/` 作長期存放

Panel 對應（在校）：`S:\...\08_Others\1_Agenda_Minutes\`（發佈須用戶批准）
