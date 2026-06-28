# Google Forms（由 JSON spec 建立）

用 `configs/` 內 OAuth 憑證，透過 Google Forms API 由 JSON spec 建立問卷。

## 憑證

| 檔案 | 用途 |
|------|------|
| `configs/gcp-oauth.keys.json` | OAuth client（Desktop） |
| `configs/google-forms-oauth-token.json` | 已授權 token（含 refresh） |

首次授權需在本機瀏覽器完成 OAuth；token 過期會自動 refresh 並寫回 `google-forms-oauth-token.json`。

## CLI

```bash
python shared-tools/google-forms/create_google_form.py shared-tools/google-forms/examples/elearning-staff-survey-2026-27.spec.json

# 儲存 form ID / 連結
python shared-tools/google-forms/create_google_form.py path/to/form.spec.json --json-out output/form-meta.json
```

## Spec 格式

```json
{
  "title": "問卷標題",
  "document_title": "Google Drive 檔名（可選）",
  "description": "問卷說明（可選）",
  "questions": [
    { "type": "description", "title": "...", "description": "..." },
    { "type": "section", "title": "...", "description": "..." },
    { "type": "text", "title": "...", "required": false },
    { "type": "paragraph", "title": "...", "required": true },
    {
      "type": "choice",
      "title": "...",
      "choice_type": "RADIO",
      "options": ["A", "B"],
      "required": true
    }
  ]
}
```

`choice_type`：`RADIO`（單選）、`CHECKBOX`（多選）、`DROP_DOWN`（下拉）。

範例：`examples/elearning-staff-survey-2026-27.spec.json`
