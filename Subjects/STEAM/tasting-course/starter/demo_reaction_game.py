"""
考反應遊戲——老師示範版
M5StickS3 · UIFlow 2.0 MicroPython

載入方式：
  切換至 Python 模式（右上角切換按鈕）→ 貼上 → 執行

遊戲流程：
  開始 → 等待（隨機 1.5–3.5 秒）→ GO！→ 結果
    ↑                                        ↓
    └──────────── BtnA / BtnB ───────────────┘
  等待期間按 BtnA → 顯示「太早了！」

畫面為橫向 240×135。BtnA = 側面，BtnB = 正面，BtnPWR = 頂部。
"""
import M5
from M5 import *
import time
import random

# ── 顏色 ──────────────────────────────────────────────────────────
C_BG_START    = 0x003366
C_BG_WAIT     = 0x1A1A1A
C_BG_GO       = 0x003300
C_BG_EARLY    = 0x330000
C_WHITE       = 0xFFFFFF
C_GREEN       = 0x00FF44
C_RED         = 0xFF2200
C_GOLD        = 0xFFD700
C_GREY        = 0x888888
C_DIM         = 0x444444

# ── LED 控制（SK6812，GPIO 19）─────────────────────────────────────
try:
    import neopixel, machine
    _np = neopixel.NeoPixel(machine.Pin(19), 1)
    def set_led(r, g, b):
        _np[0] = (r, g, b)
        _np.write()
except Exception:
    def set_led(r, g, b):
        pass  # LED 不可用時，遊戲照常運行

# ── 狀態機 ────────────────────────────────────────────────────────
STATE_START     = 0
STATE_WAITING   = 1
STATE_GO        = 2
STATE_RESULT    = 3
STATE_TOO_EARLY = 4

state      = STATE_START
go_time    = 0   # GO！出現時的 ticks_ms()
wait_until = 0   # 等待結束時的 ticks_ms()

# ── 畫面輔助函式 ───────────────────────────────────────────────────
def cls(bg):
    Widgets.fillScreen(bg)

def lbl(text, x, y, scale, fg, bg, font=Widgets.FONTS.DejaVu18):
    Widgets.Label(text, x, y, scale, fg, bg, font)

# ── 各畫面 ────────────────────────────────────────────────────────
def screen_start():
    global state
    state = STATE_START
    set_led(0, 0, 40)
    cls(C_BG_START)
    lbl("考反應！",   8,  20, 1.0, C_WHITE,  C_BG_START, Widgets.FONTS.DejaVu24)
    lbl("按 A 開始",  8,  72, 1.0, C_GOLD,   C_BG_START)
    lbl("按 B 離開",  8, 108, 1.0, C_GREY,   C_BG_START, Widgets.FONTS.DejaVu12)


def screen_waiting():
    global state, wait_until
    state = STATE_WAITING
    wait_until = time.ticks_ms() + random.randint(1500, 3500)
    set_led(30, 0, 0)
    cls(C_BG_WAIT)
    lbl("準備好…",    8,  45, 1.0, C_WHITE,  C_BG_WAIT)
    lbl("唔好撳！",   8,  85, 1.0, C_DIM,    C_BG_WAIT, Widgets.FONTS.DejaVu12)


def screen_go():
    global state, go_time
    state = STATE_GO
    go_time = time.ticks_ms()
    set_led(0, 80, 0)
    cls(C_BG_GO)
    lbl("NOW!",       5,  10, 1.0, C_GREEN,  C_BG_GO, Widgets.FONTS.DejaVu40)
    lbl("撳 A！",     8,  90, 1.0, C_WHITE,  C_BG_GO)


def screen_result(ms):
    global state
    state = STATE_RESULT

    if ms < 220:
        rating, rating_col, bg = "反應超快！🔥", C_GOLD,   0x1A1400
    elif ms < 350:
        rating, rating_col, bg = "好快！👍",     C_GREEN,  0x001400
    elif ms < 500:
        rating, rating_col, bg = "唔錯！",       0x44AAFF, 0x000E1A
    else:
        rating, rating_col, bg = "繼續練習 💪",  C_GREY,   0x111111

    set_led(0, 0, 60)
    cls(bg)
    lbl(str(ms) + " ms",   5,  10, 1.0, C_WHITE,    bg, Widgets.FONTS.DejaVu40)
    lbl(rating,             5,  72, 1.0, rating_col, bg)
    lbl("A再試  B退出",     5, 108, 1.0, C_GREY,     bg, Widgets.FONTS.DejaVu12)


def screen_too_early():
    global state
    state = STATE_TOO_EARLY
    set_led(80, 0, 0)
    cls(C_BG_EARLY)
    lbl("太早了！",   5,  30, 1.0, C_RED,   C_BG_EARLY, Widgets.FONTS.DejaVu24)
    lbl("😬",         5,  72, 1.0, C_WHITE, C_BG_EARLY)
    lbl("按 A 再試",  5, 108, 1.0, C_GREY,  C_BG_EARLY, Widgets.FONTS.DejaVu12)


# ── 主迴圈 ────────────────────────────────────────────────────────
M5.begin()
screen_start()

while True:
    M5.update()

    if state == STATE_START:
        if BtnA.wasPressed():
            screen_waiting()

    elif state == STATE_WAITING:
        if BtnA.wasPressed():
            screen_too_early()
        elif time.ticks_diff(time.ticks_ms(), wait_until) >= 0:
            screen_go()

    elif state == STATE_GO:
        if BtnA.wasPressed():
            ms = time.ticks_diff(time.ticks_ms(), go_time)
            screen_result(ms)

    elif state == STATE_RESULT:
        if BtnA.wasPressed():
            screen_waiting()
        elif BtnB.wasPressed():
            screen_start()

    elif state == STATE_TOO_EARLY:
        if BtnA.wasPressed():
            screen_waiting()

    time.sleep_ms(10)
