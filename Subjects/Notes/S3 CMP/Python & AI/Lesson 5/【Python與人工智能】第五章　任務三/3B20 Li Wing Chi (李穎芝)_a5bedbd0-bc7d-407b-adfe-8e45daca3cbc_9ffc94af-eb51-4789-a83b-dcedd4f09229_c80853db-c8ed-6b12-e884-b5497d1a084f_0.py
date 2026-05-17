import tkinter as tk
from tkinter import messagebox
import random
import time

class UltimateTicTacToe:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🔥 極速過三關：終極挑戰 🔥")
        self.root.configure(bg="#2C3E50")
        
        self.score = 0
        self.timer_val = 5
        self.timer_running = False
        self.board_state = [["" for _ in range(3)] for _ in range(3)]
        self.buttons = [[None for _ in range(3)] for _ in range(3)]
        
        self.setup_ui()
        self.reset_game()

    def setup_ui(self):
        # 分數與計時器顯示
        self.info_frame = tk.Frame(self.root, bg="#2C3E50")
        self.info_frame.pack(pady=10, fill="x")
        
        self.score_label = tk.Label(self.info_frame, text=f"得分: {self.score}", 
                                    font=('微軟正黑體', 16, 'bold'), fg="#F1C40F", bg="#2C3E50")
        self.score_label.pack(side=tk.LEFT, padx=20)
        
        self.timer_label = tk.Label(self.info_frame, text=f"剩餘時間: {self.timer_val}s", 
                                     font=('微軟正黑體', 16, 'bold'), fg="#E74C3C", bg="#2C3E50")
        self.timer_label.pack(side=tk.RIGHT, padx=20)

        # 遊戲主棋盤
        self.grid_frame = tk.Frame(self.root, bg="#34495E", bd=5, relief="ridgeline")
        self.grid_frame.pack(padx=20, pady=10)
        
        for r in range(3):
            for c in range(3):
                btn = tk.Button(
                    self.grid_frame, text="", font=('Arial', 32, 'bold'),
                    width=4, height=1, bg="#ECF0F1", activebackground="#BDC3C7",
                    command=lambda row=r, col=c: self.player_move(row, col)
                )
                btn.grid(row=r, column=c, padx=4, pady=4)
                self.buttons[r][c] = btn

    def start_timer(self):
        if not self.timer_running:
            self.timer_running = True
            self.update_timer()

    def update_timer(self):
        if self.timer_running:
            if self.timer_val > 0:
                self.timer_val -= 1
                self.timer_label.config(text=f"剩餘時間: {self.timer_val}s")
                self.root.after(1000, self.update_timer)
            else:
                # 時間到，隨機落子
                self.auto_random_move()

    def auto_random_move(self):
        empty = [(r, c) for r in range(3) for c in range(3) if self.board_state[r][c] == ""]
        if empty:
            r, c = random.choice(empty)
            self.player_move(r, c)

    def player_move(self, r, c):
        if self.board_state[r][c] == "":
            self.make_move(r, c, "X", "#E74C3C")
            self.timer_running = False # 暫時停止計時
            
            if not self.check_end("X"):
                self.root.after(400, self.ai_move)

    def ai_move(self):
        # 簡單 AI：優先阻擋或進攻
        move = self.get_smart_move()
        self.make_move(move[0], move[1], "O", "#3498DB")
        
        if not self.check_end("O"):
            self.timer_val = 5 # 重置時間
            self.timer_label.config(text=f"剩餘時間: {self.timer_val}s")
            self.start_timer()

    def get_smart_move(self):
        # 簡單邏輯：隨機找空位 (模擬玩家對戰壓力)
        empty = [(r, c) for r in range(3) for c in range(3) if self.board_state[r][c] == ""]
        return random.choice(empty)

    def make_move(self, r, c, char, color):
        self.board_state[r][c] = char
        self.buttons[r][c].config(text=char, fg=color, state="disabled")

    def check_end(self, player):
        s = self.board_state
        win = False
        # 檢查勝利邏輯
        for i in range(3):
            if s[i][0] == s[i][1] == s[i][2] != "": win = True
            if s[0][i] == s[1][i] == s[2][i] != "": win = True
        if s[0][0] == s[1][1] == s[2][2] != "": win = True
        if s[0][2] == s[1][1] == s[2][0] != "": win = True
        
        if win:
            self.timer_running = False
            if player == "X":
                bonus = self.timer_val * 10
                self.score += (100 + bonus)
                messagebox.showinfo("YOU WIN!", f"神速！獲得 100 分 + 獎勵 {bonus} 分！")
            else:
                messagebox.showerror("LOSE", "太慢了！電腦獲勝。")
            self.reset_game()
            return True
        
        if all(cell != "" for row in s for cell in row):
            messagebox.showinfo("DRAW", "平局！再接再厲。")
            self.reset_game()
            return True
        return False

    def reset_game(self):
        self.timer_running = False
        self.timer_val = 5
        self.board_state = [["" for _ in range(3)] for _ in range(3)]
        for r in range(3):
            for c in range(3):
                self.buttons[r][c].config(text="", state="normal", bg="#ECF0F1")
        self.score_label.config(text=f"總得分: {self.score}")
        self.start_timer()

if __name__ == "__main__":
    game = UltimateTicTacToe()
    game.root.mainloop()