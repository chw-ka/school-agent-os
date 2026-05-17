import tkinter as tk
from tkinter import messagebox
import random
import time

class UltimateTicTacToe:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("TIC-TAC-TOE: ULTIMATE EDITION")
        self.window.configure(bg="#2c3e50")
        
        self.scores = {"Player": 0, "AI": 0}
        self.current_player = "X"
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.buttons = [[None for _ in range(3)] for _ in range(3)]
        self.timer_value = 5
        self.timer_running = False
        
        self.setup_ui()
        self.reset_game()

    def setup_ui(self):
        # 分數與難度顯示區
        self.header = tk.Frame(self.window, bg="#34495e", pady=10)
        self.header.pack(fill="x")
        
        self.score_label = tk.Label(
            self.header, text="YOU: 0  |  AI: 0", 
            font=("Verdana", 14, "bold"), fg="#ecf0f1", bg="#34495e"
        )
        self.score_label.pack()

        self.timer_label = tk.Label(
            self.window, text="剩餘時間: 5s", 
            font=("Verdana", 12), fg="#e74c3c", bg="#2c3e50"
        )
        self.timer_label.pack(pady=5)

        # 棋盤區
        self.game_frame = tk.Frame(self.window, bg="#2c3e50")
        self.game_frame.pack(padx=20, pady=20)

        for r in range(3):
            for c in range(3):
                btn = tk.Button(
                    self.game_frame, text="", font=("Arial Black", 24),
                    width=4, height=2, bg="#ecf0f1", relief="flat",
                    command=lambda row=r, col=c: self.on_click(row, col)
                )
                btn.grid(row=r, column=c, padx=4, pady=4)
                self.buttons[r][c] = btn

    def update_timer(self):
        if not self.timer_running: return
        if self.timer_value > 0:
            self.timer_value -= 1
            self.timer_label.config(text=f"⏳ 限時快下: {self.timer_value}s")
            self.window.after(1000, self.update_timer)
        else:
            self.timer_label.config(text="⏰ 時間到！換 AI 下棋")
            self.window.after(1000, self.ai_move)

    def on_click(self, r, c):
        if self.board[r][c] == "" and self.current_player == "X":
            self.make_move(r, c, "X")
            self.timer_running = False # 停止計時
            if not self.check_winner_flow():
                self.current_player = "O"
                self.window.after(600, self.ai_move)

    def ai_move(self):
        # 使用 Minimax 進行決策
        best_score = -float('inf')
        move = None
        for r in range(3):
            for c in range(3):
                if self.board[r][c] == "":
                    self.board[r][c] = "O"
                    score = self.minimax(self.board, 0, False)
                    self.board[r][c] = ""
                    if score > best_score:
                        best_score = score
                        move = (r, c)
        
        if move:
            self.make_move(move[0], move[1], "O")
            if not self.check_winner_flow():
                self.current_player = "X"
                self.start_player_turn()

    def start_player_turn(self):
        self.timer_value = 5
        self.timer_running = True
        self.timer_label.config(text="⏳ 限時快下: 5s")
        self.update_timer()

    def make_move(self, r, c, player):
        self.board[r][c] = player
        color = "#e67e22" if player == "X" else "#3498db"
        self.buttons[r][c].config(text=player, fg=color, bg="white")

    def minimax(self, board, depth, is_max):
        winner = self.get_winner_logic()
        if winner == "O": return 1
        if winner == "X": return -1
        if all(cell != "" for row in board for cell in row): return 0

        if is_max:
            best = -float('inf')
            for r in range(3):
                for c in range(3):
                    if board[r][c] == "":
                        board[r][c] = "O"
                        best = max(best, self.minimax(board, depth+1, False))
                        board[r][c] = ""
            return best
        else:
            best = float('inf')
            for r in range(3):
                for c in range(3):
                    if board[r][c] == "":
                        board[r][c] = "X"
                        best = min(best, self.minimax(board, depth+1, True))
                        board[r][c] = ""
            return best

    def get_winner_logic(self):
        for i in range(3):
            if self.board[i][0] == self.board[i][1] == self.board[i][2] != "": return self.board[i][0]
            if self.board[0][i] == self.board[1][i] == self.board[2][i] != "": return self.board[0][i]
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != "": return self.board[0][0]
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != "": return self.board[0][2]
        return None

    def check_winner_flow(self):
        winner = self.get_winner_logic()
        if winner:
            self.timer_running = False
            msg = "太強了！你贏了！" if winner == "X" else "AI 統治了世界！"
            if winner == "X": self.scores["Player"] += 1
            else: self.scores["AI"] += 1
            self.score_label.config(text=f"YOU: {self.scores['Player']}  |  AI: {self.scores['AI']}")
            messagebox.showinfo("Game Over", msg)
            self.reset_game()
            return True
        if all(self.board[r][c] != "" for r in range(3) for c in range(3)):
            messagebox.showinfo("Game Over", "勢均力敵，再來一局！")
            self.reset_game()
            return True
        return False

    def reset_game(self):
        self.board = [["" for _ in range(3)] for _ in range(3)]
        for r in range(3):
            for c in range(3):
                self.buttons[r][c].config(text="", bg="#ecf0f1")
        self.current_player = "X"
        self.start_player_turn()

if __name__ == "__main__":
    app = UltimateTicTacToe()
    app.window.mainloop()