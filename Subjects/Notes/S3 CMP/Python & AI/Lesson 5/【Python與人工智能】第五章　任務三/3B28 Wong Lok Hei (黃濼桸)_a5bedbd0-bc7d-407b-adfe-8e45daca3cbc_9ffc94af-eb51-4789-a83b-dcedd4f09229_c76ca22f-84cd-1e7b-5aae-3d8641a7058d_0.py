import tkinter as tk
from tkinter import messagebox
import random
import math

class UltimateTicTacToe:
    def __init__(self, root):
        self.root = root
        self.root.title("過三關：終極強化版")
        self.root.geometry("400x600")
        self.root.configure(bg="#1a1a2e") # 深藍黑色背景
        
        self.human = "X"
        self.ai = "O"
        self.score = 0
        self.difficulty = tk.StringVar(value="Hard")
        
        self.board_state = [["" for _ in range(3)] for _ in range(3)]
        self.buttons = [[None for _ in range(3)] for _ in range(3)]
        
        self.setup_ui()

    def setup_ui(self):
        # 標題與積分
        header_frame = tk.Frame(self.root, bg="#16213e", pady=20)
        header_frame.pack(fill="x")
        
        tk.Label(header_frame, text="ULTIMATE TTT", font=("Courier New", 24, "bold"), 
                 fg="#e94560", bg="#16213e").pack()
        
        self.score_label = tk.Label(header_frame, text=f"SCORE: {self.score}", 
                                   font=("Arial", 14), fg="#ffffff", bg="#16213e")
        self.score_label.pack()

        # 難度切換
        diff_frame = tk.Frame(self.root, bg="#1a1a2e", pady=10)
        diff_frame.pack()
        for mode in ["Easy", "Normal", "Hard"]:
            rb = tk.Radiobutton(diff_frame, text=mode, variable=self.difficulty, value=mode,
                                bg="#1a1a2e", fg="#4ecca3", selectcolor="#1a1a2e",
                                activebackground="#1a1a2e", font=("Arial", 10, "bold"),
                                command=self.reset_game)
            rb.pack(side=tk.LEFT, padx=10)

        # 棋盤容器
        self.grid_frame = tk.Frame(self.root, bg="#1a1a2e", padx=20, pady=20)
        self.grid_frame.pack()

        for r in range(3):
            for c in range(3):
                btn = tk.Button(self.grid_frame, text="", font=('Arial', 36, 'bold'), 
                                width=3, height=1, bg="#0f3460", fg="white",
                                relief="flat", activebackground="#e94560",
                                command=lambda r=r, c=c: self.handle_click(r, c))
                btn.grid(row=r, column=c, padx=5, pady=5)
                self.buttons[r][c] = btn

        # 狀態提示
        self.status_label = tk.Label(self.root, text="YOUR TURN", font=("Arial", 12), 
                                    fg="#4ecca3", bg="#1a1a2e", pady=10)
        self.status_label.pack()

    def handle_click(self, r, c):
        if self.board_state[r][c] == "" and self.status_label.cget("text") == "YOUR TURN":
            self.place_symbol(r, c, self.human)
            
            if not self.check_end_game():
                self.status_label.config(text="AI THINKING...", fg="#e94560")
                self.root.after(600, self.ai_move)

    def ai_move(self):
        mode = self.difficulty.get()
        if mode == "Easy":
            move = self.get_random_move()
        elif mode == "Normal":
            move = self.get_best_move() if random.random() > 0.4 else self.get_random_move()
        else:
            move = self.get_best_move()

        if move:
            self.place_symbol(move[0], move[1], self.ai)
            self.status_label.config(text="YOUR TURN", fg="#4ecca3")
            self.check_end_game()

    def place_symbol(self, r, c, player):
        self.board_state[r][c] = player
        target_btn = self.buttons[r][c]
        color = "#4ecca3" if player == "X" else "#e94560"
        
        # 視覺動畫：點擊時顏色突變
        target_btn.config(text=player, fg=color, state="disabled", disabledforeground=color)

    def check_end_game(self):
        win_info = self.get_winning_line(self.board_state)
        if win_info:
            winner, line = win_info
            self.highlight_winner(line)
            if winner == "X":
                bonus = {"Easy": 10, "Normal": 50, "Hard": 500}[self.difficulty.get()]
                self.score += bonus
                messagebox.showinfo("VICTORY", f"完美一擊！獲得 {bonus} 分！")
            else:
                messagebox.showinfo("DEFEAT", "這就是科技的力量！")
            self.reset_game()
            return True
        
        if all(cell != "" for row in self.board_state for cell in row):
            messagebox.showinfo("DRAW", "不分上下！")
            self.reset_game()
            return True
        return False

    def highlight_winner(self, line):
        # 獲勝時的閃爍效果
        for r, c in line:
            self.buttons[r][c].config(bg="#f1c40f") # 變為金黃色

    def get_winning_line(self, b):
        # 回傳贏家是誰以及在哪條線上 (r, c)
        for i in range(3):
            if b[i][0] == b[i][1] == b[i][2] != "": return b[i][0], [(i,0), (i,1), (i,2)]
            if b[0][i] == b[1][i] == b[2][i] != "": return b[0][i], [(0,i), (1,i), (2,i)]
        if b[0][0] == b[1][1] == b[2][2] != "": return b[0][0], [(0,0), (1,1), (2,2)]
        if b[0][2] == b[1][1] == b[2][0] != "": return b[0][2], [(0,2), (1,1), (2,0)]
        return None

    # --- Minimax 核心 (與前版邏輯相同，維持無敵強度) ---
    def get_best_move(self):
        best_score = -math.inf
        move = None
        for r in range(3):
            for c in range(3):
                if self.board_state[r][c] == "":
                    self.board_state[r][c] = self.ai
                    score = self.minimax(self.board_state, 0, False)
                    self.board_state[r][c] = ""
                    if score > best_score:
                        best_score = score
                        move = (r, c)
        return move

    def minimax(self, board, depth, is_maximizing):
        win_res = self.get_winning_line(board)
        if win_res:
            winner = win_res[0]
            return 10 - depth if winner == self.ai else depth - 10
        if all(cell != "" for row in board for cell in row): return 0

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

    def get_random_move(self):
        empty = [(r, c) for r in range(3) for c in range(3) if self.board_state[r][c] == ""]
        return random.choice(empty) if empty else None

    def reset_game(self):
        self.board_state = [["" for _ in range(3)] for _ in range(3)]
        self.score_label.config(text=f"SCORE: {self.score}")
        self.status_label.config(text="YOUR TURN", fg="#4ecca3")
        for r in range(3):
            for c in range(3):
                self.buttons[r][c].config(text="", state="normal", bg="#0f3460")

if __name__ == "__main__":
    root = tk.Tk()
    game = UltimateTicTacToe(root)
    root.mainloop()