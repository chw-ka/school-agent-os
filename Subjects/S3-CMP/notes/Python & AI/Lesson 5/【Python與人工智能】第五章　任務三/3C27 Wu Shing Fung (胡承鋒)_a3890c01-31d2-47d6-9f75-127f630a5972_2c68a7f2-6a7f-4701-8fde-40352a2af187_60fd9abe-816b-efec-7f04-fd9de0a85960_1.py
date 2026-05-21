import tkinter as tk
import random
import math
import time

# ================= 全局常量 =================
class GameConfig:
    W, H = 1100, 950
    GRID_ROWS, GRID_COLS = 5, 6
    CELL_SIZE = 100
    START_X, START_Y = 250, 420
    
    # 數值平衡
    GOLD = 5000
    BASE_HP = 100
    UNIT_PRICE = 200
    PRICE_GROWTH = 1.15
    MERGE_FEE = 50
    
    # 視覺風格
    ACCENT = "#00f2ff"
    BG = "#0b0c10"

# ================= 視覺特效引擎 =================
class FX:
    def __init__(self, canvas):
        self.canvas = canvas
        self.items = [] # 儲存粒子或文字

    def explode(self, x, y, color):
        for _ in range(12):
            dx, dy = random.uniform(-5, 5), random.uniform(-5, 5)
            p = self.canvas.create_oval(x-3, y-3, x+3, y+3, fill=color, outline="")
            self.items.append({"id": p, "v": (dx, dy), "life": 1.0, "type": "p"})

    def float_msg(self, x, y, txt, color="gold"):
        m = self.canvas.create_text(x, y, text=txt, fill=color, font=("Verdana", 14, "bold"))
        self.items.append({"id": m, "v": (0, -2), "life": 1.0, "type": "m"})

    def update(self):
        for item in self.items[:]:
            item["life"] -= 0.05
            self.canvas.move(item["id"], item["v"][0], item["v"][1])
            if item["life"] <= 0:
                self.canvas.delete(item["id"])
                self.items.remove(item)

# ================= 實體類 =================
class Enemy:
    def __init__(self, canvas, wave):
        self.canvas = canvas
        self.max_hp = 150 + (wave * 70)
        self.hp = self.max_hp
        self.spd = 1.5 + (wave * 0.1)
        self.active = True
        self.color = random.choice(["#ff4d4d", "#f9ca24", "#686de0"])
        
        self.id = canvas.create_polygon(self.get_pts(-100, 100), fill=self.color, outline="white", width=2)
        
        # 精密血條動畫層
        self.hp_bg = canvas.create_rectangle(-100, 50, -30, 58, fill="#1a1a1a")
        self.hp_white = canvas.create_rectangle(-100, 50, -30, 58, fill="white") # 緩衝條
        self.hp_main = canvas.create_rectangle(-100, 50, -30, 58, fill="#2ecc71") # 主條

    def get_pts(self, x, y):
        return [x, y, x+40, y+20, x, y+40, x+15, y+20]

    def move(self):
        if not self.active: return
        self.canvas.move(self.id, self.spd, 0)
        c = self.canvas.coords(self.id)
        if not c: return
        x1, y1 = c[0], c[1]
        
        # 血條平滑縮放與位置跟隨
        ratio = max(0, self.hp / self.max_hp)
        self.canvas.coords(self.hp_bg, x1, y1-20, x1+70, y1-12)
        self.canvas.coords(self.hp_main, x1, y1-20, x1 + (70 * ratio), y1-12)
        
        # 緩衝動畫邏輯
        w_c = self.canvas.coords(self.hp_white)
        if w_c[2] > x1 + (70 * ratio):
            self.canvas.coords(self.hp_white, x1, y1-20, w_c[2]-2, y1-12)
        else:
            self.canvas.coords(self.hp_white, x1, y1-20, x1 + (70 * ratio), y1-12)

    def die(self):
        self.canvas.delete(self.id)
        self.canvas.delete(self.hp_bg)
        self.canvas.delete(self.hp_white)
        self.canvas.delete(self.hp_main)
        self.active = False

