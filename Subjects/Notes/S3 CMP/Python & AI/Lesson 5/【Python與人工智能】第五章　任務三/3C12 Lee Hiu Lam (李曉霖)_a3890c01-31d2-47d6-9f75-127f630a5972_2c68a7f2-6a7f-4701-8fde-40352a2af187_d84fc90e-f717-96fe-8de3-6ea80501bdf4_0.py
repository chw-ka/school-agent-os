import tkinter as tk
from tkinter import messagebox
import random

class PopularGame:
    def __init__(self, root):
        self.root = root
        self.root.title("極速對決：絕望過三關")
        self.root.configure(bg='#1a1a1a') # 深色主題
        
        self.current_player = "X"
        self.game_state = [["" for _ in range(3)] for _ in range(3)]
        self.board = [[None for _ in range(3)] for _ in range(3)]
        self.timer_val = 5
        self.timer_running = False
        
        self.difficulty = tk.StringVar(value="Normal")
        self.setup_ui()

    def setup_ui(self):
        # 頂部控制區
        self.header = tk.Frame(self.root, bg='#1a1a1a')
        self.header.pack(pady=10)
        
        # 難度選擇按鈕
        for diff in [("簡單", "Easy"), ("普通", "Normal"), ("地獄", "Hell")]:
            tk.Radiobutton(self.header, text=diff[0], variable=self.difficulty, value=diff[1],
                           bg='#1a1a1a', fg='white', selectcolor='#333333', font=('Arial', 10),
                           command=self.reset_game).pack(side=tk.LEFT, padx=10)

        # 計時器顯示 (受歡迎秘訣：創造緊張感)
        self.label_timer = tk.Label(self.root, text=f"剩餘時間: {self.timer_val}s", 
                                    font=('Arial', 18, 'bold'), bg='#1a1a1a', fg='#ffcc00')
        self.label_timer.pack(pady=5)

        # 棋盤容器
        self.grid_frame = tk.Frame(self.root, bg='#333333', padx=5, pady=5)
        self.grid_frame.pack(pady=10)

        for r in range(3):
            for c in range(3):
                btn = tk.Button(self.grid_frame, text="", font=('Verdana', 32, 'bold'),
                                width=4, height=1, bg='#2d2d2d', fg='white', relief="flat",
                                activebackground='#404040',
                                command=lambda row=r, col=c: self.player_move(row, col))
                btn.grid(row=r, column=c, padx=3, pady=3)
                self.board[r][c] = btn
        
        self.start_timer()

    def start_timer(self):
        if not self.timer_running:
            self.timer_running = True
            self.tick()

    def tick(self):
        if self.timer_running and self.current_player == "X":
            if self.timer_val > 0:
                self.timer_val -= 1
                self.label_timer.config(text=f"剩餘時間: {self.timer_val}s")
                self.root.after(1000, self.tick)
            else:
                # 時間到，強制隨機下一棋 (受歡迎秘訣：懲罰機制)
                self.force_random_move()

    def force_random_move(self):
        empty = [(r, c) for r in range(3) for c in range(3) if self.game_state[r][c] == ""]
        if empty:
            r, c = random.choice(empty)
            self.player_move(r, c)

    def player_move(self, r, c):
        if self.game_state[r][c] == "" and self.current_player == "X":
            self.timer_val = 5 # 重置計時
            self.execute_move(r, c, "X")
            if not self.check_end("X"):
                self.current_player = "O"
                self.label_timer.config(text="電腦進攻中...", fg='#00ffcc')
                self.root.after(600, self.computer_move)

    def computer_move(self):
        mode = self.difficulty.get()
        if mode == "Easy":
            move = self.get_random_move()
        elif mode == "Normal":
            # 混合邏輯：60% 聰明，40% 隨機
            move = self.get_best_move() if random.random() < 0.6 else self.get_random_move()
        else:
            move = self.get_best_move()

        if move:
            self.execute_move(move[0], move[1], "O")
            if not self.check_end("O"):
                self.current_player = "X"
                self.timer_val = 5
                self.label_timer.config(text=f"剩餘時間: {self.timer_val}s", fg='#ffcc00')

    def execute_move(self, r, c, p):
        self.game_state[r][c] = p
        color = "#ff4d4d" if p == "X" else "#00d9ff"
        self.board[r][c].config(text=p, fg=color)

    def check_end(self, p):
        win_path = self.get_win_path(p)
        if win_path:
            self.timer_running = False
            # 受歡迎秘訣：視覺高亮回饋
            for r, c in win_path:
                self.board[r][c].config(bg='#00cc44', fg='white')
            messagebox.showinfo("Game Over", f"玩家 {p} 統治了比賽！")
            self.reset_game()
            return True
        
        if all(self.game_state[r][c] != "" for r in range(3) for c in range(3)):
            messagebox.showinfo("Game Over", "勢均力敵，平手！")
            self.reset_game()
            return True
        return False

    def get_win_path(self, p):
        # 回傳贏球的座標路徑以便變色
        for i in range(3):
            if all(self.game_state[i][j] == p for j in range(3)): return [(i,0),(i,1),(i,2)]
            if all(self.game_state[j][i] == p for j in range(3)): return [(0,i),(1,i),(2,i)]
        if all(self.game_state[i][i] == p for i in range(3)): return [(0,0),(1,1),(2,2)]
        if all(self.game_state[i][2-i] == p for i in range(3)): return [(0,2),(1,1),(2,0)]
        return None

    # --- AI 核心 ---
    def get_random_move(self):
        empty = [(r, c) for r in range(3) for c in range(3) if self.game_state[r][c] == ""]
        return random.choice(empty) if empty else None

    def get_best_move(self):
        best_score = -float('inf')
        move = None
        for r in range(3):
            for c in range(3):
                if self.game_state[r][c] == "":
                    self.game_state[r][c] = "O"
                    score = self.minimax(self.game_state, 0, False)
                    self.game_state[r][c] = ""
                    if score > best_score:
                        best_score = score
                        move = (r, c)
        return move

    def minimax(self, state, depth, is_max):
        if self.is_win(state, "O"): return 10
        if self.is_win(state, "X"): return -10
        if all(state[r][c] != "" for r in range(3) for c in range(3)): return 0
        
        scores = []
        for r in range(3):
            for c in range(3):
                if state[r][c] == "":
                    state[r][c] = "O" if is_max else "X"
                    scores.append(self.minimax(state, depth+1, not is_max))
                    state[r][c] = ""
        return max(scores) if is_max else min(scores)

    def is_win(self, b, p):
        return any(all(b[i][j] == p for j in range(3)) for i in range(3)) or \
               any(all(b[j][i] == p for j in range(3)) for i in range(3)) or \
               all(b[i][i] == p for i in range(3)) or all(b[i][2-i] == p for i in range(3))

    def reset_game(self):
        self.game_state = [["" for _ in range(3)] for _ in range(3)]
        self.current_player = "X"
        self.timer_val = 5
        for r in range(3):
            for c in range(3):
                self.board[r][c].config(text="", bg='#2d2d2d')
        if not self.timer_running:
            self.start_timer()

if __name__ == "__main__":
    root = tk.Tk()
    game = PopularGame(root)
    root.mainloop()