import tkinter as tk
from tkinter import messagebox
import random
import winsound

class MemoryGameHardcorePro:
    def __init__(self, root):
        self.root = root
        self.root.title("Google 記憶挑戰：極限難度版")
        self.root.geometry("400x650") # 稍微加高視窗以容納按鈕
        self.root.configure(bg="#202124")
        
        # 遊戲變數
        self.sequence = []
        self.player_sequence = []
        self.score = 0
        self.high_score = 0
        self.difficulty = tk.StringVar(value="普通") # 預設難度
        
        self.colors = ["#4285F4", "#EA4335", "#FBBC05", "#34A853"]
        self.light_colors = ["#8ab4f8", "#f28b82", "#fdd663", "#81c995"]
        self.sounds = [440, 554, 659, 880] 

        self.setup_ui()

    def setup_ui(self):
        # 1. 難度選擇區塊 (加上外框讓它更明顯)
        diff_frame = tk.LabelFrame(self.root, text=" 難度模式 ", font=('Arial', 10), 
                                   bg="#202124", fg="#ffffff", padx=10, pady=10)
        diff_frame.pack(pady=15)
        
        # 建立三個按鈕
        for level in ["簡單", "普通", "困難"]:
            rb = tk.Radiobutton(
                diff_frame, text=level, variable=self.difficulty, 
                value=level, font=('Arial', 11, 'bold'), 
                bg="#202124", fg="#8ab4f8", 
                selectcolor="#3c4043", # 選中時的圓圈顏色
                activebackground="#202124", 
                activeforeground="white"
            )
            rb.pack(side=tk.LEFT, padx=15)

        # 2. 分數顯示
        self.score_label = tk.Label(
            self.root, text=f"得分: {self.score}  |  最高分: {self.high_score}",
            font=('Arial', 14, 'bold'), bg="#202124", fg="white"
        )
        self.score_label.pack(pady=10)

        # 3. 提示訊息
        self.info_label = tk.Label(
            self.root, text="選擇難度後點擊開始！",
            font=('Arial', 12, 'bold'), bg="#202124", fg="#EA4335"
        )
        self.info_label.pack(pady=5)

        # 4. 2x2 記憶按鈕矩陣
        self.btn_frame = tk.Frame(self.root, bg="#202124")
        self.btn_frame.pack(pady=10)
        
        self.buttons = []
        for i in range(4):
            btn = tk.Button(
                self.btn_frame, bg=self.colors[i], 
                width=12, height=6, relief="flat",
                command=lambda x=i: self.handle_player_input(x),
                state="disabled"
            )
            btn.grid(row=i//2, column=i%2, padx=10, pady=10)
            self.buttons.append(btn)

        # 5. 開始按鈕
        self.start_btn = tk.Button(
            self.root, text="開始挑戰", font=('Arial', 12, 'bold'),
            bg="#8ab4f8", fg="#202124", width=15, height=2,
            command=self.start_game
        )
        self.start_btn.pack(pady=20)

    def start_game(self):
        self.score = 0
        self.sequence = []
        self.start_btn.config(state="disabled")
        self.next_level()

    def next_level(self):
        self.score_label.config(text=f"得分: {self.score}  |  最高分: {self.high_score}")
        self.player_sequence = []
        
        # 難度邏輯處理
        level = self.difficulty.get()
        
        # 困難模式：每過 3 關一次增加 2 個顏色
        num_to_add = 1
        if level == "困難" and self.score > 0 and self.score % 3 == 0:
            num_to_add = 2
            
        for _ in range(num_to_add):
            self.sequence.append(random.randint(0, 3))
        
        # 速度邏輯
        if level == "簡單":
            self.current_speed = 750
        elif level == "普通":
            self.current_speed = max(250, 600 - (self.score * 35))
        else: # 困難
            self.current_speed = max(180, 450 - (self.score * 50))
            
        self.play_sequence()

    def play_sequence(self):
        self.info_label.config(text="● 電腦示範中...", fg="#FBBC05")
        self.root.update()
        for btn in self.buttons: btn.config(state="disabled")
        
        self.root.after(600)

        for idx in self.sequence:
            self.flash_button(idx, is_computer=True)
            self.root.after(int(self.current_speed * 0.4)) 
            
        self.root.after(100, self.set_player_turn)

    def set_player_turn(self):
        self.info_label.config(text="★ 換你了！", fg="#34A853")
        for btn in self.buttons: btn.config(state="normal")

    def flash_button(self, index, is_computer=False):
        winsound.Beep(self.sounds[index], 200)
        original_color = self.colors[index]
        self.buttons[index].config(bg=self.light_colors[index])
        self.root.update()
        
        flash_time = 300 if is_computer else 150
        self.root.after(flash_time, lambda: self.buttons[index].config(bg=original_color))
        self.root.update()

    def handle_player_input(self, index):
        winsound.Beep(self.sounds[index], 100)
        self.flash_button_only(index)
        self.player_sequence.append(index)
        
        current_step = len(self.player_sequence) - 1
        if self.player_sequence[current_step] != self.sequence[current_step]:
            self.game_over()
            return

        if len(self.player_sequence) == len(self.sequence):
            self.score += 1
            if self.score > self.high_score: self.high_score = self.score
            self.info_label.config(text="正確！下一關...", fg="#4285F4")
            for btn in self.buttons: btn.config(state="disabled")
            self.root.after(800, self.next_level)

    def flash_button_only(self, index):
        original_color = self.colors[index]
        self.buttons[index].config(bg=self.light_colors[index])
        self.root.after(150, lambda: self.buttons[index].config(bg=original_color))

    def game_over(self):
        winsound.Beep(200, 500)
        self.info_label.config(text="挑戰失敗", fg="#EA4335")
        messagebox.showinfo("GAME OVER", f"難度: {self.difficulty.get()}\n得分: {self.score}")
        self.start_btn.config(state="normal")
        for btn in self.buttons: btn.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    game = MemoryGameHardcorePro(root)
    root.mainloop()