class Turret:
    def __init__(self, canvas, r, c, lv=1):
        self.canvas = canvas
        self.r, self.c, self.lv = r, c, lv
        self.type = random.choice(["雷射", "重砲", "脈衝"])
        self.x = c * 100 + 300
        self.y = r * 100 + 470
        self.cd = 0
        self.visuals = []
        self.render()

    def render(self):
        for v in self.visuals: self.canvas.delete(v)
        self.visuals = []
        
        colors = {"雷射": "#00f2ff", "重砲": "#eb4d4b", "脈衝": "#be2edd"}
        col = colors[self.type]
        
        # 根據等級呈現不同的樣子
        if self.lv < 4:
            b = self.canvas.create_oval(self.x-35, self.y-35, self.x+35, self.y+35, fill="#1f2833", outline=col, width=2)
        elif self.lv < 8:
            b = self.canvas.create_rectangle(self.x-40, self.y-40, self.x+40, self.y+40, fill="#1f2833", outline=col, width=3)
        else: # 頂級神裝
            b = self.canvas.create_polygon(self.x, self.y-45, self.x+45, self.y, self.x, self.y+45, self.x-45, self.y, fill="#1f2833", outline=col, width=4)
        
        c = self.canvas.create_oval(self.x-20, self.y-20, self.x+20, self.y+20, fill=col)
        t = self.canvas.create_text(self.x, self.y, text=f"{self.type}\nLv.{self.lv}", fill="white", font=("Arial Black", 9))
        self.visuals = [b, c, t]

    def shoot(self, enemies, bullets):
        self.cd += 1
        limit = max(4, 20 - self.lv * 2)
        if self.cd >= limit:
            target = self.find_target(enemies)
            if target:
                bullets.append(Bullet(self.canvas, self.x, self.y, target, 20+self.lv*15, self.type))
                self.cd = 0

    def find_target(self, enemies):
        valid = [e for e in enemies if 0 < self.canvas.coords(e.id)[0] < 1100]
        return max(valid, key=lambda e: e.hp) if valid else None

class Bullet:
    def __init__(self, canvas, x, y, target, dmg, t_type):
        self.canvas = canvas
        self.target, self.dmg = target, dmg
        self.id = canvas.create_line(x, y, x, y, fill="white", width=3)
        self.x, self.y = x, y
        self.spd = 25

    def update(self):
        if not self.target.active: return False
        try:
            c = self.canvas.coords(self.target.id)
            tx, ty = (c[0]+c[4])/2, (c[1]+c[5])/2
            dx, dy = tx - self.x, ty - self.y
            dist = math.hypot(dx, dy)
            if dist < 20:
                self.target.hp -= self.dmg
                return False
            self.x += (dx/dist) * self.spd
            self.y += (dy/dist) * self.spd
            self.canvas.coords(self.id, self.x, self.y, self.x-(dx/dist)*10, self.y-(dy/dist)*10)
            return True
        except: return False

