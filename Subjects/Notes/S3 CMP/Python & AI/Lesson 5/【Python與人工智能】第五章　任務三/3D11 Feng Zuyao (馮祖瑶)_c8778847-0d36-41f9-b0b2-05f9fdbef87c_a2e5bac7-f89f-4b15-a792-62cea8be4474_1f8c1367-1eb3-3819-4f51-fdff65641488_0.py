Python

import tkinter as tk
from tkinter import messagebox
import random
import time

class UltimateTicTacToe:
    def __init__(self, root):
        self.root = root
        self.root.title("🔥 終極過三關：生死時速 🔥")
        self.root.geometry("400x550")
        self.root.configure(bg="#2c3e50")

        self.current_player = "X"
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.buttons = [[None for _ in range(3)] for _ in range(3)]
        self.score = 0
        self.timer_val = 3.0
        self.timer_running = False
        
        self.setup_ui()
        self.reset_game()

    def setup_ui(self):
        # 分數與計時器顯示
        self.info_label = tk.Label(
            self.root, text="準備好了嗎？", 
            font=('Verdana', 16, 'bold'), bg="#2c3e50", fg="#ecf0f1"
        )
        self.info_label.pack(pady=10)

        self.timer_label = tk.Label(
            self.root, text="剩餘時間: 3.0s", 
            font=('Courier', 20, 'bold'), bg="#2c3e50", fg="#e74c3c"
        )
        self.timer_label.pack(pady=5)

        # 棋盤容器
        board_frame = tk.Frame(self.root, bg="#34495e", pdy=10, pdx=10)
        board_frame.pack(pady=20)

        for r in range(3):
            for c in range(3):
                btn = tk.Button(
                    board_frame, text="", font=('Arial', 30, 'bold'),
                    width=4, height=2, bg="#ecf0f1", activebackground="#bdc3c7",
                    command=lambda r=r, c=c: self.player_move(r, c)
                )
                btn.grid(row=r, column=c, padx=5, pady=5)
                self.buttons[r][c] = btn

    def start_timer(self):
        self.timer_val = 3.0
        if not self.timer_running:
            self.timer_running = True
            self.update_timer()

    def update_timer(self):
        if self.timer_running:
            if self.timer_val <= 0:
                self.game_over("時間到！你猶豫了，AI 獲勝！")
            else:
                self.timer_label.config(text=f"剩餘時間: {self.timer_val:.1f}s")
                self.timer_val -= 0.1
                # 倒計時緊急顏色變化
                if self.timer_val < 1.0:
                    self.timer_label.config(fg="#ff0000")
                else:
                    self.timer_label.config(fg="#e74c3c")
                self.root.after(100, self.update_timer)

    def player_move(self, r, c):
        if self.board[r][c] == "" and self.current_player == "X":
            self.make_move(r, c, "X")
            # 視覺反饋
            self.buttons[r][c].config(bg="#3498db")
            
            if not self.check_logic():
                self.current_player = "O"
                self.timer_running = False # AI 思考時暫停計時
                self.root.after(400, self.ai_move)

    def ai_move(self):
        # 這裡使用 Task 2 的智慧型邏輯
        move = self.get_best_move()
        if move:
            self.make_move(move[0], move[1], "O")
            self.buttons[move[0]][move[1]].config(bg="#e67e22")
            
            if not self.check_logic():
                self.current_player = "X"
                self.start_timer() # 輪到玩家，開始奪命計時

    def make_move(self, r, c, player):
        self.board[r][c] = player
        self.buttons[r][c].config(text=player, fg="white")

    def check_logic(self):
        winner = self.check_winner(self.board)
        if winner:
            self.game_over("🎉 奇蹟！你贏了！" if winner == "X" else "💀 AI 碾壓了你！")
            return True
        if all(cell != "" for row in self.board for cell in row):
            self.game_over("🤝 勢均力敵，平局！")
            return True
        return False

    def get_best_move(self):
        # 快速實作：優先贏棋 > 阻擋 > 隨機
        for p in ["O", "X"]:
            for r in range(3):
                for c in range(3):
                    if self.board[r][c] == "":
                        self.board[r][c] = p
                        if self.check_winner(self.board) == p:
                            self.board[r][c] = ""
                            return (r, c)
                        self.board[r][c] = ""
        empty = [(r, c) for r in range(3) for c in range(3) if self.board[r][c] == ""]
        return random.choice(empty) if empty else None

    def check_winner(self, b):
        lines = [b[i] for i in range(3)] + [[b[r][i] for r in range(3)] for i in range(3)] + \
                [[b[i][i] for i in range(3)], [b[i][2-i] for i in range(3)]]
        for line in lines:
            if line[0] == line[1] == line[2] != "": return line[0]
        return None

    def game_over(self, msg):
        self.timer_running = False
        messagebox.showinfo("戰果", msg)
        self.reset_game()

    def reset_game(self):
        self.board = [["" for _ in range(3)] for _ in range(3)]
        for r in range(3):
            for c in range(3):
                self.buttons[r][c].config(text="", bg="#ecf0f1")
        self.current_player = "X"
        self.timer_label.config(text="準備...", fg="#e74c3c")
        self.info_label.config(text="下一手由 X 開始！")
        # 玩家點擊第一步後才會啟動計時

if __name__ == "__main__":
    root = tk.Tk()
    app = UltimateTicTacToe(root)
    root.mainloop()