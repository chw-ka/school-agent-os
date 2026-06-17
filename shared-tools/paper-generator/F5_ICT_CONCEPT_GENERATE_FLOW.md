# F5 ICT 出卷：Concept → Generate → Review（目標流程）

> **狀態：目標架構（2026-05）** — skill 主文檔：`.cursor/skills/generate-f5-ict-exam/SKILL.md`  
> **過渡實作：** `regenerate_exam02.py`（bank pick + transform）仍可用，但唔再擴充；見文末 Legacy。

## 點解改方向？

| 舊做法（pick-transform） | 問題 |
|--------------------------|------|
| 從 `question-bank` **揀** DSE 題再改寫 | stem 本質係 DSE 原文，難降到 ≤60% |
| similarity 做 **pick gate** | 成卷 re-seed（80×120 MCQ tries），長時間 silent |
| 「quality check」一次過 | 概念問題同相似度問題混埋，難 partial fix |

**新做法：** bank → **patterns + concept map**（side products）→ **generate** 新題 → **review**（可分階段、可只 regen 失敗 slot）。

---

## Side products（唔係試卷，係出卷基建）

### 1. `concept_map.json`（tree）

**來源：**

- `Subjects/DSE-ICT/edb/ICT_C&A Guide_c_final.pdf` — 必修 A–E、選修 EA–EC 單元結構
- `Subjects/DSE-ICT/question-bank/` — 每 concept 出現次數、常見 marks、DSE 年份分布
- `MarkingScheme` / 評卷 — **common_mistakes**（待 extract）

**結構（建議）：**

```json
{
  "version": 2,
  "source": "Subjects/DSE-ICT/edb/ICT_C&A Guide_c_final.pdf",
  "tree": {
    "A": {
      "label": "資訊處理",
      "topics": {
        "A-b": {
          "label": "數據組織及數據控制",
          "concepts": ["欄位", "記錄", "鍵值"],
          "common_mistakes": ["混淆欄位與記錄"]
        }
      }
    }
  }
}
```

**基礎：** `curriculum_concepts.json`（C&A 單元結構）  
**工具：** `shared-tools/paper-generator/build_concept_map.py`  
**輸出：** `Subjects/DSE-ICT/question-bank/concept_map.json`

```bash
.venv/bin/python shared-tools/paper-generator/build_concept_map.py
# 合併 style_patterns 術語提示（預設開啟）
.venv/bin/python shared-tools/paper-generator/build_concept_map.py --dry-run
```

`concept_map.json` 包含：`tree.compulsory` / `tree.elective`（每 topic 有 concepts、keywords、bank_stats、common_mistakes）、`concept_index`（逐 concept 統計）、`f5_exam_scope`、`out_of_syllabus_rules`、`mcq_compulsory_slot_order`。

### 2. `style_patterns.json`（問法庫，唔係題庫）

從 bank **extract**，唔保留完整 stem：

| 欄位 | 例子 |
|------|------|
| `concept` | `試算表` |
| `question_types` | `mcq`, `short`, `sql`, `erd` |
| `command_verbs` | `以下哪一項正確描述`, `寫出` |
| `terminology` | `欄位`, `記錄`, `SELECT` |
| `scenario_frames` | `網店訂單`, `戲院預訂` |
| `subpart_templates` | `(a) 寫出 CREATE TABLE…` |
| `distractor_patterns` | MCQ 常見混淆項類型 |

**工具：** `shared-tools/paper-generator/extract_style_patterns.py`  
**輸出：** `Subjects/DSE-ICT/question-bank/style_patterns.json`

```bash
.venv/bin/python shared-tools/paper-generator/extract_style_patterns.py
# 自訂年份／輸出
.venv/bin/python shared-tools/paper-generator/extract_style_patterns.py \
  --years 2021 2022 2023 2024 2025 --dry-run
```

---

## 八步流程（operator + agent）

