---
name: generate-f5-ict-mcq
description: >-
  Generates and reviews S5 ICT Exam02 甲部 MCQ (Core A/B/D) from blueprint, with
  partial regen on failing MCQ slots. Use when the user asks to 出MC、改善MC質素、
  重出甲部、平衡概念分佈、或修正 MCQ options/keys，而唔想影響乙丙。
disable-model-invocation: true
---

# Generate S5 ICT MCQ (甲部)

## Scope

- **Only**: 甲部 30 MCQ（Core A×10 → Core B×10 → Core D×10）
- **Not included**: 乙部、丙部長題；任何 DOCX 人手改題（改 spec 再 render）

## Inputs / Outputs

- **Input**: `Subjects/S5-ICT/assessments/<YYYY-YYYY>/Term 02/_generation/exam_blueprint.json`
- **Output**: `.../_generation/<YY>_<YY>_S5_ICT_Exam02.spec.json`（只更新 `mcq-*` items）
- **Optional**: `.../_generation/<...>.partial_regen.json`（slot-level regen report）

## Workflow (MCQ-only)

1. **Confirm blueprint MCQ ordering**
   - Must be **Core A → Core B → Core D** blocks (10 each).

2. **Generate MCQ items**
   - Use the existing pipeline entrypoint that supports blueprint-based generation (do not hand-edit DOCX).

3. **Question review (spec only)**
   - Run `shared-tools/paper-generator/question_review.py` (alias for `run_question_spec_check`) targeting the candidate spec.
   - If MCQ issues exist (bad distractors, no correct option, ambiguous stem, key mismatch), record failing `mcq-*` ids.

4. **Partial regen (MCQ slots only)**
   - Regenerate **only** failing `mcq-*` slots (max 10 attempts / slot).
   - Stop early once the MCQ slot passes quality checks.

5. **Exit criteria**
   - All MCQ slots pass spec checks (or remaining unresolved are explicitly listed).

## Quality gates (MCQ)

- **Answerability**: exactly one best answer; options mutually exclusive.
- **Option sanity**: no “correct answer not in options”; no duplicated options.
- **Concept fit**: Core A/B/D only (no elective EC concepts in MCQ).
- **Difficulty calibration**: mix of recall + application; avoid over-trivial repeats.

## Notes / Constraints

- Do **not** “fix” MCQ by editing DOCX text. Fix spec and re-render.
- Similarity thresholds against bank/past are **review signals**, not a pick-time hard block.

