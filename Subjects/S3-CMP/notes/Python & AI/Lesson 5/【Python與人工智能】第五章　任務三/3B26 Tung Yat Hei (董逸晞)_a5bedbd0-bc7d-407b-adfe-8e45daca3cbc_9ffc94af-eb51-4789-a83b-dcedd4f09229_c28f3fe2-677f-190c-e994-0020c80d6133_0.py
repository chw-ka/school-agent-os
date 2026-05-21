import tkinter as tk
from tkinter import messagebox, ttk
import random
import math

class TicTacToeTurbo:
    def __init__(self, root):
        self.root = root
        self.root.title("過三關：疾速對決 Turbo")
        self.root.geometry("450x650")
        self.root.configure(bg="#1a1a2e") # 深藍色背景
        
        # 遊戲數據
        self.board = [[None for _ in range(3)] for _ in range(3)]
        self.buttons = [[None for _ in range(3)] for _ in range(3)]
        self.difficulty = tk.StringVar(value="Hard")
        self.score = 0
        self.combo = 0
        self.time_left = 5
        self.game_over = False
        self.timer_job = None

        self.create_widgets()
        self.reset_timer()

    def create_widgets(self):
        # 頂部積分與狀態
        self.info_frame = tk.Frame(self.root, bg="#16213e", pady=10)
        self.info_frame.pack(fill="x")
        
        self.score_label = tk.Label(self.info_frame, text=f"積分: {self.score}  連勝: {self.combo}", 
                                    fg="#e94560", bg="#16213e", font=("Microsoft JhengHei", 14, "bold"))
        self.score_label.pack()

        # 進度條 (時間壓力)
        self.style = ttk.Style()
        self.style.theme_use('default')
        self.style.configure("TProgressbar", thickness=10, troughcolor='#1a1a2e', background='#e94560')
        self.progress = ttk.Progressbar(self.root, style="TProgressbar", orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=10)

        # 棋盤
        board_container = tk.Frame(self.root, bg="#1a1a2e")
        board_container.pack(pady=20)

        for r in range(3):
            for c in range(3):
                btn = tk.Button(
                    board_container, text="", font=("Verdana", 40, "bold"),
                    width=4, height=1, bg="#0f3460", fg="white",
                    relief="flat", activebackground="#533483",
                    command=lambda r=r, c=c: self.player_click(r, c)
                )
                btn.grid(row=r, column=c, padx=8, pady=8)
                self.buttons[r][c] = btn

        # 難度切換區
        ctrl_frame = tk.Frame(self.root, bg="#1a1a2e")
        ctrl_frame.pack(pady=10)
        for text, mode in [("簡單", "Easy"), ("普通", "Medium"), ("地獄", "Hard")]:
            tk.Radiobutton(ctrl_frame, text=text, variable=self.difficulty, value=mode,
                           bg="#1a1a2e", fg="white", selectcolor="#e94560",
                           font=("Microsoft JhengHei", 10)).pack(side="left", padx=10)

    def reset_timer(self):
        if self.timer_job:
            self.root.after_cancel(self.timer_job)
        self.time_left = 5
        self.update_timer()

    def update_timer(self):
        if self.game_over: return
        
        self.progress['value'] = (self.time_left / 5) * 100
        if self.time_left <= 0:
            self.flash_screen("#e94560") # 震動警告
            messagebox.showwarning("超時", "思考太久了！這回合換電腦下。")
            self.computer_move()
        else:
            self.time_left -= 0.1
            self.timer_job = self.root.after(100, self.update_timer)

    def player_click(self, r, c):
        if self.board[r][c] is None and not self.game_over:
            self.make_move(r, c, "X")
            if not self.game_over:
                self.reset_timer() # 換電腦下時暫停計時
                self.root.after(300, self.computer_move)

    def make_move(self, r, c, player):
        color = "#e94560" if player == "X" else "#00d2ff"
        self.board[r][c] = player
        self.buttons[r][c].config(text=player, fg=color, bg="#16213e")
        
        winner = self.get_winner_raw()
        if winner:
            self.end_game(winner)
        elif self.is_board_full():
            self.end_game("Draw")

    def end_game(self, result):
        self.game_over = True
        if self.timer_job: self.root.after_cancel(self.timer_job)
        
        if result == "X":
            points = {"Easy": 100, "Medium": 300, "Hard": 1000}[self.difficulty.get()]
            self.combo += 1
            self.score += points * self.combo
            msg = f"太強了！獲得 {points * self.combo} 分！"
            self.flash_screen("#00ff00") # 勝利閃爍
        elif result == "O":
            self.combo = 0
            msg = "被擊敗了！挑戰失敗。"
            self.flash_screen("#ff0000") # 失敗閃爍
        else:
            msg = "平局！再接再厲。"
            
        self.score_label.config(text=f"積分: {self.score}  連勝: {self.combo}")
        messagebox.showinfo("戰果", msg)
        self.root.after(500, self.reset_game)

    def flash_screen(self, color):
        orig_bg = self.root.cget("bg")
        self.root.config(bg=color)
        self.root.after(100, lambda: self.root.config(bg=orig_bg))

    # --- (以下保留原本的 Minimax 邏輯及隨機邏輯) ---
    def get_winner_raw(self):
        b = self.board
        lines = b + [[b[i][j] for i in range(3)] for j in range(3)] + \
                [[b[i][i] for i in range(3)], [b[i][2-i] for i in range(3)]]
        for line in lines:
            if line[0] and all(x == line[0] for x in line): return line[0]
        return None

    def is_board_full(self):
        return all(self.board[r][c] is not None for r in range(3) for c in range(3))

    def computer_move(self):
        if self.game_over: return
        mode = self.difficulty.get()
        if mode == "Easy":
            move = self.get_random_move()
        elif mode == "Medium":
            move = self.get_best_move() if random.random() < 0.5 else self.get_random_move()
        else:
            move = self.get_best_move()
        
        if move:
            self.make_move(move[0], move[1], "O")
            if not self.game_over: self.reset_timer()

    def get_random_move(self):
        cells = [(r, c) for r in range(3) for c in range(3) if self.board[r][c] is None]
        return random.choice(cells) if cells else None

    def get_best_move(self):
        best_score = -math.inf
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
        win = self.get_winner_raw()
        if win == "O": return 10 - depth
        if win == "X": return depth - 10
        if self.is_board_full(): return 0
        
        scores = []
        for r in range(3):
            for c in range(3):
                if board[r][c] is None:
                    board[r][c] = "O" if is_max else "X"
                    scores.append(self.minimax(board, depth + 1, not is_max))
                    board[r][c] = None
        return max(scores) if is_max else min(scores)

    def reset_game(self):
        self.game_over = False
        self.board = [[None for _ in range(3)] for _ in range(3)]
        for r in range(3):
            for c in range(3):
                self.buttons[r][c].config(text="", bg="#0f3460")
        self.reset_timer()

if __name__ == "__main__":
    root = tk.Tk()
    game = TicTacToeTurbo(root)
    root.mainloop()