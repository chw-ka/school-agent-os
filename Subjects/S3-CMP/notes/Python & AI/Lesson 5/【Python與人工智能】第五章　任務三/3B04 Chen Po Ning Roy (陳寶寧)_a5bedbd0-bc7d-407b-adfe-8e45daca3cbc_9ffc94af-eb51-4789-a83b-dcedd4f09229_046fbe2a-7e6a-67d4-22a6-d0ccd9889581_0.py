import tkinter as tk
from tkinter import messagebox, simpledialog
import random

class WorldConquerorPro:
    def __init__(self, root):
        self.root = root
        self.root.title("世界征服者：閃擊戰爭 Pro")
        self.root.geometry("1200x800")
        self.root.configure(bg="#1A1A1A")

        # 1. 基礎參數設定
        self.grid_size = 15
        self.cell_size = 80
        self.turn = 1
        self.selected_unit = None
        
        # 單位數據：[成本, 威力, 最大MP, 攻擊消耗MP]
        self.unit_info = {
            "步兵": {"cost": 15, "power": 6, "max_mp": 3, "atk_cost": 3, "icon": "🪖"},
            "坦克": {"cost": 50, "power": 20, "max_mp": 5, "atk_cost": 2, "icon": "🚜"},
            "火炮": {"cost": 40, "power": 15, "max_mp": 2, "atk_cost": 2, "icon": "💥"}
        }

        self.countries = {
            "Player": {"name": "盟軍", "color": "#2980B9", "money": 500},
            "Enemy": {"name": "軸心", "color": "#C0392B", "money": 500}
        }

        # 2. 初始化地圖
        self.board = [[self.generate_cell(r, c) for c in range(self.grid_size)] for r in range(self.grid_size)]
        self.setup_initial_positions()

        # 3. 建立 UI
        self.setup_ui()
        self.draw_map()

        # 4. 綁定快捷鍵 (作弊碼)
        self.root.bind("`", lambda e: self.open_cheat_panel())

    def generate_cell(self, r, c):
        rand = random.random()
        ctype = "平原"
        if rand < 0.08: ctype = "城市"
        elif rand < 0.12: ctype = "工廠"
        elif rand < 0.05: ctype = "雷達站"
        return {"owner": None, "units": {}, "type": ctype, "mp": 0}

    def setup_initial_positions(self):
        # 玩家起點
        self.board[1][1] = {"owner": "Player", "type": "首都", "units": {"步兵": 15}, "mp": 3}
        # AI 起點
        self.board[self.grid_size-2][self.grid_size-2] = {"owner": "Enemy", "type": "首都", "units": {"步兵": 15}, "mp": 3}

    def setup_ui(self):
        # 右側控制面板
        self.side_panel = tk.Frame(self.root, bg="#252525", width=220)
        self.side_panel.pack(side=tk.RIGHT, fill=tk.Y)

        tk.Label(self.side_panel, text="COMMANDER", fg="#F1C40F", bg="#252525", font=("Arial", 16, "bold")).pack(pady=20)
        
        for name in self.unit_info:
            tk.Button(self.side_panel, text=f"徵召 {name}\n(${self.unit_info[name]['cost']})", 
                      command=lambda n=name: self.recruit_unit(n),
                      bg="#34495E", fg="white", width=18, pady=5).pack(pady=5)

        tk.Button(self.side_panel, text="結束回合", command=self.next_turn, 
                  bg="#27AE60", fg="white", font=("Arial", 12, "bold"), width=18, pady=10).pack(side=tk.BOTTOM, pady=30)

        # 中央地圖區 (捲軸功能)
        self.map_frame = tk.Frame(self.root, bg="#1A1A1A")
        self.map_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.map_frame, bg="#1E272E", highlightthickness=0)
        self.v_scroll = tk.Scrollbar(self.map_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.h_scroll = tk.Scrollbar(self.map_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=self.v_scroll.set, xscrollcommand=self.h_scroll.set)

        self.v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas.config(scrollregion=(0, 0, self.grid_size*self.cell_size, self.grid_size*self.cell_size))
        self.canvas.bind("<Button-1>", self.handle_click)

        # 狀態欄
        self.status_bar = tk.Label(self.root, text="", bg="#2C3E50", fg="white", font=("Arial", 11, "bold"))
        self.status_bar.place(x=10, y=10)

    def draw_map(self):
        self.canvas.delete("all")
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                x1, y1 = c*self.cell_size, r*self.cell_size
                cell = self.board[r][c]
                
                # 領土顏色
                base_color = self.countries[cell["owner"]]["color"] if cell["owner"] else "#2C3E50"
                if cell["owner"] == "Player" and cell["mp"] <= 0 and cell["units"]:
                    base_color = "#1B4F72" # 已耗盡行動力的暗藍色
                
                self.canvas.create_rectangle(x1, y1, x1+self.cell_size, y1+self.cell_size, fill=base_color, outline="#1A1A1A")
                
                # 建築物
                if cell["type"] != "平原":
                    icon = "🏰" if cell["type"]=="首都" else "🏙️" if cell["type"]=="城市" else "📡" if cell["type"]=="雷達站" else "🏭"
                    self.canvas.create_text(x1+40, y1+15, text=f"{icon} {cell['type']}", fill="#F1C40F", font=("Arial", 8, "bold"))

                # 單位顯示
                if cell["units"]:
                    y_off = 35
                    for u_name, count in cell["units"].items():
                        if count > 0:
                            self.canvas.create_text(x1+40, y1+y_off, text=f"{u_name}:{count}", fill="white", font=("Arial", 8))
                            y_off += 15
                    if cell["owner"] == "Player":
                        self.canvas.create_text(x1+65, y1+70, text=f"MP:{cell['mp']}", fill="#00FFCC", font=("Arial", 7))

                # 選中標記
                if self.selected_unit == (r, c):
                    self.canvas.create_rectangle(x1+3, y1+3, x1+self.cell_size-3, y1+self.cell_size-3, outline="#FFD700", width=3)
        self.update_status()

    def handle_click(self, event):
        cx, cy = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        c, r = int(cx // self.cell_size), int(cy // self.cell_size)
        if r >= self.grid_size or c >= self.grid_size: return

        if self.selected_unit:
            sr, sc = self.selected_unit
            cell_s = self.board[sr][sc]
            
            # 範圍檢查與行動力檢查
            if abs(sr-r) <= 1 and abs(sc-c) <= 1 and cell_s["mp"] > 0:
                cost = 1 if self.board[r][c]["owner"] in ["Player", None] else self.get_battle_cost(cell_s)
                if cell_s["mp"] >= cost:
                    self.process_action(sr, sc, r, c, cost)
                    # 如果還有 MP 且格子還有兵，保持選中，實現連續移動
                    self.selected_unit = (r, c) if self.board[r][c]["mp"] > 0 and self.board[r][c]["units"] else None
                else:
                    self.selected_unit = None
            else:
                self.selected_unit = (r, c) if self.board[r][c]["owner"] == "Player" else None
        else:
            if self.board[r][c]["owner"] == "Player":
                self.selected_unit = (r, c)
        
        self.draw_map()

    def get_battle_cost(self, cell):
        return 2 if "坦克" in cell["units"] else 3

    def process_action(self, sr, sc, tr, tc, cost):
        s, t = self.board[sr][sc], self.board[tr][tc]
        
        if t["owner"] != "Enemy": # 移動或合併
            for u, count in s["units"].items():
                t["units"][u] = t["units"].get(u, 0) + count
            t["owner"], t["mp"], s["units"], s["mp"] = "Player", s["mp"]-cost, {}, 0
        else: # 戰鬥
            s_power = sum(n * self.unit_info[u]["power"] for u, n in s["units"].items())
            t_power = sum(n * self.unit_info[u]["power"] for u, n in t["units"].items())
            
            if s_power > t_power:
                win_ratio = (s_power - t_power) / s_power
                new_units = {u: int(n * win_ratio) for u, n in s["units"].items()}
                t["units"], t["owner"], t["mp"], s["units"], s["mp"] = new_units, "Player", s["mp"]-cost, {}, 0
            else:
                s["units"], s["mp"] = {}, 0

    def next_turn(self):
        # 結算收益與恢復行動力
        radar_count = sum(1 for row in self.board for c in row if c["type"]=="雷達站" and c["owner"]=="Player")
        
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                cell = self.board[r][c]
                if cell["owner"]:
                    self.countries[cell["owner"]]["money"] += 15
                    if cell["type"] == "城市": self.countries[cell["owner"]]["money"] += 35
                    if cell["type"] == "工廠" and cell["units"]:
                        u = random.choice(list(cell["units"].keys())); cell["units"][u] += 3
                    
                    # 恢復 MP (坦克 5, 其餘 3, 雷達加成)
                    if cell["units"]:
                        base_mp = 5 if "坦克" in cell["units"] else 3
                        cell["mp"] = base_mp + (1 if radar_count >= 1 else 0)
        
        self.turn += 1
        self.draw_map()

    def recruit_unit(self, u_name):
        if not self.selected_unit:
            messagebox.showinfo("提示", "請先點選你的領土！")
            return
        r, c = self.selected_unit
        cell = self.board[r][c]
        cost = self.unit_info[u_name]["cost"]
        if cell["owner"] == "Player" and self.countries["Player"]["money"] >= cost:
            self.countries["Player"]["money"] -= cost
            cell["units"][u_name] = cell["units"].get(u_name, 0) + 8
            cell["mp"] = self.unit_info[u_name]["max_mp"]
            self.draw_map()

    def update_status(self):
        self.status_bar.config(text=f"回合: {self.turn} | 資金: ${self.countries['Player']['money']} | 密技: ~ 鍵")

    def open_cheat_panel(self):
        cmd = simpledialog.askstring("作弊終端", "輸入指令 (money / move / win / army):")
        if not cmd: return
        if cmd == "money": self.countries["Player"]["money"] += 5000
        elif cmd == "move":
            for r in range(self.grid_size):
                for c in range(self.grid_size): self.board[r][c]["mp"] = 99
        elif cmd == "army" and self.selected_unit:
            r, c = self.selected_unit
            self.board[r][c]["units"] = {"坦克": 500, "火炮": 500}
            self.board[r][c]["mp"] = 5
        elif cmd == "win":
            messagebox.showinfo("Cheat", "瞬間征服世界！")
            self.root.destroy()
        self.draw_map()

if __name__ == "__main__":
    root = tk.Tk()
    game = WorldConquerorPro(root)
    root.mainloop()