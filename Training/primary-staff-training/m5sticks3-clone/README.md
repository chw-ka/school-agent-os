# M5StickS3 批量 Clone 教學（esptool.py，無 SD 卡）

用 **master M5StickS3**（已裝 M5Launcher + 小智 + WiFi 設定）備份 flash partitions，再還原到另外 20 部機。全程用 **esptool**，唔使 SD 卡。

## 你會得到咩

| 檔案 / 資料夾 | 用途 |
|---|---|
| `firmware/Launcher-m5stack-sticks3.bin` | M5Launcher 2.7.2（StickS3） |
| `firmware/custom_8Mb2.csv` | M5Launcher 預設 partition 參考 |
| `scripts/backup-master.sh` | 從 master 讀取備份 |
| `scripts/provision-device.sh` | 還原到 target 機 |
| `backups/` | 執行 backup 後產生（已 gitignore） |

## 前置準備

### 硬體
- Mac（已測試 Homebrew Python）
- USB-C 線
- 1 部 **master** StickS3（設定已完成）
- 最多 20 部 **target** StickS3

### 軟體（一次性）

```bash
cd m5sticks3-clone
./scripts/setup.sh
```

會建立 `.venv`、安裝 `esptool`，並下載 M5Launcher firmware。

### 進入 Download Mode（每部機都要）

1. USB 連接電腦  
2. **長按 Reset** 直到機身 **綠色 LED 閃爍**  
3. 放開 → 進入 download mode  

### 搵 Serial Port（macOS）

```bash
ls /dev/cu.usb*
# 例：/dev/cu.usbmodem1101
```

---

## 流程概覽

```mermaid
flowchart LR
  A[Master StickS3] -->|backup-master.sh| B[backups/]
  B -->|provision-device.sh x20| C[Target StickS3 #1..#20]
  C --> D[逐部綁定小智驗證碼]
```

---

## Step 1：備份 Master 機

```bash
./scripts/backup-master.sh /dev/cu.usbmodem1101
```

會讀取並儲存：

| 備份檔 | 內容 |
|---|---|
| `backups/bootloader-region.bin` | 0x00000–0x0FFFF |
| `backups/partition-table.bin` | Partition table |
| `backups/partitions/*.bin` | 每個 partition（含 M5Launcher、小智 app、NVS/WiFi、SPIFFS/FAT 等） |
| `backups/manifest.json` | Partition 清單同 offset |

**重要：** 備份前請確認 master 機：
- M5Launcher 版本係你想要嘅版本  
- 小智已安裝並可正常連 WiFi  
- WiFi 設定已儲存好  

---

## Step 2：還原到 Target 機（重複 20 次）

```bash
# 插上一部 target StickS3 → download mode → 執行：
./scripts/provision-device.sh /dev/cu.usbmodem1102
```

**預設會寫入 master bootloader**（`INCLUDE_BOOT=1`）。新機 / 原廠 StickS3 **一定要** 用 master bootloader，否則會直接 boot 入小智、睇唔到 M5Launcher。

預設模式 `apps-data` 會還原：

- **Bootloader region**（0x0–0xFFFF）← M5Launcher 開機關鍵  
- Partition table  
- 所有 app partitions（**app0 = M5Launcher**、sticks/stick1 = 小智）  
- 所有 data partitions（NVS、SPIFFS、otadata 等）  
- **跳過** `phy_init`（保留 target 原廠 RF 校正）

### 點解 clone 後會「冇 M5Launcher」？

Master 機 flash layout：

| Partition | 內容 |
|---|---|
| `app0` @ 0x10000 | **M5Launcher** |
| `sticks` @ 0x180000 | **小智**（ota_0） |
| `otadata` | 指向 boot **ota_0 → 小智** |

若 target 仍用 **原廠 bootloader**，佢會跟 `otadata` 直接 boot 入 `sticks`（小智），**跳過** `app0` 嘅 M5Launcher。

**解法：** provision 時必須寫入 master 嘅 bootloader（而家已係預設）。

### 已經 provision 咗、冇 Launcher 點算？

只補 bootloader（快）：

```bash
./scripts/fix-launcher-boot.sh /dev/cu.usbmodem1102
```

或完整重做：

```bash
./scripts/provision-device.sh /dev/cu.usbmodem1102
```

### 開機後點入 M5Launcher？

1. 正常開機會見 M5Launcher splash，然後自動入小智  
2. 想留喺 Launcher：**splash 出現時按 M5（Enter）** → 開 Launcher 選單  

### 進階選項

```bash
# 跳過 bootloader（只適用 target 已有 master bootloader）
INCLUDE_BOOT=0 ./scripts/provision-device.sh /dev/cu.usbmodem1102

# 連 phy_init 都 clone（一般唔建議）
MODE=full ./scripts/provision-device.sh /dev/cu.usbmodem1102
```

---

## Step 3：小智逐部綁定（必做）

