import tkinter as tk
from tkinter import messagebox
import random

class MineSweeper:
    def __init__(self, root):
        self.root = root
        self.root.title("雷區突圍: MINE RUSH")
        self.root.configure(bg="#2C3E50")
        
        # 遊戲參數
        self.size = 8
        self.mines_count = 10
        
        # 建立 UI 框架
        self.setup_ui()
        # 初始化數據並啟動遊戲
        self.start_game()

    def setup_ui(self):
        """建立不變的 UI 元素"""
        self.info_label = tk.Label(self.root, font=('Arial', 14, 'bold'), 
                                  bg="#2C3E50", fg="#ECF0F1", pady=10)
        self.info_label.pack()

        self.grid_frame = tk.Frame(self.root, bg="#34495E", padx=5, pady=5)
        self.grid_frame.pack()

        # 預先建立按鈕矩陣
        self.buttons = [[None for _ in range(self.size)] for _ in range(self.size)]
        for r in range(self.size):
            for c in range(self.size):
                btn = tk.Button(self.grid_frame, width=3, height=1, font=('Arial', 12, 'bold'),
                                bg="#95A5A6", relief="raised")
                # 使用預設參數綁定座標
                btn.config(command=lambda row=r, col=c: self.on_left_click(row, col))
                btn.bind("<Button-2>", lambda e, row=r, col=c: self.on_right_click(row, col))
                btn.bind("<Button-3>", lambda e, row=r, col=c: self.on_right_click(row, col))
                btn.grid(row=r, column=c, padx=1, pady=1)
                self.buttons[r][c] = btn

    def start_game(self):
        """重置所有數據，恢復按鈕狀態"""
        self.game_over = False
        self.revealed = [[False for _ in range(self.size)] for _ in range(self.size)]
        self.board = [[0 for _ in range(self.size)] for _ in range(self.size)]
        
        # 1. 隨機佈雷 (確保不重複)
        all_coords = [(r, c) for r in range(self.size) for c in range(self.size)]