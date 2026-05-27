---
name: generate-f5-ict-long
description: >-
  Generates S5 ICT Exam02 丙部長題 (integrated, DSE Paper 2D / Paper 2 feel) with
  strict depth/coherence gates: one scenario, chained subparts, tables/diagrams
  and pseudocode blanks. Use when the user asks to 出長題、做到好似 25_26_S5_ICT_Exam02
  丙部嗰種質素、或要「一條大題串多個子程式/子題」而唔係兩句短問。
disable-model-invocation: true
---

# Generate S5 ICT long integrated questions (丙部)

## Scope

- **Only**: 丙部（40 marks）— integrated long questions (algorithm + data structure + DB/programming case).
- Goal: match the “質素” of `WrittenExam/25_26_S5_ICT_Exam02.docx` Section C:
  - single scenario sustained across many subparts
  - multi-step reasoning, tracking, and code/pseudocode completion
  - explicit data tables / arrays / diagrams referenced in the text

## Required depth profile (hard gates)

Each `c-*` slot must satisfy **at least 4** of the following:

1. **Scenario continuity**: one named system/context used across all subparts.
2. **Chained subparts**: later parts depend on earlier outputs/definitions.
3. **Data artifact**: includes at least one of (table, array listing, diagram description, state trace table).
4. **Pseudocode completion**: has ≥3 blanks or missing lines with labels (e.g. (a1)(a2)… or (c1)(c2)…).
5. **State reasoning**: requires tracing (stack/queue/linked list pointers, indices, front/rear/head).
6. **Mark depth**: \(\ge 10\) marks per long question OR ≥3 subparts with non-trivial mark split.

If a generated slot fails gates, **regen that slot only** (max 10 attempts/slot).

## Inputs / Outputs

- **Input**: `.../_generation/exam_blueprint.json`
- **Output**: `.../_generation/<...>.spec.json`（只更新 `c-*` items）

## Workflow (丙部-only)

1. **Pick a DSE reference pattern (not stem)**
   - Use bank-derived `style_patterns.json` and `concept_map.json` to decide the ask-shape.
   - Example ask-shapes to emulate:
     - linked list + insertion procedure + pointer table
     - 2D array + helper subprograms + charting / scoring / optimization
     - stack/queue operations embedded inside a larger system behavior

2. **Generate the integrated slot**
   - Create:
     - scenario intro
     - required tables/arrays (inline or clearly described)
     - subparts with explicit marks and labeled blanks
   - Ensure all variable names are introduced before use.

3. **Spec checks**
   - Run `shared-tools/paper-generator/question_review.py` to catch:
     - missing definitions, inconsistent indices, impossible constraints, ambiguous answers
   - Run `shared-tools/paper-generator/paper_review.py` after render to ensure:
     - no markdown artifacts
     - correct subpart indentation (`\t(a)\t...`)

4. **Partial regen loop**
   - Fix only the failing `c-*` items; keep passing items unchanged.

## Anti-patterns (avoid)

- “Two-line” short questions disguised as long questions (e.g. only stack push/pop).
- Mixing unrelated concepts in one slot without narrative linkage (e.g. queue + binary search with no shared data story).
- Referencing “see table” without providing any table/array content.

## Recommended slot templates (targets)

- **Linked list case**: arrays `data[]`, `next[]`, `head`; operations `insert_after/delete/find`; asks include pointer updates.
- **2D array case**: define `score[m][n]`; helper routines; chart; bonus/optimization routine with blanks.
- **Queue/stack in system**: print spooler queue, undo/redo stack, clinic triage queue with clear front/rear updates.

