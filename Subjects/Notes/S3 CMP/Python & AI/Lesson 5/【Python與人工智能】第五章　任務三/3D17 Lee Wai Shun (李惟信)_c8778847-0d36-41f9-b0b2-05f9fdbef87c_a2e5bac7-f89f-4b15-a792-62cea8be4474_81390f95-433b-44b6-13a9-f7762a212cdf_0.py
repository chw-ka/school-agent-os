import tkinter as tk
from tkinter import messagebox
import random

class StickmanWarGame:
    def __init__(self, root):
        self.root = root
        self.root.title("火柴人戰爭：圓球版 (Stickman War: Ball Edition)")
        self.root.configure(bg="#2C3E50")
        
        # --- 遊戲數據 ---
        self.blue_gold, self.red_gold = 200, 200
        self.blue_tower_hp, self.red_tower_hp = 1000, 1000
        self.mine_level, self.upgrade_cost, self.gold_per_tick = 1, 300, 25
        self.blue_soldiers, self.red_soldiers = [], []
        
        # Defines base size (diameter). We'll map these to unit types.
        self.troop_configs = {
            "Warrior":  {"cost": 50,  "hp": 100, "atk": 5,  "spd": 4, "size": 30, "color": "#3498DB"}, # Blueish ball
            "Giant":    {"cost": 150, "hp": 400, "atk": 10, "spd": 1, "size": 60, "color": "#9B59B6"}, # Purplish ball
            "Assassin": {"cost": 80,  "hp": 50,  "atk": 15, "spd": 8, "size": 20, "color": "#E67E22"}  # Orangish ball
        }
        
        # We no longer need PIL or image loading.
        self.use_shapes = True 
        
        self.setup_ui()
        self.update_resources()
        self.red_team_ai()
        self.game_loop()

    def setup_ui(self):
        self.info_frame = tk.Frame(self.root, bg="#34495E", pady=10)
        self.info_frame.pack(fill="x")
        
        self.blue_label = tk.Label(self.info_frame, text=f"藍軍: {self.blue_gold}", fg="#3498DB", bg="#34495E", font=("Arial", 12, "bold"))
        self.blue_label.pack(side=tk.LEFT, padx=30)
        
        self.level_label = tk.Label(self.info_frame, text=f"金礦: Lv.{self.mine_level}", fg="#F1C40F", bg="#34495E", font=("Arial", 12, "bold"))
        self.level_label.pack(side=tk.LEFT, padx=20)
        
        self.red_label = tk.Label(self.info_frame, text=f"紅軍: {self.red_gold}", fg="#E74C3C", bg="#34495E", font=("Arial", 12, "bold"))
        self.red_label.pack(side=tk.RIGHT, padx=30)

        self.canvas = tk.Canvas(self.root, width=900, height=450, bg="#ECF0F1", highlightthickness=0)
        self.canvas.pack(pady=10)
        
        # 基地建築 (Tower Bases)
        self.canvas.create_rectangle(0, 150, 60, 400, fill="#2E4053")
        self.blue_hp_bar = self.canvas.create_rectangle(5, 130, 55, 140, fill="#2ECC71")
        
        self.canvas.create_rectangle(840, 150, 900, 400, fill="#2E4053")
        self.red_hp_bar = self.canvas.create_rectangle(845, 130, 895, 140, fill="#2ECC71")

        self.btn_frame = tk.Frame(self.root, bg="#2C3E50", pady=15)
        self.btn_frame.pack()
        
        for name, data in self.troop_configs.items():
            tk.Button(self.btn_frame, text=f"召喚 {name}\n${data['cost']}", 
                      command=lambda n=name: self.spawn_unit("blue", n),
                      bg="#34495E", fg="white", font=("Arial", 9, "bold"), width=12).pack(side=tk.LEFT, padx=5)
        
        self.upgrade_btn = tk.Button(self.btn_frame, text=f"升級金礦\n${self.upgrade_cost}", 
                                    command=self.upgrade_mine, bg="#F1C40F", font=("Arial", 9, "bold"), width=12)
        self.upgrade_btn.pack(side=tk.LEFT, padx=20)

    def upgrade_mine(self):
        if self.blue_gold >= self.upgrade_cost:
            self.blue_gold -= self.upgrade_cost
            self.mine_level += 1
            self.gold_per_tick += 15
            self.upgrade_cost = int(self.upgrade_cost * 1.6)
            self.update_ui_text()

    def update_resources(self):
        self.blue_gold += self.gold_per_tick
        self.red_gold += 30
        self.update_ui_text()
        self.root.after(1000, self.update_resources)

    def update_ui_text(self):
        self.blue_label.config(text=f"藍軍: {self.blue_gold}")
        self.red_label.config(text=f"紅軍: {self.red_gold}")
        self.level_label.config(text=f"金礦: Lv.{self.mine_level}")
        self.upgrade_btn.config(text=f"升級金礦\n${self.upgrade_cost}")

    def spawn_unit(self, team, type_name):
        data = self.troop_configs[type_name]
        gold_attr = f"{team}_gold"
        
        if getattr(self, gold_attr) >= data['cost']:
            setattr(self, gold_attr, getattr(self, gold_attr) - data['cost'])
            self.update_ui_text()
            
            # The 'size' is used as the diameter of the ball.
            radius = data['size'] / 2
            # Units are aligned slightly above the ground line (y=380)
            ground_y = 380
            
            x_center = 65 + radius if team == "blue" else 835 - radius
            y_center = ground_y - radius
            
            # Draw the unit as a ball (oval/circle)
            if team == "blue":
                # For blue team, use the config color
                ball_color = data['color']
            else:
                # For red team, we use a different hue (usually red/orange)
                # To make it distinct but type-specific, we'll map the config colors
                # to redder versions, or use a consistent Red indicator.
                if type_name == "Warrior": ball_color = "#C0392B" # Dark Red
                elif type_name == "Giant": ball_color = "#922B21" # Deep Dark Red
                elif type_name == "Assassin": ball_color = "#D35400" # Orange/Red
            
            # Create the ball (filled circle)
            s_id = self.canvas.create_oval(
                x_center - radius, y_center - radius,
                x_center + radius, y_center + radius,
                fill=ball_color, outline="white", width=2
            )
            
            # Store necessary data (using x_center for simpler movement)
            unit = {
                "id": s_id, "x": x_center, "radius": radius,
                "hp": data['hp'], "atk": data['atk'], 
                "spd": data['spd'], "dead": False, "type": type_name, "team": team
            }
            (self.blue_soldiers if team == "blue" else self.red_soldiers).append(unit)

    def red_team_ai(self):
        type_name = random.choice(list(self.troop_configs.keys()))
        self.spawn_unit("red", type_name)
        self.root.after(random.randint(2000, 5000), self.red_team_ai)

    def play_shake(self, unit_id):
        dx = random.randint(-2, 2)
        dy = random.randint(-1, 1) # Small vertical vibration for balls
        self.canvas.move(unit_id, dx, dy)
        self.root.after(50, lambda: self.canvas.move(unit_id, -dx, -dy))

    def play_death(self, unit, team):
        if unit["dead"]: return
        unit["dead"] = True
        u_id = unit["id"]
        
        # 立即從活躍列表中移除，防止邏輯重複計算
        if team == "blue":
            if unit in self.blue_soldiers: self.blue_soldiers.remove(unit)
        else:
            if unit in self.red_soldiers: self.red_soldiers.remove(unit)
            
        # 死亡動畫：向下沉並消失 (Sink and disappear)
        self.canvas.move(u_id, 0, 10)
        # Briefly change color to grey on death before deleting
        self.canvas.itemconfig(u_id, fill="#7F8C8D", outline="#7F8C8D")
        self.root.after(500, lambda: self.canvas.delete(u_id))

    def cleanup(self):
        # 遍歷複本以安全移除死亡單位
        for b in self.blue_soldiers[:]:
            if b["hp"] <= 0: self.play_death(b, "blue")
        for r in self.red_soldiers[:]:
            if r["hp"] <= 0: self.play_death(r, "red")
            
        # 更新塔血條
        bw = max(0, (self.blue_tower_hp / 1000) * 50)
        self.canvas.coords(self.blue_hp_bar, 5, 130, 5 + bw, 140)
        
        rw = max(0, (self.red_tower_hp / 1000) * 50)
        # 修正紅軍血條：從右側往左扣
        self.canvas.coords(self.red_hp_bar, 895 - rw, 130, 895, 140)

    def game_loop(self):
        # 藍軍移動與戰鬥邏輯
        # For simplicity, combat range is based on the combined radii
        combat_range_buffer = 5
        
        for i, b in enumerate(self.blue_soldiers):
            if b["dead"]: continue
            fighting = False
            
            # 撞到敵方基地: Check distance between ball edge and base edge
            if b["x"] + b["radius"] >= 840:
                self.red_tower_hp -= b["atk"]
                fighting = True
            else:
                # 撞到紅軍: Check distance between center points vs combined radii
                for r in self.red_soldiers:
                    if not r["dead"]:
                        # Euclidean distance would be better, but simple x-axis check is OK for this game
                        # if (r["x"] - b["x"]) < (b["radius"] + r["radius"] + combat_range_buffer):
                        
                        # Simpler x-axis edge-to-edge check:
                        if (r["x"] - r["radius"]) - (b["x"] + b["radius"]) < combat_range_buffer:
                            r["hp"] -= b["atk"]
                            fighting = True
                            break
            
            if fighting: 
                self.play_shake(b["id"])
            else:
                b["x"] += b["spd"]
                self.canvas.move(b["id"], b["spd"], 0)

        # 紅軍移動與戰鬥邏輯
        for i, r in enumerate(self.red_soldiers):
            if r["dead"]: continue
            fighting = False
            
            # 撞到藍方基地
            if r["x"] - r["radius"] <= 60:
                self.blue_tower_hp -= r["atk"]
                fighting = True
            else:
                # 撞到藍軍
                for b in self.blue_soldiers:
                    if not b["dead"]:
                        # Simple x-axis edge-to-edge check (reversed for red):
                        if (r["x"] - r["radius"]) - (b["x"] + b["radius"]) < combat_range_buffer:
                            b["hp"] -= r["atk"]
                            fighting = True
                            break
            
            if fighting: 
                self.play_shake(r["id"])
            else:
                r["x"] -= r["spd"]
                self.canvas.move(r["id"], -r["spd"], 0)

        self.cleanup()
        
        if self.blue_tower_hp > 0 and self.red_tower_hp > 0:
            self.root.after(50, self.game_loop)
        else:
            winner = "藍軍" if self.red_tower_hp <= 0 else "紅軍"
            messagebox.showinfo("戰鬥結束", f"遊戲結束！{winner} 獲勝！")
            # Clear remaining units visually
            for u in self.blue_soldiers + self.red_soldiers:
                self.canvas.delete(u["id"])
            # In a real game, reset states here instead of destroying root.
            # self.root.destroy() 

if __name__ == "__main__":
    root = tk.Tk()
    # Prevent resizing to keep canvas coordinates simple
    root.resizable(False, False)
    game = StickmanWarGame(root)
    root.mainloop()