```mermaid
flowchart TD
  S0[Side products<br/>concept_map + style_patterns]
  S1[1. exam_blueprint.json<br/>考核比例 + slots]
  S2[2. concepts from bank stats]
  S3[3. concept_review]
  S4[4. generate → spec.json]
  S5[5. question_review]
  S6[6. partial regen max 10/slot]
  S7[7. render DOCX]
  S8[8. paper_review]

  S0 --> S1
  S1 --> S2 --> S3
  S3 -->|pass| S4 --> S5
  S5 -->|fail| S6 --> S4
  S5 -->|pass| S7 --> S8
```

### Step 1 — `exam_blueprint.json`

放 `Subjects/S5-ICT/assessments/{學年}/Term {NN}/_generation/`。

- 卷面：甲 30 / 乙 30 / 丙 40（7 題，無 c-04）；MCQ Core A→B→D block order
- 每 slot：`id`, `section`, `marks`, `concepts[]`, `question_type`, `core`（MCQ）
- `meta.concept_targets` — 全卷 concept 次數上下限

**工具：**

```bash
.venv/bin/python shared-tools/paper-generator/build_exam_blueprint.py --review
# → exam_blueprint.json + exam_blueprint.concept_review.json

.venv/bin/python shared-tools/paper-generator/concept_review.py \
  --blueprint "Subjects/S5-ICT/assessments/2025-2026/Term 02/_generation/exam_blueprint.json" \
  --json "…/exam_blueprint.concept_review.json"
```

### Step 2 — Concepts from bank

- 用 bank 統計「邊啲 concept DSE 點考」作 **參考**，唔 copy 題文
- 對照 `concept_map.json` 揀考核點

### Step 3 — concept_review

檢查項：

- slot 間 concept 重覆是否合理
- 對 C&A tree：out-of-syllabus（`out_of_syllabus_rules`）
- common mistakes 有冇覆蓋到（選用）
- blueprint `concept_targets` min/max

**產物：** `*.concept_review.json`（pass / issues / regenerate_concepts）

### Step 4 — Generate

- **輸入：** `exam_blueprint.json` + `style_patterns.json`
- **輸出：** `25_26_S5_ICT_Exam02.spec.json`（`dse_source` = `generated://…`）
- **工具：**

```bash
.venv/bin/python shared-tools/paper-generator/generate_from_blueprint.py \
  --concept-review --question-check --set-written-picks
```

- **實作：** `f5_ict_generate_from_blueprint.py`（slot 模板 + MCQ key rebalance）
- 首輪 `question_review` 可能仍有 duplicate／concept conflict → Phase 5 partial regen

### Step 5 — question_review

等同現行 `run_question_spec_check`（過渡名），檢查：

| 檢查 | 說明 |
|------|------|
| Duplicate | vs 校內 past + template |
| Bank similarity | vs `DSE-ICT/question-bank`（**review**，唔 block pick） |
| Coherence | 乙丙 scenario / subpart 通順 |
| Answers | MCQ key、缺答案 |
| Concepts | MCQ A→B→D sequence |

### Step 6 — Partial regen

```bash
.venv/bin/python shared-tools/paper-generator/partial_regen_spec.py --rounds 3
# 或 generate_from_blueprint.py --partial-regen --regen-rounds 3
```

```text
FOR each slot_id IN failed_slots:
  FOR attempt IN 1..10:
    regenerate slot_id only (variant seed)
    IF local review (intra-dup + coherence) ok: BREAK
  ELSE: append to unresolved_slots in *.partial_regen.json
REPEAT rounds until question_review clean or max rounds
STOP — no whole-paper re-seed loop
```

### Step 7 — Render DOCX

```bash
.venv/bin/python shared-tools/paper-generator/render_from_spec.py --force
```

- `spec_mcq_render.py` — spec 甲部 → template MCQ row blocks（`_layout_mcq_block`）
- `written_picks_from_items` + `written_picks_render` — 乙丙全文寫入模板
- 模板：`24_25_S5_ICT_Exam02.docx` → `25_26_S5_ICT_Exam02.docx`

