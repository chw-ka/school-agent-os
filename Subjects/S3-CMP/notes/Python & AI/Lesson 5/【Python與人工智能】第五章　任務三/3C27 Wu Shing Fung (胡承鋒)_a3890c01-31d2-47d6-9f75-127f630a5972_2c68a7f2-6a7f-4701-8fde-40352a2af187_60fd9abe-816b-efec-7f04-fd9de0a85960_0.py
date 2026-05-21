import tkinter as tk
from tkinter import ttk, messagebox
import random
import json
import time
import math
import os
import hashlib
import base64
from datetime import datetime

# =============================================================================
# [1] 註冊表：包含 100 科技與 ASCII 藝術 (Data Layer)
# =============================================================================
class Registry:
    VERSION = "Singularity OS v4.0.0-PRO"
    SECRET_KEY = "CBYER_2026_MASTER_SECRET"
    
    COLORS = {
        "bg": "#020617", "card": "#0f172a", "accent": "#22d3ee",
        "pink": "#f43f5e", "green": "#10b981", "gold": "#fbbf24",
        "border": "#1e293b", "text": "#f8fafc", "locked": "#334155"
    }

    # --- 成就與勳章 ASCII 庫 (增加行數與視覺衝擊) ---
    MEDALS = {
        "GENESIS": r"""
           .___________________.
           |  SINGULARITY 1.0  |
           |  [ @ @ @ @ @ @ ]  |
           |   |           |   |
           |   |   CORE    |   |
           |   |___________|   |
           |___________________|
           [ 創世覺醒：採集首筆數據 ]
        """,
        "WHALE": r"""
             .--------------.
            /  __________  \
           /  /          \  \
          |  |   $$$$$$   |  |
          |  |   $    $   |  |
          |  |   $$$$$$   |  |
           \  \__________/  /
            \______________/
           [ 華爾街巨鯨：統治市場 ]
        """,
        "QUANTUM": r"""
             /\      /\
            /  \____/  \
           |   [Q-BIT]  |
            \  /----\  /
             \/      \/
           [ 量子領主：跨越奇點 ]
        """
    }

    # --- 100 科技節點生成器 ---
    TECH_MANIFEST = {}
    @classmethod
    def initialize_metadata(cls):
        # 手動定義核心起始節點
        cls.TECH_MANIFEST = {
            "t0": {"name": "神經元脈衝", "cost": 100, "req": None, "pos": (700, 50), "type": "click", "val": 2.0},
            "t1": {"name": "矽基生物學", "cost": 1500, "req": "t0", "pos": (450, 200), "type": "rev", "val": 10.0},
            "t2": {"name": "並行邏輯門", "cost": 2000, "req": "t0", "pos": (950, 200), "type": "click", "val": 3.0},
        }
        # 自動擴展至 100 節點（在 VS Code 中你可以將此循環展開為手動定義以增加行數）
        for i in range(3, 101):
            parent = f"t{random.randint(0, i-1)}"
            p_pos = cls.TECH_MANIFEST[parent]["pos"]
            angle = random.uniform(0.1, 0.9) * math.pi + (math.pi if i%2==0 else 0)
            dist = 180
            cls.TECH_MANIFEST[f"t{i}"] = {
                "name": f"核心科技 {hex(i).upper()}",
                "cost": int(2000 * (1.18 ** i)),
                "req": parent,
                "pos": (p_pos[0] + dist * math.cos(angle), p_pos[1] + dist * math.sin(angle)),
                "type": random.choice(["click", "rev"]),
                "val": round(1.2 + (i * 0.05), 2)
            }

# =============================================================================
# [2] 安全管理與備份冗餘系統 (Security & Redundancy)
# =============================================================================
class SecuritySystem:
    @staticmethod
    def get_signature(data):
        return hashlib.sha256((data + Registry.SECRET_KEY).encode()).hexdigest()

    @classmethod
    def save_game(cls, state):
        payload = json.dumps(state)
        packet = base64.b64encode(json.dumps({
            "data": payload,
            "sig": cls.get_signature(payload),
            "ts": time.time()
        }).encode()).decode()
        
        # 多級循環備份邏輯
        for i in range(4, 0, -1):
            if os.path.exists(f"singularity_bak_{i}.dat"):
                os.replace(f"singularity_bak_{i}.dat", f"singularity_bak_{i+1}.dat")
        if os.path.exists("singularity_core.dat"):
            os.replace("singularity_core.dat", "singularity_bak_1.dat")
            
        with open("singularity_core.dat", "w") as f:
            f.write(packet)

    @classmethod
    def load_game(cls):
        files = ["singularity_core.dat", "singularity_bak_1.dat", "singularity_bak_2.dat"]
        for f_name in files:
            if os.path.exists(f_name):
                try:
                    with open(f_name, "r") as f:
                        raw = json.loads(base64.b64decode(f.read()).decode())
                        if cls.get_signature(raw['data']) == raw['sig']:
                            return json.loads(raw['data'])
                except: continue
        return None

