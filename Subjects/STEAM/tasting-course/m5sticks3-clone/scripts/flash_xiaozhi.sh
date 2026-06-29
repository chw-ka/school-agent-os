#!/usr/bin/env bash
# 將單一裝置從 UIFlow 2.0 切換至小智模式。
# 只寫入 otadata（開機分區指標）+ nvs（含小智設定的 WiFi 憑證）。
# 小智韌體（stick1 分區）已從複製時存入裝置，無需重新刷入。
# 速度極快：每部裝置約 5 秒。
#
# 用法：
#   ./flash_xiaozhi.sh                     # 自動偵測連接埠
#   ./flash_xiaozhi.sh /dev/cu.usbmodem101 # 指定連接埠
#
# 還原至 UIFlow 2.0：  ./flash_all.sh --quick
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ESPTOOL="$SCRIPT_DIR/../.venv/bin/esptool.py"
XIAOZHI_DIR="$SCRIPT_DIR/../xiaozhi"

if [ ! -f "$ESPTOOL" ]; then
  echo "請先執行 setup.sh。"
  exit 1
fi

if [ ! -d "$XIAOZHI_DIR" ] || [ -z "$(ls "$XIAOZHI_DIR"/*.bin 2>/dev/null)" ]; then
  echo "錯誤：在 $XIAOZHI_DIR 找不到小智分區 bin 檔"
  echo "請先從已啟動小智的主機裝置備份："
  echo "  1. 將主機切換至小智（M5Launcher → 選擇小智）"
  echo "  2. 執行：esptool.py read_flash 0xd000 0x2000 xiaozhi/otadata_xiaozhi.bin"
  echo "  3. 執行：esptool.py read_flash 0x9000 0x4000 xiaozhi/nvs_xiaozhi.bin"
  exit 1
fi

PORT="${1:-}"
if [ -z "$PORT" ]; then
  PORT=$(ls /dev/cu.usbmodem* /dev/ttyUSB* 2>/dev/null | head -1)
  [ -z "$PORT" ] && { echo "找不到 USB 序列埠。請插入裝置。"; exit 1; }
fi
echo "正在刷入小智至：$PORT"

"$ESPTOOL" --port "$PORT" --baud 460800 --chip esp32s3 write_flash --no-progress \
  0x9000  "$XIAOZHI_DIR/nvs_xiaozhi.bin" \
  0xd000  "$XIAOZHI_DIR/otadata_xiaozhi.bin"

echo "完成。重新開機後裝置將啟動小智。"
echo "還原 UIFlow 2.0：  ./flash_all.sh --quick"
