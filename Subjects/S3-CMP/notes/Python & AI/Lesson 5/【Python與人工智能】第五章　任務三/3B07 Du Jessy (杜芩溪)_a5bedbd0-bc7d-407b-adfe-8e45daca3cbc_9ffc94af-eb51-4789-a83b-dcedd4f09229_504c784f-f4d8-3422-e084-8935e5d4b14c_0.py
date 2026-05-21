import tkinter as tk
from tkinter import messagebox
import random
import math
import time

class TouhouCatGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("東方喵幻想：甜點保衛戰 🐱🌸")
        self.root.geometry("500x750")
        self.root.resizable(False, False)

        # 遊戲變數
        self.is_running = False
        self.difficulty = tk.StringVar(value="Normal")
        self.boss_hp = 100
        self.cat_hp = 100
        self.start_time = 0
        self.bullets = []
        self.cat_bullets = []
        self.boss_dir = 1
        self.is_pressing = False
        self.leaderboard = [] # 儲存秒數

        self.show_story_screen()

    def show_story_screen(self):
        """故事介紹與難度選擇畫面"""
        self.start_canvas = tk.Canvas(self.root, width=500, height=750)
        self.start_canvas.pack()

        # 深藍到粉色的漸變背景
        for i in range(750):
            r = int(10 + (255 - 10) * (i / 750))
            g = int(20 + (182 - 20) * (i / 750))
            b = int(60 + (193 - 60) * (i / 750))
            self.start_canvas.create_line(0, i, 500, i, fill=f'#{r:02x}{g:02x}{b:02x}')

        story_text = (
            "✨ 【 故事背景 】 ✨\n\n"
            "傳說在喵星的幻想鄉，甜點是力量的來源。\n"
            "白色外星飛船突然降臨，試圖奪走所有糖果！\n"
            "黃色小貓將挺身而出，在 30 秒內擊落敵機。\n\n"
            "🌸 【 操作指南 】 🌸\n\n"
            "● 移動滑鼠：控制小貓，避開符號煙花。\n"
            "● 核心判定：只有擊中中心的「紅點」才會受傷。\n"
            "● 長按攻擊：滑鼠左鍵長按，發射「顏文字」攻擊。\n"
            "● 目標：擊墜飛船，挑戰排行榜最速紀錄！"
        )
        self.start_canvas.create_text(250, 280, text=story_text, font=('Microsoft JhengHei', 12, 'bold'), 
                                     fill="#FFF0F5", justify="center")

        # 難度選擇按鈕
        diff_frame = tk.Frame(self.root, bg="#FFC0CB")
        for d, v in [("簡單", "Easy"), ("普通", "Normal"), ("困難", "Hard")]:
            tk.Radiobutton(diff_frame, text=d, variable=self.difficulty, value=v, 
                           font=('Microsoft JhengHei', 10), bg="#FFC0CB").pack(side="left", padx=10)
        self.start_canvas.create_window(250, 480, window=diff_frame)

        btn = tk.Button(self.root, text="進入幻想鄉 (ฅ'ω'ฅ)", font=('Microsoft JhengHei', 14, 'bold'),
                        command=self.start_game, bg="white", fg="#FF69B4", relief="flat")
        self.start_canvas.create_window(250, 580, window=btn)

    def start_game(self):
        self.start_canvas.destroy()
        self.setup_battle_ui()
        self.is_running = True
        self.boss_hp = 100
        self.cat_hp = 100
        self.bullets = []
        self.cat_bullets = []
        self.start_time = time.time()
        self.spawn_loop()
        self.game_loop()

    def setup_battle_ui(self):
        self.canvas = tk.Canvas(self.root, width=500, height=750, bg="#05051A")
        self.canvas.pack()

        # 白色外星飛船
        self.boss = self.canvas.create_text(250, 100, text="🛸", font=('Arial', 80), fill="white")
        
        # 血條介面 (Boss 上，小貓下)
        self.canvas.create_text(50, 30, text="BOSS", fill="white", font=('Arial', 10, 'bold'))
        self.boss_bar = self.canvas.create_rectangle(80, 25, 450, 35, fill="#FF1493")
        
        self.canvas.create_text(50, 720, text="CAT", fill="white", font=('Arial', 10, 'bold'))
        self.cat_bar = self.canvas.create_rectangle(80, 715, 450, 725, fill="#00FF7F")

        # 黃色小貓與判定點
        self.cat = self.canvas.create_oval(0,0,36,36, fill="#FFD700", outline="#FFA500", width=2)
        self.hitbox = self.canvas.create_oval(0,0,8,8, fill="red", outline="white") # 判定點
        self.cat_face = self.canvas.create_text(0,0, text="OwO", font=('Arial', 8, 'bold'))

        self.root.bind("<Motion>", self.mouse_move)
        self.root.bind("<ButtonPress-1>", lambda e: setattr(self, 'is_pressing', True))
        self.root.bind("<ButtonRelease-1>", lambda e: setattr(self, 'is_pressing', False))

    def mouse_move(self, e):
        self.canvas.coords(self.cat, e.x-18, e.y-18, e.x+18, e.y+18)
        self.canvas.coords(self.hitbox, e.x-4, e.y-4, e.x+4, e.y+4)
        self.canvas.coords(self.cat_face, e.x, e.y)

    def spawn_loop(self):
        """彈幕發射 (Hard 模式使用 Minimax 邏輯預判玩家)"""
        if not self.is_running: return
        
        diff = self.difficulty.get()
        bx, by = self.canvas.coords(self.boss)
        hx, hy = self.canvas.coords(self.hitbox)[0:2]

        # 煙花符號
        sym = random.choice(["🌸", "✨", "⭐", "🍭", "🍀", "🎀", "🔮"])
        
        # 密度設定
        count = 1 if diff == "Easy" else (3 if diff == "Normal" else 8)
        interval = 150 if diff == "Easy" else (70 if diff == "Normal" else 30)

        for _ in range(count):
            if diff == "Hard":
                # 困難：自機狙 (鎖定玩家位置並帶有微幅偏移覆蓋)
                angle = math.atan2(hy - by, hx - bx) + random.uniform(-0.1, 0.1)
            else:
                angle = random.uniform(0.5, 2.6)

            speed = random.randint(4, 10)
            bid = self.canvas.create_text(bx, by+40, text=sym, font=('Arial', 18), fill="#FFB6C1")
            self.bullets.append({'id': bid, 'vx': math.cos(angle)*speed, 'vy': math.sin(angle)*speed})
            
        self.root.after(interval, self.spawn_loop)

    def game_loop(self):
        if not self.is_running: return

        # 1. 飛船移動
        b_speed = 5 if self.difficulty.get() != "Hard" else 12
        self.canvas.move(self.boss, b_speed * self.boss_dir, 0)
        bx = self.canvas.coords(self.boss)[0]
        if bx > 450 or bx < 50: self.boss_dir *= -1

        # 2. 小貓長按攻擊
        if self.is_pressing:
            cx, cy = self.canvas.coords(self.hitbox)[0:2]
            atk_text = random.choice(["(>᎑<)", "(ฅ'ω'ฅ)", "✧", "♥", "Nya!"])
            aid = self.canvas.create_text(cx+4, cy-25, text=atk_text, fill="#FFD700", font=('Arial', 10, 'bold'))
            self.cat_bullets.append(aid)

        # 3. 更新子彈位置與碰撞檢測
        self.update_objects()

        # 4. 檢查勝負條件
        elapsed = time.time() - self.start_time
        if self.boss_hp <= 0:
            self.end_game(f"Happy End! ✧*｡٩(ˊᗜˋ*)و✧*｡\n白色飛船已墜毀！\n你的戰鬥時間：{elapsed:.2f}秒")
        elif self.cat_hp <= 0:
            self.end_game("Game Over (╥﹏╥)\n小貓力竭了，再試一次吧！")
        else:
            self.root.after(20, self.game_loop)

    def update_objects(self):
        # 敵方子彈
        hx1, hy1, hx2, hy2 = self.canvas.coords(self.hitbox)
        for b in self.bullets[:]:
            self.canvas.move(b['id'], b['vx'], b['vy'])
            x, y = self.canvas.coords(b['id'])
            # 碰撞中心紅點
            if hx1 < x < hx2 and hy1 < y < hy2:
                self.cat_hp -= 2
                self.canvas.delete(b['id'])
                self.bullets.remove(b)
            elif y > 750:
                self.canvas.delete(b['id'])
                self.bullets.remove(b)

        # 玩家颜文字子彈
        bx1, by1, bx2, by2 = self.canvas.bbox(self.boss)
        for cb in self.cat_bullets[:]:
            self.canvas.move(cb, 0, -18)
            x, y = self.canvas.coords(cb)
            if bx1 < x < bx2 and by1 < y < by2:
                self.boss_hp -= 1
                self.canvas.delete(cb)
                self.cat_bullets.remove(cb)
            elif y < 0:
                self.canvas.delete(cb)
                self.cat_bullets.remove(cb)
        
        # 更新血條視覺
        self.canvas.coords(self.boss_bar, 80, 25, 80 + (370 * max(0, self.boss_hp)/100), 35)
        self.canvas.coords(self.cat_bar, 80, 715, 80 + (370 * max(0, self.cat_hp)/100), 725)

    def end_game(self, msg):
        self.is_running = False
        messagebox.showinfo("結局", msg)
        self.root.destroy()

if __name__ == "__main__":
    game = TouhouCatGame()
    game.root.mainloop()