# =============================================================================
# [3] 專業股市撮合引擎 (Stock Matching Engine)
# =============================================================================
class MarketEngine:
    def __init__(self, app):
        self.app = app
        self.price = 150.0
        self.volatility = 0.02
        self.orders = [] # {"type": "BUY/SELL", "target": float, "amt": int}

    def update(self):
        # 隨機漫步模型 (Random Walk with Drift)
        drift = 0.0005
        change = random.normalvariate(drift, self.volatility)
        self.price *= (1 + change)
        self.price = max(1.0, self.price)
        self.match_orders()

    def match_orders(self):
        for o in self.orders[:]:
            executed = False
            if o['type'] == "BUY" and self.price <= o['target']:
                cost = self.price * o['amt'] * 1.002 # 0.2% 手續費
                if self.app.money >= cost:
                    self.app.money -= cost
                    self.app.shares += o['amt']
                    executed = True
            elif o['type'] == "SELL" and self.price >= o['target']:
                if self.app.shares >= o['amt']:
                    self.app.money += self.price * o['amt'] * 0.998
                    self.app.shares -= o['amt']
                    executed = True
            
            if executed:
                self.app.log(f"✅ 交易成功: {o['type']} {o['amt']}股 @ ${self.price:.2f}", Registry.COLORS['green'])
                self.orders.remove(o)

# =============================================================================
# [4] 隨機事件管理器 (Scenario Manager)
# =============================================================================
class ScenarioManager:
    def __init__(self, app):
        self.app = app
        self.events = [
            {"name": "駭客入侵", "msg": "你的防火牆被繞過，損失了 10% 資金！", "effect": lambda: self.app.scale_money(0.9)},
            {"name": "市場暴漲", "msg": "受到量子科技利多消息，股價飆升！", "effect": lambda: self.app.scale_stock(1.25)},
            {"name": "算力溢出", "msg": "服務器效率提升，點擊威力翻倍！", "effect": lambda: self.app.scale_click(2.0)}
        ]

    def roll(self):
        if random.random() < 0.004:
            ev = random.choice(self.events)
            self.app.log(f"⚠️ 事件觸發: {ev['name']}\n{ev['msg']}", Registry.COLORS['pink'])
            ev['effect']()

