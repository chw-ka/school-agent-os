# generate-f5-ict-exam — reference

## Target pipeline（目標）

```
side products (concept_map + style_patterns)
  → exam_blueprint.json
  → concept_review
  → generate slots → build_f5_ict_exam_spec → save spec
  → question_review
  → [partial regen failed slots, max 10 each]
  → generate / render_docx
  → paper_review
```

詳見 `shared-tools/paper-generator/F5_ICT_CONCEPT_GENERATE_FLOW.md`。

## Legacy pipeline（過渡，仍可用）

```
pick bank → prepare_mcq_final_rows → build_f5_ict_exam_spec → save spec
  → run_question_spec_check (FAIL stops here)
  → generate / render_docx
  → run_post_render_check
```

> `regenerate_exam02.py` 可能因 seed retry 跑很久且無 progress；有現成 spec 時勿全量 re-pick。

## Key paths (25/26 Term 2 example)

| Role | Path |
|------|------|
| Regenerate (legacy) | `Subjects/S5-ICT/past-papers/2025-2026/Term 02/_generation/regenerate_exam02.py` |
| Output DOCX | `.../WrittenExam/25_26_S5_ICT_Exam02.docx` |
| Spec | `.../_generation/25_26_S5_ICT_Exam02.spec.json` |
| Blueprint (target) | `.../_generation/exam_blueprint.json` |
| Template | `Subjects/S5-ICT/past-papers/2024-2025/Term 02/WrittenExam/24_25_S5_ICT_Exam02.docx` |
| DSE bank | `Subjects/DSE-ICT/question-bank/` |
| C&A Guide | `Subjects/DSE-ICT/edb/ICT_C&A Guide_c_final.pdf` |
| Concept map (partial) | `Subjects/DSE-ICT/question-bank/curriculum_concepts.json` |
| Concept map (target tree) | `Subjects/DSE-ICT/question-bank/concept_map.json` 🔲 |
| Style patterns (target) | `Subjects/DSE-ICT/question-bank/style_patterns.json` 🔲 |

## Review commands（過渡：仍叫 question/paper check）

```bash
# question_review — spec only
.venv/bin/python -c "
from pathlib import Path
import sys
sys.path.insert(0, 'shared-tools/paper-generator')
from post_check import run_question_spec_check
raise SystemExit(run_question_spec_check(
    candidate_spec=Path('Subjects/S5-ICT/past-papers/2025-2026/Term 02/_generation/25_26_S5_ICT_Exam02.spec.json'),
    template=Path('Subjects/S5-ICT/past-papers/2024-2025/Term 02/WrittenExam/24_25_S5_ICT_Exam02.docx'),
    subject_subpath='S5-ICT',
))
"

# paper_review — after render
.venv/bin/python -c "
from pathlib import Path
import sys
sys.path.insert(0, 'shared-tools/paper-generator')
from post_check import run_post_render_check
raise SystemExit(run_post_render_check(
    candidate_spec=Path('Subjects/S5-ICT/past-papers/2025-2026/Term 02/_generation/25_26_S5_ICT_Exam02.spec.json'),
    candidate_docx=Path('Subjects/S5-ICT/past-papers/2025-2026/Term 02/WrittenExam/25_26_S5_ICT_Exam02.docx'),
    template=Path('Subjects/S5-ICT/past-papers/2024-2025/Term 02/WrittenExam/24_25_S5_ICT_Exam02.docx'),
))
"
```

CLI:

```bash
.venv/bin/python shared-tools/question-quality-check/check_spec_cli.py \
  --candidate "Subjects/S5-ICT/past-papers/2025-2026/Term 02/_generation/25_26_S5_ICT_Exam02.spec.json" \
  --template "Subjects/S5-ICT/past-papers/2024-2025/Term 02/WrittenExam/24_25_S5_ICT_Exam02.docx"
```

## Similarity thresholds（question_review）

| Check | Threshold | Module |
|-------|-----------|--------|
| MCQ vs bank / past | ≤ **60%**（review 指標） | `f5_ict_from_dse._BANK_SIM_THRESH` |
| Written whole scenario vs bank | ≤ **60%** | `_BANK_SIM_THRESH_WRITTEN_STEM` |
| Written subpart vs bank part | ≤ **85%** | `_BANK_SIM_THRESH_WRITTEN_SUBPART` |
| Spec text vs DOCX（乙丙, paper_review） | ≥ **92%** | `written_spec_docx_check.py` |

**目標：** 唔再喺 `build_mcq_payload_from_bank` pick 時 hard-fail；只喺 question_review 報告。

## Partial regen（目標，待實作）

| 規則 | 值 |
|------|-----|
| Max attempts per slot | **10** |
| On exhaustion | `unresolved_slots` in `*.regen_report.json` |
| Forbidden | Whole-paper re-seed loop（legacy `MAX_SEED_TRIES=80`） |

## Code map

| Step | Target | Legacy (now) |
|------|--------|--------------|
| Side products | `extract_style_patterns.py` 🔲 | — |
| Concept map tree | `concept_map.json` 🔲 | `curriculum_concepts.json` |
| Blueprint | `exam_blueprint.json` 🔲 | `f5_ict_spec.py` meta |
| concept_review | CLI 🔲 | `concept_check.py` |
| Generate | agent / `generate_item` 🔲 | `f5_ict_from_dse` pick+transform |
| question_review | rename 🔲 | `post_check.run_question_spec_check` |
| Spec assembly | `f5_ict_spec.py` | same |
| DOCX render | `f5_ict_blueprint_db_web.generate` | same |
| paper_review | rename 🔲 | `post_check.run_post_render_check` |
| 乙丙 render | `written_picks_render.py` | same |

## Implementation status

| Phase | 狀態 |
|-------|------|
| 0 Docs | ✅ |
| 1 style_patterns | 🔲 |
| 2 concept_map tree | 🔲 |
| 3 blueprint + concept_review | 🔲 |
| 4 generate → spec | 🔲 |
| 5 partial regen | 🔲 |
| 6 乙丙 render | 🟡 |
| 7 deprecate pick-transform | 🔲 |

## New academic year

1. Copy `past-papers/{old}/Term 02` → `{new}/Term 02`
2. Update paths in `regenerate_exam02.py`（過渡）或新 `build_exam.py`（目標）
3. Follow skill **Target architecture** from blueprint step

## Alternate render entry

```bash
.venv/bin/python shared-tools/paper-generator/f5_ict_blueprint_db_web.py \
  --output "Subjects/S5-ICT/past-papers/2025-2026/Term 02/WrittenExam/25_26_S5_ICT_Exam02.docx" \
  --spec "Subjects/S5-ICT/past-papers/2025-2026/Term 02/_generation/25_26_S5_ICT_Exam02.spec.json"
```

Spec must exist before render; run question_review first.
