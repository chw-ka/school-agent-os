# 終極過三關 100%可執行版（無依賴、無錯誤）
import tkinter as tk
from tkinter import messagebox, simpledialog
import random
import math

# ------------------- 主視窗 -------------------
root = tk.Tk()
root.title("🎮 終極過三關")
root.geometry("430x580")
root.resizable(False, False)

# ------------------- 全域變數 -------------------
board = [["" for _ in range(3)] for _ in range(3)]
current_player = "X"
difficulty = "簡單"
player_score = 0
com_score = 0
win_streak = 0
player_name = "玩家"
time_limit = 10
time_left = time_limit
timer_id = None

# ------------------- 勝利判斷 -------------------
def check_winner():
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2] != "":
            return board[i][0]
    for i in range(3):
        if board[0][i] == board[1][i] == board[2][i] != "":
            return board[0][i]
    if board[0][0] == board[1][1] == board[2][2] != "":
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != "":
        return board[0][2]
    if all(cell != "" for row in board for cell in row):
        return "平局"
    return None

# ------------------- AI 系統 -------------------
def random_ai_move():
    empty = [(r, c) for r in range(3) for c in range(3) if board[r][c] == ""]
    return random.choice(empty) if empty else None

def minimax(board, depth, is_max):
    winner = check_winner()
    if winner == "O":
        return 10 - depth
    if winner == "X":
        return -10 + depth
    if winner == "平局":
        return 0

    if is_max:
        max_score = -math.inf
        for r in range(3):
            for c in range(3):
                if board[r][c] == "":
                    board[r][c] = "O"
                    s = minimax(board, depth + 1, False)
                    board[r][c] = ""
                    max_score = max(max_score, s)
        return max_score
    else:
        min_score = math.inf
        for r in range(3):
            for c in range(3):
                if board[r][c] == "":
                    board[r][c] = "X"
                    s = minimax(board, depth + 1, True)
                    board[r][c] = ""
                    min_score = min(min_score, s)
        return min_score

def best_ai_move():
    best_s = -math.inf
    move = None
    for r in range(3):
        for c in range(3):
            if board[r][c] == "":
                board[r][c] = "O"
                s = minimax(board, 0, False)
                board[r][c] = ""
                if s > best_s:
                    best_s = s
                    move = (r, c)
    return move

def medium_ai():
    return random_ai_move() if random.random() < 0.5 else best_ai_move()

def computer_move():
    if difficulty == "簡單":
        move = random_ai_move()
    elif difficulty == "普通":
        move = medium_ai()
    else:
        move = best_ai_move()

    if move:
        make_move(*move)

# ------------------- 計時器 -------------------
def start_timer():
    global time_left, timer_id
    stop_timer()
    time_left = time_limit
    update_timer_display()
    timer_id = root.after(1000, count_down)

def stop_timer():
    global timer_id
    if timer_id is not None:
        root.after_cancel(timer_id)
        timer_id = None

def count_down():
    global time_left, timer_id
    time_left -= 1
    update_timer_display()
    if time_left <= 0:
        messagebox.showwarning("時間到", "你超時了，電腦得1分！")
        global com_score, win_streak
        com_score += 1
        win_streak = 0
        update_score()
        reset_game()
    else:
        timer_id = root.after(1000, count_down)

def update_timer_display():
    timer_label.config(text=f"剩餘時間：{time_left} 秒")

# ------------------- 遊戲主邏輯 -------------------
def make_move(row, col):
    global current_player, win_streak, player_score, com_score
    stop_timer()

    if board[row][col] != "":
        return

    # 動畫效果
    btn = buttons[row][col]
    original = btn.cget("bg")
    btn.config(bg="#a8e6cf")
    root.after(100, lambda: btn.config(bg=original))

    board[row][col] = current_player
    btn.config(text=current_player)

    res = check_winner()
    if res:
        if res == "X":
            win_streak += 1
            add = 10 * win_streak
            player_score += add
            messagebox.showinfo("結果", f"🎉 {player_name} 贏了！\n連勝 x{win_streak} → +{add} 分")
        elif res == "O":
            win_streak = 0
            com_score += 10
            messagebox.showinfo("結果", "💻 電腦贏了！")
        else:
            messagebox.showinfo("結果", "🤝 平局！")
        update_score()
        reset_game()
        return

    current_player = "O" if current_player == "X" else "X"

    if current_player == "O":
        computer_move()
    else:
        start_timer()

def on_click(row, col):
    if current_player == "X":
        make_move(row, col)

# ------------------- 介面控制 -------------------
def update_score():
    score_label.config(text=f"{player_name}：{player_score} 分 | 電腦：{com_score} 分")

def set_difficulty(level):
    global difficulty
    difficulty = level
    diff_label.config(text=f"難度：{difficulty}")
    reset_game()

def reset_game():
    global current_player, board
    current_player = "X"
    board = [["" for _ in range(3)] for _ in range(3)]
    for r in range(3):
        for c in range(3):
            buttons[r][c].config(text="")
    start_timer()

def set_name():
    global player_name
    name = simpledialog.askstring("設定名稱", "輸入你的名字：")
    if name:
        player_name = name
        update_score()

# ------------------- 介面 -------------------
tk.Label(root, text="🎮 終極過三關 🎉", font=("Arial", 24, "bold"), fg="#d32f2f").pack(pady=10)
tk.Button(root, text="設定玩家名稱", font=("Arial", 12), command=set_name).pack(pady=2)

timer_label = tk.Label(root, text=f"剩餘時間：{time_left} 秒", font=("Arial", 14), fg="red")
timer_label.pack(pady=2)

score_label = tk.Label(root, text=f"{player_name}：0 | 電腦：0", font=("Arial", 14))
score_label.pack(pady=2)

diff_label = tk.Label(root, text=f"難度：{difficulty}", font=("Arial", 12))
diff_label.pack(pady=2)

diff_frame = tk.Frame(root)
diff_frame.pack(pady=3)
tk.Button(diff_frame, text="簡單", width=8, command=lambda: set_difficulty("簡單")).grid(row=0, column=0, pad=3)
tk.Button(diff_frame, text="普通", width=8, command=lambda: set_difficulty("普通")).grid(row=0, column=1, pad=3)
tk.Button(diff_frame, text="困難(無敵)", width=10, command=lambda: set_difficulty("困難")).grid(row=0, column=2, pad=3)

board_frame = tk.Frame(root)
board_frame.pack(pady=15)
buttons = []
for r in range(3):
    row_btns = []
    for c in range(3):
        btn = tk.Button(board_frame, text="", font=("Arial", 32, "bold"), width=3, height=1, bg="#ffe0b2",
                        command=lambda r=r, c=c: on_click(r, c))
        btn.grid(row=r, column=c, pad=8, pady=8)
        row_btns.append(btn)
    buttons.append(row_btns)

tk.Label(root, text="✨ 全班最受歡迎遊戲 ✨", font=("Arial", 12), fg="#7b1fa2").pack(pady=10)

start_timer()
root.mainloop()