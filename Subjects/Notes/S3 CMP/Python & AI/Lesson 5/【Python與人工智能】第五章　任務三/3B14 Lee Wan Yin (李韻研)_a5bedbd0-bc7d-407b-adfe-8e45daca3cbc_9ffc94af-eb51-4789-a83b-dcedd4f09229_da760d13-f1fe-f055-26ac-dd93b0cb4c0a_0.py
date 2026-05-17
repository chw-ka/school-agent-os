# Task3_3X99.py - 超受歡迎強化版過三關 (連擊+計時+音效+特效+AI)
import tkinter as tk
from tkinter import messagebox
import random
import copy
import winsound

# ========== 主視窗 ==========
root = tk.Tk()
root.title("✨ 超夯過三關 ✨")
root.geometry("450x600")
root.resizable(False, False)
root.configure(bg="#1e1e2f")

# ========== 遊戲全域變數 ==========
board = [["" for _ in range(3)] for _ in range(3)]
buttons = []
current_player = "X"
difficulty = "普通"

score_player = 0
score_com = 0
score_draw = 0
streak = 0

time_left = 10
timer_running = False

# ========== 判斷勝利 ==========
def check_winner(b):
    for i in range(3):
        if b[i][0] == b[i][1] == b[i][2] != "":
            return b[i][0]
    for i in range(3):
        if b[0][i] == b[1][i] == b[2][i] != "":
            return b[0][i]
    if b[0][0] == b[1][1] == b[2][2] != "":
        return b[0][0]
    if b[0][2] == b[1][1] == b[2][0] != "":
        return b[0][2]
    if all(c != "" for r in b for c in r):
        return "draw"
    return None

# ========== 電腦隨機移動 ==========
def com_random():
    empty = [(i,j) for i in range(3) for j in range(3) if board[i][j] == ""]
    return random.choice(empty) if empty else None

# ========== Minimax 無敵 AI ==========
def minimax(b, max_turn):
    res = check_winner(b)
    if res == "O": return 1
    if res == "X": return -1
    if res == "draw": return 0
    if max_turn:
        best = -999
        for i in range(3):
            for j in range(3):
                if b[i][j] == "":
                    b[i][j] = "O"
                    s = minimax(b, False)
                    b[i][j] = ""
                    best = max(best, s)
        return best
    else:
        best = 999
        for i in range(3):
            for j in range(3):
                if b[i][j] == "":
                    b[i][j] = "X"
                    s = minimax(b, True)
                    b[i][j] = ""
                    best = min(best, s)
        return best

def com_best():
    best_s = -999
    move = None
    for i in range(3):
        for j in range(3):
            if board[i][j] == "":
                board[i][j] = "O"
                s = minimax(board, False)
                board[i][j] = ""
                if s > best_s:
                    best_s = s
                    move = (i,j)
    return move

# ========== 計時器 ==========
def start_timer():
    global time_left, timer_running
    stop_timer()
    time_left = 10
    timer_running = True
    update_timer()

def stop_timer():
    global timer_running
    timer_running = False

def update_timer():
    global time_left, timer_running
    if not timer_running:
        return
    if time_left > 0:
        time_label.config(text=f"剩餘時間：{time_left} 秒")
        time_left -= 1
        root.after(1000, update_timer)
    else:
        messagebox.showwarning("時間到","你太慢囉！換電腦下")
        computer_turn()

# ========== 電腦回合 ==========
def computer_turn():
    stop_timer()
    res = check_winner(board)
    if res:
        game_over(res)
        return
    if difficulty == "簡單":
        r,c = com_random()
    elif difficulty == "普通":
        r,c = com_random() if random.random()<0.4 else com_best()
    else:
        r,c = com_best()
    board[r][c] = "O"
    buttons[r][c].config(text="O", fg="#4fc3f7")
    winsound.Beep(200, 100)
    res = check_winner(board)
    if res:
        game_over(res)
        return
    start_timer()

