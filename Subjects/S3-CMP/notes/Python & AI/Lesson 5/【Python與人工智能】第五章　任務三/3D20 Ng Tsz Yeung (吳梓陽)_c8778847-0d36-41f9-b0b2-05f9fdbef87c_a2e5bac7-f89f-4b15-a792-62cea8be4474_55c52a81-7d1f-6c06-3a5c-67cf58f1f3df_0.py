import tkinter as tk
from tkinter import messagebox
import time

class NeonChess:
    def __init__(self, root):
        self.root = root
        self.root.title("Neon Speed Chess - 極速霓虹西洋棋")
        self.root.configure(bg="#1a1a1a")

        self.turn = "White"
        self.timer_limit = 10  # 每步限時 10 秒
        self.current_time = self.timer_limit
        self.selected_piece = None
        self.board_state = {} # 儲存棋子位置

        # 初始化棋盤 (簡化標記：P=Pawn, R=Rook, N=Knight, B=Bishop, Q=Queen, K=King)
        self.setup_pieces()
        self.create_widgets()
        self.update_timer()

    def setup_pieces(self):
        # 初始化簡化的棋盤佈局
        layout = ["R", "N", "B", "Q", "K", "B", "N", "R"]
        for i, p in enumerate(layout):
            self.board_state[(0, i)] = ("Black", p)
            self.board_state[(1, i)] = ("Black", "P")
            self.board_state[(6, i)] = ("White", "P")
            self.board_state[(7, i)] = ("White", p)

    def create_widgets(self):
        # 標題與計時器
        self.info_label = tk.Label(self.root, text=f"輪到: {self.turn}", font=('Arial', 18, 'bold'), fg="#00ffcc", bg="#1a1a1a")
        self.info_label.pack(pady=10)

        self.timer_label = tk.Label(self.root, text=f"剩餘時間: {self.current_time}s", font=('Consolas', 24), fg="#ff0055", bg="#1a1a1a")
        self.timer_label.pack()

        # 棋盤容器
        self.board_frame = tk.Frame(self.root, bg="#333", padx=5, pady=5)
        self.board_frame.pack(pady=20)

        self.buttons = {}
        for r in range(8):
            for c in range(8):
                color = "#2e2e2e" if (r + c) % 2 == 0 else "#3d3d3d"
                btn = tk.Button(self.board_frame, width=4, height=2, bg=color, relief="flat",
                                font=('Arial', 16, 'bold'), command=lambda row=r, col=c: self.handle_click(row, col))
                btn.grid(row=r, column=c)
                self.buttons[(r, c)] = btn
        
        self.refresh_board()

    def refresh_board(self):
        # 根據 board_state 渲染棋子
        unicode_pieces = {
            "White": {"K": "♔", "Q": "♕", "R": "♖", "B": "♗", "N": "♘", "P": "♙"},
            "Black": {"K": "♚", "Q": "♛", "R": "♜", "B": "♝", "N": "♞", "P": "♟"}
        }
        for r in range(8):
            for c in range(8):
                piece = self.board_state.get((r, c))
                if piece:
                    color = "#ffffff" if piece[0] == "White" else "#000000"
                    self.buttons[(r, c)].config(text=unicode_pieces[piece[0]][piece[1]], fg=color)
                else:
                    self.buttons[(r, c)].config(text="", fg="white")
                
                # 恢復背景色
                base_color = "#2e2e2e" if (r + c) % 2 == 0 else "#3d3d3d"
                self.buttons[(r, c)].config(bg=base_color)

    def handle_click(self, r, c):
        piece = self.board_state.get((r, c))

        # 點擊自己的棋子 -> 選取
        if piece and piece[0] == self.turn:
            self.refresh_board() # 清除舊的高亮
            self.selected_piece = (r, c)
            self.buttons[(r, c)].config(bg="#00ffcc") # 選取特效
        
        # 已有選取棋子 -> 嘗試移動
        elif self.selected_piece:
            # 這裡簡化為：只要不是自己的棋子就能移動 (完整規則需在此加入邏輯)
            self.board_state[(r, c)] = self.board_state.pop(self.selected_piece)
            self.selected_piece = None
            self.switch_turn()

    def switch_turn(self):
        self.turn = "Black" if self.turn == "White" else "White"
        self.current_time = self.timer_limit # 重置時間
        self.info_label.config(text=f"輪到: {self.turn}", fg="#00ffcc" if self.turn == "White" else "#ffaa00")
        self.refresh_board()

    def update_timer(self):
        if self.current_time > 0:
            self.current_time -= 1
            self.timer_label.config(text=f"剩餘時間: {self.current_time}s")
            # 倒數警告閃爍
            if self.current_time <= 3:
                self.timer_label.config(fg="#ffffff" if self.current_time % 2 == 0 else "#ff0055")
            self.root.after(1000, self.update_timer)
        else:
            messagebox.showwarning("逾時！", f"{self.turn} 思考太久，直接判輸！")
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    game = NeonChess(root)
    root.mainloop()