### Step 8 — paper_review

- `run_post_render_check` — footer、cover、乙丙結構
- `written_spec_docx_check` — 每 slot spec text vs DOCX ≥92%

---

## Review 命名對照

| 目標名 | 現行模組 | 輸入 |
|--------|----------|------|
| concept_review | `concept_review.py` | blueprint + concept_map |
| question_review | `question_review.py` → `post_check.run_question_review` | `*.spec.json` |
| paper_review | `paper_review.py` → `post_check.run_paper_review` | spec + DOCX |

`run_question_review` / `run_paper_review` 為 `post_check` 別名（Phase 7）。

---

## Similarity 政策（新）

| 階段 | 角色 |
|------|------|
| Generate | 唔讀 bank stem；自然低相似 |
| question_review | 甲部 stem 目標 ≤60% vs bank + past；乙丙 stem ≤60%、子題 ≤85% |
| Fail | regen **該 slot only**，唔成卷 retry |

Review 閾值常數仍喺 `f5_ict_from_dse.py` / `quality_lib.py`。  
**Pick-time gate 預設關閉**（`f5_ict_pipeline_flags.PICK_TIME_BANK_SIM_GATE`）；legacy pick 設 `PICK_TIME_BANK_SIM_GATE=1`。

---

## 實施 phase

| Phase | 交付 | 狀態 |
|-------|------|------|
| **0** | Skill + 本文 + `EXAM_SPEC_AND_DOCX` 更新 | ✅ |
| **1** | `extract_style_patterns.py` | ✅ |
| **2** | `concept_map.json` tree | ✅ |
| **3** | `exam_blueprint.json` schema + `concept_review` | ✅ |
| **4** | `generate_from_blueprint.py` → spec | ✅ |
| **5** | `partial_regen_spec.py`（max 10/slot） | ✅ |
| **6** | `render_from_spec.py` + paper_review | ✅ |
| **7** | Deprecate pick-transform；review CLI aliases | ✅ |

---

## 主入口（Phase 7）

```bash
.venv/bin/python shared-tools/paper-generator/build_f5_exam02.py
# = generate_from_blueprint --partial-regen --question-check
#   + render_from_spec --force

.venv/bin/python shared-tools/paper-generator/question_review.py
.venv/bin/python shared-tools/paper-generator/paper_review.py
```

`Subjects/…/_generation/regenerate_exam02.py` **預設轉發** `build_f5_exam02.py`；`--legacy-pick` 先會跑舊 bank pick。

---

## Legacy：`regenerate_exam02.py --legacy-pick`

Bank pick + transform；`PICK_TIME_BANK_SIM_GATE=1`、seed 進度每 5 次。

**唔再擴充。** 新卷用 blueprint generate；相似度只喺 `question_review` / partial regen 處理。

舊規劃文檔 `F5_ICT_DSE_BLUEPRINT_FLOW.md` 已刪除（2026-05 整理）。

---

## 相關路徑

| 角色 | Path |
|------|------|
| C&A Guide | `Subjects/DSE-ICT/edb/ICT_C&A Guide_c_final.pdf` |
| Bank | `Subjects/DSE-ICT/question-bank/` |
| iClass depth (Core D 校準) | `Subjects/DSE-ICT/iclass-hk/` → `iclass_hk_depth.py`；spec 每題 `depth_references` |
| Curriculum (flat) | `.../curriculum_concepts.json` |
| Template | `Subjects/S5-ICT/past-papers/2024-2025/Term 02/WrittenExam/24_25_S5_ICT_Exam02.docx` |
| Spec / generation | `Subjects/S5-ICT/assessments/2025-2026/Term 02/_generation/` |
| Spec↔DOCX | `EXAM_SPEC_AND_DOCX.md` |
