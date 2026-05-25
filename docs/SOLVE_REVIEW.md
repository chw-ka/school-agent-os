# Solve review（解題審查）— Phases 1–4

用 LLM（**DeepSeek** / Gemini / OpenAI-compatible）模擬中五學生逐題作答，找出「答唔到」的題目，並把修復建議餵返 partial regen。

## 第一步：設定 API key（只需做一次）

### 推薦：DeepSeek

完整教學 → **[DEEPSEEK_API.md](DEEPSEEK_API.md)**

```bash
cd /Users/warren_chan/Projects/school-agent-os
cp .env.example .env
# 編輯 .env：
#   DSE_ICT_LLM_PROVIDER=deepseek
#   DEEPSEEK_API_KEY=sk-...

.venv/bin/pip install -r requirements.txt
.venv/bin/python shared-tools/paper-generator/solve_review.py --check-key
.venv/bin/python shared-tools/paper-generator/solve_review.py --test-api --provider deepseek
```

### 備選：Gemini

若學校 Google 專案有配額，見 [GOOGLE_API_KEY.md](GOOGLE_API_KEY.md)。Gemini 被 403/429 時請改用 DeepSeek。

```env
GOOGLE_API_KEY=...
DSE_ICT_LLM_PROVIDER=gemini
```

---

## Phase 1 — 解題報告

```bash
.venv/bin/python shared-tools/paper-generator/solve_review.py \
  --provider deepseek \
  --spec "Subjects/S5-ICT/past-papers/2025-2026/Term 02/_generation/25_26_S5_ICT_Exam02.spec.json" \
  --sync-tables --save-spec \
  --merge-rules
```

- 讀每題 `text` + **render 會用嘅表**（`f5_ict_written_tables` 同款）  
- 輸出：`25_26_S5_ICT_Exam02.solve_review.json`  
- `--merge-rules` 更新 `Subjects/DSE-ICT/question-bank/solve_generation_rules.json`（Phase 4）

---

## Phase 2 — 用 feedback 修題 + partial regen

先跑 Phase 1，再：

```bash
.venv/bin/python shared-tools/paper-generator/partial_regen_spec.py \
  --solve-repair \
  --rounds 2
```

- 讀 `*.solve_review.json` 的 blocked slots  
- 先 **LLM repair**（按 `repair_constraints`），再 **pattern regen**  
- 仍會跑 `question_review`

---

## Phase 3 — 對照已 render 的 DOCX

```bash
.venv/bin/python shared-tools/paper-generator/solve_review.py \
  --docx "Subjects/S5-ICT/past-papers/2025-2026/Term 02/WrittenExam/25_26_S5_ICT_Exam02.docx"
```

- 檢查卷面表格數量是否足夠（「見表」題）  
- 可選：有 PDF 時 `--vision-page 5` 用該頁圖做 vision（需 PDF 與 DOCX 同 stem）

---

## Phase 4 — 累積生成規則

每次 `--merge-rules` 會把 `issue_kinds` / `repair_constraints` 寫入：

`Subjects/DSE-ICT/question-bank/solve_generation_rules.json`

之後出題工具可讀取（`solve_generation_rules.constraints_for_slot`）。

---

## 一條龍（generate + solve + repair）

```bash
.venv/bin/python shared-tools/paper-generator/generate_from_blueprint.py \
  --concept-review --partial-regen --regen-rounds 2

.venv/bin/python shared-tools/paper-generator/solve_review.py --sync-tables --save-spec --merge-rules

.venv/bin/python shared-tools/paper-generator/partial_regen_spec.py --solve-repair --rounds 2

.venv/bin/python shared-tools/paper-generator/render_from_spec.py
```

---

## 費用與時間

- 全卷約 43 次 LLM 呼叫（每題一次）  
- 預設 `gemini-2.0-flash`，一般比 vision 平  
- 可先 `--item b-05` 試一題

---

## 故障

| 情況 | 處理 |
|------|------|
| `GOOGLE_API_KEY is not set` | 完成上面 `.env` 設定 |
| `python-dotenv` 缺失 | `pip install python-dotenv` 或 `pip install -r requirements.txt` |
| 全部 blocked | 睇 `*.solve_review.json` 的 `repair_constraints`，人手改 spec 或再 `--solve-repair` |
