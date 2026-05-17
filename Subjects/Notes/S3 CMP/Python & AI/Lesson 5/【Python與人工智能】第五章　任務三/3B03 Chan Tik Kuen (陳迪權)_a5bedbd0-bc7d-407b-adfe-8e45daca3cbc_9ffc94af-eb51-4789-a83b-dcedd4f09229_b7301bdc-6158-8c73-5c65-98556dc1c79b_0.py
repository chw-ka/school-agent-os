# Task3_3X99.py - 超受歡迎強化版過三關（連擊+計時+音效+分數+動畫）
import tkinter as tk
from tkinter import messagebox, ttk
import random
import math
import time
import winsound

# ====================== 主視窗與全域設定 ======================
root = tk.Tk()
root.title("✨ 超級過三關 ✨")
root.geometry("450x600")
root.resizable(False, False)

current_player = "X"
board = [["", "", ""], ["", "", ""], ["", "", ""]]
buttons = []
difficulty = "hard"
game_start_time = 0
player_score = 0
combo = 0
combo_timer = None

# ====================== 音效功能 ======================
def play_click():
    try:
        winsound.Beep(800, 80)
    except:
        pass

def play_win():
    try:
        winsound.Beep(1200, 200)
        winsound.Beep(1500, 200)
    except:
        pass

def play_lose():
    try:
        winsound.Beep(400, 200)
        winsound.Beep(300, 200)
    except:
        pass

# ====================== 勝利判斷 ======================
def check_winner():
    for row in range(3):
        if board[row][0] == board[row][1] == board[row][2] != "":
            return board[row][0]
    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] != "":
            return board[0][col]
    if board[0][0] == board[1][1] == board[2][2] != "":
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != "":
        return board[0][2]
    if all(cell != "" for row in board for cell in row):
        return "Tie"
    return None

# ====================== Minimax 無敵電腦 ======================
def minimax(board, depth, is_max):
    w = check_winner()
    if w == "O": return 1
    if w == "X": return -1
    if w == "Tie": return 0
    if is_max:
        best = -math.inf
        for r in range(3):
            for c in range(3):
                if board[r][c] == "":
                    board[r][c] = "O"
                    s = minimax(board, depth+1, False)
                    board[r][c] = ""
                    best = max(best, s)
        return best
    else:
        best = math.inf
        for r in range(3):
            for c in range(3):
                if board[r][c] == "":
                    board[r][c] = "X"
                    s = minimax(board, depth+1, True)
                    board[r][c] = ""
                    best = min(best, s)
        return best

def best_move():
    best_s = -math.inf
    move = (0,0)
    for r in range(3):
        for c in range(3):
            if board[r][c] == "":
                board[r][c] = "O"
                s = minimax(board,0,False)
                board[r][c] = ""
                if s>best_s:
                    best_s = s
                    move = (r,c)
    return move

# ====================== 連擊系統 ======================
def reset_combo():
    global combo
    combo = 0
    combo_label.config(text="連擊: 0x")

def add_combo():
    global combo
    combo +=1
    combo_label.config(text=f"連擊: {combo}x")
    if combo_timer:
        root.after_cancel(combo_timer)
    combo_timer = root.after(5000, reset_combo)

# ====================== 計時更新 ======================
def update_timer():
    if game_start_time == 0:
        return
    elapsed = int(time.time() - game_start_time)
    timer_label.config(text=f"時間: {elapsed} 秒")
    root.after(1000, update_timer)

# ====================== 遊戲結束 ======================
def game_over(result):
    global player_score
    t = int(time.time() - game_start_time)
    base = max(1000 - t*10, 200)
    add = combo * 50
    total = base + add

    if result == "X":
        player_score += total
        play_win()
        messagebox.showinfo("勝利", f"🎉 你贏了！\n分數: {total}\n連擊: {combo}")
    elif result == "O":
        play_lose()
        messagebox.showinfo("失敗", "💻 電腦獲勝")
    else:
        messagebox.showinfo("平局", "🤝 平手")

    score_label.config(text=f"總分: {player_score}")
    reset_board()

# ====================== 電腦下棋 ======================
def computer_go():
    r,c = best_move()
    board[r][c] = "O"
    buttons[r][c].config(text="O", fg="red")
    res = check_winner()
    if res:
        game_over(res)
        return
    global current_player
    current_player = "X"

# ====================== 玩家點擊 ======================
def click(r,c):
    global current_player
    if board[r][c] != "" or current_player != "X":
        return
    play_click()
    board[r][c] = "X"
    buttons[r][c].config(text="X", fg="blue")
    res = check_winner()
    if res:
        game_over(res)
        return
    add_combo()
    current_player = "O"
    root.after(500, computer_go)

# ====================== 重置遊戲 ======================
def reset_board():
    global board, current_player, game_start_time
    board = [["","",""],["","",""],["","",""]]
    current_player = "X"
    game_start_time = time.time()
    for r in range(3):
        for c in range(3):
            buttons[r][c].config(text="", bg="#f8f8f8")
    update_timer()

# ====================== 建立介面 ======================
# 標題
title = tk.Label(root, text="✨ 超級過三關 ✨", font=("Arial",28,"bold"))
title.pack(pady=10)

# 資訊列
frame_info = tk.Frame(root)
frame_info.pack()

timer_label = tk.Label(frame_info, text="時間: 0", font=("Arial",14))
timer_label.grid(row=0,column=0,padx=10)

combo_label = tk.Label(frame_info, text="連擊: 0x", font=("Arial",14))
combo_label.grid(row=0,column=1,padx=10)

score_label = tk.Label(frame_info, text="總分: 0", font=("Arial",14))
score_label.grid(row=0,column=2,padx=10)

# 棋盤
frame_board = tk.Frame(root)
frame_board.pack(pady=15)

for r in range(3):
    row_btns = []
    for c in range(3):
        btn = tk.Button(frame_board, text="", font=("Arial",36,"bold"),
                        width=3, height=1, bg="#f8f8f8",
                        command=lambda r=r,c=c: click(r,c))
        btn.grid(row=r, column=c, padx=8, pady=8)
        row_btns.append(btn)
    buttons.append(row_btns)

# 重置按鈕
reset_btn = tk.Button(root, text="🔄 重新開始", font=("Arial",16,"bold"),
                      bg="#42a5f5", fg="white", command=reset_board)
reset_btn.pack(pady=10)

# 說明
tip = tk.Label(root, text="特色：連擊加倍｜計時挑戰｜音效反饋｜分數系統",
               font=("Arial",11))
tip.pack(pady=5)

# 開始遊戲
game_start_time = time.time()
update_timer()
root.mainloop()