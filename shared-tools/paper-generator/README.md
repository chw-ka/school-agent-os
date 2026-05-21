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

## F5 ICT 範例

```bash
.venv/bin/python shared-tools/paper-generator/f5_ict_blueprint_db_web.py
.venv/bin/python shared-tools/paper-generator/f5_ict_blueprint_db_web.py --render-anyway
```

**規劃中（DSE 題庫藍本出卷）：** 見 [`F5_ICT_DSE_BLUEPRINT_FLOW.md`](F5_ICT_DSE_BLUEPRINT_FLOW.md) — 先補齊 `Subjects/DSE-ICT/question-bank/` 2019–2025。

## 新增 recipe

1. 實作 `build_*_exam_spec() -> dict`（`question-quality-check/exam_spec.py`）
2. 在 `paper-formatter/` 或本目錄加入 render 腳本
3. 呼叫 `post_check.run_spec_check` / `run_post_generation_check`

## 舊名稱

原 `exam-generator/` 已改名為 `paper-generator/`。
