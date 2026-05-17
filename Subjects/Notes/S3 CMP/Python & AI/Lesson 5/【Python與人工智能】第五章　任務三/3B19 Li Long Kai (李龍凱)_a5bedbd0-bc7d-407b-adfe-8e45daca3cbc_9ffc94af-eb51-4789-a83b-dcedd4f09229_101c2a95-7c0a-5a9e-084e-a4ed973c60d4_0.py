import tkinter as tk
import random

# --- 遊戲平衡設定 ---
WIDTH = 600
HEIGHT = 700
BASKET_WIDTH = 110
BASKET_HEIGHT = 20
BASE_SPEED = 6       # 起始速度
LEVEL_UP_STEP = 5    # 每得幾分提升一次難度
MAX_LIVES = 3        # 最大生命值

class UltimateAppleGame:
    def __init__(self, root):
        self.root = root
        self.root.title("極限蘋果：黃金與炸彈 🍎")
        self.root.resizable(False, False)

        # 遊戲變數
        self.score = 0
        self.lives = MAX_LIVES
        self.level = 1
        self.speed = BASE_SPEED
        self.items = [] # 儲存畫面上的所有物體
        self.game_running = True

        # 介面初始化
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="#1a1a1a", highlightthickness=0)
        self.canvas.pack()

        # 1. 藍色長方形籃子
        self.basket_y = HEIGHT - 50
        self.basket = self.canvas.create_rectangle(
            WIDTH//2 - BASKET_WIDTH//2, self.basket_y,
            WIDTH//2 + BASKET_WIDTH//2, self.basket_y + BASKET_HEIGHT,
            fill="#3498db", outline="#ecf0f1", width=2
        )

        # 2. UI 顯示 (左上角分數，右上角生命與等級)
        self.ui_score = self.canvas.create_text(
            20, 20, text=f"SCORE: {self.score}", 
            font=("Fixedsys", 20, "bold"), fill="#f1c40f", anchor="nw"
        )
        self.ui_lives = self.canvas.create_text(
            WIDTH - 20, 20, text=f"{'❤' * self.lives}", 
            font=("Arial", 20), fill="#e74c3c", anchor="ne"
        )
        self.ui_level = self.canvas.create_text(
            WIDTH // 2, 20, text=f"LEVEL {self.level}", 
            font=("Fixedsys", 16), fill="#95a5a6", anchor="n"
        )

        # 綁定操作
        self.canvas.bind("<Motion>", self.move_basket)
        
        # 啟動遊戲
        self.spawn_loop()
        self.update_loop()

    def move_basket(self, event):
        if not self.game_running: return
        x = event.x
        # 邊界限制
        x = max(BASKET_WIDTH//2, min(WIDTH - BASKET_WIDTH//2, x))
        self.canvas.coords(
            self.basket, 
            x - BASKET_WIDTH//2, self.basket_y, 
            x + BASKET_WIDTH//2, self.basket_y + BASKET_HEIGHT
        )

    def create_item(self, type="apple"):
        """生成不同類型的物體"""
        x = random.randint(30, WIDTH - 30)
        if type == "apple":
            item = self.canvas.create_oval(x, -30, x+25, -5, fill="#e74c3c", outline="white", tags="apple")
        elif type == "gold":
            item = self.canvas.create_oval(x, -30, x+25, -5, fill="#f1c40f", outline="white", tags="gold")
        elif type == "bomb":
            item = self.canvas.create_oval(x, -30, x+30, 0, fill="#2c3e50", outline="red", width=2, tags="bomb")
        
        self.items.append(item)

    def spawn_loop(self):
        """控制物體生成的節奏"""
        if not self.game_running: return
        
        # 隨機生成邏輯：80% 紅蘋果, 10% 金蘋果, 10% 炸彈
        rand = random.random()
        if rand < 0.8:
            self.create_item("apple")
        elif rand < 0.9:
            self.create_item("gold")
        else:
            self.create_item("bomb")

        # 隨等級加快生成速度
        wait_time = max(400, 1000 - (self.level * 50))
        self.root.after(wait_time, self.spawn_loop)

    def update_loop(self):
        """核心遊戲邏輯更新"""
        if not self.game_running: return

        b_coords = self.canvas.coords(self.basket)

        for item in self.items[:]:
            self.canvas.move(item, 0, self.speed)
            pos = self.canvas.coords(item)
            tag = self.canvas.gettags(item)[0]

            # 1. 碰撞檢測 (接到物體)
            if pos[3] >= b_coords[1] and pos[1] <= b_coords[3] and \
               pos[2] >= b_coords[0] and pos[0] <= b_coords[2]:
                
                if tag == "apple":
                    self.score += 1
                elif tag == "gold":
                    self.score += 5
                elif tag == "bomb":
                    self.end_game("你接到了炸彈！💥")
                    return

                self.cleanup_item(item)
                self.check_level_up()

            # 2. 掉到地上
            elif pos[3] >= HEIGHT:
                if tag != "bomb": # 炸彈掉地上沒關係，蘋果掉地上扣命
                    self.lives -= 1
                    self.update_ui()
                    if self.lives <= 0:
                        self.end_game("蘋果掉光了！🍎")
                        return
                self.cleanup_item(item)

        self.root.after(20, self.update_loop)

    def cleanup_item(self, item):
        self.canvas.delete(item)
        if item in self.items:
            self.items.remove(item)

    def check_level_up(self):
        """更新等級與速度"""
        new_level = (self.score // LEVEL_UP_STEP) + 1
        if new_level > self.level:
            self.level = new_level
            self.speed += 0.8
            self.update_ui()

    def update_ui(self):
        self.canvas.itemconfig(self.ui_score, text=f"SCORE: {self.score}")
        self.canvas.itemconfig(self.ui_lives, text=f"{'❤' * self.lives}")
        self.canvas.itemconfig(self.ui_level, text=f"LEVEL {self.level}")

    def end_game(self, reason):
        self.game_running = False
        # 繪製半透明遮罩效果
        self.canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill="black", stipple="gray50")
        self.canvas.create_text(WIDTH//2, HEIGHT//2 - 50, text="GAME OVER", 
                                font=("Fixedsys", 40, "bold"), fill="#e74c3c")
        self.canvas.create_text(WIDTH//2, HEIGHT//2, text=reason, 
                                font=("微軟正黑體", 18), fill="white")
        self.canvas.create_text(WIDTH//2, HEIGHT//2 + 60, text=f"最終得分: {self.score}", 
                                font=("微軟正黑體", 24, "bold"), fill="#f1c40f")
        self.canvas.create_text(WIDTH//2, HEIGHT - 100, text="請關閉視窗重新挑戰", 
                                font=("微軟正黑體", 12), fill="#95a5a6")

if __name__ == "__main__":
    root = tk.Tk()
    game = UltimateAppleGame(root)
    root.mainloop()