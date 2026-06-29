#!/usr/bin/env bash
# 從主機備份將所有已連接的 M5StickS3 裝置刷機。
# 插好所有 USB-C 線後執行此腳本。
# 每部裝置在各自連接埠上偵測，並行刷機。
#
# 用法：
#   ./flash_all.sh          # 刷新所有偵測到的裝置
#   ./flash_all.sh --quick  # 快速重設：只寫 NVS + SPIFFS（每部約 30 秒）
#                           # 兩節課之間使用（韌體完好時）
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ESPTOOL="$SCRIPT_DIR/../.venv/bin/esptool.py"
BACKUPS="$SCRIPT_DIR/../backups/partitions"

if [ ! -f "$ESPTOOL" ]; then
  echo "請先執行 setup.sh。"
  exit 1
fi

QUICK=false
[[ "${1:-}" == "--quick" ]] && QUICK=true

# 偵測所有已連接的 M5StickS3 連接埠
PORTS=($(ls /dev/cu.usbmodem* /dev/ttyUSB* 2>/dev/null || true))
if [ ${#PORTS[@]} -eq 0 ]; then
  echo "找不到 USB 序列埠。請插入學生裝置。"
  exit 1
fi
echo "找到 ${#PORTS[@]} 部裝置：${PORTS[*]}"
echo ""

flash_device() {
  local port="$1"
  local label="[${port##*/}]"
  local CMD="$ESPTOOL --port $port --baud 460800 --chip esp32s3 write_flash --no-progress"

  if $QUICK; then
    # 快速重設——只寫 NVS（WiFi 憑證）+ SPIFFS（UIFlow 專案）
    echo "$label 快速重設：寫入 NVS + SPIFFS"
    $CMD \
      0x9000   "$BACKUPS/nvs__0x9000__0x4000.bin" \
      0x430000 "$BACKUPS/spiffs__0x430000__0x70000.bin" \
      && echo "$label 完成（快速）" \
      || echo "$label 失敗"
  else
    # 完整還原——寫入所有分區（bootloader 除外）
    echo "$label 完整刷機：寫入所有分區"
    $CMD \
      0x9000   "$BACKUPS/nvs__0x9000__0x4000.bin" \
      0xd000   "$BACKUPS/otadata__0xd000__0x2000.bin" \
      0xf000   "$BACKUPS/phy_init__0xf000__0x1000.bin" \
      0x10000  "$BACKUPS/app0__0x10000__0x160000.bin" \
      0x170000 "$BACKUPS/coredump__0x170000__0x10000.bin" \
      0x180000 "$BACKUPS/sticks__0x180000__0x2b0000.bin" \
      0x430000 "$BACKUPS/spiffs__0x430000__0x70000.bin" \
      0x4a0000 "$BACKUPS/stick1__0x4a0000__0x2b0000.bin" \
      && echo "$label 完成（完整）" \
      || echo "$label 失敗"
  fi
}

export -f flash_device
export ESPTOOL BACKUPS QUICK

# 並行刷新所有連接埠
for port in "${PORTS[@]}"; do
  flash_device "$port" &
done
wait

echo ""
echo "所有裝置刷機完成。請重新開機，裝置將啟動 UIFlow 2.0。"
