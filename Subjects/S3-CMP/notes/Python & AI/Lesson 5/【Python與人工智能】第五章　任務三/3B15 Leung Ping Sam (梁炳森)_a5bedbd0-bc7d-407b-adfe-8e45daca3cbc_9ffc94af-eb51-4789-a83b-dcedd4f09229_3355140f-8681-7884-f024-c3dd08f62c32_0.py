import tkinter as tk
from tkinter import messagebox
import random

class TicTacToeCombo:
    def __init__(self, root):
        self.root = root
        self.root.title("過三關：連擊加倍版")
        
        # 遊戲數據
        self.player = "X"
        self.computer = "O"
        self.board = [""] * 9
        self.score = 0
        self.combo = 0
        self.game_active = True
        
        self.create_widgets()

    def create_widgets(self):
        # 分數顯示區
        self.info_frame = tk.Frame(self.root)
        self.info_frame.pack(pady=10)
        
        self.score_label = tk.Label(self.info_frame, text=f"總分: {self.score}", font=('Arial', 12, 'bold'))
        self.score_label.grid(row=0, column=0, padx=20)
        
        self.combo_label = tk.Label(self.info_frame, text=f"連擊: x{self.combo}", font=('Arial', 12, 'bold'), fg="red")
        self.combo_label.grid(row=0, column=1, padx=20)

        # 棋盤區
        self.grid_frame = tk.Frame(self.root)
        self.grid_frame.pack()
        
        self.buttons = []
        for i in range(9):
            btn = tk.Button(self.grid_frame, text="", font=('Arial', 20, 'bold'), width=5, height=2,
                            command=lambda i=i: self.player_move(i))
            btn.grid(row=i//3, column=i%3, padx=2, pady=2)
            self.buttons.append(btn)

    def player_move(self, index):
        if self.board[index] == "" and self.game_active:
            self.make_move(index, self.player)
            
            # 若玩家未獲勝且還有空格，換電腦
            if self.game_active and "" in self.board:
                self.root.after(400, self.computer_move)

    def computer_move(self):
        if not self.game_active: return
        
        empty_indices = [i for i, val in enumerate(self.board) if val == ""]
        if empty_indices:
            move = random.choice(empty_indices)
            self.make_move(move, self.computer)

    def make_move(self, index, char):
        self.board[index] = char
        color = "#2196F3" if char == "X" else "#F44336"
        self.buttons[index].config(text=char, fg=color)
        
        winner = self.check_winner()
        if winner:
            self.handle_end(winner)
        elif "" not in self.board:
            self.handle_end("draw")

    def check_winner(self):
        wins = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
        for a, b, c in wins:
            if self.board[a] == self.board[b] == self.board[c] != "":
                for i in [a, b, c]: self.buttons[i].config(bg="#FFF176") # 贏家格子變色
                return self.board[a]
        return None

    def handle_end(self, result):
        self.game_active = False
        if result == self.player:
            self.combo += 1
            points = 100 * self.combo
            self.score += points
            msg = f"你贏了！\n獲得分數: {points}\n目前連擊: {self.combo}"
        elif result == "draw":
            self.combo = 0
            msg = "平手！連擊中斷。"
        else:
            self.combo = 0
            msg = "電腦贏了！連擊中斷。"

        self.update_labels()
        messagebox.showinfo("遊戲結束", msg)
        self.reset_board()

    def update_labels(self):
        self.score_label.config(text=f"總分: {self.score}")
        self.combo_label.config(text=f"連擊: x{self.combo}")

    def reset_board(self):
        self.board = [""] * 9
        self.game_active = True
        for btn in self.buttons:
            btn.config(text="", bg="SystemButtonFace")

if __name__ == "__main__":
    root = tk.Tk()
    app = TicTacToeCombo(root)
    root.mainloop()