#!/usr/bin/env bash
# Provision one target M5StickS3 from master backup (no SD card required).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ ! -x "$ROOT/.venv/bin/python" ]]; then
  echo "Run scripts/setup.sh first."
  exit 1
fi

PORT="${1:-${PORT:-}}"
MODE="${MODE:-apps-data}"
# Default ON: new/factory StickS3 need master bootloader or M5Launcher in app0 is skipped.
INCLUDE_BOOT="${INCLUDE_BOOT:-1}"

if [[ -z "$PORT" ]]; then
  echo "Usage: $0 <serial-port>"
  echo "Example: $0 /dev/cu.usbmodem1101"
  echo ""
  echo "Environment overrides:"
  echo "  MODE=full              Also restore phy_init (RF calibration)"
  echo "  INCLUDE_BOOT=0         Skip bootloader (only if target already has master bootloader)"
  exit 1
fi

if [[ ! -f "$ROOT/backups/manifest.json" ]]; then
  echo "Missing backups/manifest.json"
  echo "Connect the master StickS3 and run: ./scripts/backup-master.sh <port>"
  exit 1
fi

ARGS=(scripts/partition_utils.py provision --port "$PORT" --mode "$MODE")
if [[ "$INCLUDE_BOOT" == "0" ]]; then
  ARGS+=(--no-include-bootloader)
fi

echo "==> Provisioning target on $PORT (mode=$MODE, include_bootloader=$INCLUDE_BOOT)"
echo "    Download mode: long-press RESET until green LED blinks."
echo ""

.venv/bin/python "${ARGS[@]}"

echo ""
echo "Target flashed. Power-cycle and check M5Launcher splash at boot."
echo "Press M5 during splash to open Launcher menu."
echo "Already flashed without bootloader? Run: ./scripts/fix-launcher-boot.sh $PORT"
