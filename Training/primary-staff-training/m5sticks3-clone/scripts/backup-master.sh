#!/usr/bin/env bash
# Backup master M5StickS3 (M5Launcher + 小智 + WiFi settings) via esptool.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ ! -x "$ROOT/.venv/bin/python" ]]; then
  echo "Creating Python venv and installing esptool..."
  python3 -m venv .venv
  .venv/bin/pip install -r requirements.txt
fi

PORT="${1:-${PORT:-}}"
if [[ -z "$PORT" ]]; then
  echo "Usage: $0 <serial-port>"
  echo "Example: $0 /dev/cu.usbmodem1101"
  echo ""
  echo "Tip (macOS): ls /dev/cu.usb*"
  exit 1
fi

echo "==> Master backup from $PORT"
echo "    Put the device in download mode first:"
echo "    USB connected -> long-press RESET until the green LED blinks."
echo ""

.venv/bin/python scripts/partition_utils.py backup --port "$PORT"

echo ""
echo "Done. Backup stored in: $ROOT/backups/"
