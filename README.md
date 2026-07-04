# School-Agent-OS

基於 **Agentic Infrastructure** 的校園自動化系統。核心理念：**基礎設施大於 Prompt**，將行政與教學功能拆解為可重用的「微服務工具 (Shared Tools)」。

## Repo Structure

- `.cursorrules`: 根目錄憲法（工作原則、格式規範、隱私）
- `.cursor/rules/`: Agent 持久規則（例如 panel 共用資料夾同步）
- `.cursor/skills/`: 專案 Agent 技能（例如 `panel-storage-sync`、`tidy-up`）
- `shared-tools/`: 可重用 Python 工具（Skills）
- `Subjects/`: 教學區（依科目/級別分資料與流程）— 見 [Subjects/STORAGE.md](Subjects/STORAGE.md)、[NAV.md](NAV.md)
- `Administrative/`: 行政區（依功能分資料與流程）
- `templates/`: 學校標準 Word/PDF 範本

## Two machines (school / home)

| 環境 | 素材來源 |
|------|----------|
| **家中** | 本 repo（GitHub）— 無法存取 `S:` 科組資料夾 |
| **學校** | Repo + 可選從 `S:\02_Teaching and Learning\03_Key Learning Areas\Technology\08_Others` 拉入或發佈 |

在校將需要的檔案拉入 `Subjects/` 後 **commit + push**，家中即可 `git pull` 繼續工作。發佈檔案至 S: **須經批准**。詳見 [Subjects/STORAGE.md](Subjects/STORAGE.md)。

## Quick Start (Formatter Tool)

1. 建立並啟用 venv（建議）：
   - macOS/Linux:
     - `python3 -m venv .venv`
     - `source .venv/bin/activate`
   - Windows (PowerShell):
     - `python -m venv .venv`
     - `.venv\Scripts\Activate.ps1`
2. 安裝依賴：
   - `pip install -r requirements.txt`
3. 準備 Word 範本：
   - 參考 `templates/README.md` 放入 `templates/exam_template.docx`
4. 產生試卷：
   - `python shared-tools/paper-formatter/exam_generator.py --help`

## Panel sync helper (school only)

Dry-run pull from panel share into repo:

```powershell
.cursor/skills/panel-storage-sync/scripts/pull-from-panel.ps1 -Subject S2-CMP -Year 2024-2025 -WhatIf
```

Remove `-WhatIf` to copy; then commit and push.

## CHW API（學校資料 MCP）

學生、班別、教師等資料由獨立 repo **[chw-api](https://github.com/chw-ka/chw-api)** 提供（`https://api.chw.edu.hk`），本 repo 透過 MCP 或 REST 取用，不併入 chw-api 程式碼。

- 設定 Cursor MCP：複製 `.cursor/mcp.json.example`，填入 `X-API-Key`
- 工具清單與開發說明：[docs/chw-api.md](docs/chw-api.md)
