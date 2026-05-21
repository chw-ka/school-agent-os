import tkinter as tk
from tkinter import messagebox
import random
import time

class UltimateTicTacToe:
    def __init__(self, root):
        self.root = root
        self.root.title("過三關：量子消散版 🚀")
        self.root.configure(bg="#1a1a2e")
        
        # 核心邏輯變數
        self.board = [[None for _ in range(3)] for _ in range(3)]
        self.buttons = [[None for _ in range(3)] for _ in range(3)]
        
        # 追蹤標記的順序 (用於實作消失機制)
        self.history = {"X": [], "O": []} 
        self.current_player = "X"
        self.timer_val = 5
        self.game_active = True

        self.setup_ui()
        self.update_timer()

    def setup_ui(self):
        # 標題與計時器顯示
        self.info_label = tk.Label(
            self.root, text="玩家 X 的回合", font=("Microsoft JhengHei", 16, "bold"),
            bg="#16213e", fg="#e94560", pady=10
        )
        self.info_label.pack(fill="x")

        self.timer_label = tk.Label(
            self.root, text=f"剩餘時間: {self.timer_val}s", font=("Arial", 12),
            bg="#1a1a2e", fg="#0f3460"
        )
        self.timer_label.pack()

        # 棋盤容器
        self.grid_frame = tk.Frame(self.root, bg="#1a1a2e")
        self.grid_frame.pack(padx=20, pady=20)

        for r in range(3):
            for c in range(3):
                btn = tk.Button(
                    self.grid_frame, text="", font=("Verdana", 35, "bold"),
                    width=4, height=2, bg="#0f3460", fg="white",
                    relief="flat", activebackground="#16213e",
                    command=lambda r=r, c=c: self.handle_click(r, c)
                )
                btn.grid(row=r, column=c, padx=5, pady=5)
                self.buttons[r][c] = btn

    def update_timer(self):
        if self.game_active:
            if self.timer_val > 0:
                self.timer_val -= 1
                self.timer_label.config(text=f"剩餘時間: {self.timer_val}s", fg="#e94560" if self.timer_val < 3 else "#4ecca3")
                self.root.after(1000, self.update_timer)
            else:
                # 逾時懲罰：自動隨機下棋
                self.auto_move()

    def handle_click(self, r, c):
        if self.board[r][c] is None and self.game_active:
            self.execute_move(r, c, self.current_player)

    def execute_move(self, r, c, player):
        # 1. 放置新棋子
        self.board[r][c] = player
        self.history[player].append((r, c))
        
        # 2. 檢查是否超過 3 個棋子 (消失機制)
        if len(self.history[player]) > 3:
            old_r, old_c = self.history[player].pop(0)
            self.board[old_r][old_c] = None
            self.buttons[old_r][old_c].config(text="", bg="#0f3460")

        # 3. 更新即將消失的棋子視覺 (警告色)
        self.refresh_board_ui()

        # 4. 判斷勝負
        if self.check_win(player):
            self.game_over(f"玩家 {player} 獲勝！")
            return

        # 5. 切換玩家與重置計時器
        self.current_player = "O" if player == "X" else "X"
        self.info_label.config(text=f"玩家 {self.current_player} 的回合", fg="#4ecca3" if self.current_player == "O" else "#e94560")
        self.timer_val = 6 # 重置計時
        
        if self.current_player == "O":
            self.root.after(600, self.ai_smart_move)

    def refresh_board_ui(self):
        for r in range(3):
            for c in range(3):
                val = self.board[r][c]
                if val:
                    # 如果是該玩家最老的棋子，顯示半透明感/警告色
                    is_oldest = False
                    if len(self.history[val]) == 3 and (r, c) == self.history[val][0]:
                        is_oldest = True
                    
                    color = "#e94560" if val == "X" else "#4ecca3"
                    bg_color = "#533440" if is_oldest else "#16213e"
                    self.buttons[r][c].config(text=val, fg=color, bg=bg_color)
                else:
                    self.buttons[r][c].config(text="", bg="#0f3460")

    def ai_smart_move(self):
        # 簡單 AI：優先連線，否則隨機
        empty_cells = [(r, c) for r in range(3) for c in range(3) if self.board[r][c] is None]
        if empty_cells and self.game_active:
            move = random.choice(empty_cells)
            self.execute_move(move[0], move[1], "O")

    def auto_move(self):
        # 逾時處理
        if self.current_player == "X":
            empty_cells = [(r, c) for r in range(3) for c in range(3) if self.board[r][c] is None]
            if empty_cells:
                move = random.choice(empty_cells)
                self.execute_move(move[0], move[1], "X")
        self.update_timer()

    def check_win(self, p):
        for i in range(3):
            if all(self.board[i][j] == p for j in range(3)): return True
            if all(self.board[j][i] == p for j in range(3)): return True
        if all(self.board[i][i] == p for i in range(3)): return True
        if all(self.board[i][2-i] == p for i in range(3)): return True
        return False

    def game_over(self, msg):
        self.game_active = False
        messagebox.showinfo("Game Over", msg)
        self.reset_game()

    def reset_game(self):
        self.board = [[None for _ in range(3)] for _ in range(3)]
        self.history = {"X": [], "O": []}
        self.current_player = "X"
        self.timer_val = 5
        self.game_active = True
        self.refresh_board_ui()
        self.update_timer()

if __name__ == "__main__":
    root = tk.Tk()
    game = UltimateTicTacToe(root)
    root.mainloop()