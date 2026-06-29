"""
將根目錄 .env 的 DeepSeek API 金鑰注入 starter/main.py
生成 starter/main_with_key.py——可作為 UIFlow 專案分享，
但請勿提交至 git。

用法：
    python scripts/gen_starter.py
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
# 向上尋找含 .env 的 git 根目錄（統一金鑰存放位置）
REPO_ROOT = ROOT
for _ in range(4):
    if (REPO_ROOT / ".env").exists() and (REPO_ROOT / ".git").exists():
        break
    REPO_ROOT = REPO_ROOT.parent

def load_env(path: Path) -> dict:
    env = {}
    if not path.exists():
        return env
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip()
    return env

def main():
    env = load_env(REPO_ROOT / ".env")
    key = env.get("DEEPSEEK_API_KEY", "")
    if not key or key.startswith("sk-REPLACE"):
        print("錯誤：請先在 .env 中設定 DEEPSEEK_API_KEY")
        sys.exit(1)

    src = (ROOT / "starter" / "main.py").read_text()
    out = re.sub(
        r'DEEPSEEK_API_KEY\s*=\s*"sk-REPLACE_WITH_YOUR_KEY"',
        f'DEEPSEEK_API_KEY = "{key}"',
        src,
    )

    dest = ROOT / "starter" / "main_with_key.py"
    dest.write_text(out)
    print(f"已生成：{dest}")
    print("請將此檔案匯入 UIFlow 2.0。請勿提交至 git。")

if __name__ == "__main__":
    main()
