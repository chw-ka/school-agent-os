import tkinter as tk
from tkinter import messagebox
import time

class CyberTicTacToe:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic-Tac-Toe: Cyber Strike")
        self.root.geometry("450x650")
        self.root.configure(bg='#0f0c29') # 深夜霓虹底色
        
        self.player_hp = {"X": 3, "O": 3}
        self.current_player = "X"
        self.board = [[None for _ in range(3)] for _ in range(3)]
        self.buttons = [[None for _ in range(3)] for _ in range(3)]
        
        self.timer_limit = 5.0
        self.start_time = time.time()
        self.combo = 0
        self.last_move_time = 0
        
        self.create_widgets()
        self.update_clock()

    def create_widgets(self):
        # 標題與狀態欄
        self.header = tk.Label(self.root, text="CYBER STRIKE", font=('Courier', 30, 'bold'), 
                              fg='#00d2ff', bg='#0f0c29', pady=20)
        self.header.pack()

        self.info_frame = tk.Frame(self.root, bg='#0f0c29')
        self.info_frame.pack(fill='x', padx=20)

        self.hp_label = tk.Label(self.info_frame, text=f"X: {'❤️'*3}  VS  O: {'💙'*3}", 
                                font=('Arial', 14), fg='#ffffff', bg='#0f0c29')
        self.hp_label.pack(side=tk.LEFT)

        self.combo_label = tk.Label(self.info_frame, text="Combo: 0", font=('Arial', 14), 
                                   fg='#f8ff00', bg='#0f0c29')
        self.combo_label.pack(side=tk.RIGHT)

        # 倒計時條
        self.canvas = tk.Canvas(self.root, width=400, height=10, bg="#1a1a2e", highlightthickness=0)
        self.canvas.pack(pady=20)
        self.timer_bar = self.canvas.create_rectangle(0, 0, 400, 10, fill="#00ff41")

        # 棋盤
        self.game_frame = tk.Frame(self.root, bg='#0f0c29')
        self.game_frame.pack(pady=10)

        for r in range(3):
            for c in range(3):
                btn = tk.Button(
                    self.game_frame, text="", font=('Verdana', 35, 'bold'), 
                    width=4, height=1, bg='#16213e', fg='#ffffff',
                    activebackground='#0f3460', borderwidth=0,
                    command=lambda r=r, c=c: self.handle_click(r, c)
                )
                btn.grid(row=r, column=c, padx=5, pady=5)
                self.buttons[r][c] = btn

    def update_clock(self):
        elapsed = time.time() - self.start_time
        remaining = max(0, self.timer_limit - elapsed)
        
        # 更新計時條長度和顏色
        width = (remaining / self.timer_limit) * 400
        color = "#ff4d4d" if remaining < 2 else "#00ff41"
        self.canvas.coords(self.timer_bar, 0, 0, width, 10)
        self.canvas.itemconfig(self.timer_bar, fill=color)

        if remaining <= 0:
            self.timeout()
        else:
            self.root.after(50, self.update_clock)

    def handle_click(self, r, c):
        if self.board[r][c] is not None: return

        # Combo 邏輯：2秒內下棋連擊加1
        now = time.time()
        if now - self.last_move_time < 2.0:
            self.combo += 1
        else:
            self.combo = 0
        self.last_move_time = now
        self.combo_label.config(text=f"Combo: {self.combo}")

        # 下棋動作
        self.board[r][c] = self.current_player
        btn_color = "#00d2ff" if self.current_player == "X" else "#9d50bb"
        self.buttons[r][c].config(text=self.current_player, fg=btn_color, bg='#1a1a2e')
        
        if self.check_winner():
            self.process_win(self.current_player)
        elif self.is_draw():
            self.process_draw()
        else:
            self.switch_player()

    def switch_player(self):
        self.current_player = "O" if self.current_player == "X" else "X"
        self.start_time = time.time() # 重置計時器

    def timeout(self):
        messagebox.showwarning("超時！", f"玩家 {self.current_player} 思考太久，扣除 1 點生命值！")
        self.lose_hp(self.current_player)

    def lose_hp(self, player):
        self.player_hp[player] -= 1
        self.update_ui()
        if self.player_hp[player] <= 0:
            messagebox.showinfo("Game Over", f"最終贏家是: {'X' if player == 'O' else 'O'}!")
            self.full_reset()
        else:
            self.reset_round()

    def process_win(self, winner):
        messagebox.showinfo("圓滿收工", f"玩家 {winner} 達成擊殺！(Combo: {self.combo})")
        loser = "O" if winner == "X" else "X"
        self.lose_hp(loser)

    def process_draw(self):
        messagebox.showinfo("平手", "雙方格擋成功，不扣血！")
        self.reset_round()

    def update_ui(self):
        self.hp_label.config(text=f"X: {'❤️'*self.player_hp['X']}  VS  O: {'💙'*self.player_hp['O']}")

    def check_winner(self):
        # 這裡復用之前的判斷邏輯
        b = self.board
        p = self.current_player
        for i in range(3):
            if all(b[i][j] == p for j in range(3)) or all(b[j][i] == p for j in range(3)): return True
        if b[0][0] == b[1][1] == b[2][2] == p or b[0][2] == b[1][1] == b[2][0] == p: return True
        return False

    def is_draw(self):
        return all(self.board[r][c] is not None for r in range(3) for c in range(3))

    def reset_round(self):
        self.board = [[None for _ in range(3)] for _ in range(3)]
        for r in range(3):
            for c in range(3):
                self.buttons[r][c].config(text="", bg='#16213e')
        self.start_time = time.time()
        self.combo = 0
        self.combo_label.config(text="Combo: 0")

    def full_reset(self):
        self.player_hp = {"X": 3, "O": 3}
        self.update_ui()
        self.reset_round()

if __name__ == "__main__":
    root = tk.Tk()
    game = CyberTicTacToe(root)
    root.mainloop()