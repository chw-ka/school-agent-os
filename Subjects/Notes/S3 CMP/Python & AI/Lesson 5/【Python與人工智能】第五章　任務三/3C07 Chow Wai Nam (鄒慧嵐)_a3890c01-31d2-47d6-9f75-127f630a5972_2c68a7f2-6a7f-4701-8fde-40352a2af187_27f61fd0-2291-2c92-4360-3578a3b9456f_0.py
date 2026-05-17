import tkinter as tk
import random
import winsound

class UltimateSnake:
    def __init__(self, root):
        self.root = root
        self.root.title("Task3 - 幻彩衝刺貪食蛇")
        self.root.configure(bg='#1a1a2e')

        self.width = 600
        self.height = 400
        self.grid_size = 20
        
        # 難度速度設定
        self.difficulty_speeds = {"簡單": 180, "普通": 100, "困難": 50}
        self.selected_time = 60 # 預設 1 分鐘
        self.is_boosting = False 
        
        self.reset_data()
        self.setup_ui()

    def reset_data(self):
        self.snake = [(100, 100), (80, 100), (60, 100)]
        self.direction = "Right"
        self.score = 0
        self.running = False
        self.time_left = self.selected_time
        self.food = (200, 200)

    def setup_ui(self):
        # 頂部控制面板
        self.control_panel = tk.Frame(self.root, bg='#16213e', pady=10)
        self.control_panel.pack(fill=tk.X)

        # 1. 難度選擇
        tk.Label(self.control_panel, text="難度:", fg="white", bg='#16213e').pack(side=tk.LEFT, padx=5)
        self.diff_var = tk.StringVar(value="普通")
        for level in self.difficulty_speeds.keys():
            rb = tk.Radiobutton(self.control_panel, text=level, variable=self.diff_var, 
                                value=level, fg="white", bg='#16213e', selectcolor="#0f3460")
            rb.pack(side=tk.LEFT, padx=2)

        # 2. 時間選擇
        tk.Label(self.control_panel, text=" | 時間:", fg="white", bg='#16213e').pack(side=tk.LEFT, padx=5)
        self.time_var = tk.IntVar(value=60)
        time_options = [("1m", 60), ("3m", 180), ("5m", 300)]
        for label, sec in time_options:
            rb_t = tk.Radiobutton(self.control_panel, text=label, variable=self.time_var, 
                                  value=sec, fg="white", bg='#16213e', selectcolor="#0f3460")
            rb_t.pack(side=tk.LEFT, padx=2)

        # 3. Start 鍵
        self.start_btn = tk.Button(self.control_panel, text=" 開始遊戲 ", command=self.press_start,
                                   bg='#e94560', fg='white', relief='flat', padx=15, font=('Arial', 10, 'bold'))
        self.start_btn.pack(side=tk.RIGHT, padx=20)

        # 提示與分數資訊
        self.info_label = tk.Label(self.root, text="選好難度與時間後，按下『開始遊戲』", fg="#08d9d6", bg='#1a1a2e', font=('微軟正黑體', 11))
        self.info_label.pack(pady=5)

        # 遊戲畫布
        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height, bg="#1a1a2e", highlightthickness=2, highlightbackground="#e94560")
        self.canvas.pack(pady=10, padx=20)

        # 綁定鍵盤
        self.root.bind("<KeyPress>", self.handle_keypress)
        self.root.bind("<KeyRelease>", self.handle_keyrelease)

    def press_start(self):
        """按下 Start 鍵的處理"""
        if self.running: return
        self.selected_time = self.time_var.get()
        self.reset_data()
        self.start_game()

    def start_game(self):
        self.running = True
        self.start_btn.config(state=tk.DISABLED) # 遊戲中禁用開始鍵
        self.food = self.create_food()
        self.update_clock()
        self.game_loop()

    def update_clock(self):
        if self.time_left > 0 and self.running:
            self.time_left -= 1
            self.root.after(1000, self.update_clock)
        elif self.time_left <= 0 and self.running:
            self.end_game_display("TIME UP!")

    def handle_keypress(self, event):
        mapping = {"Up": "Down", "Down": "Up", "Left": "Right", "Right": "Left"}
        if event.keysym in mapping and event.keysym != mapping.get(self.direction):
            self.direction = event.keysym
        if event.keysym == "Return": self.is_boosting = True

    def handle_keyrelease(self, event):
        if event.keysym == "Return": self.is_boosting = False

    def move_snake(self):
        hx, hy = self.snake[0]
        if self.direction == "Up": hy -= self.grid_size
        elif self.direction == "Down": hy += self.grid_size
        elif self.direction == "Left": hx -= self.grid_size
        elif self.direction == "Right": hx += self.grid_size
        
        new_head = (hx, hy)
        if (hx < 0 or hx >= self.width or hy < 0 or hy >= self.height or new_head in self.snake):
            self.end_game_display("GAME OVER")
            return

        self.snake.insert(0, new_head)
        if new_head == self.food:
            self.score += 10
            try: winsound.Beep(1200, 50)
            except: pass
            self.food = self.create_food()
        else:
            self.snake.pop()

    def create_food(self):
        while True:
            x = random.randint(0, (self.width - self.grid_size) // self.grid_size) * self.grid_size
            y = random.randint(0, (self.height - self.grid_size) // self.grid_size) * self.grid_size
            if (x, y) not in self.snake: return (x, y)

    def draw(self):
        if not self.running: return
        self.canvas.delete("all")
        # 食物
        self.canvas.create_oval(self.food[0]+2, self.food[1]+2, self.food[0]+self.grid_size-2, self.food[1]+self.grid_size-2, fill="#f9ed69", outline="white")
        # 蛇
        for i, (x, y) in enumerate(self.snake):
            head_color = "#ff2e63" if not self.is_boosting else "#ff9f43"
            color = head_color if i == 0 else "#08d9d6"
            self.canvas.create_rectangle(x, y, x+self.grid_size, y+self.grid_size, fill=color, outline="#1a1a2e")
        
        # 實時資訊
        self.canvas.create_text(60, 20, text=f"SCORE: {self.score}", fill="white", font=('Arial', 10, 'bold'))
        self.canvas.create_text(540, 20, text=f"TIME: {self.time_left}s", fill="white", font=('Arial', 10, 'bold'))

    def game_loop(self):
        if self.running:
            self.move_snake()
            self.draw()
            base_speed = self.difficulty_speeds[self.diff_var.get()]
            speed = base_speed // 3 if self.is_boosting else base_speed
            self.root.after(speed, self.game_loop)

    def end_game_display(self, title):
        self.running = False
        self.start_btn.config(state=tk.NORMAL) # 結束後恢復按鈕
        self.root.after(100, self._final_draw, title)

    def _final_draw(self, title):
        self.canvas.delete("all")
        self.canvas.create_rectangle(0, 0, self.width, self.height, fill="#1a1a2e")
        self.canvas.create_text(self.width//2, self.height//2 - 40, text=title, fill="#e94560", font=('Arial', 50, 'bold'))
        self.canvas.create_text(self.width//2, self.height//2 + 40, text=f"FINAL SCORE: {self.score}", fill="white", font=('Arial', 26, 'bold'))
        self.info_label.config(text="遊戲結束！重新選擇後按開始")

if __name__ == "__main__":
    root = tk.Tk()
    game = UltimateSnake(root)
    root.mainloop()