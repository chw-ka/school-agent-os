import tkinter as tk
import random
import time

class SpeedDodgeGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("極速閃避 - 考驗你的手速與反應！")
        self.root.resizable(False, False)

        # 遊戲參數
        self.width = 600
        self.height = 400
        self.player_size = 20
        self.balls = []
        self.start_time = 0
        self.running = False

        # 畫布
        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height, bg="#1a1a1a", highlightthickness=0)
        self.canvas.pack()

        # 玩家方塊
        self.player = self.canvas.create_rectangle(0, 0, self.player_size, self.player_size, fill="#3498db", outline="#ecf0f1")

        # 狀態文字
        self.info_text = self.canvas.create_text(self.width//2, self.height//2, text="點擊畫面開始遊戲\n(用滑鼠控制藍色方塊)", 
                                               fill="white", font=("Arial", 16, "bold"), justify="center")

        # 綁定滑鼠移動
        self.canvas.bind("<Motion>", self.move_player)
        self.canvas.bind("<Button-1>", self.start_game)

    def start_game(self, event=None):
        if self.running: return
        
        # 重置狀態
        self.running = True
        self.start_time = time.time()
        self.canvas.itemconfig(self.info_text, text="")
        self.balls = []
        self.canvas.delete("ball") # 清除舊的球
        
        self.game_loop()

    def move_player(self, event):
        # 讓方塊中心跟隨滑鼠
        x1 = event.x - self.player_size // 2
        y1 = event.y - self.player_size // 2
        x2 = x1 + self.player_size
        y2 = y1 + self.player_size
        self.canvas.coords(self.player, x1, y1, x2, y2)

    def create_ball(self):
        # 隨機生成紅球
        side = random.choice(['top', 'bottom', 'left', 'right'])
        size = random.randint(10, 25)
        
        if side == 'top':
            x, y = random.randint(0, self.width), -size
            vx, vy = random.uniform(-2, 2), random.uniform(2, 5)
        elif side == 'bottom':
            x, y = random.randint(0, self.width), self.height + size
            vx, vy = random.uniform(-2, 2), random.uniform(-5, -2)
        elif side == 'left':
            x, y = -size, random.randint(0, self.height)
            vx, vy = random.uniform(2, 5), random.uniform(-2, 2)
        else: # right
            x, y = self.width + size, random.randint(0, self.height)
            vx, vy = random.uniform(-5, -2), random.uniform(-2, 2)

        ball = self.canvas.create_oval(x, y, x+size, y+size, fill="#e74c3c", outline="#c0392b", tags="ball")
        self.balls.append({'id': ball, 'vx': vx, 'vy': vy})

    def game_loop(self):
        if not self.running: return

        elapsed_time = time.time() - self.start_time
        
        # 難度增加：時間越久，球出現機率越高
        if random.random() < 0.05 + (elapsed_time * 0.002):
            self.create_ball()

        # 移動所有的球
        player_coords = self.canvas.coords(self.player)
        
        for ball_data in self.balls[:]:
            self.canvas.move(ball_data['id'], ball_data['vx'], ball_data['vy'])
            pos = self.canvas.coords(ball_data['id'])

            # 碰撞檢測 (簡單重疊判定)
            if self.check_collision(player_coords, pos):
                self.end_game(elapsed_time)
                return

            # 移除超出邊界的球
            if pos[0] < -50 or pos[2] > self.width + 50 or pos[1] < -50 or pos[3] > self.height + 50:
                self.canvas.delete(ball_data['id'])
                self.balls.remove(ball_data)

        self.root.after(20, self.game_loop)

    def check_collision(self, p, b):
        # p: player [x1, y1, x2, y2], b: ball [x1, y1, x2, y2]
        return not (p[2] < b[0] or p[0] > b[2] or p[3] < b[1] or p[1] > b[3])

    def end_game(self, score):
        self.running = False
        final_score = round(score, 2)
        self.canvas.itemconfig(self.info_text, text=f"GAME OVER!\n生存時間: {final_score} 秒\n\n點擊畫面重新開始")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    game = SpeedDodgeGame()
    game.run()