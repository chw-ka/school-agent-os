import tkinter as tk
from tkinter import messagebox, ttk
import random
import math

class UltimateTicTacToe:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("過三關：火柴人與地獄 AI")
        self.window.geometry("600x650") # 加寬以容納火柴人
        self.window.configure(bg='#2c3e50')

        # 遊戲數據
        self.board = [[None for _ in range(3)] for _ in range(3)]
        self.buttons = [[None for _ in range(3)] for _ in range(3)]
        self.current_player = "X"
        self.time_left = 10
        self.game_active = True
        
        self.difficulty_names = ["新手", "入門", "中等", "困難", "地獄"]
        self.quotes = {
            "start": ["加油！我看好你！", "別輸給電腦啊！", "準備好了嗎？"],
            "hurry": ["快點！沒時間了！", "你在猶豫什麼？", "滴答滴答..."],
            "win": ["太神啦！你贏了！", "人類的榮光！", "電腦也不過如此嘛。"],
            "lose": ["沒事，勝敗乃兵家常事。", "這電腦太作弊了吧？", "下次一定贏！"],
            "draw": ["不相上下，精彩！", "平局也是一種實力。", "僵持不下了呢。"]
        }

        self.setup_ui()
        self.update_timer()

    def setup_ui(self):
        # 頂部狀態欄 (時間)
        self.top_frame = tk.Frame(self.window, bg='#2c3e50')
        self.top_frame.pack(pady=10, fill='x')
        
        self.timer_label = tk.Label(self.top_frame, text=f"剩餘時間: {self.time_left}s", 
                                   font=('Arial', 18, 'bold'), fg='#e74c3c', bg='#2c3e50')
        self.timer_label.pack()

        # 主容器 (左：棋盤，右：火柴人)
        self.main_container = tk.Frame(self.window, bg='#2c3e50')
        self.main_container.pack(pady=20)

        # --- 左側棋盤 ---
        self.left_frame = tk.Frame(self.main_container, bg='#34495e', bd=5)
        self.left_frame.grid(row=0, column=0, padx=20)

        for r in range(3):
            for c in range(3):
                btn = tk.Button(self.left_frame, text="", font=('Arial', 30, 'bold'), 
                               width=4, height=1, bg='#ecf0f1',
                               command=lambda row=r, col=c: self.player_click(row, col))
                btn.grid(row=r, column=c, padx=3, pady=3)
                self.buttons[r][c] = btn

        # --- 右側火柴人區域 ---
        self.right_frame = tk.Frame(self.main_container, bg='#2c3e50')
        self.right_frame.grid(row=0, column=1, padx=20)

        # 畫火柴人
        self.canvas = tk.Canvas(self.right_frame, width=150, height=200, bg='#2c3e50', highlightthickness=0)
        self.canvas.pack()
        self.draw_stickman()

        # 對話氣泡文字
        self.speech_label = tk.Label(self.right_frame, text=random.choice(self.quotes["start"]), 
                                    font=('微軟正黑體', 12, 'bold'), fg='white', bg='#8e44ad', 
                                    wraplength=120, pady=10, padx=10)
        self.speech_label.pack(pady=10)

        # 底部難度選擇
        self.diff_combo = ttk.Combobox(self.window, values=self.difficulty_names, state="readonly")
        self.diff_combo.current(4) # 預設地獄
        self.diff_combo.pack(pady=10)

    def draw_stickman(self):
        c = self.canvas
        # 頭
        c.create_oval(60, 20, 90, 50, outline='white', width=2)
        # 身體
        c.create_line(75, 50, 75, 120, fill='white', width=2)
        # 手
        c.create_line(75, 70, 45, 90, fill='white', width=2)
        c.create_line(75, 70, 105, 90, fill='white', width=2)
        # 腳
        c.create_line(75, 120, 55, 170, fill='white', width=2)
        c.create_line(75, 120, 95, 170, fill='white', width=2)

    def speak(self, category):
        msg = random.choice(self.quotes[category])
        self.speech_label.config(text=msg)

    def update_timer(self):
        if self.game_active:
            if self.time_left > 0:
                self.time_left -= 1
                self.timer_label.config(text=f"剩餘時間: {self.time_left}s")
                if self.time_left <= 3:
                    self.speak("hurry")
                self.window.after(1000, self.update_timer)
            else:
                self.speak("lose")
                messagebox.showinfo("時間到！", "你思考太久了，這局算電腦贏喔！")
                self.reset()

    def player_click(self, r, c):
        if self.board[r][c] is None and self.current_player == "X" and self.game_active:
            self.make_move(r, c, "X", "#2ecc71")
            if not self.check_game_over():
                self.current_player = "O"
                self.time_left = 10 # 重置時間給 AI
                self.window.after(500, self.ai_turn)

    def ai_turn(self):
        if not self.game_active: return
        diff_idx = self.diff_combo.current()
        intelligence = [0, 0.25, 0.5, 0.75, 1.0][diff_idx]
        
        move = self.get_minimax_move() if random.random() < intelligence else self.get_random_move()

        if move:
            self.make_move(move[0], move[1], "O", "#e67e22")
            if not self.check_game_over():
                self.current_player = "X"
                self.time_left = 10 # 重置時間給玩家

    def make_move(self, r, c, player, color):
        self.board[r][c] = player
        self.buttons[r][c].config(text=player, fg=color, state='disabled', disabledforeground=color)

    def get_random_move(self):
        empty = [(r, c) for r in range(3) for c in range(3) if self.board[r][c] is None]
        return random.choice(empty) if empty else None

    def get_minimax_move(self):
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

    def minimax(self, board, depth, is_maxing):
        res = self.get_winner_logic(board)
        if res == "O": return 10 - depth
        if res == "X": return depth - 10
        if self.is_full(board): return 0
        if is_maxing:
            best = -math.inf
            for r in range(3):
                for c in range(3):
                    if board[r][c] is None:
                        board[r][c] = "O"; s = self.minimax(board, depth+1, False); board[r][c] = None
                        best = max(s, best)
            return best
        else:
            best = math.inf
            for r in range(3):
                for c in range(3):
                    if board[r][c] is None:
                        board[r][c] = "X"; s = self.minimax(board, depth+1, True); board[r][c] = None
                        best = min(s, best)
            return best

    def get_winner_logic(self, b):
        for i in range(3):
            if b[i][0] == b[i][1] == b[i][2] and b[i][0]: return b[i][0]
            if b[0][i] == b[1][i] == b[2][i] and b[0][i]: return b[0][i]
        if b[0][0] == b[1][1] == b[2][2] and b[1][1]: return b[1][1]
        if b[0][2] == b[1][1] == b[2][0] and b[1][1]: return b[1][1]
        return None

    def is_full(self, b):
        return all(all(row) for row in b)

    def check_game_over(self):
        winner = self.get_winner_logic(self.board)
        if winner:
            self.game_active = False
            self.speak("win" if winner == "X" else "lose")
            messagebox.showinfo("結束", f"贏家是: {winner}")
            self.reset()
            return True
        if self.is_full(self.board):
            self.game_active = False
            self.speak("draw")
            messagebox.showinfo("結束", "平局！")
            self.reset()
            return True
        return False

    def reset(self):
        self.board = [[None for _ in range(3)] for _ in range(3)]
        for r in range(3):
            for c in range(3):
                self.buttons[r][c].config(text="", state='normal', bg='#ecf0f1')
        self.current_player = "X"
        self.time_left = 10
        self.game_active = True
        self.speak("start")
        self.update_timer()

if __name__ == "__main__":
    UltimateTicTacToe().window.mainloop()