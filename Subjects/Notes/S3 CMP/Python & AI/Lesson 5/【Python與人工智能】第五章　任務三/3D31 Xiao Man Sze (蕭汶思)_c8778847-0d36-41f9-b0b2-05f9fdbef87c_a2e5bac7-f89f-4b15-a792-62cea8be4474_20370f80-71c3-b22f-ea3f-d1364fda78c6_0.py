import tkinter as tk
import random
from tkinter import messagebox
import winsound

class FunSnake:
    def __init__(self, root):
        self.root = root
        self.root.title("超進化貪食蛇：黃金傳送門")
        
        self.width, self.height = 600, 400
        self.grid_size = 20
        
        # 遊戲主界面
        self.game_frame = tk.Frame(self.root)
        self.canvas = tk.Canvas(self.game_frame, width=self.width, height=self.height, bg="#0d0d21", highlightthickness=0)
        self.canvas.pack()
        
        self.info_frame = tk.Frame(self.game_frame, bg="#222")
        self.info_frame.pack(fill=tk.X)
        
        self.score_label = tk.Label(self.info_frame, text="分數: 0", fg="gold", bg="#222", font=("微軟正黑體", 12, "bold"))
        self.score_label.pack(side=tk.LEFT, padx=20)
        
        self.timer_canvas = tk.Canvas(self.info_frame, width=200, height=10, bg="black")
        self.timer_canvas.pack(side=tk.RIGHT, padx=20)

        # 難度選單
        self.menu_frame = tk.Frame(self.root, bg="#0d0d21", padx=50, pady=50)
        self.menu_frame.pack()
        tk.Label(self.menu_frame, text="✨ 超進化貪食蛇 ✨", fg="cyan", bg="#0d0d21", font=("微軟正黑體", 24, "bold")).pack(pady=20)
        
        for level, d, t in [("新手 (Easy)", 180, 1.0), ("挑戰 (Normal)", 120, 1.5), ("地獄 (Hell)", 70, 2.2)]:
            tk.Button(self.menu_frame, text=level, font=("微軟正黑體", 12), width=20, bg="cyan",
                      command=lambda d=d, t=t: self.start_game(d, t)).pack(pady=10)

        self.root.bind("<KeyPress>", self.change_direction)
        self.running = False

    def start_game(self, init_delay, time_drain):
        self.menu_frame.pack_forget()
        self.game_frame.pack()
        self.init_delay = init_delay
        self.time_drain = time_drain
        self.reset_game()

    def reset_game(self):
        self.snake = [(100, 100), (80, 100), (60, 100)]
        self.direction = "Right"
        self.score = 0
        self.delay = self.init_delay
        self.time_left = 100
        self.is_golden = False # 是否處於黃金狀態
        self.running = True
        self.spawn_item()
        self.game_loop()

    def spawn_item(self):
        """ 隨機生成普通食物或黃金果實 """
        x = random.randint(0, (self.width-20)//20) * 20
        y = random.randint(0, (self.height-20)//20) * 20
        self.food_type = "golden" if random.random() < 0.2 else "normal"
        self.food = (x, y)

    def change_direction(self, event):
        keys = {"Up": "Down", "Down": "Up", "Left": "Right", "Right": "Left"}
        if event.keysym in keys and event.keysym != keys.get(self.direction):
            self.direction = event.keysym

    def move(self):
        head_x, head_y = self.snake[0]
        if self.direction == "Up": head_y -= self.grid_size
        elif self.direction == "Down": head_y += self.grid_size
        elif self.direction == "Left": head_x -= self.grid_size
        elif self.direction == "Right": head_x += self.grid_size
        
        # --- 傳送門邏輯 (Warp Portal) ---
        head_x %= self.width
        head_y %= self.height
        
        new_head = (head_x, head_y)

        # 撞到自己或時間耗盡
        if new_head in self.snake or self.time_left <= 0:
            self.game_over()
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            if self.food_type == "golden":
                self.score += 50
                self.time_left = 100 # 黃金果實補滿時間
                winsound.Beep(1200, 100)
                self.is_golden = True # 觸發特效
            else:
                self.score += 10
                self.time_left = min(100, self.time_left + 30)
                winsound.Beep(800, 50)
                self.is_golden = False
            
            self.spawn_item()
            if self.delay > 50: self.delay -= 3
        else:
            self.snake.pop()
            self.time_left -= self.time_drain

    def draw(self):
        self.canvas.delete("all")
        
        # 畫食物特效
        f_color = "gold" if self.food_type == "golden" else "#ff3366"
        f_size = 3 if self.food_type == "golden" else 0
        self.canvas.create_oval(self.food[0]-f_size, self.food[1]-f_size, 
                                self.food[0]+20+f_size, self.food[1]+20+f_size, 
                                fill=f_color, outline="white", width=2)
        
        # 畫蛇與特效
        for i, (x, y) in enumerate(self.snake):
            if i == 0:
                color = "yellow" if self.is_golden else "cyan"
            else:
                color = "#005555"
            self.canvas.create_rectangle(x, y, x+20, y+20, fill=color, outline="#0d0d21")

    def update_ui(self):
        self.score_label.config(text=f"分數: {self.score} {'⭐' if self.is_golden else ''}")
        self.timer_canvas.delete("bar")
        bar_color = "gold" if self.is_golden else ("red" if self.time_left < 30 else "cyan")
        self.timer_canvas.create_rectangle(0, 0, self.time_left * 2, 10, fill=bar_color, tags="bar")

    def game_loop(self):
        if self.running:
            self.move()
            self.draw()
            self.update_ui()
            self.root.after(int(self.delay), self.game_loop)

    def game_over(self):
        self.running = False
        winsound.Beep(200, 500)
        messagebox.showinfo("Game Over", f"最終得分: {self.score}\n你吃了{'很多' if self.score > 100 else ''}黃金果實！")
        self.game_frame.pack_forget()
        self.menu_frame.pack()

if __name__ == "__main__":
    root = tk.Tk()
    app = FunSnake(root)
    root.mainloop()