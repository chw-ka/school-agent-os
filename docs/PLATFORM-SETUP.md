# Platform submodule 設定

本 repo 以 **`_platform/`** git submodule 掛載共建平台（`shared-tools`、`templates`、通用 Cursor skills）。

## 首次設定

```bash
git clone --recurse-submodules https://github.com/chw-ka/school-agent-os.git
cd school-agent-os
./scripts/link-platform.sh          # macOS/Linux：建立 shared-tools 等 symlink
pip install -r _platform/requirements.txt
cp .env.example .env                # API keys 留在 personal repo 根目錄
```

已 clone 但未拉 submodule：

```bash
git submodule update --init --recursive
./scripts/link-platform.sh
```

## 更新 platform

```bash
cd _platform && git pull origin main && cd ..
git add _platform
git commit -m "Bump platform submodule"
./scripts/link-platform.sh          # 通常 symlink 毋須改；保險起見可再跑
```

或 pin 某 tag：

```bash
cd _platform && git checkout v0.1.0 && cd ..
git add _platform && git commit -m "Pin platform v0.1.0"
```

## Symlinks（向後相容）

| Symlink | 指向 |
|---------|------|
| `shared-tools/` | `_platform/shared-tools/` |
| `templates/` | `_platform/templates/` |
| `.cursor/skills/meeting-minutes` 等 | `_platform/.cursor/skills/…` |

現有文件與 CLI 仍可用 `python shared-tools/...`；毋須改路徑。

**Windows：** Git 需啟用 symlink（`git config core.symlinks true`），或以管理員執行 `scripts/link-platform.ps1`（若提供）；否則直接使用 `_platform/shared-tools/` 路徑。

## Platform repo 獨立推送（maintainer）

Platform 源碼在 sibling repo `school-agent-os-platform`（本機）或 GitHub：

```bash
cd ../school-agent-os-platform   # 或 _platform
git push -u origin main          # 首次需 gh repo create / 手動建 repo
```

`.gitmodules` 內 URL：`https://github.com/chw-ka/school-agent-os-platform.git`

## Personal vs platform 分工

| Platform `_platform/` | Personal（本 repo） |
|-----------------------|---------------------|
| `shared-tools/`, `templates/` | `Subjects/`, `Administrative/` |
| `meeting-minutes`, `tidy-up`, `_template` skills | `generate-f5-ict-*`, `panel-storage-sync`, … |
| Tool API docs in `_platform/docs/` | `NAV.md`, `Subjects/STORAGE.md` |

見 [PLATFORM-COLLABORATION.md](PLATFORM-COLLABORATION.md)。
