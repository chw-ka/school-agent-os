---
name: cloudsams-browser-login
description: >-
  Opens CHW CloudSAMS in the Cursor automation browser (same tab, no popup)
  via CLO SSO POST hack, then navigates to ASR import or other flows. Use when
  the user asks to open CloudSAMS, log into CloudSAMS, fix expired session,
  or resume browser/CDP score import on chw.sams.edu.hk.
---

# CloudSAMS browser login (same window)

## Problem

CLO’s `WebSAMSRedirect(webSAMS_Id)` POSTs to `/RedirectToApp` with **`target="_blank"`** and `submitToPopup()`. The Cursor automation browser cannot follow that popup, so CDP upload/import automation never reaches `chw.sams.edu.hk`.

## Solution (same-tab SSO)

While logged into **CLO** on `https://clo.edb.gov.hk/`, POST `/RedirectToApp` with **`target="_self"`** via `browser_cdp` → `Runtime.evaluate`. CloudSAMS opens in the **same tab** the agent already controls.

## CHW constants

| Item | Value |
|------|--------|
| CLO home | `https://clo.edb.gov.hk/Home/Index` |
| CloudSAMS (CHW) | `https://chw.sams.edu.hk/` |
| School | CARMEL HOLY WORD SECONDARY SCHOOL (524573000133) |
| `webSAMS_Id` | **`840`** |
| ASR score import | `https://chw.sams.edu.hk/flows/asr/data_entry/import` |

If `webSAMS_Id` ever changes: on CLO home click **CloudSAMS**, read modal button `onclick="WebSAMSRedirect('…')"`.

## Workflow

1. **`browser_tabs`** — note `viewId` (e.g. `006d9d`). Use **one tab only** for the whole session.
2. **`browser_lock`** before automation.
3. **CLO session**
   - If not on CLO: navigate to `https://clo.edb.gov.hk/`.
   - User must be logged in (username visible, e.g. `warren922`). If not, ask user to sign in to CLO first.
4. **Same-window redirect** — call `browser_cdp` with `method: Runtime.evaluate` and the script in [scripts/same_window_redirect.js](scripts/same_window_redirect.js). Must run on a CLO page (token lives in DOM).
5. **Verify** — after navigation (~3–5s), URL should be `https://chw.sams.edu.hk/...`, title **CloudSAMS System**, user link visible (e.g. `warren`).
6. **Go to target** — e.g. `browser_navigate` to ASR import URL above.
7. **`browser_unlock`** when done with this step.

## Success checks

- URL contains `chw.sams.edu.hk` (not `login.xhtml`, not `expired.xhtml`)
- Page title: `CloudSAMS System Version …`
- Import page shows **選擇檔案** and **儲存** (save disabled until file uploaded)

## Failure modes

| Symptom | Action |
|---------|--------|
| `no token` from redirect script | Not on CLO while logged in — open CLO home, ensure login |
| `WebSAMSRedirect` / `submitToPopup` null error | Expected if using stock CLO button — use same-window POST instead |
| `expired.xhtml` | Session timed out — redo CLO login + same-window redirect |
| Tab on `clo.edb.gov.hk` after school click only | Popup path was used — use POST hack |

## After login: ASR score import

Score import automation lives under:

`Administrative/CHW/websams-management/cloudsams-templates/asr/_local/_cdp_exec/`

- Use **`viewId` from step 1** in all `browser_cdp` calls (`actions.jsonl` / `build_chunk_actions.py` must match).
- Do **not** start multiple `run_direct_import.py` / `mcp_driver.py` instances (they race on `cdp_pending.json`).
- Zips: `import-zips/DE_52457320260707_{124,134,144}.zip` (≤10 xls each).

## User phrases → action

- “open CloudSAMS” / “open cloudsams same window” → this skill, stop at CloudSAMS home or import page as context implies
- “session expired” / “try again” → CLO login + same-window redirect + reopen import page
- “continue import” → login if needed, then CDP bridge for remaining zips

## Do not

- Rely on CLO “Login via CLO” link from `chw.sams.edu.hk/login.xhtml` alone (does not SSO into automation tab)
- Use `fetch('http://127.0.0.1:…')` from HTTPS CloudSAMS (mixed content blocked)
- Open CloudSAMS in a new popup/window for automation
