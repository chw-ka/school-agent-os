import tkinter as tk
from tkinter import messagebox
import time

class UltimateTicTacToe:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("量子縮圈：生存過三關")
        self.window.configure(bg='#1e1e1e')
        
        # 遊戲邏輯變量
        self.current_player = "X"
        self.board = [[None for _ in range(3)] for _ in range(3)]
        self.buttons = [[None for _ in range(3)] for _ in range(3)]
        
        # 核心機制：存儲棋子的先後順序
        # 格式: [(row, col), ...]，最多只允許存 3 個，第 4 個進入時，第 1 個消失
        self.history = {"X": [], "O": []}
        
        self.timer_val = 50
        self.running = True
        
        self.create_widgets()
        self.update_timer()

    def create_widgets(self):
        # 標題與說明
        header = tk.Label(self.window, text="注意：場上每人最多存在 3 顆棋子！", 
                          fg="#00FFCC", bg="#1e1e1e", font=('Arial', 12, 'bold'))
        header.pack(pady=10)

        # 遊戲區域
        self.game_frame = tk.Frame(self.window, bg='#1e1e1e')
        self.game_frame.pack(padx=20, pady=10)

        for r in range(3):
            for c in range(3):
                btn = tk.Button(
                    self.game_frame, text="", font=('Verdana', 30, 'bold'),
                    width=4, height=1, bg="#2d2d2d", fg="white",
                    activebackground="#3d3d3d", relief="flat",
                    command=lambda row=r, col=c: self.play(row, col)
                )
                btn.grid(row=r, column=c, padx=5, pady=5)
                self.buttons[r][c] = btn

        # 進度條（模擬時間壓力）
        self.canvas = tk.Canvas(self.window, width=300, height=10, bg="#1e1e1e", highlightthickness=0)
        self.canvas.pack(pady=20)
        self.timer_bar = self.canvas.create_rectangle(0, 0, 300, 10, fill="#00FFCC")

    def update_timer(self):
        if self.running:
            self.timer_val -= 1
            width = (self.timer_val / 50) * 300
            self.canvas.coords(self.timer_bar, 0, 0, width, 10)
            
            if self.timer_val <= 0:
                self.auto_move()
            
            self.window.after(100, self.update_timer)

    def play(self, r, c):
        if self.board[r][c] is None:
            self.timer_val = 50 # 重置時間
            self.make_move(r, c)
            
            if self.check_win():
                self.running = False
                messagebox.showinfo("勝利！", f"玩家 {self.current_player} 成功存活並獲勝！")
                self.reset_game()
            else:
                self.current_player = "O" if self.current_player == "X" else "X"

    def make_move(self, r, c):
        # 1. 正常落子
        player = self.current_player
        self.board[r][c] = player
        self.history[player].append((r, c))
        
        # 2. 如果棋子超過 3 個，移除最舊的一個
        if len(self.history[player]) > 3:
            old_r, old_c = self.history[player].pop(0)
            self.board[old_r][old_c] = None
            self.buttons[old_r][old_c].config(text="", bg="#2d2d2d")

        # 3. 更新 UI
        self.refresh_board()

    def refresh_board(self):
        for r in range(3):
            for c in range(3):
                val = self.board[r][c]
                if val:
                    # 快要消失的棋子（最舊的）顏色變淡
                    is_oldest = False
                    if (r, c) == self.history[val][0] and len(self.history[val]) == 3:
                        is_oldest = True
                    
                    color = "#FF3366" if val == "X" else "#33CCFF"
                    bg_color = "#442222" if is_oldest else "#2d2d2d"
                    
                    self.buttons[r][c].config(text=val, fg=color, bg=bg_color)
                else:
                    self.buttons[r][c].config(text="", bg="#2d2d2d")

    def auto_move(self):
        # 超時自動落子邏輯
        empty_cells = [(r, c) for r in range(3) for c in range(3) if self.board[r][c] is None]
        if empty_cells:
            r, c = random.choice(empty_cells) if 'random' in globals() else empty_cells[0]
            self.play(r, c)

    def check_win(self):
        b = self.board
        lines = ([[b[i][0], b[i][1], b[i][2]] for i in range(3)] +
                 [[b[0][i], b[1][i], b[2][i]] for i in range(3)] +
                 [[b[0][0], b[1][1], b[2][2]], [b[0][2], b[1][1], b[2][0]]])
        return [self.current_player]*3 in lines

    def reset_game(self):
        self.board = [[None for _ in range(3)] for _ in range(3)]
        self.history = {"X": [], "O": []}
        self.current_player = "X"
        self.timer_val = 50
        self.running = True
        self.refresh_board()

if __name__ == "__main__":
    import random
    app = UltimateTicTacToe()
    app.window.mainloop()