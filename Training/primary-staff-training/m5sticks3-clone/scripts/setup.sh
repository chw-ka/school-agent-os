#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "==> Setting up m5sticks3-clone tooling"

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi

.venv/bin/pip install -r requirements.txt

LAUNCHER="$ROOT/firmware/Launcher-m5stack-sticks3.bin"
VERSION="${LAUNCHER_VERSION:-2.7.2}"
URL="https://github.com/bmorcelli/Launcher/releases/download/${VERSION}/Launcher-m5stack-sticks3.bin"

if [[ ! -f "$LAUNCHER" ]]; then
  echo "==> Downloading M5Launcher ${VERSION} for StickS3"
  curl -L -o "$LAUNCHER" "$URL"
fi

chmod +x scripts/*.sh

echo ""
echo "Setup complete."
echo "  esptool: $(.venv/bin/python -m esptool version)"
echo "  firmware: $LAUNCHER ($(du -h "$LAUNCHER" | cut -f1))"
echo ""
echo "Next steps:"
echo "  1) Connect MASTER StickS3 -> ./scripts/backup-master.sh /dev/cu.usbmodemXXX"
echo "  2) For each target       -> ./scripts/provision-device.sh /dev/cu.usbmodemXXX"