Clone **唔會** 複製小智雲端綁定。每部機仍有 **獨立 MAC** 同 **獨立驗證碼**。

每部 target 開機後：

1. 確認已連上學校 WiFi（如 WiFi 已隨 NVS/SPIFFS clone，通常會自動連）  
2. 聽/睇 **6 位驗證碼**（語音、螢幕或 USB 串口）  
3. 登入 [小智 AI 控制面板](https://docs.m5stack.com/zh_CN/guide/realtime/xiaozhi/sticks3) → **添加設備**  
4. 用 `docs/device-log.csv` 記錄：`編號 | MAC | 驗證碼 | 綁定日期`

### 睇串口驗證碼（可選）

```bash
.venv/bin/python -m esptool --port /dev/cu.usbmodem1102 monitor
# 如無 monitor，可用 screen：
# screen /dev/cu.usbmodem1102 115200
```

---

## 常見問題

### Q: M5Burner 用 1.5M baud rate 會唔會影響 esptool backup？

**唔會。** M5Burner 燒錄時用幾高 baud rate，同 esptool 讀 flash 無關。  
esptool 用 460800 成功讀到 4096 bytes 就代表連接正常。  
若見 `Partition table is empty` 但 read 成功，通常係 **partition table 解析 bug**（已修正），唔係 baud rate 問題。

### Q: WiFi clone 咗但連唔到？

- 確認學校 WiFi 係 **2.4GHz**（StickS3 唔支援純 5GHz）  
- 重新喺 master 設定 WiFi 後再做一次 backup  
- 檢查 `backups/partitions/` 有無 `nvs__*` 同 `spiffs__*` 檔案  

### Q: 開機 boot loop / 白屏？

- 試 `INCLUDE_BOOT=1` 再 provision 一次  
- 確認 master 同 target 都係 **StickS3（ESP32-S3, 8MB flash）**  
- M5Launcher 版本要一致；如 master 用 OTA 升級過，以 master backup 為準  

### Q: 可唔可以 `read-flash 0 0x800000` 成粒 flash copy？

唔建議。全 flash clone 可能帶埋 otadata / app 狀態問題，且小智仍要逐部綁定。  
用 partition 方式較安全、可預測。

### Q: GitHub 嘅 Launcher `.bin` 可唔可以直接燒去新機？

Release 嘅 `Launcher-m5stack-sticks3.bin` 係 **app image**，唔係完整 factory image。  
新機最好用 **master backup + `INCLUDE_BOOT=1`**，或用 [Launcher Web Flasher](https://bmorcelli.github.io/Launcher/)。  
`./scripts/flash-launcher.sh` 只適用於已有 bootloader + partition table 嘅機。

### Q: 20 部要幾耐？

| 步驟 | 時間（約） |
|---|---|
| Master backup（一次） | 3–5 分鐘 |
| 每部 provision | 3–5 分鐘 |
| 每部小智綁定 | 2 分鐘 |
| **20 部總計** | **約 2–3 小時** |

---

## 手動 esptool 指令（參考）

如需手動操作，venv 內 esptool 用法如下：

```bash
# 讀 partition table
.venv/bin/python -m esptool --chip esp32s3 -p /dev/cu.usbmodem1101 -b 460800 \
  read-flash 0x8000 0x1000 backups/partition-table.bin

# 寫某個 partition（例：NVS）
.venv/bin/python -m esptool --chip esp32s3 -p /dev/cu.usbmodem1102 -b 460800 \
  write-flash --flash-size 8MB --flash-mode dio --flash-freq 80m \
  0x9000 backups/partitions/nvs__nvs__0x9000.bin

# 讀 MAC
.venv/bin/python -m esptool --chip esp32s3 -p /dev/cu.usbmodem1101 read-mac
```

---

## 專案結構

```
m5sticks3-clone/
├── README.md
├── requirements.txt
├── firmware/
│   ├── Launcher-m5stack-sticks3.bin
│   └── custom_8Mb2.csv
├── scripts/
│   ├── setup.sh
│   ├── backup-master.sh
│   ├── provision-device.sh
│   ├── fix-launcher-boot.sh
│   ├── flash-launcher.sh
│   └── partition_utils.py
├── backups/          # gitignored，backup 後產生
└── docs/
    └── device-log.csv
```

---

## 參考連結

- [M5Launcher GitHub](https://github.com/bmorcelli/Launcher)
- [M5Launcher Web Flasher](https://bmorcelli.github.io/Launcher/)
- [StickS3 小智官方教學](https://docs.m5stack.com/zh_CN/guide/realtime/xiaozhi/sticks3)
- [esptool 文件](https://docs.espressif.com/projects/esptool/en/latest/)

---

## 免責

- Clone 前請備份 master 機  
- 大量寫 flash 有風險；確保 USB 線穩定、唔中斷  
- 小智帳號綁定請遵守學校 / 平台使用政策  
