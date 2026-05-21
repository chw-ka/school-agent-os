import tkinter as tk
from tkinter import messagebox
import math
import time
import random

# 注意：winsound 僅限 Windows。若在 Mac/Linux 請改用系統嗶聲
try:
    import winsound
    def play_sound(freq, duration):
        winsound.Beep(freq, duration)
except ImportError:
    def play_sound(freq, duration):
        print('\a') # 系統預設提示音

class TicTacToePro:
    def __init__(self, root):
        self.root = root
        self.root.title("過三關 Pro: 極限挑戰")
        
        # 遊戲設定
        self.ai = "O"
        self.human = "X"
        self.time_limit = 5.0  # 5 秒思考時間
        self.remaining_time = self.time_limit
        self.score = 0
        self.combo = 0
        self.last_win_time = 0
        self.game_over = False
        
        # 棋盤初始化
        self.board = [[None for _ in range(3)] for _ in range(3)]
        self.buttons = [[None for _ in range(3)] for _ in range(3)]
        
        self.create_widgets()
        self.update_timer()

    def create_widgets(self):
        # 資訊面板
        self.info_frame = tk.Frame(self.root)
        self.info_frame.pack(pady=10)
        
        self.label_score = tk.Label(self.info_frame, text=f"分數: {self.score} (Combo: {self.combo})", font=('Arial', 12))
        self.label_score.pack()
        
        self.label_timer = tk.Label(self.info_frame, text=f"剩餘時間: {self.remaining_time:.1f}s", font=('Arial', 14, 'bold'), fg="red")
        self.label_timer.pack()

        # 棋盤
        self.grid_frame = tk.Frame(self.root)
        self.grid_frame.pack()
        
        for r in range(3):
            for c in range(3):
                btn = tk.Button(self.grid_frame, text="", font=('Arial', 20, 'bold'), width=6, height=3,
                                command=lambda row=r, col=c: self.player_move(row, col))
                btn.grid(row=r, column=c, padx=2, pady=2)
                self.buttons[r][c] = btn

    def update_timer(self):
        if not self.game_over:
            self.remaining_time -= 0.1
            if self.remaining_time <= 0:
                self.remaining_time = 0
                self.label_timer.config(text="時間到！自動棄權")
                play_sound(200, 500) # 低音代表失敗
                messagebox.showinfo("超時", "你考慮太久了，AI 直接獲勝！")
                self.reset_game(loss=True)
            else:
                self.label_timer.config(text=f"剩餘時間: {self.remaining_time:.1f}s")
                self.root.after(100, self.update_timer)

    def player_move(self, r, c):
        if self.board[r][c] is None and not self.game_over:
            play_sound(600, 100) # 玩家落子音
            self.make_move(r, c, self.human)
            if not self.game_over:
                # 玩家下完，重置時間給 AI (雖然 AI 算很快)
                self.remaining_time = self.time_limit 
                self.root.after(200, self.computer_move)

    def computer_move(self):
        if self.game_over: return
        move = self.get_best_move()
        if move:
            play_sound(400, 100) # AI 落子音
            self.make_move(move[0], move[1], self.ai)
            self.remaining_time = self.time_limit # 重置時間給玩家

    def make_move(self, r, c, player):
        self.board[r][c] = player
        self.buttons[r][c].config(text=player, fg="blue" if player == "X" else "red")
        
        winner = self.get_winner()
        if winner:
            self.handle_end(winner)
        elif self.is_draw():
            self.handle_end("draw")

    def handle_end(self, result):
        self.game_over = True
        if result == self.human:
            play_sound(1000, 500) # 勝利高音
            # 連擊邏輯：20秒內連續獲勝分數加倍
            current_time = time.time()
            if current_time - self.last_win_time < 20:
                self.combo += 1
            else:
                self.combo = 1
            
            reward = 100 * self.combo
            self.score += reward
            self.last_win_time = current_time
            msg = f"你贏了！獲得 {reward} 分！"
        elif result == self.ai:
            play_sound(300, 500)
            self.combo = 0
            msg = "AI 贏了！不可戰勝的傳說持續中。"
        else:
            play_sound(500, 200)
            msg = "平手！"
            
        messagebox.showinfo("遊戲結束", msg)
        self.reset_game()

    # --- Minimax 核心邏輯 (不可戰勝) ---
    def get_best_move(self):
        best_score = -math.inf
        move = None
        for r in range(3):
            for c in range(3):
                if self.board[r][c] is None:
                    self.board[r][c] = self.ai
                    score = self.minimax(0, False)
                    self.board[r][c] = None
                    if score > best_score:
                        best_score = score
                        move = (r, c)
        return move

    def minimax(self, depth, is_maxing):
        winner = self.get_winner()
        if winner == self.ai: return 10 - depth
        if winner == self.human: return depth - 10
        if self.is_draw(): return 0

        if is_maxing:
            best = -math.inf
            for r in range(3):
                for c in range(3):
                    if self.board[r][c] is None:
                        self.board[r][c] = self.ai
                        best = max(best, self.minimax(depth + 1, False))
                        self.board[r][c] = None
            return best
        else:
            best = math.inf
            for r in range(3):
                for c in range(3):
                    if self.board[r][c] is None:
                        self.board[r][c] = self.human
                        best = min(best, self.minimax(depth + 1, True))
                        self.board[r][c] = None
            return best

    # --- 輔助工具 ---
    def get_winner(self):
        b = self.board
        for i in range(3):
            if b[i][0] == b[i][1] == b[i][2] and b[i][0]: return b[i][0]
            if b[0][i] == b[1][i] == b[2][i] and b[0][i]: return b[0][i]
        if b[0][0] == b[1][1] == b[2][2] and b[0][0]: return b[0][0]
        if b[0][2] == b[1][1] == b[2][0] and b[0][2]: return b[0][2]
        return None

    def is_draw(self):
        return all(all(row) for row in self.board)

    def reset_game(self, loss=False):
        self.board = [[None for _ in range(3)] for _ in range(3)]
        for r in range(3):
            for c in range(3):
                self.buttons[r][c].config(text="")
        
        self.game_over = False
        self.remaining_time = self.time_limit
        self.label_score.config(text=f"分數: {self.score} (Combo: {self.combo})")
        self.update_timer()

if __name__ == "__main__":
    root = tk.Tk()
    game = TicTacToePro(root)
    root.mainloop()