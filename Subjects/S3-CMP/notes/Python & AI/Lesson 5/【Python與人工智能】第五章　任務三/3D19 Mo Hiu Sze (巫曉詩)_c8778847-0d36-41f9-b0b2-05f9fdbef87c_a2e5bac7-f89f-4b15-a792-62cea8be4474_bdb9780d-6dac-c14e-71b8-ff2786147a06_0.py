import tkinter as tk
from tkinter import messagebox
import random

class UltimateTicTacToe:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("終極挑戰：閃電過三關 ⚡")
        self.window.configure(bg="#2C3E50")
        
        # 遊戲數據
        self.board = [None] * 9
        self.current_player = "X"
        self.scores = {"Player": 0, "AI": 0}
        self.timer_value = 5
        self.timer_job = None
        
        self.setup_ui()
        self.start_timer()

    def setup_ui(self):
        # 分數看板
        self.score_label = tk.Label(
            self.window, text=f"玩家: {self.scores['Player']} | AI: {self.scores['AI']}",
            font=("Microsoft JhengHei", 14, "bold"), bg="#2C3E50", fg="white"
        )
        self.score_label.pack(pady=10)

        # 倒數計時顯示
        self.timer_label = tk.Label(
            self.window, text=f"剩餘時間: {self.timer_value}s",
            font=("Microsoft JhengHei", 18, "bold"), bg="#2C3E50", fg="#E74C3C"
        )
        self.timer_label.pack(pady=5)

        # 棋盤容器 (修正：移除無效的 p_adj 參數)
        frame = tk.Frame(self.window, bg="#34495E")
        frame.pack(padx=20, pady=20)

        self.buttons = []
        for i in range(9):
            btn = tk.Button(
                frame, text="", font=("Arial", 30, "bold"), width=4, height=2,
                bg="#ECF0F1", fg="#2C3E50", relief="flat",
                command=lambda idx=i: self.player_click(idx)
            )
            btn.grid(row=i//3, column=i%3, padx=5, pady=5)
            self.buttons.append(btn)

        # 重置與說明按鈕
        btn_frame = tk.Frame(self.window, bg="#2C3E50")
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="重新開始", command=self.reset_game).pack(side=tk.LEFT, padx=5)

    def start_timer(self):
        if self.timer_job:
            self.window.after_cancel(self.timer_job)
        self.timer_value = 5
        self.update_timer()

    def update_timer(self):
        self.timer_label.config(text=f"剩餘時間: {self.timer_value}s")
        if self.timer_value > 0:
            self.timer_value -= 1
            self.timer_job = self.window.after(1000, self.update_timer)
        else:
            messagebox.showwarning("超時！", "考慮太久了，AI 直接獲勝！")
            self.end_game("AI")

    def player_click(self, idx):
        if self.board[idx] is None and self.current_player == "X":
            if self.timer_job:
                self.window.after_cancel(self.timer_job) # 玩家點擊後暫停計時
            self.make_move(idx, "X")
            if not self.check_winner():
                self.current_player = "O"
                self.window.after(300, self.ai_move)

    def ai_move(self):
        move = self.get_best_move()
        if move is not None:
            self.make_move(move, "O")
            if not self.check_winner():
                self.current_player = "X"
                self.start_timer() # AI 下完輪到玩家，重啟計時

    def make_move(self, idx, player):
        self.board[idx] = player
        color = "#FF7675" if player == "X" else "#74B9FF"
        self.buttons[idx].config(text=player, fg="white", bg=color)
        
    def check_winner(self):
        win_coords = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
        for a, b, c in win_coords:
            if self.board[a] == self.board[b] == self.board[c] and self.board[a] is not None:
                for idx in [a, b, c]: self.buttons[idx].config(bg="#F1C40F")
                self.end_game("Player" if self.board[a] == "X" else "AI")
                return True
        if None not in self.board:
            self.end_game("Draw")
            return True
        return False

    def end_game(self, result):
        if self.timer_job:
            self.window.after_cancel(self.timer_job)
        
        if result == "Player":
            self.scores["Player"] += 1
            messagebox.showinfo("Win!", "你竟然贏了無敵 AI！")
        elif result == "AI":
            self.scores["AI"] += 1
            messagebox.showinfo("Lose", "AI 守住了它的王座。")
        else:
            messagebox.showinfo("Draw", "平手！不分伯仲。")
        self.reset_game()

    def reset_game(self):
        if self.timer_job:
            self.window.after_cancel(self.timer_job)
        self.board = [None] * 9
        for btn in self.buttons:
            btn.config(text="", bg="#ECF0F1")
        self.current_player = "X"
        self.score_label.config(text=f"玩家: {self.scores['Player']} | AI: {self.scores['AI']}")
        self.start_timer()

    # --- Minimax AI ---
    def get_best_move(self):
        best_score = -float('inf')
        move = None
        for i in range(9):
            if self.board[i] is None:
                self.board[i] = "O"
                score = self.minimax(self.board, 0, False)
                self.board[i] = None
                if score > best_score:
                    best_score = score
                    move = i
        return move

    def minimax(self, board, depth, is_maxing):
        res = self.quick_check(board)
        if res == "O": return 10 - depth
        if res == "X": return depth - 10
        if None not in board: return 0

        if is_maxing:
            best = -float('inf')
            for i in range(9):
                if board[i] is None:
                    board[i] = "O"
                    best = max(best, self.minimax(board, depth + 1, False))
                    board[i] = None
            return best
        else:
            best = float('inf')
            for i in range(9):
                if board[i] is None:
                    board[i] = "X"
                    best = min(best, self.minimax(board, depth + 1, True))
                    board[i] = None
            return best

    def quick_check(self, b):
        win_coords = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
        for a, b_idx, c in win_coords:
            if b[a] == b[b_idx] == b[c] and b[a] is not None:
                return b[a]
        return None

if __name__ == "__main__":
    game = UltimateTicTacToe()
    game.window.mainloop()