# S5-ICT

中五資訊及通訊科技（ICT）工作區。

## 建議結構

- `assessments/`：出卷工作區（`_generation/`、`exam-input/`、`*.spec.json`）
- `past-papers/`：終稿庫（可派發之 `.pdf` / `.docx`）
- `notes/`、`resources/`：可按需要新增

DSE 官方卷及題庫見 [`../DSE-ICT/`](../DSE-ICT/)（F4–F6 共用）。

## 出中五試卷（主流程）

**Agent / 操作步驟：** Cursor skill [`generate-f5-ict-exam`](../../.cursor/skills/generate-f5-ict-exam/SKILL.md)

**目標：** concept blueprint → **生成**題目（不抄題庫）→ concept / question / paper **review** → 校內模板 DOCX。  
詳見 `shared-tools/paper-generator/F5_ICT_CONCEPT_GENERATE_FLOW.md`。

Phase 3（blueprint + concept review）：

```bash
.venv/Scripts/python shared-tools/paper-generator/build_exam_blueprint.py --review
```

**一鍵（建議）：**

```bash
.venv/Scripts/python shared-tools/paper-generator/build_f5_exam02.py --force-render
```

或 `regenerate_exam02.py`（無參數，轉發同上）。`--legacy-pick` 才用舊 bank pick（較慢）。

已有 spec 時：`render_from_spec.py` 或 `build_f5_exam02.py --render-only`。

**產物：**

- `past-papers/.../WrittenExam/*.docx`（交付用終稿）
- `assessments/.../_generation/*.spec.json`（內容 source of truth，不作學生卷發佈）

**試卷結構：** 甲部 MCQ（Core A→B→D）；乙部結構題；丙部 Module A+C 數據庫（無 MC）。

技術細節：`shared-tools/paper-generator/EXAM_SPEC_AND_DOCX.md`。
