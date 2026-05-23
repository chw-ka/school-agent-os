---
name: generate-f5-ict-exam
description: >-
  End-to-end workflow to build an S5 ICT school exam: concept blueprint,
  DSE-style generation (not bank copy), concept/question/paper review, DOCX
  deliverable. Use when generating or regenerating 中五 ICT 試卷, Term 2 Exam02,
  past-papers under Subjects/S5-ICT, or when the user wants a paper that feels
  like DSE but is not traceable to one DSE year.
---

# Generate S5 ICT exam

## Target architecture（目標流程，2026-05 起）

**原則：** question-bank 唔再 **抄題**；bank + C&A Guide 只提供 **concept map** 同 **問法／語法／專有名詞** patterns。題目由 blueprint **生成**，similarity 喺 **question review** 階段驗證，唔喺 pick 階段 hard-block 成卷。

| Layer | Artifact | Checks |
|-------|----------|--------|
| **Side products** | `concept_map.json`（tree）、`style_patterns.json` | 定期由 bank + `edb/ICT_C&A Guide_c_final.pdf` 更新 |
| **Planning** | `exam_blueprint.json` | **concept_review** |
| **Intellect** | `_generation/*.spec.json` | **question_review** |
| **Execution** | `WrittenExam/*.docx` | **paper_review**（spec == docx） |

**Mandatory order:**

1. 設計考核比例 → `exam_blueprint.json`
2. 從 DSE bank / past paper 統計攞 **concepts**（唔攞 stem 原文）
3. **concept_review** — 重覆、對 C&A concept map、common mistakes、out-of-syllabus
4. **generate** — 按 style patterns 自製每 slot 題目（agent 或 `generate_item` tool）
5. **question_review** — vs bank／校內 past、乙丙 coherence、缺答案、前文後理
6. Fail → **只 regen 有問題 slot**，每 slot **最多 10 次**；仍 fail → `unresolved_slots` report，**唔 loop 成卷**
7. Pass → **render DOCX**（甲部、封面、footer 要準；乙丙 render 持續改善）
8. **paper_review** — footer／cover／乙丙結構；written spec↔DOCX ≥92%

```mermaid
flowchart TD
  subgraph side["Side products（一次性／定期）"]
    CA["ICT_C&A Guide PDF"]
    BANK["question-bank JSON"]
    CM["concept_map.json"]
    SP["style_patterns.json"]
    CA --> CM
    BANK --> CM
    BANK --> SP
  end

  subgraph plan["1–3 Planning"]
    BP["exam_blueprint.json"]
    CR["concept_review"]
    BP --> CR
    CM --> CR
  end

  subgraph gen["4 Generate"]
    G["generate slots → spec.json"]
    CR -->|pass| G
    SP --> G
    CM --> G
  end

  subgraph qr["5–6 Question review + partial regen"]
    QR["question_review"]
    G --> SPEC["*.spec.json"]
    SPEC --> QR
    QR -->|fail slot| REGEN["regen failed slots only<br/>max 10 / slot"]
    REGEN --> G
    QR -->|pass| RENDER
  end

  subgraph deliver["7–8 Render + paper review"]
    RENDER["generate() → DOCX"]
    PR["paper_review"]
    RENDER --> PR
  end
```

詳細 schema、實施 phase、工具清單 → [`reference.md`](reference.md) 及 `shared-tools/paper-generator/F5_ICT_CONCEPT_GENERATE_FLOW.md`。

---

## Legacy implementation（過渡期，仍可用）

> **已知問題：** `regenerate_exam02.py` 用 bank **pick + transform**，pick 時要求 ≤60% similarity，好多 concept 難過關 → 大量 seed retry、**長時間無 output 似 hang**。  
> **過渡策略：** 已有合格 `*.spec.json` 時，只做 question_review + render；唔好無謂 re-pick 成卷。  
> 新卷應跟 **Target architecture** 逐步遷移，唔再擴充 pick-transform 邏輯。

| Phase | Tool name（目標） | 現行模組（過渡） |
|-------|-------------------|------------------|
| Concept | `concept_review` | `concept_check.py`（question-quality-check） |
| Question | `question_review` | `run_question_spec_check` / `check_spec.py` |
| Paper | `paper_review` | `run_post_render_check` |

Legacy 一鍵（Term 02 2025–26）：

```bash
cd /path/to/school-agent-os
.venv/bin/python "Subjects/S5-ICT/past-papers/2025-2026/Term 02/_generation/regenerate_exam02.py"
```

改 spec 後只跑 review（唔 re-pick）：

```bash
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
```

---

## What “done” looks like

