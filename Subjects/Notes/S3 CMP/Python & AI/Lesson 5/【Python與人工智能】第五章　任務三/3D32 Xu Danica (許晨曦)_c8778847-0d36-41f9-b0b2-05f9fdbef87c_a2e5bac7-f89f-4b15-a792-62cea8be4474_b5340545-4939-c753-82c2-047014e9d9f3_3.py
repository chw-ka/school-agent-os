import tkinter as tk
from tkinter import messagebox
import random
import math
import time

class UltimateSnake:
    def __init__(self, root):
        self.root = root
        self.root.title("SNAKE: MULTIVERSE - GOD EDITION")
        self.root.geometry("600x850")
        self.root.configure(bg="#050505")
        self.root.resizable(False, False)
        
        self.size = 600
        self.grid = 20
        self.running = False
        self.waiting_for_start = False
        self.loop_id = None
        
        self.show_main_menu()

    def show_main_menu(self):
        # 徹底清理舊狀態
        self.running = False
        if self.loop_id:
            self.root.after_cancel(self.loop_id)
            self.loop_id = None
            
        for widget in self.root.winfo_children():
            widget.destroy()
        
        menu = tk.Frame(self.root, bg="#050505")
        menu.pack(expand=True)
        
        tk.Label(menu, text="SNAKE MULTIVERSE", fg="#00ffcc", bg="#050505", font=("Fixedsys", 40, "bold")).pack(pady=20)
        
        # 1. 模式選擇
        tk.Label(menu, text="STEP 1: SELECT MODE", fg="#888", bg="#050505", font=("Fixedsys", 12)).pack()
        self.mode_var = tk.StringVar(value="Classic")
        modes = [("普通玩法", "Classic"), ("雙生鏡面", "Twin"), ("無限傳送", "Portal"), ("黑暗迷霧", "Fog")]
        for text, val in modes:
            tk.Radiobutton(menu, text=text, variable=self.mode_var, value=val, fg="#fff", bg="#050505", 
                           selectcolor="#333", font=("Arial", 11), indicatoron=0, width=25, pady=5).pack(pady=2)

        # 2. 難度選擇
        tk.Label(menu, text="\nSTEP 2: SELECT DIFFICULTY", fg="#888", bg="#050505", font=("Fixedsys", 12)).pack()
        diffs = [("NORMAL", 150, 15), ("INSANE", 80, 10), ("GOD MODE", 45, 6)]
        for name, speed, t_limit in diffs:
            btn = tk.Button(menu, text=name, font=("Fixedsys", 16), fg="#000", bg="#00ffcc", width=20,
                           command=lambda s=speed, t=t_limit, n=name: self.setup_game(s, t, n))
            btn.pack(pady=5)

    def setup_game(self, speed, t_limit, name):
        self.mode = self.mode_var.get()
        self.difficulty_name = name
        self.base_delay = speed
        self.time_limit = t_limit
        
        for widget in self.root.winfo_children(): widget.destroy()
        
        self.canvas = tk.Canvas(self.root, width=self.size, height=self.size, bg="#000", highlightthickness=2, highlightbackground="#333")
        self.canvas.pack(pady=10)
        
        self.info_label = tk.Label(self.root, text="PRESS [ SPACE ] TO START", fg="#ff0055", bg="#050505", font=("Fixedsys", 22))
        self.info_label.pack()

        # 初始化兩條蛇的位置
        self.snake_a = [(200, 300), (180, 300), (160, 300)]
        self.snake_b = [(400, 300), (420, 300), (440, 300)] if self.mode == "Twin" else []
        
        self.direction = "Right"
        self.next_dir = "Right"
        self.score = 0
        self.current_time = self.time_limit
        self.poison = None
        self.waiting_for_start = True
        
        self.create_food()
        self.draw_scene()
        
        self.root.bind("<space>", self.start_logic)
        self.root.bind("<KeyPress>", self.handle_keys)

    def start_logic(self, event):
        if self.waiting_for_start:
            self.waiting_for_start = False
            self.running = True
            self.game_loop()
            self.countdown()

    def handle_keys(self, e):
        dists = {"Up": "Down", "Down": "Up", "Left": "Right", "Right": "Left"}
        if e.keysym in dists and e.keysym != dists.get(self.direction):
            self.next_dir = e.keysym

    def game_loop(self):
        if not self.running: return
        self.direction = self.next_dir
        
        # A 蛇移動邏輯
        hx, hy = self.snake_a[0]
        if self.direction == "Up": hy -= self.grid
        elif self.direction == "Down": hy += self.grid
        elif self.direction == "Left": hx -= self.grid
        elif self.direction == "Right": hx += self.grid
        
        if self.mode == "Portal":
            hx %= self.size
            hy %= self.size
        new_head_a = (hx, hy)

        # B 蛇鏡面邏輯
        new_head_b = None
        if self.mode == "Twin":
            bx, by = self.snake_b[0]
            b_dir = self.direction
            if b_dir == "Left": b_dir = "Right"
            elif b_dir == "Right": b_dir = "Left"
            if b_dir == "Up": by -= self.grid
            elif b_dir == "Down": by += self.grid
            elif b_dir == "Left": bx -= self.grid
            elif b_dir == "Right": bx += self.grid
            new_head_b = (bx, by)

        # 死亡判定
        if self.check_crash(new_head_a, self.snake_a) or (self.mode == "Twin" and self.check_crash(new_head_b, self.snake_b)):
            self.end_game("CRITICAL ERROR")
            return

        self.snake_a.insert(0, new_head_a)
        if self.mode == "Twin": self.snake_b.insert(0, new_head_b)

        # 吃到蘋果判定
        if new_head_a == self.food or (new_head_b and new_head_b == self.food):
            self.score += 1
            self.current_time = self.time_limit
            self.base_delay = max(35, self.base_delay - 2)
            self.create_food()
        elif self.poison and (new_head_a == self.poison or (new_head_b and new_head_b == self.poison)):
            self.score += 5
            self.base_delay = max(30, self.base_delay - 12)
            self.poison = None
        else:
            self.snake_a.pop()
            if self.mode == "Twin": self.snake_b.pop()

        self.draw_scene()
        self.loop_id = self.root.after(self.base_delay, self.game_loop)

    def check_crash(self, head, body):
        x, y = head
        if self.mode != "Portal":
            if x < 0 or x >= self.size or y < 0 or y >= self.size: return True
        return head in body

    def draw_scene(self):
        self.canvas.delete("all")
        
        # 繪製食物
        fx, fy = self.food
        self.canvas.create_rectangle(fx, fy, fx+self.grid, fy+self.grid, fill="#00ffcc", outline="#fff")
        if self.poison:
            px, py = self.poison
            self.canvas.create_rectangle(px, py, px+self.grid, py+self.grid, fill="#ff00ff", outline="#fff")

        # 繪製蛇
        for i, (x, y) in enumerate(self.snake_a):
            c = "#00ffcc" if i == 0 else "#005544"
            self.canvas.create_rectangle(x, y, x+self.grid, y+self.grid, fill=c, outline="#000")
        
        if self.mode == "Twin":
            for i, (x, y) in enumerate(self.snake_b):
                c = "#ffcc00" if i == 0 else "#665500"
                self.canvas.create_rectangle(x, y, x+self.grid, y+self.grid, fill=c, outline="#000")

        # 高級迷霧效果
        if self.mode == "Fog" and self.running:
            hx, hy = self.snake_a[0]
            # 圓形探照燈：32個點組成的平滑多邊形
            radius = 110 + math.sin(time.time() * 6) * 8
            mask_pts = [0,0, 600,0, 600,600, 0,600, 0,0]
            hole_pts = []
            for i in range(33):
                ang = i * (2 * math.pi / 32)
                hole_pts.extend([hx + 10 + radius * math.cos(-ang), hy + 10 + radius * math.sin(-ang)])
            self.canvas.create_polygon(mask_pts + hole_pts, fill="#050505", fill_rule=tk.EVENODD)

    def create_food(self):
        while True:
            self.food = (random.randint(2, 27) * self.grid, random.randint(2, 27) * self.grid)
            if self.food not in self.snake_a: break
        if random.random() < 0.2:
            self.poison = (random.randint(2, 27) * self.grid, random.randint(2, 27) * self.grid)
        else: self.poison = None

    def countdown(self):
        if not self.running: return
        if self.current_time > 0:
            self.current_time -= 1
            self.info_label.config(text=f"SCORE: {self.score:03d} | TIME: {self.current_time}s | {self.mode}")
            self.root.after(1000, self.countdown)
        else: self.end_game("TIME OVER")

    def end_game(self, msg):
        self.running = False
        self.canvas.create_rectangle(120, 220, 480, 380, fill="#111", outline="#ff0055", width=4)
        self.canvas.create_text(300, 270, text=msg, fill="#fff", font=("Fixedsys", 24))
        self.canvas.create_text(300, 320, text=f"SCORE: {self.score}", fill="#00ffcc", font=("Fixedsys", 20))
        tk.Button(self.root, text="RETRY", font=("Fixedsys", 14), bg="#00ffcc", command=self.show_main_menu).pack(pady=20)

if __name__ == "__main__":
    root = tk.Tk()
    game = UltimateSnake(root)
    root.mainloop()