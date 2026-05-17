import tkinter as tk
from tkinter import messagebox
import random

class ArcadeTicTacToe:
    def __init__(self, root):
        self.root = root
        self.root.title("極限過三關：時速挑戰")
        self.root.configure(bg="#121212") # 深色電競風背景
        
        self.current_player = "X"
        self.board_state = [["" for _ in range(3)] for _ in range(3)]
        self.buttons = [[None for _ in range(3)] for _ in range(3)]
        self.game_over = False
        self.timer_val = 5  # 5秒限時
        self.timer_job = None
        
        self.create_widgets()
        self.start_timer()

    def create_widgets(self):
        # 狀態與計時器顯示
        self.header_frame = tk.Frame(self.root, bg="#121212")
        self.header_frame.pack(pady=10)
        
        self.status_label = tk.Label(
            self.header_frame, text="你的回合!", 
            font=('Microsoft JhengHei', 14, 'bold'), bg="#121212", fg="#00E5FF"
        )
        self.status_label.pack()

        self.timer_label = tk.Label(
            self.header_frame, text=f"剩餘時間: {self.timer_val}s", 
            font=('Consolas', 18, 'bold'), bg="#121212", fg="#FF0055"
        )
        self.timer_label.pack()

        # 棋盤容器
        self.board_frame = tk.Frame(self.root, bg="#121212")
        self.board_frame.pack(padx=20, pady=10)

        for r in range(3):
            for c in range(3):
                btn = tk.Button(
                    self.board_frame, text="", font=('Arial', 30, 'bold'),
                    width=4, height=1, bg="#1E1E1E", fg="white",
                    activebackground="#333333", relief="flat",
                    command=lambda r=r, c=c: self.player_move(r, c)
                )
                btn.grid(row=r, column=c, padx=4, pady=4)
                self.buttons[r][c] = btn

    def start_timer(self):
        if self.timer_job:
            self.root.after_cancel(self.timer_job)
        
        if not self.game_over and self.current_player == "X":
            if self.timer_val > 0:
                self.timer_label.config(text=f"剩餘時間: {self.timer_val}s")
                self.timer_val -= 1
                self.timer_job = self.root.after(1000, self.start_timer)
            else:
                self.timer_label.config(text="時間到！")
                self.auto_random_move() # 時間到強制幫你下

    def auto_random_move(self):
        empty_cells = [(r, c) for r in range(3) for c in range(3) if self.board_state[r][c] == ""]
        if empty_cells:
            r, c = random.choice(empty_cells)
            self.player_move(r, c)

    def player_move(self, r, c):
        if self.board_state[r][c] == "" and not self.game_over and self.current_player == "X":
            if self.timer_job: self.root.after_cancel(self.timer_job)
            self.make_move(r, c, "X")
            
            if not self.game_over:
                self.current_player = "O"
                self.status_label.config(text="電腦進攻中...")
                self.root.after(600, self.computer_move)

    def computer_move(self):
        if self.game_over: return
        empty_cells = [(r, c) for r in range(3) for c in range(3) if self.board_state[r][c] == ""]
        if empty_cells:
            r, c = random.choice(empty_cells