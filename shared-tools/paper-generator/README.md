# paper-generator

從範本產生試卷（recipes）。**先產出 exam spec JSON → 品質檢查 → 通過後才 render DOCX**。

## 流程

```
recipe  →  *.spec.json  →  question-quality-check  →  修 spec
                              ↓ pass
                         render DOCX（paper-formatter）
                              ↓
                         paper-quality-check（頁尾、封面）
```

`post_check.py` 會依序執行 **question-quality-check** 與 **paper-quality-check**。

寫入 DOCX 時：**清空**非封面 table → **填入**所需 table → **刪除** template 剩餘 table（`F5_ICT_REQUIRED_TABLES`）。

**試卷結構：** 甲部 MCQ（Core A/B/D）；乙、丙部只出結構題／問答。**丙部（Paper 2 / Module）不設 MC 題。**

## F5 ICT 範例

```bash
python shared-tools/paper-generator/f5_ict_blueprint_db_web.py
```

每次 generate **必須**跑完整 quality-check（duplicates、concepts、MCQ core A→B→D 順序、answer key、format）。不可略過檢查。

MCQ core 規劃：`shared-tools/paper-generator/mcq_core_plan.py`（A ×10 → B ×10 → D ×10；細分 concept 順序見 `curriculum_concepts.json`）。

**規劃中（DSE 題庫藍本出卷）：** 見 [`F5_ICT_DSE_BLUEPRINT_FLOW.md`](F5_ICT_DSE_BLUEPRINT_FLOW.md) — 先補齊 `Subjects/DSE-ICT/question-bank/` 2019–2025。

## 新增 recipe

1. 實作 `build_*_exam_spec() -> dict`（`question-quality-check/exam_spec.py`）
2. 在 `paper-formatter/` 或本目錄加入 render 腳本
3. 呼叫 `post_check.run_spec_check` / `run_post_generation_check`

## 舊名稱

原 `exam-generator/` 已改名為 `paper-generator/`。
