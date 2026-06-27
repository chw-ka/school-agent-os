#!/usr/bin/env bash
# Quick fix: restore master bootloader so M5Launcher (app0) boots instead of 小智 only.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PORT="${1:-${PORT:-}}"
if [[ -z "$PORT" ]]; then
  echo "Usage: $0 <serial-port>"
  echo ""
  echo "Use when a cloned StickS3 boots 小智 directly with no M5Launcher."
  echo "Cause: factory bootloader + master partition table (otadata boots ota_0 = 小智)."
  exit 1
fi

if [[ ! -f "$ROOT/backups/bootloader-region.bin" ]]; then
  echo "Missing backups/bootloader-region.bin — run backup-master.sh first."
  exit 1
fi

echo "==> Restoring M5Launcher bootloader on $PORT"
echo "    Download mode: long-press RESET until green LED blinks."
echo ""

.venv/bin/python scripts/partition_utils.py fix-bootloader --port "$PORT"
