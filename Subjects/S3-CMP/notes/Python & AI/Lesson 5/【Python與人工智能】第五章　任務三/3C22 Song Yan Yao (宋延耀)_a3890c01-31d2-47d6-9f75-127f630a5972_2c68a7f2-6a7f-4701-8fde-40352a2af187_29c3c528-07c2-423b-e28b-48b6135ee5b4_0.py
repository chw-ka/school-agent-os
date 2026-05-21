import tkinter as tk
import random

class NeonBrickBreaker:
    def __init__(self, root):
        self.root = root
        self.root.title("霓虹極速磚塊 - 百分提速挑戰")
        self.root.resizable(False, False)

        # 遊戲參數
        self.width = 600
        self.height = 400
        self.ball_speed_base = 4
        self.max_speed = 15  # 稍微提高上限，增加挑戰性
        self.score = 0
        self.last_speed_up_score = 0  # 記錄上一次因為分數而加速的點
        self.lives = 3
        self.game_started = False
        self.game_running = True

        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height, bg="#1a1a1a", highlightthickness=0)
        self.canvas.pack()

        self.paddle = self.canvas.create_rectangle(250, 380, 350, 390, fill="#00ffcc", outline="#00ffcc")
        self.ball = self.canvas.create_oval(290, 200, 310, 220, fill="#ff00ff", outline="#ff00ff")
        self.dx = random.choice([-self.ball_speed_base, self.ball_speed_base])
        self.dy = -self.ball_speed_base

        self.score_text = self.canvas.create_text(60, 20, text=f"Score: {self.score}", fill="white", font=('Arial', 12, 'bold'))
        self.lives_text = self.canvas.create_text(540, 20, text=f"Lives: {self.lives}", fill="white", font=('Arial', 12, 'bold'))
        self.speed_label = self.canvas.create_text(300, 20, text="速度等級: 1", fill="#00ffcc", font=('Arial', 10, 'bold'))

        self.bricks = []
        self.create_bricks()

        # 開始畫面
        self.start_overlay = self.canvas.create_rectangle(0, 0, 600, 400, fill="black", stipple="gray50")
        self.start_button = self.canvas.create_text(300, 200, text="每 100 分加速一次！\n點擊畫面開始遊戲", fill="#ff00ff", font=('Arial', 20, 'bold'), justify="center")

        self.canvas.bind("<Motion>", self.move_paddle)
        self.canvas.bind("<Button-1>", self.start_game)
        
        self.update()

    def create_bricks(self):
        # 增加更多層磚塊以確保有足夠分數達到提速門檻
        colors = ["#ff3366", "#ff9933", "#ffff33", "#33ff33", "#3399ff", "#cc33ff"]
        for row in range(6):
            for col in range(10):
                x1 = col * 60 + 2
                y1 = row * 25 + 50
                x2 = x1 + 56
                y2 = y1 + 20
                brick = self.canvas.create_rectangle(x1, y1, x2, y2, fill=colors[row % len(colors)], outline="#1a1a1a")
                self.bricks.append(brick)

    def start_game(self, event):
        if not self.game_started:
            self.game_started = True
            self.canvas.delete(self.start_overlay)
            self.canvas.delete(self.start_button)

    def move_paddle(self, event):
        x = event.x
        self.canvas.coords(self.paddle, x - 50, 380, x + 50, 390)

    def update(self):
        if self.game_running and self.game_started:
            self.canvas.move(self.ball, self.dx, self.dy)
            pos = self.canvas.coords(self.ball)

            # 牆壁與天花板碰撞
            if pos[0] <= 0 or pos[2] >= self.width:
                self.dx = -self.dx
            if pos[1] <= 0:
                self.dy = -self.dy

            # 掉落重置
            if pos[3] >= self.height:
                self.lives -= 1
                self.canvas.itemconfig(self.lives_text, text=f"Lives: {self.lives}")
                if self.lives <= 0:
                    self.game_over("GAME OVER")
                else:
                    self.canvas.coords(self.ball, 290, 200, 310, 220)
                    # 重置該回合的速度
                    current_level = (self.score // 100) + 1
                    speed = self.ball_speed_base + (current_level - 1)
                    self.dx = random.choice([-speed, speed])
                    self.dy = -speed

            # 擋板碰撞
            paddle_pos = self.canvas.coords(self.paddle)
            if pos[2] >= paddle_pos[0] and pos[0] <= paddle_pos[2]:
                if pos[3] >= paddle_pos[1] and pos[3] <= paddle_pos[3]:
                    self.dy = -abs(self.dy)

            # 磚塊碰撞
            items_hit = self.canvas.find_overlapping(*pos)
            for item in items_hit:
                if item in self.bricks:
                    self.dy = -self.dy
                    self.canvas.delete(item)
                    self.bricks.remove(item)
                    self.score += 10
                    self.canvas.itemconfig(self.score_text, text=f"Score: {self.score}")
                    
                    # --- 核心邏輯：每 100 分加速 ---
                    if self.score // 100 > self.last_speed_up_score // 100:
                        self.speed_up_ball()
                        self.last_speed_up_score = self.score
                    break

            if not self.bricks:
                self.game_over("恭喜通關！")

        self.root.after(16, self.update)

    def speed_up_ball(self):
        """執行加速並更新 UI"""
        level = (self.score // 100) + 1
        self.canvas.itemconfig(self.speed_label, text=f"速度等級: {level} (加速!!)", fill="#ff00ff")
        
        # 增加 20% 的速度，但不超過最大值
        if abs(self.dx) < self.max_speed:
            self.dx *= 1.2
            self.dy *= 1.2
            
        # 2秒後將顏色改回原色
        self.root.after(2000, lambda: self.canvas.itemconfig(self.speed_label, fill="#00ffcc", text=f"速度等級: {level}"))

    def game_over(self, message):
        self.game_running = False
        self.canvas.create_rectangle(150, 150, 450, 250, fill="black", outline="white", width=2)
        self.canvas.create_text(self.width/2, self.height/2, text=message, fill="#ff00ff", font=('Arial', 24, 'bold'))
        self.canvas.create_text(self.width/2, self.height/2 + 60, text=f"最終得分: {self.score}", fill="white", font=('Arial', 14))

if __name__ == "__main__":
    root = tk.Tk()
    game = NeonBrickBreaker(root)
    root.mainloop()