# ========== 遊戲結束 ==========
def game_over(result):
    global streak, score_player, score_com, score_draw
    stop_timer()
    if result == "X":
        streak +=1
        score_player +=1
        msg = f"🎉 你贏了！連勝 {streak} 場"
        winsound.Beep(800,200)
        winsound.Beep(1000,200)
        flash_win()
    elif result == "O":
        streak = 0
        score_com +=1
        msg = "💻 電腦獲勝"
        winsound.Beeep(300,300)
    else:
        streak = 0
        score_draw +=1
        msg = "🤝 平手"
    update_score()
    messagebox.showinfo("遊戲結束", msg)
    reset_board()

# ========== 勝利閃光特效 ==========
def flash_win(count=0):
    if count>6:
        for i in range(3):
            for j in range(3):
                buttons[i][j].config(bg="#f8f9fa")
        return
    color = "#ffeb3b" if count%2==0 else "#f8f9fa"
    for i in range(3):
        for j in range(3):
            buttons[i][j].config(bg=color)
    root.after(100, lambda: flash_win(count+1))

# ========== 玩家點擊 ==========
def click(r,c):
    global current_player
    if board[r][c] != "" or check_winner(board):
        return
    board[r][c] = "X"
    buttons[r][c].config(text="X", fg="#ff5252")
    winsound.Beep(440, 80)
    res = check_winner(board)
    if res:
        game_over(res)
        return
    root.after(300, computer_turn)

# ========== 重置棋盤 ==========
def reset_board():
    global board, current_player
    board = [["" for _ in range(3)] for _ in range(3)]
    for i in range(3):
        for j in range(3):
            buttons[i][j].config(text="", bg="#f8f9fa")
    current_player = "X"
    start_timer()

# ========== 難度 & 分數 ==========
def set_diff(d):
    global difficulty
    difficulty = d
    diff_label.config(text=f"難度：{difficulty}")
    reset_board()

def update_score():
    p = f"玩家：{score_player}"
    c = f"電腦：{score_com}"
    d = f"平手：{score_draw}"
    score_label.config(text=f"{p} | {c} | {d}")

# ========== 介面 ==========
# 標題
title = tk.Label(root, text="✨ 超夯過三關 ✨",
                 font=("Arial",24,"bold"), bg="#1e1e2f", fg="white")
title.pack(pady=10)

# 難度
diff_label = tk.Label(root, text=f"難度：{difficulty}",
                      font=("Arial",12), bg="#1e1e2f", fg="white")
diff_label.pack()

# 難度按鈕
f_diff = tk.Frame(root, bg="#1e1e2f")
f_diff.pack(pady=5)
tk.Button(f_diff,text="簡單", command=lambda:set_diff("簡單"),
          bg="#66bb6a",fg="white",width=8).grid(row=0,column=0,padx=4)
tk.Button(f_diff,text="普通", command=lambda:set_diff("普通"),
          bg="#ffc107",fg="black",width=8).grid(row=0,column=1,padx=4)
tk.Button(f_diff,text="無敵", command=lambda:set_diff("無敵"),
          bg="#e53935",fg="white",width=8).grid(row=0,column=2,padx=4)

# 計時
time_label = tk.Label(root, text="剩餘時間：10 秒",
                      font=("Arial",12), bg="#1e1e2f", fg="#ffeb3b")
time_label.pack(pady=5)

# 分數
score_label = tk.Label(root, text="玩家：0 | 電腦：0 | 平手：0",
                      font=("Arial",11), bg="#1e1e2f", fg="white")
score_label.pack(pady=5)

# 棋盤
frame = tk.Frame(root, bg="#1e1e2f")
frame.pack(pady=15)
for i in range(3):
    row = []
    for j in range(3):
        btn = tk.Button(frame, text="", font=("Arial",32,"bold"),
                        width=3, height=1, bg="#f8f9fa",
                        command=lambda r=i,c=j: click(r,c))
        btn.grid(row=i, column=j, padx=6, pady=6)
        row.append(btn)
    buttons.append(row)

# ========== 開始 ==========
start_timer()
root.mainloop()