---
name: generate-f5-ict-short
description: >-
  Generates and reviews S5 ICT Exam02 乙部短題/中題 (structured, non-integrated)
  from blueprint and style patterns, without touching MCQ or 丙部長題. Use when
  the user asks to 出短題、重出乙部、調整乙部題型比例、或提升「似DSE Paper 1B」
  但保持題目較短、可分拆獨立小問。
disable-model-invocation: true
---

# Generate S5 ICT short structured questions (乙部)

## Scope

- **Only**: 乙部（Core units structured questions; typically 6 items / 30 marks）
- Target: Paper 1B style **short-to-medium** questions (multi-part ok, but not long integrated programming-case).
- **Not included**: 甲部 MCQ、丙部長題（integrated algorithms / DB programming case）

## Inputs / Outputs

- **Input**: `.../_generation/exam_blueprint.json`
- **Output**: `.../_generation/<...>.spec.json`（只更新 `b-*` items）

## Workflow (乙部-only)

1. **Blueprint sanity**
   - Each `b-*` slot must declare concepts + marks per subpart.

2. **Generate from patterns**
   - Use `style_patterns.json` ask shapes (verbs / scenario frames / subpart templates).
   - Must not copy bank stems verbatim; generate a fresh school scenario.

3. **Spec review**
   - Run `shared-tools/paper-generator/question_review.py` on the candidate spec.
   - Common failure modes to catch:
     - Missing data (table not provided, undefined variable, unclear index base)
     - Inconsistent marks vs work required
     - Ambiguous questions (“state any two” without constraints; multi-correct without telling)

4. **Partial regen**
   - Regenerate **only** failing `b-*` slots (max 10 attempts / slot).

## Quality gates (乙部 short questions)

- **Self-contained**: all required data included in the slot (tables/figures referenced must exist).
- **Marking alignment**: each subpart’s marks match expected steps.
- **Clarity**: index base (0/1), data types, units (MB vs MiB) stated.
- **DSE feel**: command verbs + terminology consistent with `style_patterns.json`.

## Output formatting constraints (render readiness)

- Subparts must be formatted as `\t(a)\t... \t(x 分)` patterns so DOCX render checks don’t error.
- Avoid markdown artifacts (`**`, backticks, underscores) in final spec text.

