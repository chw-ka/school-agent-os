import tkinter as tk
from tkinter import messagebox
import random

class StarDodger:
    def __init__(self, root):
        self.root = root
        self.root.title("Task3_3X99 - 星際躲避者")
        self.root.resizable(False, False)

        # 遊戲參數
        self.width = 400
        self.height = 500
        self.score = 0
        self.speed = 5
        self.combo = 0
        self.game_over = False

        # 畫布設定
        self.canvas = tk.Canvas(root, width=self.width, height=self.height, bg="#000d1a", highlightthickness=0)
        self.canvas.pack()

        # 玩家角色 (方塊)
        self.player_size = 30
        self.player = self.canvas.create_rectangle(
            self.width//2 - 15, self.height - 50,
            self.width//2 + 15, self.height - 20,
            fill="#00ffcc", outline="#ffffff"
        )

        # UI 顯示
        self.score_text = self.canvas.create_text(60, 20, text="Score: 0", fill="white", font=("Courier", 14))
        self.combo_text = self.canvas.create_text(60, 40, text="Combo: 0", fill="#ff3366", font=("Courier", 12))

        # 障礙物列表
        self.enemies = []
        
        # 綁定按鍵
        self.root.bind("<Left>", lambda e: self.move_player(-25))
        self.root.bind("<Right>", lambda e: self.move_player(25))

        self.spawn_enemy()
        self.update_game()

    def move_player(self, dx):
        if self.game_over: return
        pos = self.canvas.coords(self.player)
        if pos[0] + dx >= 0 and pos[2] + dx <= self.width:
            self.canvas.move(self.player, dx, 0)

    def spawn_enemy(self):
        if not self.game_over:
            x_pos = random.randint(0, self.width - 30)
            enemy = self.canvas.create_oval(x_pos, -30, x_pos + 30, 0, fill="#ffcc00", outline="")
            self.enemies.append(enemy)
            # 隨遊戲進展加快生成速度
            spawn_time = max(300, 800 - (self.score * 5))
            self.root.after(spawn_time, self.spawn_enemy)

    def update_game(self):
        if self.game_over: return

        # 移動障礙物
        for enemy in self.enemies[:]:
            self.canvas.move(enemy, 0, self.speed)
            e_pos = self.canvas.coords(enemy)

            # 碰撞偵測
            p_pos = self.canvas.coords(self.player)
            if self.is_collision(p_pos, e_pos):
                self.end_game()
                return

            # 成功避開
            if e_pos[1] > self.height:
                self.canvas.delete(enemy)
                self.enemies.remove(enemy)
                self.score += 10 + (self.combo * 2)
                self.combo += 1
                self.speed = 5 + (self.score // 200) # 難度遞增
                self.update_ui()

        self.root.after(30, self.update_game)

    def is_collision(self, p, e):
        return not (p[2] < e[0] or p[0] > e[2] or p[3] < e[1] or p[1] > e[3])

    def update_ui(self):
        self.canvas.itemconfig(self.score_text, text=f"Score: {self.score}")
        self.canvas.itemconfig(self.combo_text, text=f"Combo: {self.combo}")

    def end_game(self):
        self.game_over = True
        self.canvas.create_text(self.width//2, self.height//2, 
                                text="GAME OVER", fill="#ff3366", 
                                font=("Arial", 30, "bold"))
        messagebox.showinfo("最終得分", f"你的連擊: {self.combo}\n最終總分: {self.score}")

if __name__ == "__main__":
    window = tk.Tk()
    game = StarDodger(window)
    window.mainloop()