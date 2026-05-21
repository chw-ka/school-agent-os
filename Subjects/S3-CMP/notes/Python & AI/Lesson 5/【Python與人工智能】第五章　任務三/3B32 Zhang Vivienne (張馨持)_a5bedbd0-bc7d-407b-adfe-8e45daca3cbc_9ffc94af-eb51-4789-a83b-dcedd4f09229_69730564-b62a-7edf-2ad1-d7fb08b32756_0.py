import tkinter as tk
from tkinter import messagebox
import random
import time

class SuperTicTacToe:
    def __init__(self, root):
        self.root = root
        self.root.title("🔥 終極過三關：時速對決 🔥")
        self.root.configure(bg="#1A1A1A")
        
        # 遊戲數據
        self.scores = {"Player": 0, "AI": 0}
        self.current_player = "X"
        self.game_state = [["" for _ in range(3)] for _ in range(3)]
        self.buttons = [[None for _ in range(3)] for _ in range(3)]
        self.time_left = 5
        self.timer_running = False
        
        self.setup_ui()
        self.start_timer()

    def setup_ui(self):
        # 計分板
        self.score_label = tk.Label(
            self.root, text=f"玩家 (X): {self.scores['Player']}  |  電腦 (O): {self.scores['AI']}",
            font=('Verdana', 14, 'bold'), bg="#1A1A1A", fg="#FFFFFF", pady=10
        )
        self.score_label.pack()

        # 倒數計時顯示
        self.timer_label = tk.Label(
            self.root, text=f"剩餘時間: {self.time_left}s",
            font=('Verdana', 12), bg="#1A1A1A", fg="#FF4757"
        )
        self.timer_label.pack()

        # 棋盤容器
        board_frame = tk.Frame(self.root, bg="#2F3542", padx=10, pady=10)
        board_frame.pack(pady=10)

        for r in range(3):
            for c in range(3):
                btn = tk.Button(
                    board_frame, text="", font=('Arial', 32, 'bold'),
                    width=4, height=1, bg="#2F3542", fg="#FFFFFF",
                    activebackground="#57606F", relief="flat",
                    command=lambda row=r, col=c: self.player_click(row, col)
                )
                btn.grid(row=r, column=c, padx=4, pady=4)
                self.buttons[r][c] = btn

    def start_timer(self):
        self.timer_running = True
        self.update_timer()

    def update_timer(self):
        if self.timer_running:
            if self.time_left > 0:
                self.time_left -= 1
                self.timer_label.config(text=f"剩餘時間: {self.time_left}s")
                self.root.after(1000, self.update_timer)
            else:
                # 時間到！隨機幫玩家下一棋
                self.auto_random_move()

    def auto_random_move(self):
        if self.current_player == "X":
            empty = [(r, c) for r in range(3) for c in range(3) if self.game_state[r][c] == ""]
            if empty:
                r, c = random.choice(empty)
                self.player_click(r, c)

    def player_click(self, r, c):
        if self.game_state[r][c] == "" and self.current_player == "X":
            self.make_move(r, c, "X")
            self.time_left = 6 # 重置計時
            if not self.check_end():
                self.current_player = "O"
                self.root.after(600, self.ai_smart_move)

    def make_move(self, r, c, player):
        self.game_state[r][c] = player
        color = "#1E90FF" if player == "X" else "#FF4757"
        self.buttons[r][c].config(text=player, fg=color, state=tk.DISABLED, disabledforeground=color)

    def ai_smart_move(self):
        # 使用 Minimax 確保挑戰性
        move = self.get_best_move()
        if move:
            self.make_move(move[0], move[1], "O")
            if not self.check_end():
                self.current_player = "X"
                self.time_left = 6

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

    def minimax(self, board, depth, is_maximizing):
        winner = self.get_winner()
        if winner == "O": return 10 - depth
        if winner == "X": return depth - 10
        if all(cell != "" for row in board for cell in row): return 0

        if is_maximizing:
            best = -float('inf')
            for r in range(3):
                for c in range(3):
                    if board[r][c] == "":
                        board[r][c] = "O"
                        best = max(best, self.minimax(board, depth + 1, False))
                        board[r][c] = ""
            return best
        else:
            best = float('inf')
            for r in range(3):
                for c in range(3):
                    if board[r][c] == "":
                        board[r][c] = "X"
                        best = min(best, self.minimax(board, depth + 1, True))
                        board[r][c] = ""
            return best

    def get_winner(self):
        lines = self.game_state + list(zip(*self.game_state)) # 橫與直
        lines.append([self.game_state[i][i] for i in range(3)]) # 主對角
        lines.append([self.game_state[i][2-i] for i in range(3)]) # 副對角
        for line in lines:
            if line[0] == line[1] == line[2] != "":
                return line[0]
        return None

    def check_end(self):
        win = self.get_winner()
        if win or all(c != "" for r in self.game_state for c in r):
            self.timer_running = False
            if win == "X":
                self.scores["Player"] += 1
                msg = "🔥 太強了！你贏了！"
            elif win == "O":
                self.scores["AI"] += 1
                msg = "💀 電腦獲勝！再接再厲。"
            else:
                msg = "🤝 平手！握手言和。"
            
            self.score_label.config(text=f"玩家 (X): {self.scores['Player']}  |  電腦 (O): {self.scores['AI']}")
            messagebox.showinfo("遊戲結束", msg)
            self.reset_game()
            return True
        return False

    def reset_game(self):
        self.game_state = [["" for _ in range(3)] for _ in range(3)]
        self.current_player = "X"
        self.time_left = 6
        for r in range(3):
            for c in range(3):
                self.buttons[r][c].config(text="", state=tk.NORMAL, bg="#2F3542")
        self.timer_running = True
        self.update_timer()

if __name__ == "__main__":
    root = tk.Tk()
    game = SuperTicTacToe(root)
    root.mainloop()