# ================= 核心框架 =================
class StarCommander:
    def __init__(self, root):
        self.root = root
        self.root.title("星際指揮官：終極奧義 v9.0")
        self.canvas = tk.Canvas(root, width=1100, height=950, bg="#050510", highlightthickness=0)
        self.canvas.pack()
        
        self.page = "MENU" # 頁面狀態: MENU, BATTLE
        self.gold = 5000
        self.hp = 100
        self.wave = 1
        self.turrets = {}
        self.enemies = []
        self.bullets = []
        self.fx = FX(self.canvas)
        
        self.show_menu()

    def clear_screen(self):
        self.canvas.delete("all")

    # --- 頁面 1：主菜單 ---
    def show_menu(self):
        self.clear_screen()
        self.canvas.create_text(550, 300, text="星 際 守 衛 者", fill="#00f2ff", font=("Impact", 80))
        self.canvas.create_text(550, 400, text="ETERNAL EVOLUTION", fill="white", font=("Arial", 20, "italic"))
        
        start_btn = self.canvas.create_rectangle(450, 550, 650, 610, fill="#1f2833", outline="#00f2ff", width=2)
        self.canvas.create_text(550, 580, text="開始戰鬥", fill="white", font=("微軟正黑體", 16, "bold"))
        self.canvas.tag_bind(start_btn, "<Button-1>", lambda e: self.start_game())

    # --- 頁面 2：戰鬥前線 ---
    def start_game(self):
        self.page = "BATTLE"
        self.clear_screen()
        self.setup_ui()
        self.setup_grid()
        self.tick()
        self.spawn_wave()

    def setup_ui(self):
        # 頂部狀態欄
        self.canvas.create_rectangle(0, 0, 1100, 100, fill="#1a1a2e", outline="#00f2ff")
        self.gold_ui = self.canvas.create_text(50, 50, anchor="w", text="", fill="gold", font=("Impact", 30))
        self.hp_ui = self.canvas.create_text(350, 50, anchor="w", text="", fill="#ff4d4d", font=("Impact", 20))
        self.wave_ui = self.canvas.create_text(1100//2+100, 50, text="", fill="white", font=("Impact", 35))
        
        # 功能按鈕
        m_btn = self.canvas.create_rectangle(900, 30, 1050, 70, fill="#4834d4", outline="white")
        self.canvas.create_text(975, 50, text="一鍵合成 (50G)", fill="white", font=("微軟正黑體", 10, "bold"))
        self.canvas.tag_bind(m_btn, "<Button-1>", lambda e: self.auto_merge())

    def setup_grid(self):
        for r in range(5):
            for c in range(6):
                x, y = c*100+250, r*100+420
                grid = self.canvas.create_rectangle(x, y, x+95, y+95, fill="#0f172a", outline="#1e293b")
                self.canvas.tag_bind(grid, "<Button-1>", lambda e, p=(r,c): self.click_grid(p))

    def click_grid(self, pos):
        price = int(200 * (1.15 ** len(self.turrets)))
        if pos in self.turrets:
            # 手動合成邏輯省略...
            pass
        elif self.gold >= price:
            self.gold -= price
            self.turrets[pos] = Turret(self.canvas, pos[0], pos[1])
            self.fx.float_msg(pos[1]*100+300, pos[0]*100+470, f"-{price}G", "red")

    def auto_merge(self):
        keys = list(self.turrets.keys())
        for i in range(len(keys)):
            for j in range(i+1, len(keys)):
                p1, p2 = keys[i], keys[j]
                if p1 in self.turrets and p2 in self.turrets:
                    t1, t2 = self.turrets[p1], self.turrets[p2]
                    if t1.lv == t2.lv and t1.type == t2.type and self.gold >= 50:
                        self.gold -= 50
                        self.turrets.pop(p1); t1.render() # 簡單銷毀
                        t2.lv += 1; t2.render()
                        self.fx.explode(t2.x, t2.y, "white")
                        return self.auto_merge()

    def tick(self):
        if self.page != "BATTLE": return
        self.fx.update()
        for t in self.turrets.values(): t.shoot(self.enemies, self.bullets)
        for b in self.bullets[:]:
            if not b.update():
                self.canvas.delete(b.id); self.bullets.remove(b)
        for e in self.enemies[:]:
            e.move()
            if self.canvas.coords(e.id)[0] > 1100:
                self.hp -= 10; e.die(); self.enemies.remove(e)
            elif e.hp <= 0:
                self.gold += 100; self.fx.explode(self.canvas.coords(e.id)[0], 400, e.color)
                e.die(); self.enemies.remove(e)
        
        self.update_ui_text()
        self.root.after(30, self.tick)

    def spawn_wave(self):
        if self.page == "BATTLE":
            for _ in range(5 + self.wave): self.enemies.append(Enemy(self.canvas, self.wave))
            self.wave += 1
            self.root.after(12000, self.spawn_wave)

    def update_ui_text(self):
        self.canvas.itemconfig(self.gold_ui, text=f"💰 {self.gold}")
        self.canvas.itemconfig(self.hp_ui, text=f"基 地 護 盾: {self.hp}%")
        self.canvas.itemconfig(self.wave_ui, text=f"第 {self.wave-1} 波攻勢")

if __name__ == "__main__":
    root = tk.Tk()
    StarCommander(root)
    root.mainloop()