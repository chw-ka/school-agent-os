import tkinter as tk
from tkinter import messagebox
import random
import time

class UltimateTicTacToe:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Task3_3X99 - 極限生存模式")
        self.window.configure(bg='#1e1e1e')
        
        # 遊戲數據
        self.current_player = "X"
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.buttons = [[None for _ in range(3)] for _ in range(3)]
        self.score = 0
        self.time_left = 5.0
        self.timer_running = False
        
        self.setup_ui()
        self.start_timer()

    def setup_ui(self):
        # 分數與倒數計時顯示
        self.info_label = tk.Label(
            self.window, 
            text=f"分數: {self.score}  |  剩餘時間: {self.time_left}s",
            font=('Verdana', 14, 'bold'), fg='#00FFCC', bg='#1e1e1e'
        )
        self.info_label.pack(pady=10)

        # 棋盤容器
        grid_frame = tk.Frame(self.window, bg='#333333', padx=10, pady=10)
        grid_frame.pack(pady=5)

        for r in range(3):
            for c in range(3):
                btn = tk.Button(
                    grid_frame, text="", font=('Arial', 32, 'bold'),
                    width=4, height=1, bg='#2d2d2d', fg='white',
                    activebackground='#404040', relief='flat',
                    command=lambda row=r, col=c: self.player_action(row, col)
                )
                btn.grid(row=r, column=c, padx=4, pady=4)
                self.buttons[r][c] = btn

    def start_timer(self):
        self.timer_running = True
        self.update_timer()

    def update_timer(self):
        if self.timer_running:
            if self.time_left <= 0:
                self.timer_running = False
                messagebox.showwarning("逾時！", "思考太久了，你輸了！")
                self.reset_game(total_reset=True)
            else:
                self.time_left = round(self.time_left - 0.1, 1)
                self.info_label.config(text=f"分數: {self.score}  |  剩餘時間: {self.time_left}s")
                self.window.after(100, self.update_timer)

    def player_action(self, r, c):
        if self.board[r][c] == "" and self.current_player == "X":
            self.make_move(r, c, "X")
            if not self.check_end():
                self.current_player = "O"
                self.time_left = 5.0 # 重置時間給 AI (雖然 AI 很快)
                self.window.after(300, self.ai_action)

    def ai_action(self):
        # 使用隨機與邏輯混合的 AI，增加不確定性
        move = self.get_best_move()
        if move:
            self.make_move(move[0], move[1], "O")
            if not self.check_end():
                self.current_player = "X"
                self.time_left = 5.0 # 換玩家時重置時間

    def make_move(self, r, c, player):
        self.board[r][c] = player
        color = '#FF3366' if player == "X" else '#33CCFF'
        self.buttons[r][c].config(text=player, fg=color)

    def check_end(self):
        winner = self.get_winner(self.board)
        if winner:
            self.timer_running = False
            if winner == "X":
                self.score += 1
                self.win_animation()
                messagebox.showinfo("勝利", "你贏了！難度將稍微提升！")
            elif winner == "O":
                messagebox.showinfo("失敗", f"電腦贏了！最終得分: {self.score}")
                self.score = 0
            else:
                messagebox.showinfo("平局", "旗鼓相當！")
            
            self.reset_game()
            return True
        return False

    def win_animation(self):
        # 簡單的霓虹閃爍效果
        colors = ['#FF3366', '#33CCFF', '#00FFCC', '#FFFF33']
        for _ in range(5):
            new_color = random.choice(colors)
            for r in range(3):
                for c in range(3):
                    self.buttons[r][c].config(bg=new_color)
            self.window.update()
            time.sleep(0.05)
        for r in range(3):
            for c in range(3):
                self.buttons[r][c].config(bg='#2d2d2d')

    def get_winner(self, b):
        for i in range(3):
            if b[i][0] == b[i][1] == b[i][2] != "": return b[i][0]
            if b[0][i] == b[1][i] == b[2][i] != "": return b[0][i]
        if b[0][0] == b[1][1] == b[2][2] != "": return b[0][0]
        if b[0][2] == b[1][1] == b[2][0] != "": return b[0][2]
        if all(cell != "" for row in b for cell in row): return "Tie"
        return None

    def get_best_move(self):
        # 優先尋找能贏的位置，否則隨機
        for r in range(3):
            for c in range(3):
                if self.board[r][c] == "":
                    self.board[r][c] = "O"
                    if self.get_winner(self.board) == "O":
                        self.board[r][c] = ""
                        return (r, c)
                    self.board[r][c] = ""
        
        # 擋住玩家
        for r in range(3):
            for c in range(3):
                if self.board[r][c] == "":
                    self.board[r][c] = "X"
                    if self.get_winner(self.board) == "X":
                        self.board[r][c] = ""
                        return (r, c)
                    self.board[r][c] = ""
                    
        empty = [(r, c) for r in range(3) for c in range(3) if self.board[r][c] == ""]
        return random.choice(empty) if empty else None

    def reset_game(self, total_reset=False):
        if total_reset: self.score = 0
        self.board = [["" for _ in range(3)] for _ in range(3)]
        for r in range(3):
            for c in range(3):
                self.buttons[r][c].config(text="", bg='#2d2d2d')
        self.current_player = "X"
        self.time_left = 5.0
        if not self.timer_running:
            self.start_timer()

if __name__ == "__main__":
    UltimateTicTacToe().window.mainloop()