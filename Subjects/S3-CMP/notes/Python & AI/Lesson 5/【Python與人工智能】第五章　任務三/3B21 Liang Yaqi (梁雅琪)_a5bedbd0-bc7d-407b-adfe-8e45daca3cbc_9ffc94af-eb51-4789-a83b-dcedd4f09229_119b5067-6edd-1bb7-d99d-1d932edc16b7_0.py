
import tkinter as tk
from tkinter import messagebox
import random

class UltimateTicTacToe:
    def __init__(self, root):
        self.root = root
        self.root.title("🔥 極限過三關：3秒生存戰 🔥")
        self.root.configure(bg="#2c3e50")
        
        # 核心數據：二維列表棋盤
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.buttons = [[None for _ in range(3)] for _ in range(3)]
        
        self.timer_seconds = 3
        self.timer_job = None
        self.game_over = False
        
        self.create_widgets()
        self.start_timer()

    def create_widgets(self):
        """建立介面組件"""
        # 頂部狀態欄
        self.label = tk.Label(
            self.root, text=f"⏳ 剩餘時間: {self.timer_seconds}s", 
            font=('Microsoft JhengHei', 18, 'bold'), 
            bg="#2c3e50", fg="#ecf0f1"
        )
        self.label.pack(pady=15)

        # 棋盤容器 (使用 Frame)
        grid_frame = tk.Frame(self.root, bg="#34495e", padx=10, pady=10)
        grid_frame.pack(pady=10)

        for r in range(3):
            for c in range(3):
                btn = tk.Button(
                    grid_frame, text="", font=('Arial', 24, 'bold'), 
                    width=4, height=2, bg="#ecf0f1", relief="flat",
                    command=lambda row=r, col=c: self.player_move(row, col)
                )
                btn.grid(row=r, column=c, padx=5, pady=5)
                self.buttons[r][c] = btn

    def start_timer(self):
        """倒數計時核心邏輯"""
        if self.game_over:
            return
        
        if self.timer_seconds > 0:
            self.label.config(text=f"⏱️ 快點下棋！ {self.timer_seconds}s", fg="#e74c3c")
            self.timer_seconds -= 1
            # 每 1000 毫秒 (1秒) 呼叫一次自己
            self.timer_job = self.root.after(1000, self.start_timer)
        else:
            self.label.config(text="⌛ 時間到！系統隨機出棋！")
            self.punishment_move()

    def punishment_move(self):
        """當玩家逾時，電腦強迫幫玩家下一子"""
        empty_cells = [(r, c) for r in range(3) for c in range(3) if self.board[r][c] == ""]
        if empty_cells:
            r, c = random.choice(empty_cells)
            self.make_move(r, c, "X")
            if not self.game_over:
                self.root.after(500, self.computer_move)

    def player_move(self, row, col):
        """玩家點擊處理"""
        if self.board[row][col] == "" and not self.game_over:
            # 玩家下棋，立刻停止計時
            if self.timer_job:
                self.root.after_cancel(self.timer_job)
            
            self.make_move(row, col, "X")
            
            # 如果遊戲沒結束，換電腦下
            if not self.game_over:
                self.root.after(400, self.computer_move)

    def computer_move(self):
        """電腦隨機下棋"""
        if self.game_over:
            return
            
        empty_cells = [(r, c) for r in range(3) for c in range(3) if self.board[r][c] == ""]
        if empty_cells:
            r, c = random.choice(empty_cells)
            self.make_move(r, c, "O")
            
            # 電腦下完後，重啟玩家的 3 秒計時
            if not self.game_over:
                self.timer_seconds = 3
                self.start_timer()

    def make_move(self, row, col, player):
        """執行下棋、視覺更新與勝負判定"""
        self.board[row][col] = player
        
        # 區分顏色
        if player == "X":
            self.buttons[row][col].config(text=player, fg="white", bg="#3498db")
        else:
            self.buttons[row][col].config(text=player, fg="white", bg="#e67e22")
        
        # 勝負判定
        if self.check_winner(row, col):
            self.game_over = True
            if self.timer_job:
                self.root.after_cancel(self.timer_job)
            msg = "🏆 勝利！反應很快喔！" if player == "X" else "💀 輸了...反應太慢啦！"
            messagebox.showinfo("戰鬥結果", msg)
            self.reset_game()
        elif self.check_draw():
            self.game_over = True
            messagebox.showinfo("戰鬥結果", "🤝 平手！英雄所見略同。")
            self.reset_game()

    def check_winner(self, r, c):
        p = self.board[r][c]
        # 檢查橫向、縱向、兩條對角線
        if all(self.board[r][i] == p for i in range(3)): return True
        if all(self.board[i][c] == p for i in range(3)): return True
        if r == c and all(self.board[i][i] == p for i in range(3)): return True
        if r + c == 2 and all(self.board[i][2-i] == p for i in range(3)): return True
        return False

    def check_draw(self):
        return all(self.board[r][c] != "" for r in range(3) for c in range(3))

    def reset_game(self):
        """歸零重啟"""
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.game_over = False
        self.timer_seconds = 3
        for r in range(3):
            for c in range(3):
                self.buttons[r][c].config(text="", bg="#ecf0f1")
        self.start_timer()

if __name__ == "__main__":
    root = tk.Tk()
    root.resizable(False, False)
    game = UltimateTicTacToe(root)
    root.mainloop()