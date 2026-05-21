# paper-formatter

Word 試卷排版、由 JSON/spec 填入範本、封面／頁尾套用。

## 相關工具

| 目錄 | 用途 |
|------|------|
| **`../question-quality-check/`** | 撞題、概念、答案鍵 |
| **`../paper-quality-check/`** | 頁尾、封面 |
| **`../paper-generator/`** | 出卷 recipes + 自動檢查 |

- `generate_f5_ict_blueprint_exam.py` — 轉發至 `../paper-generator/f5_ict_blueprint_db_web.py`
- `docx_inplace.py` — 封面、段落、頁尾文字
- `written_layout.py` — 乙部／丙部短答、長答排版 helper（subpart、answer blank、replace_span）

## 舊名稱

原 `formatter/` 已改名為 `paper-formatter/`。
