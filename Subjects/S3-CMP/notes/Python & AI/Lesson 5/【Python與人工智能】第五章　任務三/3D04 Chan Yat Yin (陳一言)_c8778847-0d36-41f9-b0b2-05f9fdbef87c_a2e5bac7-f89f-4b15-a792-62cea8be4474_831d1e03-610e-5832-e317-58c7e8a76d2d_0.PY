import tkinter as tk
import random
import messagebox

class HungryGame:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("瘋狂進食：Hungry Frenzy")
        self.score = 0
        self.combo = 0
        self.timer = 10  # 初始時間
        
        # 建立 UI
        self.label_score = tk.Label(self.window, text="分數: 0 | Combo: 0", font=("Arial", 18))
        self.label_score.pack()
        self.label_time = tk.Label(self.window, text="剩餘時間: 10s", font=("Arial", 18), fg="red")
        self.label_time.pack()
        
        self.frame = tk.Frame(self.window)
        self.frame.pack()
        self.buttons = [[tk.Button(self.frame, width=8, height=4, command=lambda r=i, c=j: self.eat(r, c)) 
                         for j in range(3)] for i in range(3)]
        for i in range(3):
            for j in range(3): self.buttons[i][j].grid(row=i, column=j)
            
        self.spawn_food()
        self.update_timer()
        self.window.mainloop()

    def spawn_food(self):
        """隨機生成食物"""
        for i in range(3):
            for j in range(3): self.buttons[i][j].config(text="", bg="SystemButtonFace")
        self.target = (random.randint(0,2), random.randint(0,2))
        self.buttons[self.target[0]][self.target[1]].config(text="🍎", bg="lightgreen")

    def eat(self, r, c):
        if (r, c) == self.target:
            self.combo += 1
            self.score += (10 * self.combo)
            self.timer += 1  # 吃到獎勵時間
            self.label_score.config(text=f"分數: {self.score} | Combo: {self.combo}")
            self.spawn_food()
        else:
            self.combo = 0 # 吃錯重置連擊
            self.label_score.config(text=f"分數: {self.score} | Combo: 0")

    def update_timer(self):
        if self.timer > 0:
            self.label_time.config(text=f"剩餘時間: {self.timer}s")
            self.timer -= 1
            self.window.after(1000, self.update_timer)
        else:
            messagebox.showinfo("遊戲結束", f"你餓扁了！最終分數: {self.score}")
            self.window.destroy()

if __name__ == "__main__":
    HungryGame()