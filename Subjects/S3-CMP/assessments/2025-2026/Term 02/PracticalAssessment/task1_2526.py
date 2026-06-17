"""
S3 CMP 第二學期 實習評估（2025-2026）
任務一：《智能播音員》（禁止使用任何 AI 工具）

請完成下面的填空程式，令程式能做到：
- 不斷要求使用者輸入要播音的文字
- 若使用者輸入 "Q"，程式結束
- 使用者可選擇語言："en" 或 "zh"（預設："en"）
- 每次播音：產生 mp3 → 播放 → 刪除 mp3 檔案
"""

# (a) 匯入函數庫
from
from
import


print("=== 智能播音員 ===")
print('輸入 "Q" 退出。')

# (b) 只詢問一次語言
lang = input("語言 (en/zh)：").strip().lower()
if lang not in ("en", "zh"):
    lang = "en"

while True:
    # (c) 輸入要播音的文字
    msg = input("訊息：").strip()
    if msg == "Q":
        break

    # (d) 文字轉語音：儲存 mp3、播放、刪檔
    audio =
    audio.
    playsound("output.mp3")
    os.

