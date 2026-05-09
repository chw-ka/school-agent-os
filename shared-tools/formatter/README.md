# formatter

處理 Word/PDF 排版相關工具。

目前包含：
- `exam_generator.py`: 將「題目 JSON（含 Markdown）」填入 Word 範本並自動編號、設定字體。

## formatter
Document formatting tools (Word/PDF layout) aligned with school standards.

- Primary outputs: `.docx` (and optionally PDF export via a separate pipeline).
- Enforces: 新細明體 12pt, standard margins, consistent headings/numbering.

### `exam_generator.py`
Generate a DOCX exam from JSON using a DOCX template.

- Input: exam JSON (see `example_exam.json`)
- Template: a `.docx` under `templates/` (school-approved layout)
- Output: `.docx` file (auto-numbered questions)

