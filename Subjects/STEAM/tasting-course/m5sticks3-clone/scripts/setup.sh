#!/usr/bin/env bash
# 一次性設定：在 m5sticks3-clone/ 內建立含 esptool 的虛擬環境
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV="$SCRIPT_DIR/../.venv"

python3 -m venv "$VENV"
"$VENV/bin/pip" install --quiet --upgrade pip esptool
echo "esptool 已安裝：$("$VENV/bin/esptool.py" version 2>&1 | head -1)"
echo "下一步：執行 backup.sh 備份主機裝置。"
