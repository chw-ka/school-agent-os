import tkinter as tk
import random

class Breakout:
    def __init__(self, root):
        self.root = root
        self.root.title("極速打磚塊 - Breakout!")
        
        # 遊戲參數
        self.width = 600
        self.height = 400
        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height, bg="black")
        self.canvas.pack()
        
        self.paddle_width = 100
        self.ball_speed = [3, -3]  # [x方向, y方向]
        self.score = 0
        self.lives = 3
        
        # 建立物件
        self.paddle = self.canvas.create_rectangle(250, 380, 350, 390, fill="cyan")
        self.ball = self.canvas.create_oval(290, 360, 310, 380, fill="white")
        self.score_text = self.canvas.create_text(50, 20, text=f"得分: {self.score}", fill="white", font=("Arial", 12))
        self.lives_text = self.canvas.create_text(550, 20, text=f"生命: {self.lives}", fill="white", font=("Arial", 12))
        
        self.bricks = []
        self.create_bricks()
        
        # 綁定滑鼠移動
        self.canvas.bind_all('<Motion>', self.move_paddle)
        
        self.is_running = True
        self.game_loop()

    def create_bricks(self):
        colors = ["red", "orange", "yellow", "green", "blue"]
        for row in range(5):
            for col in range(10):
                x1 = col * 60 + 2
                y1 = row * 25 + 50
                x2 = x1 + 56
                y2 = y1 + 20
                brick = self.canvas.create_rectangle(x1, y1, x2, y2, fill=colors[row])
                self.bricks.append(brick)

    def move_paddle(self, event):
        x = event.x
        # 讓球拍中心跟隨滑鼠，但不超出邊界
        if x < self.paddle_width / 2: x = self.paddle_width / 2
        if x > self.width - self.paddle_width / 2: x = self.width - self.paddle_width / 2
        self.canvas.coords(self.paddle, x - self.paddle_width/2, 380, x + self.paddle_width/2, 390)

    def game_loop(self):
        if not self.is_running: return
        
        # 移動球
        self.canvas.move(self.ball, self.ball_speed[0], self.ball_speed[1])
        pos = self.canvas.coords(self.ball) # [x1, y1, x2, y2]
        
        # 1. 牆壁碰撞
        if pos[0] <= 0 or pos[2] >= self.width:
            self.ball_speed[0] = -self.ball_speed[0]
        if pos[1] <= 0:
            self.ball_speed[1] = -self.ball_speed[1]
            
        # 2. 地板碰撞 (掉落)
        if pos[3] >= self.height:
            self.lives -= 1
            self.update_stats()
            if self.lives <= 0:
                self.game_over("GAME OVER! 你輸了。")
            else:
                self.reset_ball()
        
        # 3. 球拍碰撞
        paddle_pos = self.canvas.coords(self.paddle)
        if pos[2] >= paddle_pos[0] and pos[0] <= paddle_pos[2]:
            if pos[3] >= paddle_pos[1] and pos[3] <= paddle_pos[3]:
                self.ball_speed[1] = -abs(self.ball_speed[1]) # 強制向上反彈

        # 4. 磚塊碰撞
        for brick in self.bricks[:]:
            brick_pos = self.canvas.coords(brick)
            if pos[2] >= brick_pos[0] and pos[0] <= brick_pos[2] and \
               pos[3] >= brick_pos[1] and pos[1] <= brick_pos[3]:
                self.canvas.delete(brick)
                self.bricks.remove(brick)
                self.ball_speed[1] = -self.ball_speed[1]
                self.score += 10
                self.update_stats()
                break # 每次移動只撞一個磚塊

        if not self.bricks:
            self.game_over("恭喜！你清空了所有磚塊！")

        self.root.after(10, self.game_loop)

    def reset_ball(self):
        self.canvas.coords(self.ball, 290, 360, 310, 380)
        self.ball_speed = [3, -3]

    def update_stats(self):
        self.canvas.itemconfig(self.score_text, text=f"得分: {self.score}")
        self.canvas.itemconfig(self.lives_text, text=f"生命: {self.lives}")

    def game_over(self, message):
        self.is_running = False
        self.canvas.create_text(300, 200, text=message, fill="white", font=("Arial", 24, "bold"))

if __name__ == "__main__":
    root = tk.Tk()
    game = Breakout(root)
    root.mainloop()