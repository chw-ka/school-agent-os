# Term 02 Exam02 — generation artifacts

**Active files (concept-generate pipeline):**

| File | Purpose |
|------|---------|
| `exam_blueprint.json` | Slot plan + concepts |
| `exam_blueprint.concept_review.json` | Blueprint review report |
| `25_26_S5_ICT_Exam02.spec.json` | Exam content (source of truth) |
| `25_26_S5_ICT_Exam02.partial_regen.json` | Last partial regen report |
| `regenerate_exam02.py` | Thin wrapper → `build_f5_exam02.py` (`--legacy-pick` = old bank pick) |

**Deliverable:** `../WrittenExam/25_26_S5_ICT_Exam02.docx` (not stored here).

**Regenerate:**

```bash
.venv/bin/python shared-tools/paper-generator/build_f5_exam02.py --force-render
```

Legacy bank-pick audits (`*.bank_risk.json`, `mcq_preview.json`, PNG extracts, one-off scripts) were removed 2026-05.
