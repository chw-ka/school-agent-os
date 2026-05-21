# shared-tools

存放通用的 Python 技能腳本（Skills / Shared Tools）。

原則：
- 工具優先（Tool First）
- 輸入輸出明確（JSON/檔案路徑）
- 可重現、可測試、可重用

## 試卷工具鏈

| 目錄 | 用途 |
|------|------|
| `question-quality-check/` | 題目品質：撞題、概念、MCQ／答案鍵隨機性 |
| `paper-quality-check/` | 試卷版面：頁尾、封面 |
| `paper-generator/` | 從範本出卷；自動執行上述兩套檢查 |
| `paper-formatter/` | Word 排版、spec → DOCX |

建議流程：

```
paper-generator  →  *.spec.json  →  question-quality-check
                                        ↓ pass
                                   paper-formatter → DOCX
                                        ↓
                                   paper-quality-check
```

## 其他

| 目錄 | 用途 |
|------|------|
| `data-processor/` | 資料處理 |
| `pdf-engine/` | PDF OCR、DSE ICT 題庫 (`build_dse_ict_question_bank.py`) |

## 舊目錄名稱

| 舊名 | 新名 |
|------|------|
| `formatter/` | `paper-formatter/` |
| `exam-generator/` | `paper-generator/` |
| `paper-quality-check/`（舊，含題目+版面） | 拆成 `question-quality-check/` + `paper-quality-check/` |
