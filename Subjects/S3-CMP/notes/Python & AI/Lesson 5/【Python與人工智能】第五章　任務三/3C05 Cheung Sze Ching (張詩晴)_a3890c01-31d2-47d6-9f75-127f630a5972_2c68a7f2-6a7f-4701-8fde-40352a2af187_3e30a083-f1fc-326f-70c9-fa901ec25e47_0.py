
import tkinter as tk
from tkinter import messagebox
import random
import math

class TicTacToeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("過三關：終極挑戰版")
        self.root.geometry("400x500")
        self.root.configure(bg="#f0f0f0")

        # 1. 遊戲參數
        self.player = "X"
        self.ai = "O"
        self.current_player = self.player
        self.difficulty = tk.StringVar(value="Hard") # 預設難度
        
        # 2. 2D List 儲存棋盤狀態
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.buttons = [[None for _ in range(3)] for _ in range(3)]

        self.setup_ui()

    def setup_ui(self):
        """建立 UI 界面"""
        # 標題與難度選擇
        header = tk.Frame(self.root, bg="#f0f0f0", pady=10)
        header.pack()

        tk.Label(header, text="難度:", font=("Arial", 12), bg="#f0f0f0").pack(side=tk.LEFT)
        for text, mode in [("簡單", "Easy"), ("普通", "Medium"), ("地獄", "Hard")]:
            tk.Radiobutton(header, text=text, variable=self.difficulty, value=mode, 
                           bg="#f0f0f0", command=self.reset_game).pack(side=tk.LEFT)

        # 棋盤容器
        self.board_frame = tk.Frame(self.root, bg="#333", padx=5, pady=5)
        self.board_frame.pack(pady=20)

        for r in range(3):
            for c in range(3):
                btn = tk.Button(self.board_frame, text="", font=("Arial", 24, "bold"),
                                width=5, height=2, bg="white",
                                command=lambda row=r, col=c: self.player_click(row, col))
                btn.grid(row=r, column=c, padx=2, pady=2)
                self.buttons[r][c] = btn

        # 重置按鈕
        tk.Button(self.root, text="重新開始", font=("Arial", 12), 
                  command=self.reset_game).pack(pady=10)

    def player_click(self, r, c):
        """玩家下棋邏輯"""
        if self.board[r][c] == "" and self.current_player == self.player:
            self.make_move(r, c, self.player)
            
            if not self.check_end(self.player):
                self.current_player = self.ai
                # 稍微延遲，模擬電腦思考
                self.root.after(500, self.ai_move)

    def ai_move(self):
        """電腦下棋邏輯"""
        mode = self.difficulty.get()
        
        if mode == "Easy":
            move = self.get_random_move()
        elif mode == "Medium":
            # 40% 機率亂下，60% 機率用 Minimax
            move = self.get_best_move() if random.random() > 0.4 else self.get_random_move()
        else:
            move = self.get_best_move() # 地獄級

        if move:
            self.make_move(move[0], move[1], self.ai)
            if not self.check_end(self.ai):
                self.current_player = self.player

    def make_move(self, r, c, p):
        self.board[r][c] = p
        color = "#2196F3" if p == "X" else "#F44336"
        self.buttons[r][c].config(text=p, fg=color)

    def get_random_move(self):
        empty = [(r, c) for r in range(3) for c in range(3) if self.board[r][c] == ""]
        return random.choice(empty) if empty else None

    def get_best_move(self):
        best_score = -math.inf
        move = None
        for r in range(3):
            for c in range(3):
                if self.board[r][c] == "":
                    self.board[r][c] = self.ai
                    score = self.minimax(self.board, 0, False)
                    self.board[r][c] = ""
                    if score > best_score:
                        best_score = score
                        move = (r, c)
        return move

    def minimax(self, board, depth, is_maxing):
        # 核心演算法
        if self.win_logic(self.ai): return 10 - depth
        if self.win_logic(self.player): return depth - 10
        if self.draw_logic(): return 0

        if is_maxing:
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
                        board[r][c] = self.player
                        best = min(best, self.minimax(board, depth + 1, True))
                        board[r][c] = ""
            return best

    def win_logic(self, p):
        for i in range(3):
            if all(self.board[i][j] == p for j in range(3)): return True
            if all(self.board[j][i] == p for j in range(3)): return True
        if all(self.board[i][i] == p for i in range(3)): return True
        if all(self.board[i][2-i] == p for i in range(3)): return True
        return False

    def draw_logic(self):
        return all(self.board[r][c] != "" for r in range(3) for c in range(3))

    def check_end(self, p):
        if self.win_logic(p):
            messagebox.showinfo("遊戲結束", f"玩家 {p} 獲勝！")
            self.reset_game()
            return True
        if self.draw_logic():
            messagebox.showinfo("遊戲結束", "平手！")
            self.reset_game()
            return True
        return False

    def reset_game(self):
        self.board = [["" for _ in range(3)] for _ in range(3)]
        for r in range(3):
            for c in range(3):
                self.buttons[r][c].config(text="", bg="white")
        self.current_player = self.player

if __name__ == "__main__":
    root = tk.Tk()
    game = TicTacToeGame(root)
    root.mainloop()