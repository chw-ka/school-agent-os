import tkinter as tk
import random

class Game2048:
    def __init__(self, root):
        self.root = root
        self.root.title("2048 經典美化版")
        self.grid_size = 4
        self.board = [[0] * self.grid_size for _ in range(self.grid_size)]
        self.score = 0
        
        # 色彩配置 (符合 2048 經典風格)
        self.colors = {
            0: "#CDC1B4", 2: "#EEE4DA", 4: "#EDE0C8", 8: "#F2B179",
            16: "#F59563", 32: "#F67C5F", 64: "#F65E3B", 128: "#EDCF72",
            256: "#EDCC61", 512: "#EDC850", 1024: "#EDC53F", 2048: "#EDC22E"
        }
        
        self.setup_ui()
        self.start_game()
        
        # 綁定鍵盤事件
        self.root.bind("<Key>", self.handle_keypress)

    def setup_ui(self):
        """建立遊戲介面"""
        self.main_frame = tk.Frame(self.root, bg="#BBADA0", bd=10)
        self.main_frame.grid()
        
        self.cells = []
        for r in range(self.grid_size):
            row_cells = []
            for c in range(self.grid_size):
                cell = tk.Label(self.main_frame, text="", bg="#CDC1B4",
                                font=("Verdana", 24, "bold"), width=4, height=2)
                cell.grid(row=r, column=c, padx=5, pady=5)
                row_cells.append(cell)
            self.cells.append(row_cells)

    def start_game(self):
        """初始化遊戲，隨機產生兩個數字"""
        self.board = [[0] * self.grid_size for _ in range(self.grid_size)]
        self.add_new_tile()
        self.add_new_tile()
        self.update_ui()

    def add_new_tile(self):
        """在隨機空格處產生 2 或 4"""
        empty_cells = [(r, c) for r in range(self.grid_size) for c in range(self.grid_size) if self.board[r][c] == 0]
        if empty_cells:
            r, c = random.choice(empty_cells)
            self.board[r][c] = 2 if random.random() < 0.9 else 4

    def update_ui(self):
        """根據 board 數據更新介面顏色與文字"""
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                val = self.board[r][c]
                color = self.colors.get(val, "#3C3A32")
                text_color = "#776E65" if val <= 4 else "#F9F6F2"
                self.cells[r][c].config(text=str(val) if val != 0 else "", bg=color, fg=text_color)

    def stack(self):
        """向左壓縮非零數字"""
        new_board = [[0] * self.grid_size for _ in range(self.grid_size)]
        for r in range(self.grid_size):
            fill_pos = 0
            for c in range(self.grid_size):
                if self.board[r][c] != 0:
                    new_board[r][fill_pos] = self.board[r][c]
                    fill_pos += 1
        self.board = new_board

    def combine(self):
        """向左合併相同數字"""
        for r in range(self.grid_size):
            for c in range(self.grid_size - 1):
                if self.board[r][c] != 0 and self.board[r][c] == self.board[r][c+1]:
                    self.board[r][c] *= 2
                    self.board[r][c+1] = 0
                    self.score += self.board[r][c]

    def reverse(self):
        """水平反轉 (用於