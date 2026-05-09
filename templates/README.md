# templates

存放學校標準的 Word/PDF 範本（工具會以此作為排版「真實來源」）。

## Exam Template for `exam_generator.py`
請準備一個 docx 範本並命名為：
- `templates/exam_template.docx`

工具會嘗試替換以下 placeholder（若不存在則會在文件末尾追加）：
- `{{TITLE}}`：試卷標題
- `{{QUESTIONS}}`：題目插入點

範本內的字體/頁邊距會被尊重；若你希望工具強制套用學校標準，請用 `--enforce-standard`。

## templates
School-standard templates for Word/PDF (DOCX/PDF form templates).

- Put official, approved layouts here.
- Tools in `shared-tools/` should use these templates to guarantee consistent formatting.

