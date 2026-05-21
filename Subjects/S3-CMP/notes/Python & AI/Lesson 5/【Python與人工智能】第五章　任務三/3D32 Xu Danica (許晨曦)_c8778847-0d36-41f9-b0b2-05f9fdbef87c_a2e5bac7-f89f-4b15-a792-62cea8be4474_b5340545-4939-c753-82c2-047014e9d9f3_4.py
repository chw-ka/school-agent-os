import tkinter as tk
import random

class UltimateSnakeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("SNAKE: THE ULTIMATE EDITION")
        self.root.geometry("600x850")
        self.root.configure(bg="#050505")
        
        self.size = 600
        self.grid = 20
        self.running = False
        self.waiting_for_start = False
        self.show_main_menu()

    def show_main_menu(self):
        for widget in self.root.winfo_children(): widget.destroy()
        
        menu = tk.Frame(self.root, bg="#050505")
        menu.pack(expand=True)
        
        tk.Label(menu, text="SNAKE ULTIMATE", fg="#00ffcc", bg="#050505", font=("Fixedsys", 40, "bold")).pack(pady=20)
        
        # --- 模式選擇 ---
        tk.Label(menu, text="STEP 1: SELECT MODE", fg="#888", bg="#050505", font=("Fixedsys", 12)).pack()
        self.mode_var = tk.StringVar(value="Classic")
        modes = [("普通玩法", "Classic"), ("雙生鏡面", "Twin"), ("傳送門", "Portal"), ("黑暗迷霧", "Fog")]
        for text, val in modes:
            tk.Radiobutton(menu, text=text, variable=self.mode_var, value=val, fg="#fff", bg="#050505", 
                           selectcolor="#333", font=("Arial", 12), indicatoron=0, width=20, pady=5).pack(pady=2)

        # --- 難度選擇 ---
        tk.Label(menu, text="\nSTEP 2: SELECT DIFFICULTY", fg="#888", bg="#050505", font=("Fixedsys", 12)).pack()
        diffs = [("NORMAL", 150, 10), ("INSANE", 80, 7), ("GOD MODE", 50, 5)]
        for name, speed, t_limit in diffs:
            btn = tk.Button(menu, text=name, font=("Fixedsys", 16), fg="#000", bg="#00ffcc", width=15,
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
        
        self.info_label = tk.Label(self.root, text="PRESS [ SPACE ] TO START", fg="#ff0055", bg="#050505", font=("Fixedsys", 20))
        self.info_label.pack()

        # 初始化資料
        self.snake_a = [(200, 300), (180, 300), (160, 300)]
        self.snake_b = [(400, 300), (420, 300), (440, 300)] if self.mode == "Twin" else []
        self.direction = "Right"
        self.next_dir = "Right"
        self.score = 0
        self.current_time = self.time_limit
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
        
        # A 蛇運動
        hx, hy = self.snake_a[0]
        hx, hy = self.move_coord(hx, hy, self.direction)
        
        # 模式：傳送門
        if self.mode == "Portal":
            hx %= self.size
            hy %= self.size
        
        new_head_a = (hx, hy)

        # 模式：雙生鏡面
        new_head_b = None
        if self.mode == "Twin":
            bx, by = self.snake_b[0]
            # 鏡面反轉水平方向
            b_dir = self.direction
            if b_dir == "Left": b_dir = "Right"
            elif b_dir == "Right": b_dir = "Left"
            bx, by = self.move_coord(bx, by, b_dir)
            new_head_b = (bx, by)

        # 碰撞偵測
        if self.check_crash(new_head_a, self.snake_a) or (self.mode == "Twin" and self.check_crash(new_head_b, self.snake_b)):
            self.end_game("SYSTEM FAILURE")
            return

        self.snake_a.insert(0, new_head_a)
        if self.mode == "Twin": self.snake_b.insert(0, new_head_b)

        # 吃到食物
        if new_head_a == self.food or (new_head_b and new_head_b == self.food):
            self.score += 1
            self.current_time = self.time_limit
            self.base_delay = max(40, self.base_delay - 2)
            self.create_food()
        else:
            self.snake_a.pop()
            if self.mode == "Twin": self.snake_b.pop()

        self.draw_scene()
        self.root.after(self.base_delay, self.game_loop)

    def move_coord(self, x, y, d):
        if d == "Up": y -= self.grid
        elif d == "Down": y += self.grid
        elif d == "Left": x -= self.grid
        elif d == "Right": x += self.grid
        return x, y

    def check_crash(self, head, body):
        x, y = head
        if self.mode != "Portal":
            if x < 0 or x >= self.size or y < 0 or y >= self.size: return True
        return head in body

    def draw_scene(self):
        self.canvas.delete("all")
        
        # 繪製食物
        self.canvas.create_rectangle(self.food[0], self.food[1], self.food[0]+self.grid, self.food[1]+self.grid, fill="#ff0055", tag="food")
        
        # 繪製蛇
        for x, y in self.snake_a:
            self.canvas.create_rectangle(x, y, x+self.grid, y+self.grid, fill="#00ffcc", outline="#000")
        if self.mode == "Twin":
            for x, y in self.snake_b:
                self.canvas.create_rectangle(x, y, x+self.grid, y+self.grid, fill="#ffcc00", outline="#000")

        # 模式：黑暗迷霧 (蓋上一層黑幕，只留蛇頭周圍)
        if self.mode == "Fog":
            hx, hy = self.snake_a[0]
            # 簡單實現：畫一個巨大的黑框，中間挖洞
            self.canvas.create_polygon(
                0,0, 600,0, 600,600, 0,600, 0,0,
                hx-80, hy-80, hx-80, hy+100, hx+100, hy+100, hx+100, hy-80, hx-80, hy-80,
                fill="#000", outline="", fill_rule=tk.EVENODD
            )

    def create_food(self):
        self.food = (random.randint(2, (self.size//self.grid)-3) * self.grid,
                     random.randint(2, (self.size//self.grid)-3) * self.grid)

    def countdown(self):
        if not self.running: return
        if self.current_time > 0:
            self.current_time -= 1
            self.info_label.config(text=f"SCORE: {self.score:03d} | TIME: {self.current_time}s | MODE: {self.mode}")
            self.root.after(1000, self.countdown)
        else: self.end_game("TIME OUT")

    def end_game(self, msg):
        self.running = False
        self.canvas.create_rectangle(100, 200, 500, 400, fill="#111", outline="#ff0055", width=3)
        self.canvas.create_text(300, 280, text=f"{msg}\nFINAL SCORE: {self.score}", fill="white", font=("Fixedsys", 20), justify="center")
        tk.Button(self.root, text="RESTART", command=self.show_main_menu, bg="#00ffcc", font=("Fixedsys", 12)).pack(pady=20)

if __name__ == "__main__":
    root = tk.Tk()
    game = UltimateSnakeGame(root)
    root.mainloop()