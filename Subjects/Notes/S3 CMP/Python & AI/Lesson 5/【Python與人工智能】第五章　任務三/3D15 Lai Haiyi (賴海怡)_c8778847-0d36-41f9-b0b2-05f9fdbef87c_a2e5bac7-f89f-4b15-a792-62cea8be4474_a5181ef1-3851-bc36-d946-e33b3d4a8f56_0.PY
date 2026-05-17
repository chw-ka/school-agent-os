import tkinter as tk
from tkinter import messagebox
import random

class ChaosMemoryGame:
    def __init__(self, root):
        self.root = root
        self.root.title("舒心記憶：終極隨機挑戰")
        self.root.geometry("620x800")
        
        # 莫蘭迪療癒配色
        self.colors = {
            "bg": "#F8F9FA",         # 淨白
            "card_back": "#DEE2E6",  # 霧面灰
            "card_front": "#6C757D", # 灰石色
            "match": "#81B29A",      # 鼠尾草綠
            "danger": "#E07A5F",     # 珊瑚紅
            "combo": "#F2CC8F",      # 蜂蜜黃
            "text": "#3D405B"        # 深藍灰
        }

        self.root.configure(bg=self.colors["bg"])
        
        # 2D List 主題庫 (新增數字主題)
        self.themes_library = [
            ["動物", "🦁", "🐯", "🐼", "🐨", "🦒", "🦊", "🐶", "🐱", "🐰", "🐸", "🐷", "🐵"],
            ["英文", "WORD", "COOL", "SOFT", "WIND", "FIRE", "STAY", "KEEP", "CALM", "PURE", "LOVE", "FREE", "HOME"],
            ["工具", "🔨", "🪚", "🔧", "🪛", "🪜", "🧱", "🧰", "🔦", "🔋", "🧪", "🔭", "🔬"],
            ["數字", "111", "222", "333", "444", "555", "666", "777", "888", "999", "000", "123", "789"]
        ]
        
        self.rows, self.cols = 4, 6
        self.setup_menu()

    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def setup_menu(self):
        self.clear()
        tk.Label(self.root, text="Chaos Memory", font=('Quicksand', 48, 'bold'), 
                 bg=self.colors["bg"], fg=self.colors["text"]).pack(pady=60)

        tk.Label(self.root, text="電腦將隨機分配主題", font=('微軟正黑體', 13), 
                 bg=self.colors["bg"], fg="#888888").pack()

        # 選擇難度
        tk.Label(self.root, text="選擇你的挑戰難度", font=('微軟正黑體', 12, 'bold'), 
                 bg=self.colors["bg"], fg=self.colors["text"]).pack(pady=(30, 0))
        
        self.diff_var = tk.StringVar(value="普通")
        d_frame = tk.Frame(self.root, bg=self.colors["bg"])
        d_frame.pack(pady=10)
        
        # (記憶秒數, 生命值)
        self.diff_settings = {"簡單": (30, 99), "普通": (20, 10), "地獄": (10, 5)}
        for d in self.diff_settings.keys():
            tk.Radiobutton(d_frame, text=d, variable=self.diff_var, value=d,
                           bg=self.colors["bg"], font=('微軟正黑體', 11)).pack(side=tk.LEFT, padx=15)

        tk.Button(self.root, text="隨機主題挑戰", font=('微軟正黑體', 14, 'bold'),
                  bg=self.colors["text"], fg="white", relief="flat", padx=60, pady=15,
                  command=self.start_game).pack(pady=50)

    def start_game(self):
        diff = self.diff_var.get()
        
        # 決定主題內容
        if diff == "地獄":
            # 地獄模式：打亂所有主題
            all_content = []
            for theme in self.themes_library:
                all_content.extend(theme[1:])
            selected_content = random.sample(all_content, 12)
            self.current_theme_name = "終極打亂 (Chaos)"
        else:
            # 隨機挑選一個主題
            theme_choice = random.choice(self.themes_library)
            self.current_theme_name = theme_choice[0]
            selected_content = theme_choice[1:13]
        
        # 準備 12 對卡片
        cards = selected_content * 2
        random.shuffle(cards)
        self.board_logic = [cards[i:i+self.cols] for i in range(0, len(cards), self.cols)]
        
        # 初始化遊戲狀態
        self.mem_time, self.lives = self.diff_settings[diff]
        self.score, self.combo = 0, 0
        self.first_card = None
        self.can_click = False

        self.clear()
        self.setup_game_ui()
        self.countdown(self.mem_time)

    def setup_game_ui(self):
        # 狀態欄
        tk.Label(self.root, text=f"當前主題: {self.current_theme_name}", font=('微軟正黑體', 12, 'bold'), 
                 bg=self.colors["bg"], fg="#95A5A6").pack(pady=5)
        
        self.score_label = tk.Label(self.root, text="SCORE: 0", font=('Arial Black', 22), 
                                    bg=self.colors["bg"], fg=self.colors["text"])
        self.score_label.pack()
        
        self.combo_label = tk.Label(self.root, text="", font=('Impact', 20), 
                                    bg=self.colors["bg"], fg=self.colors["combo"])
        self.combo_label.pack()

        self.lives_label = tk.Label(self.root, text=f"LIVES: {self.lives if self.lives < 50 else '∞'}", 
                                    font=('Arial Black', 12), bg=self.colors["bg"], fg=self.colors["danger"])
        self.lives_label.pack()

        self.timer_label = tk.Label(self.root, text="", font=('Consolas', 14), bg=self.colors["bg"])
        self.timer_label.pack(pady=5)

        # 網格
        grid = tk.Frame(self.root, bg=self.colors["bg"])
        grid.pack(pady=10)
        self.buttons = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        
        for r in range(self.rows):
            for c in range(self.cols):
                btn = tk.Button(grid, text=str(self.board_logic[r][c]), font=('Arial Black', 14),
                                width=6, height=2, bg=self.colors["card_front"], fg="white", relief="flat",
                                command=lambda row=r, col=c: self.on_card_click(row, col))
                btn.grid(row=r, column=c, padx=4, pady=4)
                self.buttons[r][c] = btn

    def countdown(self, sec):
        if sec > 0:
            self.timer_label.config(text=f"記憶挑戰中... {sec}s")
            self.root.after(1000, lambda: self.countdown(sec-1))
        else:
            self.hide_all()

    def hide_all(self):
        self.can_click = True
        self.timer_label.config(text="START!", fg=self.colors["match"])
        for r in range(self.rows):
            for c in range(self.cols):
                self.buttons[r][c].config(text=" ", bg=self.colors["card_back"])

    def on_card_click(self, r, c):
        if not self.can_click or self.buttons[r][c]['bg'] == self.colors["match"]:
            return

        self.buttons[r][c].config(text=str(self.board_logic[r][c]), bg=self.colors["card_front"])

        if self.first_card is None:
            self.first_card = (r, c)
        else:
            r1, c1 = self.first_card
            if r == r1 and c == c1: return

            if self.board_logic[r][c] == self.board_logic[r1][c1]:
                self.combo += 1
                self.score += 100 * self.combo
                self.buttons[r][c].config(bg=self.colors["match"])
                self.buttons[r1][c1].config(bg=self.colors["match"])
                self.score_label.config(text=f"SCORE: {self.score}")
                if self.combo > 1: self.combo_label.config(text=f"COMBO X{self.combo}")
                self.first_card = None
                self.check_win()
            else:
                self.can_click = False
                self.combo = 0
                self.combo_label.config(text="")
                if self.lives < 50:
                    self.lives -= 1
                    self.lives_label.config(text=f"LIVES: {self.lives}")
                
                if self.lives <= 0:
                    messagebox.showerror("挑戰失敗", f"LIVES 已耗盡！\n最終得分: {self.score}")
                    self.setup_menu()
                else:
                    self.root.after(500, lambda: self.reset_cards(r, c, r1, c1))

    def reset_cards(self, r, c, r1, c1):
        self.buttons[r][c].config(text=" ", bg=self.colors["card_back"])
        self.buttons[r1][c1].config(text=" ", bg=self.colors["card_back"])
        self.first_card = None
        self.can_click = True

    def check_win(self):
        if all(btn['bg'] == self.colors["match"] for row in self.buttons for btn in row):
            messagebox.showinfo("大功告成", f"完美的記憶力！\n得分: {self.score}")
            self.setup_menu()

if __name__ == "__main__":
    root = tk.Tk()
    root.eval('tk::PlaceWindow . center')
    ChaosMemoryGame(root)
    root.mainloop()