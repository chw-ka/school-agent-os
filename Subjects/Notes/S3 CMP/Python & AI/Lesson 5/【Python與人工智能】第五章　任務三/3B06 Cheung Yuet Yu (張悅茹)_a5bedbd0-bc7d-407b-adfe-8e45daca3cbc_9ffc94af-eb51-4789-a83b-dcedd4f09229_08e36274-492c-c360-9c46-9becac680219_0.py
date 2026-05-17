import tkinter as tk
import random
from tkinter import messagebox

class EmojiLightBluePop:
    def __init__(self, root):
        self.root = root
        self.root.title("表情消消樂：清新淺藍版 ☁️")
        self.root.geometry("400x700")
        self.root.resizable(False, False)

        # 遊戲數據
        self.score = 0
        self.leaderboard = [0, 0, 0]
        self.time_left = 20
        self.game_running = False
        self.balls = []
        
        # 顏色定義 (針對淺藍背景微調了球體顏色)
        self.color_pool = [
            ("紅色", "#FF6B6B"), ("橘黃", "#FFA502"), 
            ("綠色", "#2ED573"), ("深藍", "#1E90FF"), ("紫色", "#A55EEA")
        ]
        self.color_counts = {c[1]: 0 for c in self.color_pool}
        self.emojis = ["(•‿•)", "(^◡^)", "(⊙_⊙)", "(¬_¬)", "(>_<)", "(°ロ°)"]

        self.setup_ui()

    def setup_ui(self):
        # 頂部狀態欄 (改為稍深的藍色以區分背景)
        self.header = tk.Frame(self.root, bg="#74b9ff", height=160)
        self.header.pack(fill="x")

        self.score_label = tk.Label(self.header, text="得分: 0", font=("Arial", 16, "bold"), bg="#74b9ff", fg="white")
        self.score_label.place(x=20, y=15)

        self.timer_label = tk.Label(self.header, text="時間: 20s", font=("Arial", 16, "bold"), bg="#74b9ff", fg="#d63031")
        self.timer_label.place(x=280, y=15)

        self.info_label = tk.Label(self.header, text="點擊表情球，看誰手速快！", font=("微軟正黑體", 12), bg="#74b9ff", fg="#2f3542")
        self.info_label.place(relx=0.5, y=65, anchor="center")

        # 實時計數器
        self.count_display = tk.Label(self.header, text="🔴:0 🟡:0 🟢:0 🔵:0 🟣:0", font=("Arial", 11), bg="#74b9ff", fg="#2f3542")
        self.count_display.place(relx=0.5, y=100, anchor="center")

        self.rank_label = tk.Label(self.header, text="排行榜: 0 | 0 | 0", font=("Arial", 10), bg="#74b9ff", fg="#57606f")
        self.rank_label.place(relx=0.5, y=135, anchor="center")

        # 遊戲畫布 (淺藍色背景 SkyBlue)
        self.canvas = tk.Canvas(self.root, width=400, height=480, bg="#81ecec", highlightthickness=0)
        self.canvas.pack()

        # 開始按鈕 (深藍色按鈕)
        self.start_btn = tk.Button(self.root, text="開始遊戲", font=("微軟正黑體", 14, "bold"), 
                                   bg="#0984e3", fg="white", activebackground="#74b9ff", 
                                   relief="flat", padx=20, command=self.start_game)
        self.start_btn.place(relx=0.5, y=660, anchor="center")

    def start_game(self):
        if self.game_running: return
        self.score = 0
        self.time_left = 20
        self.game_running = True
        self.balls = []
        self.color_counts = {c[1]: 0 for c in self.color_pool}
        self.canvas.delete("all")
        
        self.start_btn.config(state="disabled", text="挑戰進行中...")
        self.score_label.config(text="得分: 0")
        self.update_count_display()
        
        for _ in range(10):
            self.create_ball()
        
        self.update_timer()
        self.update_physics()

    def update_count_display(self):
        c = self.color_counts
        text = f"🔴:{c['#FF6B6B']} 🟡:{c['#FFA502']} 🟢:{c['#2ED573']} 🔵:{c['#1E90FF']} 🟣:{c['#A55EEA']}"
        self.count_display.config(text=text)

    def create_ball(self):
        if not self.game_running: return
        r = random.randint(25, 35)
        x = random.randint(r, 400 - r)
        y = random.randint(r, 200)
        c_name, c_hex = random.choice(self.color_pool)
        emoji = random.choice(self.emojis)
        
        # 加深了球體的邊框 (outline="#2f3542")，讓它在淺色背景更明顯
        ball_id = self.canvas.create_oval(x-r, y-r, x+r, y+r, fill=c_hex, outline="#2f3542", width=2)
        text_id = self.canvas.create_text(x, y, text=emoji, font=("Arial", 10, "bold"), fill="white" if c_hex=="#1E90FF" else "black")
        
        ball_data = {"bid": ball_id, "tid": text_id, "vx": random.uniform(-3, 3), 
                     "vy": random.uniform(1, 4), "color": c_hex}
        self.balls.append(ball_data)
        
        self.canvas.tag_bind(ball_id, '<Button-1>', lambda e: self.pop_ball(ball_data))
        self.canvas.tag_bind(text_id, '<Button-1>', lambda e: self.pop_ball(ball_data))

    def pop_ball(self, ball_data):
        if not self.game_running: return
        self.score += 10
        self.color_counts[ball_data["color"]] += 1
        self.update_count_display()
            
        self.canvas.delete(ball_data["bid"])
        self.canvas.delete(ball_data["tid"])
        if ball_data in self.balls: self.balls.remove(ball_data)
        
        self.score_label.config(text=f"得分: {self.score}")
        self.create_ball()

    def update_physics(self):
        if not self.game_running: return
        for ball in self.balls:
            self.canvas.move(ball["bid"], ball["vx"], ball["vy"])
            self.canvas.move(ball["tid"], ball["vx"], ball["vy"])
            pos = self.canvas.coords(ball["bid"])
            if pos[0] <= 0 or pos[2] >= 400: ball["vx"] *= -1
            if pos[1] <= 0 or pos[3] >= 480: ball["vy"] *= -1
            ball["vy"] += 0.05
        self.root.after(16, self.update_physics)

    def update_timer(self):
        if self.time_left > 0 and self.game_running:
            self.time_left -= 1
            self.timer_label.config(text=f"時間: {self.time_left}s")
            self.root.after(1000, self.update_timer)
        elif self.time_left <= 0:
            self.end_game()

    def end_game(self):
        self.game_running = False
        self.start_btn.config(state="normal", text="再挑戰一次")
        
        self.leaderboard.append(self.score)
        self.leaderboard.sort(reverse=True)
        self.leaderboard = self.leaderboard[:3]
        self.rank_label.config(text=f"排行榜: {self.leaderboard[0]} | {self.leaderboard[1]} | {self.leaderboard[2]}")
        
        max_color_hex = max(self.color_counts, key=self.color_counts.get)
        max_count = self.color_counts[max_color_hex]
        color_name = next(name for name, hex_code in self.color_pool if hex_code == max_color_hex)
        
        messagebox.showinfo("結算報告", f"挑戰結束！總分：{self.score}\n\n🎨 點擊最多的顏色：{color_name} ({max_count}次)\n\n🏆 前三名：{self.leaderboard}")

if __name__ == "__main__":
    root = tk.Tk()
    game = EmojiLightBluePop(root)
    root.mainloop()
    