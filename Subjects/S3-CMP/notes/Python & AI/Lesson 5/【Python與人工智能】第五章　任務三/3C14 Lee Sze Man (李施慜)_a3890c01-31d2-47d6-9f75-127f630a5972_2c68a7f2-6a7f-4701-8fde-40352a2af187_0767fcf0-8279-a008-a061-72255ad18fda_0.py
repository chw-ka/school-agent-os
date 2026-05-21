import tkinter as tk
from tkinter import messagebox
import random
import time

class NeonBlitzTicTacToe:
    def __init__(self, root):
        self.root = root
        self.root.title("Neon Blitz: 3x99 Ultimate")
        self.root.geometry("450x650")
        self.root.configure(bg="#0D0D0D") # 極深色背景
        
        self.current_player = "X"
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.buttons = [[None for _ in range(3)] for _ in range(3)]
        self.score = 0
        self.time_left = 3
        self.timer_running = False
        
        self.setup_ui()
        self.start_timer()

    def setup_ui(self):
        # 頂部狀態欄
        self.header = tk.Label(self.root, text="NEON BLITZ", font=("Orbitron", 30, "bold"), 
                               bg="#0D0D0D", fg="#00FFCC")
        self.header.pack(pady=20)

        self.info_frame = tk.Frame(self.root, bg="#0D0D0D")
        self.info_frame.pack(fill="x", padx=50)

        self.score_label = tk.Label(self.info_frame, text=f"連勝: {self.score}", font=("Arial", 14), 
                                    bg="#0D0D0D", fg="white")
        self.score_label.pack(side="left")

        self.timer_label = tk.Label(self.info_frame, text="⏳ 3.0s", font=("Arial", 14, "bold"), 
                                    bg="#0D0D0D", fg="#FF0055")
        self.timer_label.pack(side="right")

        # 棋盤
        self.grid_frame = tk.Frame(self.root, bg="#1A1A1A", padx=10, pady=10)
        self.grid_frame.pack(pady=20)

        for r in range(3):
            for c in range(3):
                btn = tk.Button(self.grid_frame, text="", font=("Verdana", 32, "bold"),
                                width=4, height=1, bg="#121212", fg="#00FFCC",
                                activebackground="#222222", relief="flat",
                                command=lambda row=r, col=c: self.make_move(row, col))
                btn.grid(row=r, column=c, padx=5, pady=5)
                self.buttons[r][c] = btn

        # 底部提示
        self.hint = tk.Label(self.root, text="快！輪到你落子了！", font=("Arial", 10, "italic"),
                             bg="#0D0D0D", fg="#555555")
        self.hint.pack(side="bottom", pady=20)

    def start_timer(self):
        self.time_left = 3.0
        self.timer_running = True
        self.update_timer()

    def update_timer(self):
        if self.timer_running:
            if self.time_left > 0:
                self.time_left -= 0.1
                self.timer_label.config(text=f"⏳ {max(0, self.time_left):.1f}s")
                self.root.after(100, self.update_timer)
            else:
                self.time_out()

    def time_out(self):
        messagebox.showwarning("超時！", "你思考太久了！換電腦出手！")
        self.current_player = "O"
        self.computer_move()

    def make_move(self, r, c):
        if self.board[r][c] == "" and self.current_player == "X":
            self.timer_running = False
            self.execute_move(r, c, "X")
            if not self.check_game_over():
                self.current_player = "O"
                self.root.after(400, self.computer_move)

    def execute_move(self, r, c, player):
        self.board[r][c] = player
        color = "#00FFCC" if player == "X" else "#FF0055"
        self.buttons[r][c].config(text=player, fg=color)
        # 簡單的螢幕震動效果
        self.shake_screen()

    def shake_screen(self):
        orig_pos = self.root.winfo_x()
        for _ in range(4):
            self.root.geometry(f"+{orig_pos+5}+{self.root.winfo_y()}")
            self.root.update()
            time.sleep(0.02)
            self.root.geometry(f"+{orig_pos-5}+{self.root.winfo_y()}")
            self.root.update()
            time.sleep(0.02)
        self.root.geometry(f"+{orig_pos}+{self.root.winfo_y()}")

    def computer_move(self):
        # 使用隨機與邏輯混合，增加電腦反應速度感
        empty = [(r, c) for r in range(3) for c in range(3) if self.board[r][c] == ""]
        if empty:
            r, c = random.choice(empty)
            self.execute_move(r, c, "O")
            if not self.check_game_over():
                self.current_player = "X"
                self.start_timer()

    def check_game_over(self):
        winner = self.get_winner()
        if winner or all(cell != "" for row in self.board for cell in row):
            self.timer_running = False
            if winner == "X":
                self.score += 1
                title = "勝利！"
                msg = f"太強了！連勝次數：{self.score}"
            elif winner == "O":
                self.score = 0
                title = "失敗"
                msg = "電競選手也會失手，再試一次？"
            else:
                title = "平局"
                msg = "不相上下，再來一局！"
            
            messagebox.showinfo(title, msg)
            self.reset_game()
            return True
        return False

    def get_winner(self):
        for i in range(3):
            if self.board[i][0] == self.board[i][1] == self.board[i][2] != "": return self.board[i][0]
            if self.board[0][i] == self.board[1][i] == self.board[2][i] != "": return self.board[0][i]
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != "": return self.board[0][0]
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != "": return self.board[0][2]
        return None

    def reset_game(self):
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.current_player = "X"
        for r in range(3):
            for c in range(3):
                self.buttons[r][c].config(text="", fg="#00FFCC")
        self.score_label.config(text=f"連勝: {self.score}")
        self.start_timer()

if __name__ == "__main__":
    root = tk.Tk()
    app = NeonBlitzTicTacToe(root)
    root.mainloop()