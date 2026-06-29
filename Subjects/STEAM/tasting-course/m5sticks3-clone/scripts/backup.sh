#!/usr/bin/env bash
# 從主機 M5StickS3 將所有分區備份至 backups/。
# 在複製學生裝置前，只需對主機裝置執行一次。
#
# 用法：
#   ./backup.sh                     # 自動偵測連接埠
#   ./backup.sh /dev/cu.usbmodem101 # 指定連接埠
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ESPTOOL="$SCRIPT_DIR/../.venv/bin/esptool.py"
BACKUPS="$SCRIPT_DIR/../backups"

if [ ! -f "$ESPTOOL" ]; then
  echo "請先執行 setup.sh。"
  exit 1
fi

PORT="${1:-}"
if [ -z "$PORT" ]; then
  PORT=$(ls /dev/cu.usbmodem* /dev/ttyUSB* 2>/dev/null | head -1)
  [ -z "$PORT" ] && { echo "找不到 USB 序列埠。請插入主機裝置。"; exit 1; }
fi
echo "使用連接埠：$PORT"

ESPTOOL_CMD="$ESPTOOL --port $PORT --baud 460800 --chip esp32s3"

# 分區佈局（根據教師培訓主機的 manifest.json）
declare -A PARTS=(
  [nvs]="0x9000 0x4000"
  [otadata]="0xd000 0x2000"
  [phy_init]="0xf000 0x1000"
  [app0]="0x10000 0x160000"
  [coredump]="0x170000 0x10000"
  [sticks]="0x180000 0x2b0000"
  [spiffs]="0x430000 0x70000"
  [stick1]="0x4a0000 0x2b0000"
)

mkdir -p "$BACKUPS/partitions"

for name in "${!PARTS[@]}"; do
  read -r offset size <<< "${PARTS[$name]}"
  outfile="$BACKUPS/partitions/${name}__${offset}__${size}.bin"
  echo "  讀取 $name（$offset，$size）→ $outfile"
  $ESPTOOL_CMD read_flash "$offset" "$size" "$outfile"
done

# 同時備份 bootloader 區域（0x0–0x8FFF），以備完整還原
echo "  讀取 bootloader 區域 → $BACKUPS/bootloader-region.bin"
$ESPTOOL_CMD read_flash 0x0 0x9000 "$BACKUPS/bootloader-region.bin"

echo ""
echo "備份完成。檔案已寫入 $BACKUPS/"
echo "下一步：執行 flash_all.sh 複製學生裝置。"
