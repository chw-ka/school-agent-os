# School-Agent-OS

基於 **Agentic Infrastructure** 的校園自動化系統。核心理念：**基礎設施大於 Prompt**，將行政與教學功能拆解為可重用的「微服務工具 (Shared Tools)」。

## Repo layout（platform + personal）

| 層級 | 路徑 | 說明 |
|------|------|------|
| **Platform（共建 submodule）** | `_platform/` | [school-agent-os-platform](https://github.com/chw-ka/school-agent-os-platform) — tools、templates、通用 skills |
| **Personal（本 repo）** | `Subjects/`, `Administrative/`, `Training/` | 你的教學／行政素材 |
| **Personal skills** | `.cursor/skills/`（非 symlink 者） | 科目／校務專用 workflow |
| **Compat symlinks** | `shared-tools/`, `templates/` | → `_platform/…`（現有 CLI 路徑不變） |

首次 clone 或更新 submodule 後：

```bash
git submodule update --init --recursive
./scripts/link-platform.sh
pip install -r _platform/requirements.txt
```

詳見 [docs/PLATFORM-SETUP.md](docs/PLATFORM-SETUP.md)、[docs/PLATFORM-COLLABORATION.md](docs/PLATFORM-COLLABORATION.md)。

## 根目錄索引

- `.cursorrules` — 憲法（工作原則、格式、隱私）
- `KIMI.md` — Kimi Code CLI 專案指令
- `.cursor/rules/` — 持久規則（panel sync、科目 workspace）
- `.cursor/skills/` — Agent 技能（platform 通用 + 個人專用）
- `NAV.md` — 工作項目索引
- `Subjects/` — 教學區 — [STORAGE.md](Subjects/STORAGE.md)
- `Administrative/` — 行政區

## Two machines (school / home)

| 環境 | 素材來源 |
|------|----------|
| **家中** | 本 repo（GitHub）— 無法存取 `S:` 科組資料夾 |
| **學校** | Repo + 可選從 `S:\02_Teaching and Learning\03_Key Learning Areas\Technology\08_Others` 拉入或發佈 |

在校將需要的檔案拉入 `Subjects/` 後 **commit + push**，家中即可 `git pull` 繼續工作。發佈檔案至 S: **須經批准**。詳見 [Subjects/STORAGE.md](Subjects/STORAGE.md)。

## Quick Start (Formatter Tool)

1. 建立並啟用 venv（建議）：
   - macOS/Linux: `python3 -m venv .venv && source .venv/bin/activate`
   - Windows: `python -m venv .venv && .venv\Scripts\Activate.ps1`
2. `git submodule update --init --recursive && ./scripts/link-platform.sh`
3. `pip install -r _platform/requirements.txt`
4. 參考 `_platform/templates/README.md` 放入試卷範本
5. `python shared-tools/paper-formatter/exam_generator.py --help`

## Panel sync helper (school only)

```powershell
.cursor/skills/panel-storage-sync/scripts/pull-from-panel.ps1 -Subject S2-CMP -Year 2024-2025 -WhatIf
```

## CHW API（學校資料 MCP）

學生、班別、教師等資料由 **[chw-api](https://github.com/chw-ka/chw-api)** 提供；本 repo 透過 MCP 取用。見 [docs/chw-api.md](docs/chw-api.md)。
