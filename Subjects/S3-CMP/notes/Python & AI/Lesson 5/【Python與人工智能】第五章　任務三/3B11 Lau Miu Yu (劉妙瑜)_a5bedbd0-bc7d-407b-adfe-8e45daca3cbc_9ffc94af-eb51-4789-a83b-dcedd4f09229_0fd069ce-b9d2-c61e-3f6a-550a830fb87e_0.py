import tkinter as tk
from tkinter import messagebox, ttk
import random
import math
import time
import winsound

# ======================
# 遊戲特色（受歡迎秘訣）
# 1. 分數系統 + 連擊加倍
# 2. 倒數計時壓力
# 3. 三種難度：簡單/普通/無敵
# 4. 勝利閃光特效
# 5. 點擊音效 + 勝利音效
# 6. 美觀漸層配色
# 7. 快捷鍵 R 重置
# ======================

root = tk.Tk()
root.title("🎉 超受歡迎過三關 3×99 🎉")
root.resizable(False, False)
root.configure(bg="#2c3e50")

# 全域變數
board = [["" for _ in range(3)] for _ in range(3)]
buttons = []
current_player = "X"
computer = "O"
difficulty = "普通"

score_player = 0
score_computer = 0
streak = 0
game_time = 30
start_time = 0
timer_running = False

# 音效
def play_click():
    try:
        winsound.Beep(660, 80)
    except:
        pass

def play_win():
    try:
        winsound.Beep(880, 200)
        winsound.Beep(1047, 200)
    except:
        pass

def play_lose():
    try:
        winsound.Beep(330, 200)
        winsound.Beep(220, 200)
    except:
        pass

# 判斷勝利
def check_winner(b):
    for i in range(3):
        if b[i][0]==b[i][1]==b[i][2]!="":return b[i][0]
        if b[0][i]==b[1][i]==b[2][i]!="":return b[0][i]
    if b[0][0]==b[1][1]==b[2][2]!="":return b[0][0]
    if b[0][2]==b[1][1]==b[2][0]!="":return b[0][2]
    if all(c!="" for r in b for c in r):return "TIE"
    return None

# AI
def computer_move():
    if difficulty == "簡單":
        empty = [(r,c) for r in range(3) for c in range(3) if board[r][c]==""]
        if empty:
            r,c = random.choice(empty)
            place(r,c)
    elif difficulty == "普通":
        for r in range(3):
            for c in range(3):
                if board[r][c]=="":
                    board[r][c]=computer
                    if check_winner(board)==computer:
                        place(r,c)
                        return
                    board[r][c]=""
        for r in range(3):
            for c in range(3):
                if board[r][c]=="":
                    board[r][c]=current_player
                    if check_winner(board)==current_player:
                        board[r][c]=computer
                        place(r,c)
                        return
                    board[r][c]=""
        empty = [(r,c) for r in range(3) for c in range(3) if board[r][c]==""]
        if empty:place(*random.choice(empty))
    elif difficulty == "無敵":
        best = -math.inf
        move = None
        for r in range(3):
            for c in range(3):
                if board[r][c]=="":
                    board[r][c]=computer
                    s = minimax(board,0,False)
                    board[r][c]=""
                    if s>best:best=s;move=(r,c)
        if move:place(*move)

def minimax(b,d,maximizing):
    res = check_winner(b)
    if res==computer:return 1
    if res==current_player:return -1
    if res=="TIE":return 0
    if maximizing:
        v = -math.inf
        for r in range(3):
            for c in range(3):
                if b[r][c]=="":
                    b[r][c]=computer
                    v = max(v, minimax(b,d+1,False))
                    b[r][c]=""
        return v
    else:
        v = math.inf
        for r in range(3):
            for c in range(3):
                if b[r][c]=="":
                    b[r][c]=current_player
                    v = min(v, minimax(b,d+1,True))
                    b[r][c]=""
        return v

