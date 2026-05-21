import tkinter as tk
import random

class PopularGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Task 3 - 極速打磚塊 2026")
        
        # 畫布設定
        self.width = 450
        self.height = 600
        self.cv = tk.Canvas(root, width=self.width, height=self.height, bg="#0f0c29", highlightthickness=0)
        self.cv.pack()

        # 玩家擋板
        self.paddle_w = 80
        self.paddle = self.cv.create_rectangle(0, 0, self.paddle_w, 15, fill="#00d2ff", outline="white", width=2)
        self.cv.move(self.paddle, self.width//2 - self.paddle_w//2, self.height - 40)

        # 球
        self.ball_radius = 8
        self.ball = self.cv.create_oval(0, 0, self.ball_radius*2, self.ball_radius*2, fill="#ff0080", outline="white")
        self.cv.move(self.ball, self.width//2, self.height//2)
        
        # 遊戲變數
        self.dx = 4
        self.dy = -4
        self.score = 0
        self.game_over = False
        self.bricks = []
        
        # 分數與提示
        self.score_text = self.cv.create_text(50, 20, text=f"Score: {self.score}", fill="white", font=("Arial", 14, "bold"))
        
        # 初始化磚塊
        self.create_bricks()
        
        # 綁定滑鼠控制擋板
        self.cv.bind("<Motion>", self.move_paddle)
        
        # 開始遊戲循環
        self.update()

    def create_bricks(self):
        colors = ["#ff5e62", "#ff9966", "#7f00ff", "#3a1c71"]
        for r in range(5):
            for c in range(7):
                x1 = c * 60 + 20
                y1 = r * 25 + 50
                x2 = x1 + 50
                y2 = y1 + 15
                brick = self.cv.create_rectangle(x1, y1, x2, y2, fill=random.choice(colors), outline="white")
                self.bricks.append(brick)

    def move_paddle(self, event):
        x = event.x
        # 確保擋板不超出邊界
        if x < self.paddle_w//2: x = self.paddle_w//2
        if x > self.width - self.paddle_w//2: x = self.width - self.paddle_w//2
        self.cv.coords(self.paddle, x - self.paddle_w//2, self.height - 40, x + self.paddle_w//2, self.height - 25)

    def update(self):
        if self.game_over: return

        # 移動球
        self.cv.move(self.ball, self.dx, self.dy)
        pos = self.cv.coords(self.ball)

        # 牆壁碰撞
        if pos[0] <= 0 or pos[2] >= self.width:
            self.dx *= -1
        if pos[1] <= 0:
            self.dy *= -1
        
        # 掉落地面 - 遊戲結束
        if pos[3] >= self.height:
            self.end_game()
            return

        # 擋板碰撞
        paddle_pos = self.cv.coords(self.paddle)
        if pos[2] >= paddle_pos[0] and pos[0] <= paddle_pos[2] and \
           pos[3] >= paddle_pos[1] and pos[1] <= paddle_pos[3]:
            self.dy = -abs(self.dy) # 確保向上反彈
            # 增加一點難度：反彈後稍微加速
            self.dx *= 1.02
            self.dy *= 1.02

        # 磚塊碰撞
        for brick in self.bricks[:]:
            b_pos = self.cv.coords(brick)
            if pos[2] >= b_pos[0] and pos[0] <= b_pos[2] and \
               pos[3] >= b_pos[1] and pos[1] <= b_pos[3]:
                self.cv.delete(brick)
                self.bricks.remove(brick)
                self.dy *= -1
                self.score += 10
                self.cv.itemconfig(self.score_text, text=f"Score: {self.score}")
                break

        # 贏得遊戲條件
        if not self.bricks:
            self.create_bricks() # 無盡模式：重新生成

        self.root.after(15, self.update)

    def end_game(self):
        self.game_over = True
        self.cv.create_rectangle(0, 0, self.width, self.height, fill="black", stipple="gray50")
        self.cv.create_text(self.width//2, self.height//2, text="GAME OVER", fill="#ff0080", font=("Arial", 40, "bold"))
        self.cv.create_text(self.width//2, self.height//2 + 60, text=f"Total Score: {self.score}", fill="white", font=("Arial", 20))

if __name__ == "__main__":
    root = tk.Tk()
    root.resizable(False, False)
    game = PopularGame(root)
    root.mainloop()