## Local credentials (do not commit secrets)

此資料夾存放**本機專用** API 金鑰同 OAuth 憑證。Git 只追蹤 `*.example.*` 範本；真實檔案已被 `.gitignore` 排除。

### 快速設定

```powershell
# LLM keys（培訓／一般工具）
copy configs\.env.example configs\.env
# 編輯 configs\.env 填入 GEMINI_API_KEY、DEEPSEEK_API_KEY 等

# Google Forms OAuth（shared-tools/google-forms/）
copy configs\gcp-oauth.keys.example.json configs\gcp-oauth.keys.json
# 填入 Google Cloud Console 下載嘅 Desktop OAuth client JSON
# 首次跑 create_google_form.py 會開瀏覽器授權，產生 google-forms-oauth-token.json
```

### 檔案對照

| 檔案 | 入 git？ | 用途 |
|------|---------|------|
| `.env.example` / `.env.sample` | 是（範本） | LLM API keys 說明 |
| `gcp-oauth.keys.example.json` | 是 | Google OAuth client 範本 |
| `gcp-service-account.example.json` | 是 | Service account 範本 |
| `cursor-models.example.json` | 是 | Cursor model 設定參考 |
| `.env` | **否** | 真實 API keys |
| `gcp-oauth.keys.json` | **否** | 真實 OAuth client |
| `google-forms-oauth-token.json` | **否** | 已授權 token（含 refresh） |
| `client_secret*.json` | **否** | Google 下載嘅 client secret |
| `staff-training-*.json` 等 | **否** | GCP service account 私鑰 |

### 若曾誤 commit 密鑰

1. 立即喺 Google Cloud / API 平台**輪換或撤銷**該金鑰  
2. 用 `git filter-repo` 或 GitHub secret scanning 指引清除歷史（必要時）  
3. 確認 `.gitignore` 規則生效：`git check-ignore -v configs/gcp-oauth.keys.json`
