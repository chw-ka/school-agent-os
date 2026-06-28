#!/usr/bin/env bash
# Flash M5Launcher only (for blank / factory StickS3 units).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ ! -x "$ROOT/.venv/bin/python" ]]; then
  echo "Run scripts/setup.sh first."
  exit 1
fi

PORT="${1:-${PORT:-}}"
if [[ -z "$PORT" ]]; then
  echo "Usage: $0 <serial-port>"
  exit 1
fi

LAUNCHER="$ROOT/firmware/Launcher-m5stack-sticks3.bin"
if [[ ! -f "$LAUNCHER" ]]; then
  echo "Missing $LAUNCHER"
  echo "Run scripts/setup.sh to download firmware."
  exit 1
fi

echo "==> Flashing M5Launcher to $PORT"
echo "WARNING: GitHub release .bin is an app image, not a full factory image."
echo "If this fails to boot, use the web flasher instead:"
echo "  https://bmorcelli.github.io/Launcher/"
echo ""
echo "This script writes the Launcher app to 0x10000 on a device that already"
echo "has a compatible bootloader + partition table (e.g. after M5Burner stock flash)."
echo ""

read -r -p "Continue? [y/N] " ans
if [[ "$ans" != "y" && "$ans" != "Y" ]]; then
  exit 0
fi

.venv/bin/python -m esptool --chip esp32s3 --port "$PORT" --baud 460800 \
  write-flash --flash-size 8MB --flash-mode dio --flash-freq 80m \
  0x10000 "$LAUNCHER"

echo "Done. If the device does not boot into M5Launcher, restore from master backup with:"
echo "  INCLUDE_BOOT=1 ./scripts/provision-device.sh $PORT"
