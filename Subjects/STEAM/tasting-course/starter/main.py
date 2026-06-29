"""
UIFlow 2.0 入門範本——小五 STEAM 嘗鮮課（下一節用）
DeepSeek API 直接從 M5StickS3 呼叫

載入方式：
  File → Import → 選擇此 .py 檔案
  或切換至 Python 模式直接貼上。

老師：分發前請替換 DEEPSEEK_API_KEY。
學生：只需修改 QUESTION_A 和 QUESTION_B。
"""
import M5
from M5 import *
import urequests
import json

# ── 老師填寫（請勿直接分享此金鑰）──
DEEPSEEK_API_KEY = "sk-REPLACE_WITH_YOUR_KEY"

# ── 學生修改這兩條問題 ──
QUESTION_A = "告訴我一個關於太空的有趣科學知識。"
QUESTION_B = "用一句話說一個笑話。"

# ── 介面設定 ──
label_status = None
label_answer = None

def setup():
    global label_status, label_answer
    M5.begin()
    Widgets.fillScreen(0x222222)
    label_status = Widgets.Label("準備好了！", 5, 10, 1.0, 0xFFFFFF, 0x222222, Widgets.FONTS.DejaVu18)
    label_answer = Widgets.Label("按 BtnA 或 BtnB", 5, 40, 0.8, 0xCCCCCC, 0x222222, Widgets.FONTS.DejaVu12)


def ask_deepseek(question):
    """向 DeepSeek API 發送問題，返回回答字串。"""
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + DEEPSEEK_API_KEY,
    }
    payload = json.dumps({
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": question}],
        "max_tokens": 80,
        "temperature": 0.7,
    })

    label_status.setText("思考中…")
    RGB.setColor(0xFFAA00)  # 琥珀色 LED = 等待中

    try:
        resp = urequests.post(url, headers=headers, data=payload)
        data = resp.json()
        resp.close()
        answer = data["choices"][0]["message"]["content"]
        RGB.setColor(0x00FF00)  # 綠色 LED = 完成
        return answer
    except Exception as e:
        RGB.setColor(0xFF0000)  # 紅色 LED = 出錯
        return "錯誤：" + str(e)


@M5.event.on_btnA_wasPressed
def btnA_pressed():
    answer = ask_deepseek(QUESTION_A)
    label_status.setText("BtnA：")
    label_answer.setText(answer)


@M5.event.on_btnB_wasPressed
def btnB_pressed():
    answer = ask_deepseek(QUESTION_B)
    label_status.setText("BtnB：")
    label_answer.setText(answer)


setup()
M5.run()
