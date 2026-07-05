# How to set up `GOOGLE_API_KEY` (`.env`)

> Canonical copy also in `_platform/docs/GOOGLE_API_KEY.md` (platform submodule).

Store your Gemini API key in a **repo-root `.env` file**. Python tools load it automatically when they need LLM credentials.

## Quick setup

```bash
cd /Users/warren_chan/Projects/school-agent-os

# 1. Install dotenv support (once)
pip install python-dotenv
# or: pip install -r requirements.txt

# 2. Create your private .env from the template
cp .env.example .env

# 3. Edit .env — paste your key after the equals sign (no quotes needed)
#    GOOGLE_API_KEY=AIza...your-key-here
```

Get a key: [Google AI Studio — API keys](https://aistudio.google.com/apikey).

`.env` is in `.gitignore` and will **not** be committed. Only `.env.example` (no secrets) is tracked.

---

## What it is used for

| Tool | Purpose |
|------|---------|
| `shared-tools/pdf-engine/refine_dse_ict_question_bank.py` | LLM cleanup of OCR `questions.json` → `questions_refined.json` |

On startup, `LlmConfig.from_env()` calls `load_repo_env()` (`shared-tools/repo_env.py`), which reads `school-agent-os/.env`.

| Variable | Meaning |
|----------|---------|
| `GOOGLE_API_KEY` | Primary Gemini key |
| `GEMINI_API_KEY` | Same as above (either works) |
| `DSE_ICT_LLM_PROVIDER` | `gemini` or `openai` |
| `DSE_ICT_LLM_MODEL` | Override model (default: `gemini-2.0-flash`) |
| `OPENAI_API_KEY` | If using `--provider openai` |

Variables already set in your shell are **not** overwritten by `.env`.

---

## Run a tool (no manual `source` needed)

```bash
cd /Users/warren_chan/Projects/school-agent-os

python shared-tools/pdf-engine/refine_dse_ict_question_bank.py \
  --years 2019 \
  --slugs Paper1_MultipleChoice \
  --provider gemini
```

Vision mode (more accurate on scans, more quota):

```bash
python shared-tools/pdf-engine/refine_dse_ict_question_bank.py \
  --years 2019 \
  --slugs Paper1_MultipleChoice \
  --provider gemini \
  --mode vision
```

---

## Verify

```bash
# Optional: check .env file exists (do not paste output in chat)
test -f .env && echo ".env OK"

# Dry-run: missing key shows path to .env in the error message
python -c "
import sys
sys.path.insert(0, 'shared-tools')
sys.path.insert(0, 'shared-tools/pdf-engine')
from dse_ict_llm_refine import LlmConfig
try:
    LlmConfig.from_env(provider='gemini')
    print('Gemini key loaded OK')
except RuntimeError as e:
    print(e)
"
```

---

## Troubleshooting

| Problem | What to try |
|---------|-------------|
| `GOOGLE_API_KEY is not set` | Create `.env` from `.env.example`; no spaces around `=` |
| `python-dotenv` missing | `pip install python-dotenv` |
| Key in `.env` but still fails | Run from repo; `.env` must be next to `.gitignore` / `.env.example` |
| `403` / invalid key | New key at AI Studio; no extra quotes in `.env` |
| Prefer shell export instead | `export GOOGLE_API_KEY=...` still works and takes precedence |

---

## Security

- Never commit `.env` or paste keys into issues/chat
- Rotate at [AI Studio](https://aistudio.google.com/apikey) if exposed

## Further reading

- `shared-tools/pdf-engine/README.md`
- `Subjects/DSE-ICT/README.md`
