# DeepSeek API 設定教學（school-agent-os）

用 DeepSeek 跑 **solve_review**（解題審查）、**solve_repair**（修題）、以及 pdf-engine LLM 精修。  
API 與 OpenAI 相容，本 repo 已內建 `--provider deepseek`。

---

## 1. 申請 API Key

1. 打開 [DeepSeek 开放平台](https://platform.deepseek.com/)
2. 登入／註冊
3. 進入 [API Keys](https://platform.deepseek.com/api_keys)
4. 建立 key，複製（只顯示一次）

---

## 2. 寫入 `.env`（唔好 commit）

在 repo 根目錄：

```bash
cd /Users/warren_chan/Projects/school-agent-os
cp .env.example .env
```

編輯 `.env`（建議 **註解** `GOOGLE_API_KEY`，避免自動揀 Gemini）：

```env
DSE_ICT_LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=sk-你的金鑰

# 可選：改模型或 endpoint
# DSE_ICT_LLM_MODEL=deepseek-chat
# DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
```

| 變數 | 說明 |
|------|------|
| `DSE_ICT_LLM_PROVIDER` | 設 `deepseek` 強制用 DeepSeek |
| `DEEPSEEK_API_KEY` | DeepSeek 平台金鑰 |
| `DSE_ICT_LLM_MODEL` | 預設 `deepseek-chat`；推理可用 `deepseek-reasoner` |
| `DEEPSEEK_BASE_URL` | 預設 `https://api.deepseek.com/v1` |

安裝依賴（讀 `.env` 需要）：

```bash
.venv/bin/pip install -r requirements.txt
```

---

## 3. 測試

```bash
.venv/bin/python shared-tools/paper-generator/solve_review.py --check-key
```

應見 `DEEPSEEK_API_KEY set: True`、`Recommended: deepseek`。

```bash
.venv/bin/python shared-tools/paper-generator/solve_review.py --test-api --provider deepseek
```

見 `API test passed` 即可。

---

## 4. 出卷流程用法

### 解題審查（全卷）

```bash
.venv/bin/python shared-tools/paper-generator/solve_review.py \
  --provider deepseek \
  --sync-tables --save-spec \
  --merge-rules
```

輸出：`25_26_S5_ICT_Exam02.solve_review.json`

### 跟住用 feedback 修題

```bash
.venv/bin/python shared-tools/paper-generator/partial_regen_spec.py \
  --solve-repair \
  --provider deepseek \
  --rounds 2
```

### 一條龍（generate 時）

```bash
.venv/bin/python shared-tools/paper-generator/generate_from_blueprint.py \
  --solve-review \
  --solve-repair \
  --solve-provider deepseek \
  --partial-regen
```

### pdf-engine 題庫精修

```bash
.venv/bin/python shared-tools/pdf-engine/refine_dse_ict_question_bank.py \
  --years 2024 \
  --slugs Paper1_MultipleChoice \
  --provider deepseek
```

---

## 5. CLI `--provider` 選項

| 值 | 用途 |
|----|------|
| `deepseek` | DeepSeek（`DEEPSEEK_API_KEY`） |
| `gemini` | Google AI Studio（`GOOGLE_API_KEY`） |
| `openai` | 任意 OpenAI-compatible（`OPENAI_API_KEY` + `OPENAI_BASE_URL`） |

未設 `DSE_ICT_LLM_PROVIDER` 時自動優先：**DeepSeek key → Gemini key → OpenAI key**。

---

## 6. 私隱與費用

- 試卷 `spec.json` 文字會送到 DeepSeek 伺服器做解題判斷；**只放本機 `.env`**，唔 commit key 或學生資料。
- 收費以 [DeepSeek 定價](https://platform.deepseek.com/) 為準；solve 全卷約 40+ 次短請求。
- **Vision（卷面圖）** 唔支援 DeepSeek；用 spec + `item.tables` 即可。

---

## 7. 常見錯誤

| 錯誤 | 處理 |
|------|------|
| `DEEPSEEK_API_KEY is not set` | 檢查 `.env` 路徑在 repo 根、已 `pip install python-dotenv` |
| 仍走 Gemini | 註解 `GOOGLE_API_KEY` 或設 `DSE_ICT_LLM_PROVIDER=deepseek` |
| `401` | Key 錯或過期，重新建立 |
| `402` / insufficient balance | 平台充值 |
| JSON parse 失敗 | 試 `--model deepseek-chat`；或再跑一次 |

更多 solve 流程見 [SOLVE_REVIEW.md](SOLVE_REVIEW.md)。
