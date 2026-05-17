## paper_format (migration target)
This folder is the migration target for the high-fidelity paper formatting workflow from the sibling project `chw-paper-format`.

### Key idea (why it works)
`chw-paper-format` achieves high visual similarity by **preserving the original DOCX package**:
- Extract an editable **paper model** (sections, ordered blocks, question slots) from a reference past paper.
- Generate output by **copying the source DOCX** and then **replacing only the question-related blocks** (paragraph/table indices) in-place.
This keeps Word relationships intact: styles, headers/footers, section breaks, images, numbering, and low-level layout.

**Cover page:** patch existing cover paragraphs in-place (`docx_inplace.apply_cmp_cover_*`). Do not regenerate the whole cover; change only fields that differ (often just the paper title line).

### Target architecture in School-Agent-OS
We keep "tool-first" + decoupling (data vs execution) by splitting into layers:

- `schema/` (data contracts)
  - JSON schema versions for: paper model, question bank, template profile.
- `docx_adapter/` (execution primitives)
  - Low-level docx operations (read ordered blocks, replace paragraph text, replace table cell rows).
  - Minimal XML utilities that `python-docx` does not expose safely.
- `extractor/` (read past papers → model)
  - Build `paper-model.json`, `questions.json`, and `templates.json` from a reference DOCX.
- `renderer/` (model + question bank → output docx)
  - Template-preserving clone path (preferred).
  - Fallback reconstruction path (only when source template not available).
- `validator/` (quality gates)
  - Structure similarity checks (paragraph/table counts, headings, text fingerprint).
  - Optional image-based comparison (LibreOffice + PyMuPDF) as a non-blocking enhancement.

### CLI tools (Shared Tools)
Planned CLIs under `shared-tools/paper-formatter/`:
- `paper_extract.py`: extract `paper-model.json` from a reference paper (into subject folder).
- `paper_generate.py`: generate a new DOCX by applying question replacements onto a chosen reference/template.
- `paper_compare.py`: compare generated vs reference to quantify fidelity.

### How this coexists with `exam_generator.py`
- `exam_generator.py`: generic "build from template" generator (good for simple papers).
- `paper_format/`: high-fidelity generator for "must match past paper" scenarios (CMP, DSE-style, etc.).

