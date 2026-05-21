import tkinter as tk
from tkinter import messagebox, ttk
import random

class SudokuMinimax(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("數獨 - Minimax 解題演算法")
        self.geometry("500x600")
        self.resizable(False, False)
        self.configure(bg="#f0f0f0")

        self.board = [[0]*9 for _ in range(9)]
        self.fixed = [[False]*9 for _ in range(9)]
        self.entries = [[None]*9 for _ in range(9)]

        tk.Label(self, text="數獨遊戲", font=("Arial",20,"bold"), bg="#f0f0f0").pack(pady=10)

        # 棋盤外框
        frame = tk.Frame(self, bg="#222", padx=3, pady=3)
        frame.pack(pady=10)

        for r in range(9):
            for c in range(9):
                bg = "#ffffff" if (r//3 + c//3) % 2 == 0 else "#f8f8f8"
                e = tk.Entry(
                    frame, width=2, font=("Arial",22,"bold"), justify="center",
                    bg=bg, fg="#000088"
                )
                e.grid(row=r, column=c, padx=1, pady=1)
                self.entries[r][c] = e

        # 按鈕列
        btn_f = tk.Frame(self, bg="#f0f0f0")
        btn_f.pack(pady=10)
        ttk.Button(btn_f, text="新題目", command=self.new_puzzle).grid(row=0,column=0,padx=5)
        ttk.Button(btn_f, text="Minimax 解題", command=self.solve_sudoku).grid(row=0,column=1,padx=5)
        ttk.Button(btn_f, text="清空", command=self.clear).grid(row=0,column=2,padx=5)

        self.new_puzzle()

    def is_valid(self, b, r, c, num):
        for i in range(9):
            if b[r][i] == num: return False
        for i in range(9):
            if b[i][c] == num: return False
        sr, sc = r//3*3, c//3*3
        for i in range(3):
            for j in range(3):
                if b[sr+i][sc+j] == num: return False
        return True

    # Minimax / 回溯解數獨核心
    def minimax_solve(self, b):
        for r in range(9):
            for c in range(9):
                if b[r][c] == 0:
                    for num in range(1,10):
                        if self.is_valid(b, r, c, num):
                            b[r][c] = num
                            if self.minimax_solve(b):
                                return True
                            b[r][c] = 0
                    return False
        return True

    def solve_sudoku(self):
        copy = [row[:] for row in self.board]
        if self.minimax_solve(copy):
            for r in range(9):
                for c in range(9):
                    if not self.fixed[r][c]:
                        self.entries[r][c].delete(0,"end")
                        self.entries[r][c].insert(0, str(copy[r][c]))
            messagebox.showinfo("完成", "Minimax 解題成功！")
        else:
            messagebox.showwarning("錯誤", "無解")

    def generate_full(self):
        b = [[0]*9 for _ in range(9)]
        self.minimax_solve(b)
        return b

    def new_puzzle(self):
        sol = self.generate_full()
        self.board = sol
        for r in range(9):
            for c in range(9):
                self.fixed[r][c] = True
        for _ in range(45):
            r = random.randint(0,8)
            c = random.randint(0,8)
            self.board[r][c] = 0
            self.fixed[r][c] = False
        self.update_grid()

    def update_grid(self):
        for r in range(9):
            for c in range(9):
                e = self.entries[r][c]
                e.config(state="normal")
                e.delete(0,"end")
                if self.board[r][c] != 0:
                    e.insert(0, str(self.board[r][c]))
                e.config(fg="blue" if self.fixed[r][c] else "black")

    def clear(self):
        for r in range(9):
            for c in range(9):
                if not self.fixed[r][c]:
                    self.entries[r][c].delete(0,"end")

if __name__ == "__main__":
    app = SudokuMinimax()
    app.mainloop()