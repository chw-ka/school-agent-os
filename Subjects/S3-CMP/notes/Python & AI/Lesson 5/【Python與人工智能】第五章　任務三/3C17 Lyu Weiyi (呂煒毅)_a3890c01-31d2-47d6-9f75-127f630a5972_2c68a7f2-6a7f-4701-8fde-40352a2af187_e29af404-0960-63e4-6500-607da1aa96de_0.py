import tkinter as tk
from tkinter import messagebox, ttk
import math
import winsound
import time

class UltimateTicTacToe:
    def __init__(self, root):
        self.root = root
        self.root.title("高壓過三關：極限挑戰")
        
        # 遊戲設定
        self.human = "X"
        self.ai = "O"
        self.time_limit = 3.0  # 3秒壓力
        self.remaining_time = self.time_limit
        self.score = 0
        self.combo = 1
        self.last_move_time = 0
        
        self.state = [["" for _ in range(3)] for _ in range(3)]
        self.board = [[None for _ in range(3)] for _ in range(3)]
        self.game_running = True
        
        self.create_widgets()
        self.update_timer()

    def create_widgets(self):
        # 資訊面板
        self.info_frame = tk.Frame(self.root)
        self.info_frame.pack(pady=10)
        
        self.label_score = tk.Label(self.info_frame, text="分數: 0  |  Combo: x1", font=('Arial', 12))
        self.label_score.pack()
        
        # 倒數計時條
        self.progress = ttk.Progressbar(self.root, length=200, mode='determinate', maximum=3.0)
        self.progress.pack(pady=5)
        
        # 棋盤
        self.grid_frame = tk.Frame(self.root)
        self.grid_frame.pack(padx=20, pady=20)
        
        for r in range(3):
            for c in range(3):
                btn = tk.Button(self.grid_frame, text="", font=('Arial', 24, 'bold'), width=5, height=2,
                                bg="#f0f0f0", command=lambda row=r, col=c: self.player_move(row, col))
                btn.grid(row=r, column=c, padx=2, pady=2)
                self.board[r][c] = btn

    def play_sound(self, type):
        # 使用 Windows 內建頻率聲音 (頻率, 毫秒)
        try:
            if type == "move": winsound.Beep(600, 50)
            elif type == "ai": winsound.Beep(400, 50)
            elif type == "warn": winsound.Beep(1000, 100)
            elif type == "lose": winsound.Beep(200, 500)
            elif type == "win": winsound.Beep(800, 200); winsound.Beep(1200, 200)
        except: pass # 防止非 Windows 系統報錯

    def update_timer(self):
        if not self.game_running: return
        
        self.remaining_time -= 0.05
        self.progress['value'] = self.remaining_time
        
        if self.remaining_time <= 0:
            self.play_sound("lose")
            self.end_game("時間到！你太慢了，AI 獲勝！")
        elif self.remaining_time <= 1.0:
            if int(self.remaining_time * 10) % 2 == 0: self.play_sound("warn")
            self.root.after(50, self.update_timer)
        else:
            self.root.after(50, self.update_timer)

    def player_move(self, r, c):
        if not self.game_running or self.state[r][c] != "": return
        
        # 計算 Combo 與分數
        now = time.time()
        if now - self.last_move_time < 1.5: # 1.5秒內連續下棋算 Combo
            self.combo += 1
        else:
            self.combo = 1
        
        self.score += 10 * self.combo
        self.last_move_time = now
        self.label_score.config(text=f"分數: {self.score}  |  Combo: x{self.combo}")
        
        self.play_sound("move")
        self.make_move(r, c, self.human)
        
        if self.check_end(r, c, self.human): return
        
        # 重置計時器給 AI (雖然 AI 算很快，但我們給它一點延遲感)
        self.remaining_time = self.time_limit
        self.root.after(200, self.ai_move)

    def ai_move(self):
        if not self.game_running: return
        move = self.get_best_move()
        if move:
            r, c = move
            self.play_sound("ai")
            self.make_move(r, c, self.ai)
            if not self.check_end(r, c, self.ai):
                # AI 下完，重置計時器輪到玩家
                self.remaining_time = self.time_limit

    def get_best_move(self):
        best_score = -math.inf
        move = None
        for r in range(3):
            for c in range(3):
                if self.state[r][c] == "":
                    self.state[r][c] = self.ai
                    score = self.minimax(self.state, 0, False)
                    self.state[r][c] = ""
                    if score > best_score:
                        best_score = score
                        move = (r, c)
        return move

    def minimax(self, board, depth, is_maximizing):
        res = self.check_winner_logic(board)
        if res == self.ai: return 10 - depth
        if res == self.human: return depth - 10
        if self.is_full(board): return 0

        if is_maximizing:
            best = -math.inf
            for r in range(3):
                for c in range(3):
                    if board[r][c] == "":
                        board[r][c] = self.ai
                        best = max(best, self.minimax(board, depth + 1, False))
                        board[r][c] = ""
            return best
        else:
            best = math.inf
            for r in range(3):
                for c in range(3):
                    if board[r][c] == "":
                        board[r][c] = self.human
                        best = min(best, self.minimax(board, depth + 1, True))
                        board[r][c] = ""
            return best

    def make_move(self, r, c, char):
        self.state[r][c] = char
        color = "#3498DB" if char == "X" else "#E74C3C"
        self.board[r][c].config(text=char, fg=color, state="disabled", disabledforeground=color)

    def check_end(self, r, c, p):
        win_char = self.check_winner_logic(self.state)
        if win_char:
            self.game_running = False
            if win_char == self.human:
                self.play_sound("win")
                self.end_game(f"奇蹟！你贏了！最終分數: {self.score}")
            else:
                self.play_sound("lose")
                self.end_game("AI 勝利！你終究只是人類。")
            return True
        if self.is_full(self.state):
            self.game_running = False
            self.end_game(f"平局！你的分數: {self.score}")
            return True
        return False

    def check_winner_logic(self, s):
        lines = s + [[s[i][j] for i in range(3)] for j in range(3)] + \
                [[s[i][i] for i in range(3)], [s[i][2-i] for i in range(3)]]
        for line in lines:
            if line[0] != "" and all(x == line[0] for x in line): return line[0]
        return None

    def is_full(self, s):
        return all(s[r][c] != "" for r in range(3) for c in range(3))

    def end_game(self, msg):
        self.game_running = False
        messagebox.showinfo("Game Over", msg)
        self.reset_game()

    def reset_game(self):
        self.state = [["" for _ in range(3)] for _ in range(3)]
        for r in range(3):
            for c in range(3):
                self.board[r][c].config(text="", state="normal")
        self.score = 0
        self.combo = 1
        self.remaining_time = self.time_limit
        self.game_running = True
        self.update_timer()

if __name__ == "__main__":
    root = tk.Tk()
    game = UltimateTicTacToe(root)
    root.mainloop()