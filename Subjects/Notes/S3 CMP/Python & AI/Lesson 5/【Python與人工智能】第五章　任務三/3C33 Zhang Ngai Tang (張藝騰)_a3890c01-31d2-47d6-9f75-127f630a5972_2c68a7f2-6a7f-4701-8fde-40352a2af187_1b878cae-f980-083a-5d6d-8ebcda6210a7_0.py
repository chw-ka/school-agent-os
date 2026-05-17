import tkinter as tk
from tkinter import messagebox, ttk
import random
import math
from datetime import datetime

class DeltaForceGame:
    def __init__(self, root):
        self.root = root
        self.root.title("三角洲行动 - 搜打撤")
        self.root.geometry("1200x700")
        self.root.resizable(False, False)

        # ========== 游戏配置 ==========
        self.grid_size = 10         # 10x10 网格
        self.cell_size = 55

        # ========== 玩家属性 ==========
        self.player = {
            "name": "三角洲队员",
            "hp": 120,
            "max_hp": 120,
            "attack": 28,
            "defense": 8,
            "level": 1,
            "xp": 0,
            "money": 500,           # 行动资金
            "row": 0,
            "col": 0,
            "inventory": {          # 装备/物品
                "medkit": 2,        # 医疗包
                "grenade": 1,       # 手雷
                "ammo": 3           # 弹药包
            }
        }

        # ========== 任务目标 ==========
        self.mission = {
            "target_kills": random.randint(3, 5),   # 需要击杀的敌人数量
            "current_kills": 0,
            "time_limit": 45,        # 45回合限制
            "turn_count": 0
        }

        # ========== 游戏状态 ==========
        self.game_over = False
        self.turn_mode = 'explore'   # explore / combat / shop
        self.current_enemy = None
        self.selected_action = None

        # ========== 地图元素 ==========
        self.enemies = []            # [row, col, name, hp, max_hp, attack, defense, xp, money_reward]
        self.exit_pos = None
        self.obstacles = set()
        self.items = []              # [row, col, type, value, name, emoji]
        self.shop_pos = None         # 随机商店位置

        # ========== 战斗日志 ==========
        self.battle_log = []

        # ========== UI 组件 ==========
        self.create_widgets()
        self.generate_map()
        self.update_all_displays()
        self.draw_map()

    def generate_map(self):
        """生成战术地图"""
        # 重置数据
        self.enemies = []
        self.obstacles = set()
        self.items = []
        self.player["row"], self.player["col"] = 0, 0
        self.player["hp"] = self.player["max_hp"]
        self.mission["current_kills"] = 0
        self.mission["turn_count"] = 0
        self.turn_mode = 'explore'
        self.game_over = False

        # 撤离点：地图右下角区域
        exit_options = [(9,9), (9,8), (8,9), (8,8), (7,9)]
        self.exit_pos = random.choice(exit_options)

        # 商店：随机位置（不在地图边缘）
        while True:
            row = random.randint(2, self.grid_size-3)
            col = random.randint(2, self.grid_size-3)
            if (row, col) != (0,0) and (row, col) != self.exit_pos:
                self.shop_pos = (row, col)
                break

        # 生成敌人（8-12个，不同种类）
        enemy_types = [
            {"name": "🇹🇷 武装分子", "hp": 35, "attack": 14, "defense": 3, "xp": 25, "money": 80, "emoji": "🎯"},
            {"name": "🛡️ 重装兵", "hp": 65, "attack": 18, "defense": 8, "xp": 45, "money": 120, "emoji": "🛡️"},
            {"name": "🏃 突击兵", "hp": 40, "attack": 16, "defense": 4, "xp": 30, "money": 90, "emoji": "⚡"},
            {"name": "🔫 狙击手", "hp": 30, "attack": 22, "defense": 2, "xp": 35, "money": 100, "emoji": "🎯"},
            {"name": "💣 爆破兵", "hp": 50, "attack": 20, "defense": 5, "xp": 40, "money": 110, "emoji": "💣"},
            {"name": "👑 指挥官", "hp": 80, "attack": 15, "defense": 10, "xp": 60, "money": 200, "emoji": "👑"},
        ]

        num_enemies = random.randint(8, 12)
        enemy_positions = set()

        for _ in range(num_enemies):
            while True:
                row = random.randint(1, self.grid_size-2)
                col = random.randint(1, self.grid_size-2)
                if (row, col) == (0,0) or (row, col) == self.exit_pos or (row, col) == self.shop_pos:
                    continue
                if (row, col) in enemy_positions:
                    continue
                enemy_positions.add((row, col))
                enemy_type = random.choice(enemy_types)
                self.enemies.append([
                    row, col,
                    enemy_type["name"], enemy_type["emoji"],
                    enemy_type["hp"], enemy_type["hp"],
                    enemy_type["attack"], enemy_type["defense"],
                    enemy_type["xp"], enemy_type["money"]
                ])
                break

        # 生成障碍物（15-20个）
        num_obstacles = random.randint(15, 20)
        enemy_coords = {(e[0], e[1]) for e in self.enemies}
        while len(self.obstacles) < num_obstacles:
            row = random.randint(0, self.grid_size-1)
            col = random.randint(0, self.grid_size-1)
            if (row, col) == (0,0) or (row, col) == self.exit_pos or (row, col) == self.shop_pos:
                continue
            if (row, col) in enemy_coords:
                continue
            self.obstacles.add((row, col))

        # 生成补给品（8-10个）
        num_items = random.randint(8, 10)
        item_types = [
            {"type": "medkit", "name": "医疗包", "value": 40, "emoji": "💊", "cost": 0},
            {"type": "medkit_small", "name": "绷带", "value": 20, "emoji": "🩹", "cost": 0},
            {"type": "ammo", "name": "弹药包", "value": 1, "emoji": "📦", "cost": 0},
            {"type": "grenade", "name": "手雷", "value": 1, "emoji": "💣", "cost": 0},
        ]

        item_positions = set()
        while len(self.items) < num_items:
            row = random.randint(0, self.grid_size-1)
            col = random.randint(0, self.grid_size-1)
            if (row, col) == (0,0) or (row, col) == self.exit_pos or (row, col) == self.shop_pos:
                continue
            if (row, col) in enemy_coords or (row, col) in self.obstacles:
                continue
            if (row, col) in item_positions:
                continue
            item_positions.add((row, col))
            item_type = random.choice(item_types)
            self.items.append([row, col, item_type["type"], item_type["value"], item_type["name"], item_type["emoji"]])

    def create_widgets(self):
        """创建游戏界面"""
        # 主框架
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # ========== 左侧：地图区域 ==========
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 地图画布
        self.canvas = tk.Canvas(left_frame, width=self.grid_size * self.cell_size,
                                height=self.grid_size * self.cell_size, bg='#1a1a2e', highlightthickness=2)
        self.canvas.pack()
        self.canvas.bind('<Button-1>', self.on_cell_click)

        # ========== 右侧：信息面板 ==========
        right_frame = tk.Frame(main_frame, width=350)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)
        right_frame.pack_propagate(False)

        # 玩家状态卡片
        status_card = tk.LabelFrame(right_frame, text="📋 作战状态", font=('Arial', 12, 'bold'), fg='#4a9eff')
        status_card.pack(fill=tk.X, pady=5)

        self.hp_bar = ttk.Progressbar(status_card, length=200, mode='determinate')
        self.hp_bar.pack(pady=5)

        self.hp_label = tk.Label(status_card, text="", font=('Arial', 11))
        self.hp_label.pack()

        self.stats_label = tk.Label(status_card, text="", font=('Arial', 10))
        self.stats_label.pack()

        self.money_label = tk.Label(status_card, text="", font=('Arial', 11, 'bold'), fg='gold')
        self.money_label.pack()

        # 任务目标卡片
        mission_card = tk.LabelFrame(right_frame, text="🎯 任务目标", font=('Arial', 12, 'bold'), fg='#ffaa44')
        mission_card.pack(fill=tk.X, pady=5)

        self.mission_label = tk.Label(mission_card, text="", font=('Arial', 11))
        self.mission_label.pack(pady=5)

        self.turn_label = tk.Label(mission_card, text="", font=('Arial', 10), fg='orange')
        self.turn_label.pack()

        # 装备栏
        inventory_card = tk.LabelFrame(right_frame, text="🎒 装备栏", font=('Arial', 12, 'bold'), fg='#66ff66')
        inventory_card.pack(fill=tk.X, pady=5)

        self.inventory_labels = {}
        items = [("medkit", "💊 医疗包"), ("grenade", "💣 手雷"), ("ammo", "📦 弹药包")]
        for item_id, item_name in items:
            frame = tk.Frame(inventory_card)
            frame.pack(fill=tk.X, padx=10, pady=2)
            label = tk.Label(frame, text=f"{item_name}: {self.player['inventory'].get(item_id, 0)}", font=('Arial', 10))
            label.pack(side=tk.LEFT)
            self.inventory_labels[item_id] = label
            btn = tk.Button(frame, text="使用", font=('Arial', 8), command=lambda i=item_id: self.use_item(i))
            btn.pack(side=tk.RIGHT)

        # 战斗日志
        log_card = tk.LabelFrame(right_frame, text="📜 行动日志", font=('Arial', 12, 'bold'))
        log_card.pack(fill=tk.BOTH, expand=True, pady=5)

        self.log_text = tk.Text(log_card, height=12, font=('Courier', 9), bg='#2d2d2d', fg='#ddd')
        scrollbar = tk.Scrollbar(log_card, command=self.log_text.yview)
        self.log_text.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 战斗按钮（动态显示）
        self.combat_frame = tk.Frame(right_frame)
        self.combat_frame.pack(pady=10)

        self.attack_btn = tk.Button(self.combat_frame, text="🔫 攻击", font=('Arial', 12),
                                    command=self.combat_attack, bg='#dc3545', fg='white', width=10)
        self.attack_btn.pack(side=tk.LEFT, padx=5)

        self.grenade_btn = tk.Button(self.combat_frame, text="💣 手雷", font=('Arial', 12),
                                     command=self.combat_grenade, bg='#ff9800', fg='white', width=10)
        self.grenade_btn.pack(side=tk.LEFT, padx=5)

        self.retreat_btn = tk.Button(self.combat_frame, text="🏃 战术撤退", font=('Arial', 12),
                                     command=self.combat_retreat, bg='#6c757d', fg='white', width=10)
        self.retreat_btn.pack(side=tk.LEFT, padx=5)

        # 重置按钮
        reset_btn = tk.Button(right_frame, text="🔄 重新部署", font=('Arial', 12),
                              command=self.reset_game, bg='#28a745', fg='white')
        reset_btn.pack(pady=5, fill=tk.X)

        # 初始隐藏战斗按钮
        self.show_combat_buttons(False)

    def show_combat_buttons(self, show):
        """显示/隐藏战斗按钮"""
        if show:
            self.attack_btn.pack(side=tk.LEFT, padx=5)
            self.grenade_btn.pack(side=tk.LEFT, padx=5)
            self.retreat_btn.pack(side=tk.LEFT, padx=5)
        else:
            self.attack_btn.pack_forget()
            self.grenade_btn.pack_forget()
            self.retreat_btn.pack_forget()

    def draw_map(self):
        """绘制战术地图"""
        self.canvas.delete('all')

        for row in range(self.grid_size):
            for col in range(self.grid_size):
                x1 = col * self.cell_size
                y1 = row * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                # 背景色
                if (row, col) == (self.player["row"], self.player["col"]):
                    bg_color = '#2a5a2a'
                elif (row, col) == self.exit_pos:
                    bg_color = '#2a5a3a'
                elif (row, col) == self.shop_pos:
                    bg_color = '#3a2a5a'
                elif (row, col) in self.obstacles:
                    bg_color = '#4a3a2a'
                else:
                    bg_color = '#1a1a2e'

                self.canvas.create_rectangle(x1, y1, x2, y2, outline='#3a3a5a', fill=bg_color, width=1)

                # 绘制内容
                if (row, col) == self.exit_pos:
                    self.canvas.create_text(x1 + self.cell_size//2, y1 + self.cell_size//2,
                                            text='🚁', font=('Arial', 28))
                    self.canvas.create_text(x1 + self.cell_size//2, y1 + self.cell_size - 10,
                                            text='撤离点', font=('Arial', 8), fill='#aaa')

                elif (row, col) == self.shop_pos:
                    self.canvas.create_text(x1 + self.cell_size//2, y1 + self.cell_size//2,
                                            text='🏪', font=('Arial', 28))
                    self.canvas.create_text(x1 + self.cell_size//2, y1 + self.cell_size - 10,
                                            text='军火商', font=('Arial', 8), fill='#aaa')

                elif (row, col) in self.obstacles:
                    self.canvas.create_text(x1 + self.cell_size//2, y1 + self.cell_size//2,
                                            text='🧱', font=('Arial', 24))

                else:
                    # 敌人
                    enemy_here = None
                    for enemy in self.enemies:
                        if enemy[0] == row and enemy[1] == col and enemy[4] > 0:
                            enemy_here = enemy
                            break

                    if enemy_here:
                        self.canvas.create_rectangle(x1, y1, x2, y2, fill='#5a2a2a', outline='#aa4444', width=2)
                        self.canvas.create_text(x1 + self.cell_size//2, y1 + self.cell_size//2 - 8,
                                                text=enemy_here[3], font=('Arial', 20))
                        self.canvas.create_text(x1 + self.cell_size//2, y1 + self.cell_size//2 + 10,
                                                text=f'{enemy_here[2]}', font=('Arial', 8), fill='#ff8888')
                    else:
                        # 物品
                        item_here = None
                        for item in self.items:
                            if item[0] == row and item[1] == col:
                                item_here = item
                                break

                        if item_here:
                            self.canvas.create_text(x1 + self.cell_size//2, y1 + self.cell_size//2,
                                                    text=item_here[5], font=('Arial', 26))

        # 绘制玩家
        x1 = self.player["col"] * self.cell_size
        y1 = self.player["row"] * self.cell_size
        self.canvas.create_oval(x1 + 8, y1 + 8, x1 + self.cell_size - 8, y1 + self.cell_size - 8,
                                fill='#4a9eff', outline='white', width=3)
        self.canvas.create_text(x1 + self.cell_size//2, y1 + self.cell_size//2,
                                text='🔺', font=('Arial', 20))

    def update_all_displays(self):
        """更新所有UI显示"""
        # 血条
        hp_percent = (self.player["hp"] / self.player["max_hp"]) * 100
        self.hp_bar['value'] = hp_percent
        self.hp_label.config(text=f"❤️ 生命值: {self.player['hp']}/{self.player['max_hp']}")

        # 属性
        self.stats_label.config(text=f"⚔️ 攻击 {self.player['attack']}  |  🛡️ 防御 {self.player['defense']}  |  ⭐ Lv.{self.player['level']}")

        # 资金
        self.money_label.config(text=f"💰 行动资金: ${self.player['money']}")

        # 任务
        self.mission_label.config(text=f"🎯 击杀敌人: {self.mission['current_kills']}/{self.mission['target_kills']}")
        remaining_turns = self.mission['time_limit'] - self.mission['turn_count']
        self.turn_label.config(text=f"⏱️ 剩余回合: {remaining_turns}")

        # 装备栏
        for item_id, label in self.inventory_labels.items():
            label.config(text=f"{self.get_item_icon(item_id)} {self.get_item_name(item_id)}: {self.player['inventory'].get(item_id, 0)}")

    def get_item_icon(self, item_id):
        icons = {"medkit": "💊", "grenade": "💣", "ammo": "📦"}
        return icons.get(item_id, "📦")

    def get_item_name(self, item_id):
        names = {"medkit": "医疗包", "grenade": "手雷", "ammo": "弹药包"}
        return names.get(item_id, "物品")

    def add_log(self, message, color='#ddd'):
        """添加行动日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.battle_log.append(log_entry)
        self.log_text.insert(tk.END, log_entry + "\n")
        self.log_text.see(tk.END)
        if len(self.battle_log) > 100:
            self.battle_log.pop(0)

    def use_item(self, item_id):
        """使用物品"""
        if self.game_over or self.turn_mode == 'combat':
            self.add_log("⚠️ 现在无法使用物品", '#ffaa44')
            return

        if self.player['inventory'].get(item_id, 0) <= 0:
            self.add_log(f"⚠️ 没有{self.get_item_name(item_id)}了！", '#ffaa44')
            return

        if item_id == 'medkit':
            heal = 40
            old_hp = self.player['hp']
            self.player['hp'] = min(self.player['max_hp'], self.player['hp'] + heal)
            self.player['inventory']['medkit'] -= 1
            self.add_log(f"💊 使用医疗包！恢复 {self.player['hp'] - old_hp} 生命值", '#4caf50')

        elif item_id == 'ammo':
            # 弹药包：增加攻击力（临时）
            self.player['attack'] += 5
            self.player['inventory']['ammo'] -= 1
            self.add_log(f"📦 使用弹药包！攻击力 +5（持续本场战斗）", '#ff9800')

        elif item_id == 'grenade':
            self.add_log(f"💣 手雷只能在战斗中使用！", '#ffaa44')
            return

        self.update_all_displays()
        self.mission['turn_count'] += 1
        self.check_time_limit()

    def on_cell_click(self, event):
        """点击移动"""
        if self.game_over:
            return
        if self.turn_mode == 'combat':
            self.add_log("⚔️ 战斗中！请使用战斗按钮", '#ffaa44')
            return
        if self.turn_mode == 'shop':
            return

        col = event.x // self.cell_size
        row = event.y // self.cell_size

        if row < 0 or row >= self.grid_size or col < 0 or col >= self.grid_size:
            return

        # 曼哈顿距离移动
        if abs(row - self.player["row"]) + abs(col - self.player["col"]) != 1:
            self.add_log("⚠️ 只能移动到相邻格子", '#ffaa44')
            return

        # 障碍物检查
        if (row, col) in self.obstacles:
            self.add_log("🧱 障碍物阻挡，无法通过！", '#ffaa44')
            return

        # 移动
        self.player["row"], self.player["col"] = row, col
        self.mission['turn_count'] += 1

        # 检查商店
        if (row, col) == self.shop_pos:
            self.open_shop()
            return

        # 拾取物品
        self.check_pickup()

        # 遭遇敌人
        self.check_encounter()

        # 检查撤离
        if (row, col) == self.exit_pos:
            self.check_extraction()

        # 更新时间限制
        self.check_time_limit()

        # 更新界面
        self.draw_map()
        self.update_all_displays()

    def open_shop(self):
        """打开军火商店"""
        self.turn_mode = 'shop'
        shop_window = tk.Toplevel(self.root)
        shop_window.title("🏪 军火商 - 购买装备")
        shop_window.geometry("400x300")
        shop_window.transient(self.root)
        shop_window.grab_set()

        tk.Label(shop_window, text="🏪 黑市军火商", font=('Arial', 16, 'bold'), fg='gold').pack(pady=10)

        shop_items = [
            ("💊 医疗包", 80, "medkit"),
            ("💣 手雷", 120, "grenade"),
            ("📦 弹药包", 60, "ammo"),
            ("🔫 攻击强化", 150, "attack_boost"),
            ("🛡️ 防御强化", 150, "defense_boost"),
        ]

        for name, price, item_id in shop_items:
            frame = tk.Frame(shop_window)
            frame.pack(fill=tk.X, padx=20, pady=5)

            tk.Label(frame, text=f"{name} - ${price}", font=('Arial', 11)).pack(side=tk.LEFT)

            def buy(i=item_id, p=price):
                if self.player['money'] >= p:
                    if i == "medkit":
                        self.player['inventory']['medkit'] = self.player['inventory'].get('medkit', 0) + 1
                    elif i == "grenade":
                        self.player['inventory']['grenade'] = self.player['inventory'].get('grenade', 0) + 1
                    elif i == "ammo":
                        self.player['inventory']['ammo'] = self.player['inventory'].get('ammo', 0) + 1
                    elif i == "attack_boost":
                        self.player['attack'] += 3
                        self.add_log(f"🔫 购买攻击强化！攻击力 +3", '#4caf50')
                    elif i == "defense_boost":
                        self.player['defense'] += 2
                        self.add_log(f"🛡️ 购买防御强化！防御力 +2", '#4caf50')
                    self.player['money'] -= p
                    self.add_log(f"💰 购买 {name}，花费 ${p}", '#ffaa44')
                    self.update_all_displays()
                    shop_window.destroy()
                    self.turn_mode = 'explore'
                    self.draw_map()
                else:
                    messagebox.showwarning("资金不足", f"需要 ${p}，当前 ${self.player['money']}")

            tk.Button(frame, text="购买", command=buy, bg='#28a745', fg='white', font=('Arial', 9)).pack(side=tk.RIGHT)

        tk.Button(shop_window, text="关闭", command=lambda: [shop_window.destroy(), self.setattr('turn_mode', 'explore')],
                 bg='#6c757d', fg='white').pack(pady=10)

    def check_pickup(self):
        """拾取物品"""
        for item in self.items[:]:
            if item[0] == self.player["row"] and item[1] == self.player["col"]:
                item_type = item[2]
                item_value = item[3]
                item_name = item[4]

                if item_type == 'medkit':
                    self.player['inventory']['medkit'] = self.player['inventory'].get('medkit', 0) + 1
                    self.add_log(f"💊 拾取 {item_name}！医疗包 +1", '#4caf50')
                elif item_type == 'medkit_small':
                    old_hp = self.player['hp']
                    self.player['hp'] = min(self.player['max_hp'], self.player['hp'] + item_value)
                    self.add_log(f"🩹 使用 {item_name}！恢复 {self.player['hp'] - old_hp} 生命值", '#4caf50')
                elif item_type == 'ammo':
                    self.player['inventory']['ammo'] = self.player['inventory'].get('ammo', 0) + 1
                    self.add_log(f"📦 拾取 {item_name}！弹药包 +1", '#ff9800')
                elif item_type == 'grenade':
                    self.player['inventory']['grenade'] = self.player['inventory'].get('grenade', 0) + 1
                    self.add_log(f"💣 拾取 {item_name}！手雷 +1", '#ff9800')

                self.items.remove(item)
                break

    def check_encounter(self):
        """检查遭遇战"""
        for enemy in self.enemies:
            if enemy[0] == self.player["row"] and enemy[1] == self.player["col"] and enemy[4] > 0:
                self.current_enemy = enemy
                self.turn_mode = 'combat'
                self.show_combat_buttons(True)
                self.add_log(f"⚔️ 遭遇 {enemy[3]} {enemy[2]}！", '#ff4444')
                self.add_log(f"📊 敌方: 攻击 {enemy[6]} | 防御 {enemy[7]} | 生命 {enemy[4]}/{enemy[5]}", '#ffaa44')
                self.draw_map()
                return True
        return False

    def combat_attack(self):
        """普通攻击"""
        if self.turn_mode != 'combat' or self.current_enemy is None:
            return

        enemy = self.current_enemy
        if enemy[4] <= 0:
            self.end_combat()
            return

        # 玩家攻击
        damage = max(5, self.player['attack'] - enemy[7] + random.randint(-5, 8))
        enemy[4] -= damage
        self.add_log(f"🎯 对 {enemy[2]} 造成 {damage} 伤害！", '#ff8888')

        if enemy[4] <= 0:
            self.defeat_enemy()
            return

        # 敌人反击
        enemy_damage = max(3, enemy[6] - self.player['defense'] + random.randint(-3, 6))
        self.player['hp'] -= enemy_damage
        self.add_log(f"💥 {enemy[2]} 反击造成 {enemy_damage} 伤害！", '#ff6666')

        if self.player['hp'] <= 0:
            self.game_over = True
            self.add_log("💀 三角洲队员阵亡... 任务失败 💀", 'red')
            self.show_combat_buttons(False)
            messagebox.showinfo("任务失败", "💀 你已阵亡！点击「重新部署」继续行动")
            return

        self.update_all_displays()
        self.draw_map()

    def combat_grenade(self):
        """使用手雷（高伤害）"""
        if self.turn_mode != 'combat' or self.current_enemy is None:
            return

        if self.player['inventory'].get('grenade', 0) <= 0:
            self.add_log("⚠️ 没有手雷！", '#ffaa44')
            return

        enemy = self.current_enemy
        self.player['inventory']['grenade'] -= 1

        # 手雷造成高额伤害
        damage = random.randint(35, 55)
        enemy[4] -= damage
        self.add_log(f"💣 投掷手雷！对 {enemy[2]} 造成 {damage} 爆炸伤害！", '#ff6600')

        if enemy[4] <= 0:
            self.defeat_enemy()
            return

        # 敌人反击（手雷使用后仍会被反击）
        enemy_damage = max(3, enemy[6] - self.player['defense'] + random.randint(-3, 6))
        self.player['hp'] -= enemy_damage
        self.add_log(f"💥 {enemy[2]} 愤怒反击造成 {enemy_damage} 伤害！", '#ff6666')

        if self.player['hp'] <= 0:
            self.game_over = True
            self.add_log("💀 三角洲队员阵亡... 任务失败 💀", 'red')
            self.show_combat_buttons(False)
            messagebox.showinfo("任务失败", "💀 你已阵亡！点击「重新部署」继续行动")
            return

        self.update_all_displays()
        self.draw_map()

    def defeat_enemy(self):
        """击败敌人后的奖励"""
        enemy = self.current_enemy
        xp_gain = enemy[8]
        money_gain = enemy[9]

        self.player['xp'] += xp_gain
        self.player['money'] += money_gain
        self.mission['current_kills'] += 1

        self.add_log(f"✅ 击毙 {enemy[2]}！获得 {xp_gain} 经验值 + ${money_gain}", '#4caf50')

        # 检查升级
        self.check_level_up()

        # 从地图移除敌人
        self.enemies.remove(enemy)
        self.end_combat()
        self.draw_map()
        self.update_all_displays()

        # 检查任务完成
        if self.mission['current_kills'] >= self.mission['target_kills']:
            self.add_log("🎯 任务目标达成！前往撤离点！", 'gold')

    def combat_retreat(self):
        """战术撤退"""
        if self.turn_mode != 'combat':
            return

        # 撤退成功率 70%
        if random.random() < 0.7:
            # 寻找可撤退位置
            possible_moves = []
            for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                nr, nc = self.player["row"] + dr, self.player["col"] + dc
                if 0 <= nr < self.grid_size and 0 <= nc < self.grid_size:
                    if (nr, nc) not in self.obstacles:
                        possible_moves.append((nr, nc))

            if possible_moves:
                new_row, new_col = random.choice(possible_moves)
                self.player["row"], self.player["col"] = new_row, new_col
                self.add_log(f"🏃 战术撤退成功！移动至 ({new_row}, {new_col})", '#ffaa44')
            else:
                self.add_log("😰 无路可退！", 'orange')
        else:
            # 撤退失败，受到追击伤害
            enemy = self.current_enemy
            pursuit_damage = random.randint(5, 15)
            self.player['hp'] -= pursuit_damage
            self.add_log(f"⚠️ 撤退失败！受到追击伤害 {pursuit_damage}", '#ff6666')

            if self.player['hp'] <= 0:
                self.game_over = True
                self.add_log("💀 三角洲队员阵亡... 任务失败 💀", 'red')
                self.show_combat_buttons(False)
                messagebox.showinfo("任务失败", "💀 你已阵亡！点击「重新部署」继续行动")
                return

        self.end_combat()
        self.draw_map()
        self.update_all_displays()

    def end_combat(self):
        """结束战斗"""
        self.turn_mode = 'explore'
        self.current_enemy = None
        self.show_combat_buttons(False)
        self.add_log("━━━━━━━━━━━━━━━━━━━━", '#888')

    def check_level_up(self):
        """升级系统"""
        xp_needed = self.player['level'] * 100
        if self.player['xp'] >= xp_needed:
            self.player['level'] += 1
            self.player['xp'] -= xp_needed
            self.player['max_hp'] += 15
            self.player['hp'] = self.player['max_hp']
            self.player['attack'] += 4
            self.player['defense'] += 2
            self.add_log(f"🎉 晋升！Lv.{self.player['level']} 🎉", 'gold')
            self.add_log(f"❤️ 生命上限 +15 | ⚔️ 攻击力 +4 | 🛡️ 防御力 +2", '#ffd700')
            self.check_level_up()  # 可能连升

    def check_extraction(self):
        """检查撤离条件"""
        if self.mission['current_kills'] >= self.mission['target_kills']:
            self.game_over = True
            bonus = self.mission['time_limit'] - self.mission['turn_count']
            bonus_money = max(0, bonus * 10)
            self.player['money'] += bonus_money
            self.add_log(f"🚁 成功撤离！获得奖金 ${bonus_money}", 'gold')
            messagebox.showinfo("任务成功",
                                f"🎉 三角洲行动成功！\n"
                                f"击杀: {self.mission['current_kills']}/{self.mission['target_kills']}\n"
                                f"剩余回合: {bonus}\n"
                                f"最终资金: ${self.player['money']}\n"
                                f"等级: Lv.{self.player['level']}")
        else:
            self.add_log("⚠️ 未完成任务目标，无法撤离！继续战斗", '#ffaa44')
            self.mission['turn_count'] -= 1  # 不消耗回合

    def check_time_limit(self):
        """检查时间限制"""
        if self.mission['turn_count'] >= self.mission['time_limit']:
            self.game_over = True
            messagebox.showinfo("任务失败", "⏱️ 时间耗尽！任务失败")
            self.add_log("⏱️ 时间耗尽！任务失败", 'red')

    def reset_game(self):
        """重置游戏"""
        # 重置玩家基础属性
        self.player.update({
            "hp": 120, "max_hp": 120, "attack": 28, "defense": 8,
            "level": 1, "xp": 0, "money": 500,
            "inventory": {"medkit": 2, "grenade": 1, "ammo": 3}
        })
        self.mission["target_kills"] = random.randint(3, 5)
        self.mission["current_kills"] = 0
        self.mission["turn_count"] = 0

        self.generate_map()
        self.turn_mode = 'explore'
        self.current_enemy = None
        self.game_over = False
        self.battle_log = []
        self.log_text.delete(1.0, tk.END)

        self.show_combat_buttons(False)
        self.update_all_displays()
        self.draw_map()
        self.add_log("🔄 重新部署！新的任务开始", '#4caf50')


if __name__ == "__main__":
    root = tk.Tk()
    game = DeltaForceGame(root)
    root.mainloop()