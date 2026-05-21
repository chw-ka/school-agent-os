import tkinter as tk
from tkinter import messagebox
import random

class SpeedTicTacToe:
    def __init__(self, root):
        self.root = root
        self.root.title("5秒快棋：人機大戰 Pro")
        self.root.configure(bg="#1a1a1a")
        
        # 遊戲數據
        self.board = [[None for _ in range(3)] for _ in range(3)]
        self.buttons = [[None for _ in range(3)] for _ in range(3)]
        self.current_player = "X" # 玩家
        self.score = 0
        self.combo = 0
        self.time_limit = 5 # 縮短至 5 秒
        self.time_left = self.time_limit
        self.timer_job = None
        
        self.setup_ui()
        self.start_timer()

    def setup_ui(self):
        # 頂部資訊欄
        header = tk.Frame(self.root, bg="#1a1a1a", pady=10)
        header.pack(fill="x")
        
        self.score_label = tk.Label(header, text=f"Score: {self.score}", font=("Courier", 16, "bold"), fg="#00ff00", bg="#1a1a1a")
        self.score_label.pack(side="left", padx=20)
        
        self.timer_label = tk.Label(header, text=f"TIME: {self.time_left}s", font=("Courier", 18, "bold"), fg="#ff3e3e", bg="#1a1a1a")
        self.timer_label.pack(side="right", padx=20)

        # 難度與 Combo 顯示
        sub_header = tk.Frame(self.root, bg="#1a1a1a")
        sub_header.pack()
        
        self.diff_var = tk.StringVar(value="Hard")
        for text, mode in [("簡單", "Easy"), ("困難", "Hard")]:
            tk.Radiobutton(sub_header, text=text, variable=self.diff_var, value=mode, 
                           bg="#1a1a1a", fg="white", selectcolor="#333", command=self.reset_game).pack(side="left")

        self.combo_label = tk.Label(self.root, text=f"COMBO X{self.combo}", font=("Arial", 12, "italic"), fg="#f1c40f", bg="#1a1a1a")
        self.combo_label.pack()

        # 棋盤
        grid_frame = tk.Frame(self.root, bg="#444", padx=5, pady=5)
        grid_frame.pack(pady=10)
        
        for r in range(3):
            for c in range(3):
                btn = tk.Button(grid_frame, text="", font=('Helvetica', 30, 'bold'), 
                                width=4, height=1, bg="#333", fg="white", relief="flat",
                                command=lambda row=r, col=c: self.player_move(row, col))
                btn.grid(row=r, column=c, padx=2, pady=2)
                self.buttons[r][c] = btn

    # --- 計時邏輯 ---
    def start_timer(self):
        if self.timer_job: self.root.after_cancel(self.timer_job)
        self.time_left = self.time_limit
        self.run_timer()

    def run_timer(self):
        self.timer_label.config(text=f"TIME: {self.time_left}s")
        if self.time_left > 0:
            self.time_left -= 1
            self.timer_job = self.root.after(1000, self.run_timer)
        else:
            self.handle_timeout()

    def handle_timeout(self):
        messagebox.showwarning("Oops!", "時間到！這局算輸，Combo 中斷。")
        self.combo = 0
        self.reset_game()

    # --- 遊戲邏輯 ---
    def player_move(self, r, c):
        if self.board[r][c] is None and self.current_player == "X":
            self.make_move(r, c, "X")
            if not self.check_end():
                self.current_player = "O"
                self.root.after(300, self.ai_turn) # 電腦快速回應

    def ai_turn(self):
        move = self.get_minimax_move() if self.diff_var.get() == "Hard" else self.get_random_move()
        if move:
            self.make_move(move[0], move[1], "O")
            if not self.check_end():
                self.current_player = "X"
                self.start_timer() # 輪到玩家，重新開始 5 秒倒數

    def make_move(self, r, c, p):
        self.board[r][c] = p
        color = "#ff4757" if p == "X" else "#2ed573"
        self.buttons[r][c].config(text=p, fg=color)

    # --- Minimax 演算法核心 ---
    def get_minimax_move(self):
        best_score = float('-inf')
        move = None
        for r in range(3):
            for c in range(3):
                if self.board[r][c] is None:
                    self.board[r][c] = "O"
                    score = self.minimax(self.board, 0, False)
                    self.board[r][c] = None
                    if score > best_score:
                        best_score = score
                        move = (r, c)
        return move

    def minimax(self, board, depth, is_max):
        winner = self.get_winner_logic()
        if winner == "O": return 10 - depth
        if winner == "X": return depth - 10
        if all(all(cell for cell in row) for row in board): return 0

        if is_max:
            best = float('-inf')
            for r in range(3):
                for c in range(3):
                    if board[r][c] is None:
                        board[r][c] = "O"; score = self.minimax(board, depth+1, False); board[r][c] = None
                        best = max(score, best)
            return best
        else:
            best = float('inf')
            for r in range(3):
                for c in range(3):
                    if board[r][c] is None:
                        board[r][c] = "X"; score = self.minimax(board, depth+1, True); board[r][c] = None
                        best = min(score, best)
            return best

    def get_random_move(self):
        empties = [(r, c) for r in range(3) for c in range(3) if self.board[r][c] is None]
        return random.choice(empties) if empties else None

    def get_winner_logic(self):
        b = self.board
        lines = b + [[b[r][c] for r in range(3)] for c in range(3)] + \
                [[b[i][i] for i in range(3)], [b[i][2-i] for i in range(3)]]
        for line in lines:
            if line[0] and line[0] == line[1] == line[2]: return line[0]
        return None

    def check_end(self):
        winner = self.get_winner_logic()
        if winner:
            if self.timer_job: self.root.after_cancel(self.timer_job)
            if winner == "X":
                bonus = 100 * (2 ** self.combo)
                self.score += bonus
                self.combo += 1
                msg = f"你贏了！獲得 {bonus} 分！"
            else:
                self.combo = 0
                msg = "AI 獲勝！Combo 中斷。"
            messagebox.showinfo("結束", msg)
            self.reset_game()
            return True
        if all(all(c for c in row) for row in self.board):
            self.combo = 0
            messagebox.showinfo("平手", "平手！Combo 中斷。")
            self.reset_game()
            return True
        return False

    def reset_game(self):
        if self.timer_job: self.root.after_cancel(self.timer_job)
        self.board = [[None for _ in range(3)] for _ in range(3)]
        for r in range(3):
            for c in range(3):
                self.buttons[r][c].config(text="", bg="#333")
        self.score_label.config(text=f"Score: {self.score}")
        self.combo_label.config(text=f"COMBO X{self.combo}")
        self.current_player = "X"
        self.start_timer()

if __name__ == "__main__":
    root = tk.Tk()
    SpeedTicTacToe(root)
    root.mainloop()