1. **Feels like DSE** — Core A/B/D MCQ + Paper 1B/2-style 乙丙；用語跟 `dse_ict_style_guide.json` / `style_patterns.json`。
2. **Grounded in curriculum** — concepts 對齊 `concept_map.json`（來源：`edb/ICT_C&A Guide_c_final.pdf` + bank 統計）。
3. **Not traceable** — 唔係抄 DSE 某一條；question_review 確認 vs bank／校內 past 相似度合理（甲部 stem 目標 ≤60% 仍作 **review 指標**，唔作 pick gate）。
4. **School template** — `24_25_S5_ICT_Exam02.docx` 排版；spec 為內容 source of truth。

---

## Agent checklist（目標流程）

### 0 — Confirm scope

| Item | Default (Term 2 Exam02) |
|------|-------------------------|
| Subject path | `Subjects/S5-ICT/past-papers/{YYYY-YYYY}/Term 02/` |
| Template DOCX | Prior year `WrittenExam/*_Exam02.docx` |
| Output DOCX | `WrittenExam/{YY}_{YY}_S5_ICT_Exam02.docx` |
| Generation dir | `_generation/` |
| C&A Guide | `Subjects/DSE-ICT/edb/ICT_C&A Guide_c_final.pdf` |
| Bank | `Subjects/DSE-ICT/question-bank/` |
| Side products | `_generation/concept_map.json`, `style_patterns.json`（待建） |
| Python | `.venv/bin/python` from repo root |

### 1 — Blueprint

- 甲 30（Core A×10 → B×10 → D×10）、乙 6、丙 8（DB elective）；見 `mcq_core_plan.py`、`WRITTEN_SLOT_PLAN`。
- 寫 `exam_blueprint.json`：`slots[]` 每條 `id`、`concepts[]`、`marks`、`section`。

### 2 — concept_review

- 全卷 concept 分佈、slot 間重覆、對 `concept_map.json`。
- 對照 C&A out-of-syllabus rules（`curriculum_concepts.json` → 日後併入 tree map）。
- 輸出：`_generation/*.concept_review.json`（待建 CLI）。

### 3 — Generate → spec

- 每 slot：用 `style_patterns.json` + blueprint concepts **寫新題**（唔貼 bank stem）。
- 組裝 `build_f5_ict_exam_spec()` → save `*.spec.json`。

### 4 — question_review

- `run_question_spec_check`（過渡名；日後 `question_review`）。
- Fail slot → 只改該 slot，最多 10 次 regen → 仍 fail 寫入 report。

### 5 — Render + paper_review

- **Question pass 後先** `generate()` → DOCX。
- `run_post_render_check`：paper layout + written spec↔DOCX ≥92%。
- **唔好**喺 DOCX 改題目文字；改 spec 再 render。

### 6 — Publish

- Git：交付用 DOCX + spec；`_generation` 審計檔可 commit。
- Panel S：只 final DOCX/PDF，**要明示許可**（`panel-storage-sync`）。

---

## Exam structure (fixed)

| 部分 | 對應 DSE | 內容 |
|------|----------|------|
| 甲部 | Paper 1A | 30 MCQ，Core A/B/D only |
| 乙部 | Paper 1B | 6 結構題，無 MC |
| 丙部 | Paper 2 (A+C) | 8 結構題，數據庫選修，無 MC |

---

## Hard rules

1. **Tool-first** — `shared-tools/`；唔好喺 chat 貼成卷。
2. **Spec before DOCX** — question 迭代停喺 render 前。
3. **No bank copy** — bank 只供 patterns + concept 統計；生成題用新情境／數字。
4. **Partial regen** — max 10 attempts per failed slot；唔 re-seed 成卷。
5. **Privacy** — 唔 commit 成績／學生名單。
6. **Panel share** — 唔寫 `S:\...\08_Others` 除非用戶准許。

---

## Implementation status

| Phase | 內容 | 狀態 |
|-------|------|------|
| **0** | 本文檔 + skill / flow 文檔 | ✅ |
| **1** | `extract_style_patterns.py` → `style_patterns.json` | 🔲 |
| **2** | `concept_map.json` tree（C&A + bank） | 🔲（partial：`curriculum_concepts.json`） |
| **3** | `exam_blueprint.json` + `concept_review` CLI | 🔲 |
| **4** | `generate_item` / agent generate → spec | 🔲 |
| **5** | `question_review` + partial regen（max 10/slot） | 🔲（partial：`check_spec.py`） |
| **6** | Spec-driven render；乙丙改善 | 🟡（方案 A 已有；乙丙待優化） |
| **7** | Rename review modules；deprecate pick-transform | 🔲 |

---

## Related docs

- Commands & thresholds: [reference.md](reference.md)
- Technical flow & schemas: `shared-tools/paper-generator/F5_ICT_CONCEPT_GENERATE_FLOW.md`
- Spec/DOCX detail: `shared-tools/paper-generator/EXAM_SPEC_AND_DOCX.md`
- Rule: `.cursor/rules/paper-generator.mdc`
- Legacy pick flow（舊）: `F5_ICT_DSE_BLUEPRINT_FLOW.md`（歸檔說明）