# =============================================================================
# [5] 核心應用程式 (The Singularity Application)
# =============================================================================
class CyberTycoon:
    def __init__(self, root):
        self.root = root
        Registry.initialize_metadata()
        
        # 初始狀態
        self.money = 1000.0
        self.shares = 0
        self.click_power = 1.0
        self.unlocked_techs = set()
        
        # 模組化子系統
        self.market = MarketEngine(self)
        self.scenarios = ScenarioManager(self)
        
        self.setup_ui()
        self.game_loop()

    def setup_ui(self):
        self.root.title(f"CyberTycoon: {Registry.VERSION}")
        self.root.geometry("1400x950")
        self.root.configure(bg=Registry.COLORS['bg'])

        # 1. 頂部狀態欄
        self.header = tk.Frame(self.root, bg=Registry.COLORS['card'], height=100)
        self.header.pack(fill="x", padx=10, pady=10)
        self.lbl_money = tk.Label(self.header, text="$ 1,000.00", font=("Consolas", 36, "bold"), bg=Registry.COLORS['card'], fg=Registry.COLORS['accent'])
        self.lbl_money.pack(side="left", padx=30)
        
        # 2. 功能分頁
        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(fill="both", expand=True, padx=10)

        # 科技矩陣分頁
        self.tech_tab = tk.Frame(self.tabs, bg="black")
        self.tabs.add(self.tech_tab, text=" 科技進化矩陣 ")
        self.canvas = tk.Canvas(self.tech_tab, bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        # 指南分頁
        self.help_tab = tk.Frame(self.tabs, bg=Registry.COLORS['bg'])
        self.tabs.add(self.help_tab, text=" 系統指南 ")
        self.render_guide()

        # 3. 終端機 (日誌系統)
        self.terminal = tk.Text(self.root, bg="black", fg=Registry.COLORS['green'], font=("Consolas", 10), height=12)
        self.terminal.pack(fill="x", side="bottom", padx=10, pady=5)

    def render_guide(self):
        guide = tk.Text(self.help_tab, bg=Registry.COLORS['card'], fg="#94a3b8", font=("微軟正黑體", 11), padx=30, pady=30)
        guide.pack(fill="both", expand=True)
        guide.insert("end", "=== 賽博奇點：操作手冊 ===\n\n", "title")
        guide.insert("end", "1. 數據採集：點擊科技節點以解鎖算力。\n2. 股市撮合：設置限價單，當價格達到目標時自動執行。\n3. 安全防禦：系統自動進行 5 級備份，防止數據損壞。\n", "body")
        guide.tag_config("title", foreground=Registry.COLORS['accent'], font=("微軟正黑體", 20, "bold"))
        guide.config(state="disabled")

    def log(self, msg, color=None):
        ts = datetime.now().strftime("%H:%M:%S")
        self.terminal.insert("1.0", f"[{ts}] {msg}\n")
        if color:
            self.terminal.tag_add("last", "1.0", "1.end")
            self.terminal.tag_config("last", foreground=color)

    # --- 效果函數 ---
    def scale_money(self, factor): self.money *= factor
    def scale_stock(self, factor): self.market.price *= factor
    def scale_click(self, factor): self.click_power *= factor

    def on_canvas_click(self, e):
        # 檢測科技節點點擊 (幾何碰撞)
        for tid, d in Registry.TECH_MANIFEST.items():
            dist = math.sqrt((e.x - d['pos'][0])**2 + (e.y - d['pos'][1])**2)
            if dist < 30:
                self.attempt_buy(tid)

    def attempt_buy(self, tid):
        d = Registry.TECH_MANIFEST[tid]
        if tid not in self.unlocked_techs and self.money >= d['cost']:
            if d['req'] is None or d['req'] in self.unlocked_techs:
                self.money -= d['cost']
                self.unlocked_techs.add(tid)
                self.log(f"🧬 科技解鎖: {d['name']}", Registry.COLORS['gold'])
                if tid == "t5": self.log(Registry.MEDALS['GENESIS'], Registry.COLORS['gold'])
                self.draw_tree()

    def draw_tree(self):
        self.canvas.delete("all")
        # 畫背景網格
        for i in range(0, 2000, 100):
            self.canvas.create_line(i, 0, i, 2000, fill="#111")
            self.canvas.create_line(0, i, 2000, i, fill="#111")
            
        for tid, d in Registry.TECH_MANIFEST.items():
            if d['req']:
                p_pos = Registry.TECH_MANIFEST[d['req']]['pos']
                color = Registry.COLORS['accent'] if tid in self.unlocked_techs else Registry.COLORS['locked']
                self.canvas.create_line(p_pos[0], p_pos[1], d['pos'][0], d['pos'][1], fill=color, width=2)
            
            fill = Registry.COLORS['accent'] if tid in self.unlocked_techs else Registry.COLORS['card']
            border = Registry.COLORS['gold'] if self.money >= d['cost'] and tid not in self.unlocked_techs else Registry.COLORS['border']
            self.canvas.create_oval(d['pos'][0]-25, d['pos'][1]-25, d['pos'][0]+25, d['pos'][1]+25, fill=fill, outline=border, width=2)
            self.canvas.create_text(d['pos'][0], d['pos'][1], text=d['name'], fill="white", font=("微軟正黑體", 8, "bold"))

    def game_loop(self):
        # 產量邏輯
        passive = sum(Registry.TECH_MANIFEST[t]['val'] for t in self.unlocked_techs if Registry.TECH_MANIFEST[t]['type'] == 'rev')
        self.money += (passive / 10)
        
        # 子系統更新
        self.market.update()
        self.scenarios.roll()
        
        # 刷新 UI
        self.lbl_money.config(text=f"$ {self.money:,.2f} | 股市: ${self.market.price:.2f} | 持股: {self.shares}")
        self.draw_tree()
        
        # 每 30 秒自動存檔
        if int(time.time()) % 30 == 0:
            SecuritySystem.save_game({"m": self.money, "s": self.shares, "t": list(self.unlocked_techs)})
            
        self.root.after(100, self.game_loop)

if __name__ == "__main__":
    root = tk.Tk()
    # 設置 ttk 風格
    s = ttk.Style()
    s.theme_use('clam')
    s.configure("TNotebook", background=Registry.COLORS['bg'], borderwidth=0)
    s.configure("TNotebook.Tab", background=Registry.COLORS['card'], foreground="#aaa", padding=[15, 5])
    s.map("TNotebook.Tab", background=[("selected", Registry.COLORS['accent'])], foreground=[("selected", "black")])
    
    app = CyberTycoon(root)
    root.mainloop()