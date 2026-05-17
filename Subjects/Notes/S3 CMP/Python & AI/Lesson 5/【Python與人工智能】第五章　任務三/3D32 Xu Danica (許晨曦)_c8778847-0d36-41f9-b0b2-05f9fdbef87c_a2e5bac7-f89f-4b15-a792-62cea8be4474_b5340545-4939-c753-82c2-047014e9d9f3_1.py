import tkinter as tk
import random

class BreakoutPro:
    def __init__(self, root):
        self.root = root
        self.root.title("Breakout Pro: 道具與速度挑戰")
        
        self.width, self.height = 600, 500
        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height, bg="#1a1a1a")
        self.canvas.pack()
        
        # 初始參數
        self.paddle_w = 100
        self.ball_radius = 10
        self.ball_speed = [3.0, -3.0]
        self.score = 0
        self.lives = 3
        self.bricks_hit = 0
        
        # 建立基本物件
        self.paddle = self.canvas.create_rectangle(250, 470, 350, 480, fill="#00FFD1", outline="white")
        self.ball = self.canvas.create_oval(290, 450, 310, 470, fill="white")
        
        # 文字資訊
        self.score_txt = self.canvas.create_text(60, 20, text=f"Score: {self.score}", fill="white", font=("Fixedsys", 14))
        self.lives_txt = self.canvas.create_text(540, 20, text=f"Lives: {self.lives}", fill="white", font=("Fixedsys", 14))
        self.speed_txt = self.canvas.create_text(300, 20, text="Speed: 1x", fill="#FFD700", font=("Fixedsys", 12))

        self.bricks = []
        self.items = [] # 儲存掉落道具
        self.create_bricks()
        
        self.canvas.bind_all('<Motion>', self.move_paddle)
        self.is_running = True
        self.game_loop()

    def create_bricks(self):
        colors = ["#FF4C4C", "#FF9933", "#FFFF66", "#66FF66", "#4C4CFF"]
        for row in range(6):
            for col in range(10):
                x1, y1 = col * 60 + 2, row * 25 + 50
                brick = self.canvas.create_rectangle(x1, y1, x1+56, y1+20, fill=colors[row % 5], outline="black")
                self.bricks.append(brick)

    def move_paddle(self, event):
        x = max(self.paddle_w/2, min(self.width - self.paddle_w/2, event.x))
        self.canvas.coords(self.paddle, x - self.paddle_w/2, 470, x + self.paddle_w/2, 480)

    def spawn_item(self, x, y):
        # 20% 機率掉落道具
        if random.random() < 0.2:
            it_type = random.choice(["LONG", "BIG"])
            color = "#A020F0" if it_type == "BIG" else "#1E90FF"
            label = "B" if it_type == "BIG" else "L"
            item = self.canvas.create_oval(x, y, x+20, y+20, fill=color, outline="white")
            self.items.append({"id": item, "type": it_type})

    def game_loop(self):
        if not self.is_running: return
        
        # 1. 球移動與牆壁碰撞
        self.canvas.move(self.ball, self.ball_speed[0], self.ball_speed[1])
        b_pos = self.canvas.coords(self.ball)
        
        if b_pos[0] <= 0 or b_pos[2] >= self.width: self.ball_speed[0] *= -1
        if b_pos[1] <= 0: self.ball_speed[1] *= -1
        
        # 2. 掉落判定
        if b_pos[3] >= self.height:
            self.lives -= 1
            self.reset_buffs() # 死亡後道具效果消失
            if self.lives <= 0: return self.end_game("GAME OVER")
            self.reset_ball()

        # 3. 球拍反彈
        p_pos = self.canvas.coords(self.paddle)
        if b_pos[2] >= p_pos[0] and b_pos[0] <= p_pos[2] and b_pos[3] >= p_pos[1] and b_pos[3] <= p_pos[3]:
            self.ball_speed[1] = -abs(self.ball_speed[1])

        # 4. 磚塊碰撞與難度遞增
        for brick in self.bricks[:]:
            if self.check_collision(self.ball, brick):
                bx1, by1, _, _ = self.canvas.coords(brick)
                self.spawn_item(bx1, by1)
                self.canvas.delete(brick)
                self.bricks.remove(brick)
                self.ball_speed[1] *= -1
                self.score += 10
                self.bricks_hit += 1
                
                # 每 5 次擊中增加速度
                if self.bricks_hit % 5 == 0:
                    self.ball_speed[0] *= 1.1
                    self.ball_speed[1] *= 1.1
                    speed_val = round(abs(self.ball_speed[1])/3, 1)
                    self.canvas.itemconfig(self.speed_txt, text=f"Speed: {speed_val}x")
                
                self.update_ui()
                break

        # 5. 道具移動與拾取
        for item_data in self.items[:]:
            self.canvas.move(item_data["id"], 0, 3)
            i_pos = self.canvas.coords(item_data["id"])
            if i_pos[1] > self.height:
                self.canvas.delete(item_data["id"])
                self.items.remove(item_data)
            elif i_pos[2] >= p_pos[0] and i_pos[0] <= p_pos[2] and i_pos[3] >= p_pos[1]:
                self.apply_buff(item_data["type"])
                self.canvas.delete(item_data["id"])
                self.items.remove(item_data)

        if not self.bricks: return self.end_game("VICTORY!")
        self.root.after(10, self.game_loop)

    def check_collision(self, obj1, obj2):
        p1, p2 = self.canvas.coords(obj1), self.canvas.coords(obj2)
        return p1[2] >= p2[0] and p1[0] <= p2[2] and p1[3] >= p2[1] and p1[1] <= p2[3]

    def apply_buff(self, t):
        if t == "LONG":
            self.paddle_w = 160
            self.canvas.itemconfig(self.paddle, fill="#00FF00")
        elif t == "BIG":
            # 讓球半徑暫時變大
            curr = self.canvas.coords(self.ball)
            self.canvas.coords(self.ball, curr[0]-5, curr[1]-5, curr[2]+5, curr[3]+5)
            self.canvas.itemconfig(self.ball, fill="#A020F0")

    def reset_buffs(self):
        self.paddle_w = 100
        self.canvas.itemconfig(self.paddle, fill="#00FFD1")
        self.canvas.itemconfig(self.ball, fill="white")

    def reset_ball(self):
        self.canvas.coords(self.ball, 290, 450, 310, 470)
        self.ball_speed = [3.0, -3.0]
        self.update_ui()

    def update_ui(self):
        self.canvas.itemconfig(self.score_txt, text=f"Score: {self.score}")
        self.canvas.itemconfig(self.lives_txt, text=f"Lives: {self.lives}")

    def end_game(self, msg):
        self.is_running = False
        self.canvas.create_text(300, 250, text=msg, fill="white", font=("Arial", 30, "bold"))

if __name__ == "__main__":
    root = tk.Tk()
    game = BreakoutPro(root)
    root.mainloop()