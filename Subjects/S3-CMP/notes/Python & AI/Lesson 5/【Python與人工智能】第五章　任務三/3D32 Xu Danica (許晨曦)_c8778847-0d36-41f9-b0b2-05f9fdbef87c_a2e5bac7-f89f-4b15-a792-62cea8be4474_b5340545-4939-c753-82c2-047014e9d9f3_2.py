import tkinter as tk
from tkinter import messagebox
import random

class UltimateSnake:
    def __init__(self, root):
        self.root = root
        self.root.title("SNAKE: APOCALYPSE V2")
        self.root.geometry("600x750")
        self.root.configure(bg="#050505")
        
        self.size = 600
        self.grid = 20
        self.canvas = None
        self.running = False
        self.waiting_for_start = False
        
        self.show_menu()

    def show_menu(self):
        # 清除舊組件
        for widget in self.root.winfo_children():
            widget.destroy()
            
        self.menu_frame = tk.Frame(self.root, bg="#050505")
        self.menu_frame.pack(expand=True)
        
        tk.Label(self.menu_frame, text="SNAKE APOCALYPSE", fg="#ff0055", bg="#050505", 
                 font=("Fixedsys", 40, "bold")).pack(pady=20)
        
        levels = [("NORMAL", 150, 10), ("INSANE", 80, 7), ("GOD MODE", 50, 5)]
        for name, speed, t_limit in levels:
            btn = tk.Button(self.menu_frame, text=name, font=("Fixedsys", 18), 
                           fg="#00ffcc", bg="#111", width=15, cursor="hand2",
                           command=lambda s=speed, t=t_limit, n=name: self.setup_game(s, t, n))
            btn.pack(pady=10)

    def setup_game(self, speed, t_limit, name):
        self.menu_frame.destroy()
        
        self.difficulty_name = name
        self.base_delay = speed
        self.time_limit = t_limit
        
        # 建立遊戲畫布
        self.canvas = tk.Canvas(self.root, width=self.size, height=self.size, bg="#000", highlightthickness=2, highlightbackground="#333")
        self.canvas.pack(pady=10)
        
        self.info_label = tk.Label(self.root, text="PRESS [ SPACE ] TO START", fg="#ff0055", bg="#050505", font=("Fixedsys", 20))
        self.info_label.pack()

        # 初始化數據
        self.snake = [(300, 300), (280, 300), (260, 300)]
        self.direction = "Right"
        self.next_dir = "Right"
        self.score = 0
        self.current_time = self.time_limit
        self.poison = None
        self.running = False
        self.waiting_for_start = True
        
        self.draw_snake()
        self.create_food()
        self.root.bind("<space>", self.start_logic)
        self.root.bind("<KeyPress>", self.handle_keys)

    def start_logic(self, event):
        if self.waiting_for_start:
            self.waiting_for_start = False
            self.running = True
            self.info_label.config(fg="#fff", font=("Fixedsys", 14))
            self.game_loop()
            self.countdown()

    def handle_keys(self, e):
        dists = {"Up": "Down", "Down": "Up", "Left": "Right", "Right": "Left"}
        if e.keysym in dists and e.keysym != dists.get(self.direction):
            self.next_dir = e.keysym

    def create_food(self):
        self.canvas.delete("food", "poison")
        # 建立蘋果
        fx, fy = self.rand_pos()
        self.food = (fx, fy)
        self.canvas.create_rectangle(fx, fy, fx+self.grid, fy+self.grid, fill="#ff0055", outline="#fff", tag="food")
        
        # 30% 機率產生毒蘋果
        if random.random() < 0.3:
            px, py = self.rand_pos()
            self.poison = (px, py)
            self.canvas.create_rectangle(px, py, px+self.grid, py+self.grid, fill="#9b59b6", outline="#fff", tag="poison")
        else:
            self.poison = None

    def rand_pos(self):
        return (random.randint(1, (self.size//self.grid)-2) * self.grid,
                random.randint(1, (self.size//self.grid)-2) * self.grid)

    def countdown(self):
        if not self.running: return
        if self.current_time > 0:
            self.current_time -= 1
            self.update_ui()
            self.root.after(1000, self.countdown)
        else:
            self.end_game("TIME EXPIRED!")

    def game_loop(self):
        if not self.running: return
        
        self.direction = self.next_dir
        hx, hy = self.snake[0]
        if self.direction == "Up": hy -= self.grid
        elif self.direction == "Down": hy += self.grid
        elif self.direction == "Left": hx -= self.grid
        elif self.direction == "Right": hx += self.grid
        
        new_head = (hx, hy)
        
        if (hx < 0 or hx >= self.size or hy < 0 or hy >= self.size or new_head in self.snake):
            self.end_game("SYSTEM CRASHED")
            return

        self.snake.insert(0, new_head)

        # 判定碰撞
        if new_head == self.food:
            self.score += 1
            self.current_time = self.time_limit
            self.base_delay = max(30, self.base_delay - 3)
            self.create_food()
        elif self.poison and new_head == self.poison:
            # 毒蘋果懲罰：瞬間變長 3 節，速度暴增
            self.score += 5
            self.base_delay = max(25, self.base_delay - 15)
            self.poison = None
            self.canvas.delete("poison")
            # 不 pop() 尾巴，讓它直接長大
        else:
            self.snake.pop()

        self.draw_snake()
        self.root.after(self.base_delay, self.game_loop)

    def draw_snake(self):
        self.canvas.delete("body")
        for i, (x, y) in enumerate(self.snake):
            color = "#00ffcc" if i == 0 else "#005544"
            if self.difficulty_name == "GOD MODE":
                color = random.choice(["#00ffcc", "#ff0055"])
            self.canvas.create_rectangle(x, y, x+self.grid, y+self.grid, fill=color, outline="#000", tag="body")

    def update_ui(self):
        self.info_label.config(text=f"SCORE: {self.score:03d} | TIME: {self.current_time}s | MODE: {self.difficulty_name}")

    def end_game(self, msg):
        self.running = False
        # 顯示結束 UI 與返回按鈕
        self.canvas.create_rectangle(150, 200, 450, 400, fill="#111", outline="#ff0055", width=3)
        self.canvas.create_text(300, 260, text=msg, fill="white", font=("Fixedsys", 25))
        self.canvas.create_text(300, 300, text=f"FINAL SCORE: {self.score}", fill="#00ffcc", font=("Fixedsys", 18))
        
        return_btn = tk.Button(self.root, text="RETURN TO MENU", font=("Fixedsys", 14), 
                             fg="#000", bg="#00ffcc", command=self.show_menu)
        self.info_label.destroy()
        return_btn.pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    game = UltimateSnake(root)
    root.mainloop()