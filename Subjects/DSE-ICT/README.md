# DSE-ICT

DSE 資訊及通訊科技（ICT）共用參考庫 — 適用於 F4–F6（S4–S6）出卷與備課。

此資料夾存放**考評局／教育局官方文件**，不屬於任何單一級別。校內試卷、Mock、教學筆記請放在各級別工作區（`S4-ICT/`、`S5-ICT/`、`S6-ICT/`）。

## 結構

- `past-papers/`：DSE 官方歷屆卷 PDF（描述性檔名，例如 `DSE_ICT_2019_Paper2A_Database.pdf` = 卷二甲 數據庫）
- `question-bank/`：OCR 及結構化題目 JSON（**出卷參考時讀這裡，毋須每次 OCR**）
- `edb/`：教育局課程及評估指引等官方文件

## 建立題庫（一次性）

```bash
python shared-tools/pdf-engine/build_dse_ict_question_bank.py
```

需安裝 Tesseract（`chi_tra` + `eng`）。詳見 `shared-tools/pdf-engine/README.md`。
