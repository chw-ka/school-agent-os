# paper-generator

從範本產生試卷（recipes）。

## S5 ICT 出卷（主入口）

**Workflow skill（concept → generate → review → DOCX）：**

→ **[`.cursor/skills/generate-f5-ict-exam/SKILL.md`](../../.cursor/skills/generate-f5-ict-exam/SKILL.md)**

**目標流程文檔：** [`F5_ICT_CONCEPT_GENERATE_FLOW.md`](F5_ICT_CONCEPT_GENERATE_FLOW.md)

過渡一鍵（bank pick，可能慢）：`Subjects/S5-ICT/past-papers/…/Term 02/_generation/regenerate_exam02.py`

技術備註（spec ↔ DOCX）：[`EXAM_SPEC_AND_DOCX.md`](EXAM_SPEC_AND_DOCX.md)

## 流程（目標）

```
concept_map + style_patterns（side products）
  → exam_blueprint → concept_review
  → generate → *.spec.json
  → question_review → [partial regen, max 10/slot]
  → render DOCX → paper_review（spec ↔ docx）
```

**Review 命名：** concept_review / question_review / paper_review（程式仍用 `post_check`、`check_spec`，逐步改名）。

`post_check.py`：`run_question_spec_check`（question_review）、`run_post_render_check`（paper_review）。

寫入 DOCX 時：**清空**非封面 table → **填入**所需 table → **刪除** template 剩餘 table（`F5_ICT_REQUIRED_TABLES`）。

**試卷結構：** 甲部 MCQ（Core A/B/D）；乙、丙部只出結構題／問答。**丙部（Paper 2 / Module）不設 MC 題。**

## F5 ICT 範例

```bash
python shared-tools/paper-generator/f5_ict_blueprint_db_web.py
```

每次 generate **必須**跑完整 quality-check（duplicates、concepts、MCQ core A→B→D 順序、answer key、format）。不可略過檢查。

MCQ core 規劃：`shared-tools/paper-generator/mcq_core_plan.py`（A ×10 → B ×10 → D ×10；細分 concept 順序見 `curriculum_concepts.json`）。

**舊規劃（pick 藍本，已取代）：** [`F5_ICT_DSE_BLUEPRINT_FLOW.md`](F5_ICT_DSE_BLUEPRINT_FLOW.md) — 見新 flow 文檔。

## 新增 recipe

1. 實作 `build_*_exam_spec() -> dict`（`question-quality-check/exam_spec.py`）
2. 在 `paper-formatter/` 或本目錄加入 render 腳本
3. 呼叫 `post_check.run_spec_check` / `run_post_generation_check`

## 舊名稱

原 `exam-generator/` 已改名為 `paper-generator/`。