# 下棋
def place(r,c):
    global current_player, streak
    board[r][c] = current_player
    buttons[r][c].config(text=current_player)
    play_click()

    res = check_winner(board)
    if res:
        if res == current_player:
            streak +=1
            add = 100*streak
            nonlocal score_player
            score_player += add
            play_win()
            messagebox.showinfo("恭喜",f"你贏了！連擊×{streak} +{add}分")
        elif res == computer:
            streak =0
            play_lose()
            messagebox.showinfo("結束","電腦獲勝")
            score_computer +=50
        else:
            messagebox.showinfo("平手","時間到！")
        update_score()
        reset_board()
        return

    current_player = computer if current_player=="X" else "X"
    update_ui()
    if current_player == computer:
        root.after(500, computer_move)

def click(r,c):
    if not timer_running:
        start_timer()
    if board[r][c]!="" or current_player==computer:
        return
    place(r,c)

# 計時
def start_timer():
    global start_time, timer_running
    start_time = time.time()
    timer_running = True
    update_timer()

def update_timer():
    if not timer_running:return
    elapsed = int(time.time()-start_time)
    rem = max(0, game_time-elapsed)
    time_label.config(text=f"剩餘：{rem} 秒")
    if rem <=0:
        messagebox.showwarning("時間到","挑戰結束")
        reset_board()
        return
    root.after(1000, update_timer)

# UI 更新
def update_ui():
    turn_label.config(text=f"輪到：{current_player}")
    streak_label.config(text=f"連擊 ×{streak}")

def update_score():
    p_label.config(text=f"玩家：{score_player}")
    c_label.config(text=f"電腦：{score_computer}")

# 重置
def reset_board():
    global current_player, timer_running
    current_player = "X"
    timer_running = False
    for r in range(3):
        for c in range(3):
            board[r][c]=""
            buttons[r][c].config(text="",bg="#ecf0f1")
    time_label.config(text="點擊開始")
    update_ui()

def set_diff(d):
    global difficulty
    difficulty = d
    messagebox.showinfo("難度",f"已設定：{d}")
    reset_board()

# 勝利特效
def win_effect(btn):
    btn.config(bg="#f39c12")
    root.update()

# 介面
top = tk.Frame(root, bg="#34495e")
top.grid(row=0,column=0,columnspan=3,pady=8,padx=8,sticky="ew")

tk.Button(top,text="簡單",bg="#27ae60",fg="white",command=lambda:set_diff("簡單")).pack(side=LEFT,padx=4)
tk.Button(top,text="普通",bg="#f39c12",fg="white",command=lambda:set_diff("普通")).pack(side=LEFT,padx=4)
tk.Button(top,text="無敵",bg="#e74c3c",fg="white",command=lambda:set_diff("無敵")).pack(side=LEFT,padx=4)

turn_label = tk.Label(top,text="輪到：X",bg="#34495e",fg="white",font=("Arial",12))
turn_label.pack(side=RIGHT,padx=10)

info = tk.Frame(root,bg="#2c3e50")
info.grid(row=1,column=0,columnspan=3,pady=4)

p_label = tk.Label(info,text=f"玩家：{score_player}",fg="white",bg="#2c3e50")
p_label.grid(row=0,column=0,padx=10)
c_label = tk.Label(info,text=f"電腦：{score_computer}",fg="white",bg="#2c3e50")
c_label.grid(row=0,column=1,padx=10)
streak_label = tk.Label(info,text="連擊 ×0",fg="yellow",bg="#2c3e50",font=("Arial",10,"bold"))
streak_label.grid(row=0,column=2,padx=10)
time_label = tk.Label(info,text="點擊開始",fg="cyan",bg="#2c3e50")
time_label.grid(row=0,column=3,padx=10)

# 棋盤
for r in range(3):
    row_btns=[]
    for c in range(3):
        btn = tk.Button(root,text="",font=("Arial",32,"bold"),
                        bg="#ecf0f1",fg="#2c3e50",width=4,height=1,
                        command=lambda rr=r,cc=c:click(rr,cc))
        btn.grid(row=r+2,column=c,padx=4,pady=4)
        row_btns.append(btn)
    buttons.append(row_btns)

# 快捷鍵 R = 重置
root.bind("<r>",lambda e:reset_board())
root.bind("<R>",lambda e:reset_board())

update_score()
root.mainloop()