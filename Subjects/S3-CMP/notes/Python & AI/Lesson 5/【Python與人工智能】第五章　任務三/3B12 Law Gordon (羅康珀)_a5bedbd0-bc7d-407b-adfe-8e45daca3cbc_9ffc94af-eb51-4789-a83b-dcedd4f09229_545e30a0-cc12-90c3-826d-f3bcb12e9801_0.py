import tkinter as tk
from tkinter import messagebox
import random

class SuperTicTacToe:
    def __init__(self, root):
        self.root = root
        self.root.title("過三關：時空裂痕 (Infinite Mode)")
        self.root.configure(bg="#1A1A2E") # 深邃星空藍
        
        self.player_moves = [] # 追蹤玩家 X 的下棋順序
        self.ai_moves = []     # 追蹤電腦 O 的下棋順序
        self.board_state = [[None for _ in range(3)] for _ in range(3)]
        self.buttons = [[None for _ in range(3)] for _ in range(3)]
        self.win_count = 0
        
        self.setup_ui()

    def setup_ui(self):
        # 頂部資訊欄
        self.info_label = tk.Label(self.root, text="規則：每人最多 3 顆棋，第 4 步會頂掉第 1 步！", 
                                  fg="#E94560", bg="#1A1A2E", font=("Arial", 12, "bold"))
        self.info_label.pack(pady=10)
        
        self.score_label = tk.Label(self.root, text=f"連勝紀錄: {self.win_count}", 
                                   fg="#0F3460", bg="#16213E", font=("Arial", 10), width=20)
        self.score_label.pack()

        # 遊戲棋盤
        game_frame = tk.Frame(self.root, bg="#16213E", padx=10, pady=10)
        game_frame.pack(pady=10)

        for r in range(3):
            for c in range(3):
                btn = tk.Button(game_frame, text="", font=("Verdana", 30, "bold"), width=4, height=1,
                                bg="#0F3460", fg="white", activebackground="#16213E",
                                relief="flat", command=lambda r=r, c=c: self.play(r, c))
                btn.grid(row=r, column=c, padx=4, pady=4)
                self.buttons[r][c] = btn

    def play(self, r, c):
        if self.board_state[r][c] is not None: return

        # 1. 玩家下棋
        self.make_move(r, c, "X")
        self.player_moves.append((r, c))
        
        # 檢查是否超過 3 顆棋子 (消失機制)
        if len(self.player_moves) > 3:
            old_r, old_c = self.player_moves.pop(0)
            self.clear_move(old_r, old_c)
        
        # 預告下一個要消失的棋子
        self.highlight_next_to_vanish()

        if self.check_win("X"):
            self.end_game("你贏了！這波操作太神了！", True)
            return

        # 2. 電腦下棋 (稍作延遲增加真實感)
        self.root.after(400, self.ai_turn)

    def ai_turn(self):
        # 簡單 AI：優先連線或隨機
        move = self.get_smart_move()
        if move:
            r, c = move
            self.make_move(r, c, "O")
            self.ai_moves.append((r, c))
            
            if len(self.ai_moves) > 3:
                old_r, old_c = self.ai_moves.pop(0)
                self.clear_move(old_r, old_c)
            
            self.highlight_next_to_vanish()
            
            if self.check_win("O"):
                self.end_game("AI 贏了！再挑戰一次？", False)

    def make_move(self, r, c, p):
        self.board_state[r][c] = p
        color = "#E94560" if p == "X" else "#4ECCA3"
        self.buttons[r][c].config(text=p, fg=color)

    def clear_move(self, r, c):
        self.board_state[r][c] = None
        self.buttons[r][c].config(text="", bg="#0F3460")

    def highlight_next_to_vanish(self):
        # 將即將消失的按鈕背景變淡，提醒玩家
        for r in range(3):
            for c in range(3):
                self.buttons[r][c].config(bg="#0F3460")
        
        if len(self.player_moves) == 3:
            r, c = self.player_moves[0]
            self.buttons[r][c].config(bg="#1B1B3A") # 淡淡的警告色
        if len(self.ai_moves) == 3:
            r, c = self.ai_moves[0]
            self.buttons[r][c].config(bg="#1B1B3A")

    def get_smart_move(self):
        empty = [(r, c) for r in range(3) for c in range(3) if self.board_state[r][c] is None]
        # 這裡簡化 AI，優先選中心，否則隨機
        if (1, 1) in empty: return (1, 1)
        return random.choice(empty) if empty else None

    def check_win(self, p):
        for i in range(3):
            if all(self.board_state[i][j] == p for j in range(3)): return True
            if all(self.board_state[j][i] == p for j in range(3)): return True
        if self.board_state[0][0] == self.board_state[1][1] == self.board_state[2][2] == p: return True
        if self.board_state[0][2] == self.board_state[1][1] == self.board_state[2][0] == p: return True
        return False

    def end_game(self, msg, player_won):
        if player_won: self.win_count += 1
        else: self.win_count = 0
        
        messagebox.showinfo("遊戲結束", msg)
        self.score_label.config(text=f"連勝紀錄: {self.win_count}")
        self.reset()

    def reset(self):
        self.board_state = [[None for _ in range(3)] for _ in range(3)]
        self.player_moves = []
        self.ai_moves = []
        for r in range(3):
            for c in range(3):
                self.buttons[r][c].config(text="", bg="#0F3460")

if __name__ == "__main__":
    root = tk.Tk()
    app = SuperTicTacToe(root)
    root.mainloop()