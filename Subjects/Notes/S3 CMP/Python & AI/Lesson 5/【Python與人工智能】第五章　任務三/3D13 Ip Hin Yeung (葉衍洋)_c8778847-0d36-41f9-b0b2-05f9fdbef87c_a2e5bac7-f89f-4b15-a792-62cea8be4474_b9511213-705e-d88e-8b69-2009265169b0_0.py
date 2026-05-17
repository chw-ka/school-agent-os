import tkinter as tk
import random
from tkinter import messagebox
import time

# --- 遊戲設定 ---
SHAPES = {
    'I': [[1, 1, 1, 1]],
    'O': [[1, 1], [1, 1]],
    'T': [[0, 1, 0], [1, 1, 1]],
    'S': [[0, 1, 1], [1, 1, 0]],
    'Z': [[1, 1, 0], [0, 1, 1]],
    'J': [[1, 0, 0], [1, 1, 1]],
    'L': [[0, 0, 1], [1, 1, 1]]
}

COLORS = {
    'I': '#00f0f0', 'O': '#f0f000', 'T': '#a000f0',
    'S': '#00f000', 'Z': '#f00000', 'J': '#0000f0', 'L': '#f0a000'
}

class BalancedTetris:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Tetris Pro - Balanced")
        
        # 核心參數
        self.rows, self.cols = 20, 10
        self.size = 30
        self.score = 0
        self.level = 1
        self.lines_cleared_total = 0
        self.start_time = time.time()
        
        self.board = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        
        # 操控緩衝與靈敏度
        self.pressed_keys = set()
        self.last_input_time = 0
        self.input_delay = 0.15  # 適中的按鍵靈敏度
        
        self.setup_ui()
        
        # 初始方塊生成
        self.next_type = random.choice(list(SHAPES.keys()))
        self.spawn_piece()
        
        # 綁定按鍵
        self.root.bind("<KeyPress>", self.on_key_press)
        self.root.bind("<KeyRelease>", self.on_key_release)
        self.root.bind("<space>", lambda _: self.hard_drop())
        self.root.bind("<Up>", lambda _: self.rotate()) # 旋轉設為單次觸發

        self.update_timer()
        self.handle_input()
        self.run()

    def setup_ui(self):
        self.root.configure(bg='#121212')
        main_frame = tk.Frame(self.root, bg='#121212')
        main_frame.pack(padx=20, pady=20)

        # 遊戲主畫布
        self.canvas = tk.Canvas(main_frame, width=self.cols*self.size, height=self.rows*self.size, 
                                bg='#000000', highlightthickness=1, highlightbackground="#444")
        self.canvas.pack(side=tk.LEFT)

        # 右側側邊欄
        side_bar = tk.Frame(main_frame, bg='#121212', padx=20)
        side_bar.pack(side=tk.LEFT, fill=tk.Y)

        tk.Label(side_bar, text="NEXT PIECE", fg="white", bg="#121212", font=("Arial", 12, "bold")).pack()
        self.preview_canvas = tk.Canvas(side_bar, width=120, height=120, bg='#000', highlightthickness=1)
        self.preview_canvas.pack(pady=10)

        self.info_label = tk.Label(side_bar, text="", fg="#00FF00", bg="#121212", font=("Consolas", 14), justify=tk.LEFT)
        self.info_label.pack(pady=20)

    def on_key_press(self, event):
        self.pressed_keys.add(event.keysym)

    def on_key_release(self, event):
        if event.keysym in self.pressed_keys:
            self.pressed_keys.remove(event.keysym)

    def handle_input(self):
        """處理持續移動指令"""
        now = time.time()
        if now - self.last_input_time > self.input_delay:
            if "Left" in self.pressed_keys: self.move(0, -1)
            if "Right" in self.pressed_keys: self.move(0, 1)
            if "Down" in self.pressed_keys: self.drop()
            self.last_input_time = now
        self.root.after(30, self.handle_input)

    def draw_block(self, canvas, r, c, color, is_ghost=False):
        """繪製方塊（修正後的版本，無 alpha 參數）"""
        x1, y1 = c * self.size, r * self.size
        x2, y2 = x1 + self.size, y1 + self.size
        
        if is_ghost:
            canvas.create_rectangle(x1+4, y1+4, x2-4, y2-4, outline=color, width=1, dash=(2, 2))
        else:
            canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#222")
            # 加入立體高光線
            canvas.create_line(x1+2, y1+2, x2-2, y1+2, fill="#ffffff")
            canvas.create_line(x1+2, y1+2, x1+2, y2-2, fill="#ffffff")

    def spawn_piece(self):
        self.current_type = self.next_type
        self.current_piece = SHAPES[self.current_type]
        self.current_color = COLORS[self.current_type]
        self.next_type = random.choice(list(SHAPES.keys()))
        
        self.piece_pos = [0, self.cols // 2 - len(self.current_piece[0]) // 2]
        
        if not self.is_valid(self.piece_pos, self.current_piece):
            messagebox.showinfo("Game Over", f"遊戲結束！\n得分: {self.score}")
            self.root.destroy()
        
        self.draw_preview()
        self.draw_all()

    def draw_preview(self):
        self.preview_canvas.delete("all")
        shape = SHAPES[self.next_type]
        color = COLORS[self.next_type]
        for r, row in enumerate(shape):
            for c, val in enumerate(row):
                if val:
                    self.draw_block(self.preview_canvas, r+1, c+1, color)

    def is_valid(self, pos, piece):
        for r, row in enumerate(piece):
            for c, val in enumerate(row):
                if val:
                    nr, nc = pos[0] + r, pos[1] + c
                    if nr >= self.rows or nc < 0 or nc >= self.cols or (nr >= 0 and self.board[nr][nc]):
                        return False
        return True

    def rotate(self):
        rotated = [list(r) for r in zip(*self.current_piece[::-1])]
        if self.is_valid(self.piece_pos, rotated):
            self.current_piece = rotated
            self.draw_all()

    def move(self, dr, dc):
        if self.is_valid([self.piece_pos[0] + dr, self.piece_pos[1] + dc], self.current_piece):
            self.piece_pos[0] += dr
            self.piece_pos[1] += dc
            self.draw_all()
            return True
        return False

    def hard_drop(self):
        while self.move(1, 0): pass
        self.drop()

    def drop(self):
        if not self.move(1, 0):
            for r, row in enumerate(self.current_piece):
                for c, val in enumerate(row):
                    if val:
                        self.board[self.piece_pos[0] + r][self.piece_pos[1] + c] = self.current_color
            self.clear_lines()
            self.spawn_piece()
        self.draw_all()

    def clear_lines(self):
        full_rows = [i for i, row in enumerate(self.board) if all(cell is not None for cell in row)]
        for i in full_rows:
            del self.board[i]
            self.board.insert(0, [None for _ in range(self.cols)])
        
        num = len(full_rows)
        if num > 0:
            self.lines_cleared_total += num
            self.score += {1: 100, 2: 300, 3: 500, 4: 800}[num] * self.level
            self.level = (self.lines_cleared_total // 10) + 1

    def draw_all(self):
        self.canvas.delete("all")
        # 繪製已固定方塊
        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c]:
                    self.draw_block(self.canvas, r, c, self.board[r][c])
        # 繪製投影
        gp = self.piece_pos[0]
        while self.is_valid([gp + 1, self.piece_pos[1]], self.current_piece):
            gp += 1
        for r, row in enumerate(self.current_piece):
            for c, val in enumerate(row):
                if val:
                    self.draw_block(self.canvas, gp+r, self.piece_pos[1]+c, self.current_color, True)
        # 繪製活動方塊
        for r, row in enumerate(self.current_piece):
            for c, val in enumerate(row):
                if val:
                    self.draw_block(self.canvas, self.piece_pos[0]+r, self.piece_pos[1]+c, self.current_color)

    def update_timer(self):
        elapsed = int(time.time() - self.start_time)
        self.info_label.config(text=f"SCORE: {self.score}\nLEVEL: {self.level}\nTIME: {elapsed}s")
        self.root.after(1000, self.update_timer)

    def run(self):
        self.drop()
        # 速度隨等級加快
        speed = max(80, 450 - (self.level - 1) * 60)
        self.root.after(speed, self.run)

if __name__ == "__main__":
    win = tk.Tk()
    game = BalancedTetris(win)
    win.mainloop()