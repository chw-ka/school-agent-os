import tkinter as tk
from tkinter import messagebox
import random

class SnakeGame:
    def __init__(self, root):
        self.root = root
        self.root.title("極速貪食蛇 - Task 3")
        self.root.resizable(False, False)

        # 遊戲設定
        self.grid_count = 20  # 20x20 網格
        self.cell_pixel = 25 # 每個格子 25 像素
        self.canvas_size = self.grid_count * self.cell_pixel
        
        # 遊戲狀態
        self.score = 0
        self.high_score = 0
        self.initial_delay = 180  # 初始速度 (ms)
        self.delay = self.initial_delay
        self.direction = "Right"
        self.running = False

        # --- 核心邏輯：二維列表儲存狀態 ---
        # 狀態定義：0=空地, 1=蛇身, 2=食物
        self.grid_state = [[0 for _ in range(self.grid_count)] for _ in range(self.grid_count)]
        
        # 蛇身座標隊列 ([row, col])，索引 0 為蛇頭
        self.snake = [[10, 5], [10, 4], [10, 3]]
        self.food = None

        self.setup_ui()
        self.show_start_screen()

    def setup_ui(self):
        # 現代感深色資訊欄
        self.header = tk.Frame(self.root, bg="#1a1a2e", padx=15, pady=10)
        self.header.pack(fill="x")

        self.score_label = tk.Label(self.header, text=f"Score: {self.score}", 
                                    fg="#2ecc71", bg="#1a1a2e", font=("Arial", 12, "bold"))
        self.score_label.pack(side="left")

        self.high_label = tk.Label(self.header, text=f"Best: {self.high_score}", 
                                   fg="#f1c40f", bg="#1a1a2e", font=("Arial", 12, "bold"))
        self.high_label.pack(side="right")

        # 遊戲畫布 (深色模式底色)
        self.canvas = tk.Canvas(self.root, width=self.canvas_size, height=self.canvas_size, 
                                bg="#16213e", highlightthickness=0)
        self.canvas.pack()

        # 鍵盤操控綁定
        self.root.bind("<Key>", self.handle_input)

    def show_start_screen(self):
        self.canvas.delete("all")
        self.canvas.create_text(self.canvas_size/2, self.canvas_size/2, 
                                text="PRESS SPACE TO START", 
                                fill="white", font=("Arial", 18, "bold"))

    def reset_game(self):
        self.score = 0
        self.delay = self.initial_delay
        self.direction = "Right"
        self.snake = [[10, 5], [10, 4], [10, 3]]
        
        # 重置 2D List 狀態
        self.grid_state = [[0 for _ in range(self.grid_count)] for _ in range(self.grid_count)]
        for r, c in self.snake:
            self.grid_state[r][c] = 1
        
        self.spawn_food()
        self.running = True
        self.run_game()

    def spawn_food(self):
        while True:
            r, c = random.randint(0, self.grid_count - 1), random.randint(0, self.grid_count - 1)
            if self.grid_state[r][c] == 0:
                self.grid_state[r][c] = 2
                self.food = [r, c]
                break

    def handle_input(self, event):
        key = event.keysym
        if key == "space" and not self.running:
            self.reset_game()
        elif key == "Up" and self.direction != "Down": self.direction = "Up"
        elif key == "Down" and self.direction != "Up": self.direction = "Down"
        elif key == "Left" and self.direction != "Right": self.direction = "Left"
        elif key == "Right" and self.direction != "Left": self.direction = "Right"

    def run_game(self):
        if not self.running:
            return

        # 獲取當前頭部並計算新位置
        head_r, head_c = self.snake[0]
        if self.direction == "Up": head_r -= 1
        elif self.direction == "Down": head_r += 1
        elif self.direction == "Left": head_c -= 1
        elif self.direction == "Right": head_c += 1

        # 1. 碰撞偵測 (邊界或撞到自己)
        if (head_r < 0 or head_r >= self.grid_count or 
            head_c < 0 or head_c >= self.grid_count or 
            self.grid_state[head_r][head_c] == 1):
            self.game_over()
            return

        # 2. 移動與更新 2D List 狀態
        new_head = [head_r, head_c]
        is_eating = (new_head == self.food)
        
        self.snake.insert(0, new_head)
        
        if is_eating:
            self.score += 10
            # 難度曲線：吃掉食物速度加快 (縮短 delay)
            self.delay = max(45, int(self.delay * 0.96))
            self.spawn_food()
        else:
            # 沒吃食物則移除尾巴，同步更新 2D List
            tail_r, tail_c = self.snake.pop()
            self.grid_state[tail_r][tail_c] = 0

        # 將新頭部寫入 2D List
        self.grid_state[head_r][head_c] = 1

        self.draw()
        self.root.after(self.delay, self.run_game)

    def draw(self):
        self.canvas.delete("all")
        self.score_label.config(text=f"Score: {self.score}")

        # 畫食物 (亮紅色)
        fr, fc = self.food
        self.canvas.create_oval(fc*self.cell_pixel+3, fr*self.cell_pixel+3, 
                                (fc+1)*self.cell_pixel-3, (fr+1)*self.cell_pixel-3, 
                                fill="#ff2e63", outline="white")

        # 畫蛇身 (螢光綠漸層)
        for i, (r, c) in enumerate(self.snake):
            color = "#08ffc8" if i == 0 else "#2ecc71" # 頭部與身體顏色區分
            self.canvas.create_rectangle(c*self.cell_pixel+1, r*self.cell_pixel+1, 
                                         (c+1)*self.cell_pixel-1, (r+1)*self.cell_pixel-1, 
                                         fill=color, outline="#16213e")

    def game_over(self):
        self.running = False
        if self.score > self.high_score:
            self.high_score = self.score
            self.high_label.config(text=f"Best: {self.high_score}")
        
        messagebox.showinfo("Game Over", f"你輸了！\n得分: {self.score}\n最高分: {self.high_score}")
        self.show_start_screen()

if __name__ == "__main__":
    root = tk.Tk()
    game = SnakeGame(root)
    root.mainloop()
