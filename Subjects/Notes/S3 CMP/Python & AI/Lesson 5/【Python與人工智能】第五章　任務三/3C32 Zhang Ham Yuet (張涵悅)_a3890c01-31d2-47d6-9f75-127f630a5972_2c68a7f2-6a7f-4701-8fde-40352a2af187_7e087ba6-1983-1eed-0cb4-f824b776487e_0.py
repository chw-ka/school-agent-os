import tkinter as tk
import random
from tkinter import messagebox

class SubwayRun:
    def __init__(self, root):
        self.root = root
        self.root.title("極速跑酷 - 簡易版")
        
        # 遊戲參數
        self.width = 400
        self.height = 600
        self.score = 0
        self.game_speed = 10
        self.is_game_over = False
        
        # 畫布設置
        self.canvas = tk.Canvas(root, width=self.width, height=self.height, bg="#34495E", highlightthickness=0)
        self.canvas.pack()
        
        # 跑道線條 (模擬透視感)
        self.canvas.create_line(133, 0, 133, 600, fill="#7F8C8D", dash=(10, 10))
        self.canvas.create_line(266, 0, 266, 600, fill="#7F8C8D", dash=(10, 10))
        
        # 玩家設置 (位於中間跑道底部)
        self.player_lane = 1  # 0: 左, 1: 中, 2: 右
        self.player_id = self.canvas.create_rectangle(0, 0, 40, 60, fill="#3498DB", outline="white", width=2)
        self.update_player_position()
        
        # 障礙物與金幣列表
        self.items = [] # 儲存物件 ID 與 類型
        
        # 分數顯示
        self.score_text = self.canvas.create_text(50, 20, text=f"Score: {self.score}", fill="white", font=("Arial", 14, "bold"))
        
        # 綁定按鍵
        self.root.bind("<Left>", self.move_left)
        self.root.bind("<Right>", self.move_right)
        
        # 開始循環
        self.spawn_item()
        self.game_loop()

    def update_player_position(self):
        # 根據所在跑道計算 X 坐標
        lane_x = [66, 200, 333]
        x = lane_x[self.player_lane]
        y = 530
        self.canvas.coords(self.player_id, x-20, y-30, x+20, y+30)

    def move_left(self, event):
        if self.player_lane > 0 and not self.is_game_over:
            self.player_lane -= 1
            self.update_player_position()

    def move_right(self, event):
        if self.player_lane < 2 and not self.is_game_over:
            self.player_lane += 1
            self.update_player_position()

    def spawn_item(self):
        if self.is_game_over: return
        
        lane = random.randint(0, 2)
        lane_x = [66, 200, 333]
        x = lane_x[lane]
        
        # 隨機生成金幣或障礙物
        if random.random() > 0.3: # 70% 幾率生成金幣
            item = self.canvas.create_oval(x-15, -50, x+15, -20, fill="#F1C40F", outline="#D4AC0D", width=2)
            self.items.append({'id': item, 'type': 'coin'})
        else: # 30% 幾率生成障礙物
            item = self.canvas.create_rectangle(x-30, -60, x+30, -10, fill="#E74C3C", outline="black")
            self.items.append({'id': item, 'type': 'obstacle'})
            
        # 隨機間隔後生成下一個物件
        self.root.after(random.randint(600, 1200), self.spawn_item)

    def game_loop(self):
        if self.is_game_over: return
        
        items_to_remove = []
        player_coords = self.canvas.coords(self.player_id)
        
        for item in self.items:
            # 移動物件下落
            self.canvas.move(item['id'], 0, self.game_speed)
            item_coords = self.canvas.coords(item['id'])
            
            # 碰撞檢測
            if self.check_collision(player_coords, item_coords):
                if item['type'] == 'coin':
                    self.score += 10
                    self.canvas.itemconfig(self.score_text, text=f"Score: {self.score}")
                    self.canvas.delete(item['id'])
                    items_to_remove.append(item)
                    # 每吃 100 分加速一點
                    if self.score % 100 == 0: self.game_speed += 0.5
                else:
                    self.game_over()
                    return
            
            # 超出螢幕則移除
            if item_coords[1] > self.height:
                self.canvas.delete(item['id'])
                items_to_remove.append(item)
        
        # 清理已刪除的物件
        for item in items_to_remove:
            if item in self.items:
                self.items.remove(item)
                
        self.root.after(30, self.game_loop)

    def check_collision(self, p, i):
        # 簡單的矩形重疊判斷
        return not (p[2] < i[0] or p[0] > i[2] or p[3] < i[1] or p[1] > i[3])

    def game_over(self):
        self.is_game_over = True
        messagebox.showinfo("遊戲結束", f"你撞到了障礙物！\n最終得分: {self.score}")
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    game = SubwayRun(root)
    root.mainloop()