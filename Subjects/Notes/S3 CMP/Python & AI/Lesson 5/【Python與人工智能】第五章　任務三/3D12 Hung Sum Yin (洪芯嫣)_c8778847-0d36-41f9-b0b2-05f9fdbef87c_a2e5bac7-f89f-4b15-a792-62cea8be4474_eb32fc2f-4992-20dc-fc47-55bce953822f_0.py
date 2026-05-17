import tkinter as tk
from tkinter import messagebox
import random
import time

class UltimateTicTacToe:
    def __init__(self, root):
        self.root = root
        self.root.title("過三關：極限生存賽 3X99")
        self.root.geometry("400x600")
        self.root.configure(bg="#1a1a1a") # 深色酷炫背景

        self.current_player = "X"
        self.timer_value = 5
        self.score = 0
        self.game_active = True
        
        self.board_state = [[None for _ in range(3)] for _ in range(3)]
        self.setup_ui()
        self.update_timer()

    def setup_ui(self):
        # 分數與標語
        self.info_label = tk.Label(self.root, text="準備戰鬥！", font=('Microsoft JhengHei', 16, 'bold'), 
                                   bg="#1a1a1a", fg="#00ff00")
        self.info_label.pack(pady=10)

        # 計時器顯示
        self.timer_label = tk.Label(self.root, text=f"剩餘時間: {self.timer_value}s", 
                                    font=('Courier', 20, 'bold'), bg="#1a1a1a", fg="#ff3e3e")
        self.timer_label.pack(pady=5)

        # 棋盤
        self.grid_frame = tk.Frame(self.root, bg="#333", padx=10, pady=10)
        self.grid_frame.pack(pady=20)

        for r in range(3):
            for c in range(3):
                btn = tk.Button(self.grid_frame, text="", font=('Verdana', 35, 'bold'), 
                                width=3, height=1, bg="#2d2d2d", fg="white",
                                activebackground="#444", relief="flat",
                                command=lambda r=r, c=c: self.player_move(r, c))
                btn.grid(row=r, column=c, padx=3, pady=3)
                self.board_state[r][c] = btn

        # 底部嘲諷區
        self.taunt_label = tk.Label(self.root, text="AI: 快點，我等得都要生鏽了...", 
                                    font=('Microsoft JhengHei', 10), bg="#1a1a1a", fg="#888")
        self.taunt_label.pack(side=tk.BOTTOM, pady=20)

    def update_timer(self):
        if self.game_active:
            if self.timer_value > 0:
                self.timer_value -= 1
                self.timer_label.config(text=f"剩餘時間: {self.timer_value}s")
                self.root.after(1000, self.update_timer)
            else:
                self.taunt_label.config(text="AI: 沒時間了！隨便塞一個給你！", fg="#ff8c00")
                self.force_random_move()

    def force_random_move(self):
        empty_cells = [(r, c) for r in range(3) for c in range(3) if self.board_state[r][c]["text"] == ""]
        if empty_cells:
            r, c = random.choice(empty_cells)
            self.player_move(r, c)
        
    def player_move(self, r, c):
        if self.board_state[r][c]["text"] == "" and self.game_active:
            self.make_move(r, c, "X")
            self.timer_value = 6 # 重置計時 (給下一回合)
            
            if not self.check_end():
                self.root.after(400, self.ai_smart_move)

    def ai_smart_move(self):
        # 簡單的 AI：優先擋人，否則隨機
        move = self.find_winning_move("O") or self.find_winning_move("X") or self.get_random_move()
        if move:
            self.make_move(move[0], move[1], "O")
            self.check_end()
            self.taunt_label.config(text=random.choice([
                "AI: 這一手你沒想到吧？",
                "AI: 嘖嘖，太簡單了。",
                "AI: 你是在讓我的嗎？",
                "AI: 專心點！"
            ]))

    def make_move(self, r, c, player):
        color = "#00d4ff" if player == "X" else "#ff007f"
        self.board_state[r][c].config(text=player, fg=color)
        # 震動效果
        self.shake_screen()

    def find_winning_move(self, char):
        for r in range(3):
            for c in range(3):
                if self.board_state[r][c]["text"] == "":
                    self.board_state[r][c]["text"] = char
                    if self.check_win_logic(char):
                        self.board_state[r][c]["text"] = ""
                        return (r, c)
                    self.board_state[r][c]["text"] = ""
        return None

    def get_random_move(self):
        empty = [(r, c) for r in range(3) for c in range(3) if self.board_state[r][c]["text"] == ""]
        return random.choice(empty) if empty else None

    def check_win_logic(self, p):
        s = self.board_state
        for i in range(3):
            if all(s[i][j]["text"] == p for j in range(3)): return True
            if all(s[j][i]["text"] == p for j in range(3)): return True
        if s[0][0]["text"] == s[1][1]["text"] == s[2][2]["text"] == p: return True
        if s[0][2]["text"] == s[1][1]["text"] == s[2][0]["text"] == p: return True
        return False

    def shake_screen(self):
        # 簡單的視窗抖動模擬
        orig_x = self.root.winfo_x()
        for i in range(3):
            self.root.geometry(f"+{orig_x+5}+{self.root.winfo_y()}")
            self.root.update()
            time.sleep(0.02)
            self.root.geometry(f"+{orig_x-5}+{self.root.winfo_y()}")
            self.root.update()
            time.sleep(0.02)
        self.root.geometry(f"+{orig_x}+{self.root.winfo_y()}")

    def check_end(self):
        if self.check_win_logic("X"):
            self.end_game("你竟然贏了！不可能！")
            return True
        if self.check_win_logic("O"):
            self.end_game("哈哈！回家再練練吧！")
            return True
        if not self.get_random_move():
            self.end_game("平手... 算你走運。")
            return True
        return False

    def end_game(self, msg):
        self.game_active = False
        messagebox.showinfo("終局戰報", msg)
        self.reset()

    def reset(self):
        for r in range(3):
            for c in range(3):
                self.board_state[r][c].config(text="", bg="#2d2d2d")
        self.game_active = True
        self.timer_value = 5
        self.info_label.config(text="再戰一場？")

if __name__ == "__main__":
    root = tk.Tk()
    game = UltimateTicTacToe(root)
    root.mainloop()