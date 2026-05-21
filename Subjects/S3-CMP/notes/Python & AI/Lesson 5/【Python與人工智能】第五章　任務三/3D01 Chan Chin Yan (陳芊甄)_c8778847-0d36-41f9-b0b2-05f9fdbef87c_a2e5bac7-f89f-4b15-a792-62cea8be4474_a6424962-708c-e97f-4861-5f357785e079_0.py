import tkinter as tk
import random

# 遊戲配置
GAME_WIDTH = 600
GAME_HEIGHT = 600
GRID_SIZE = 20
CELL_SIZE = GAME_WIDTH // GRID_SIZE

# 顏色設定
COLORS = {
    'bg': '#1a1a2e',
    'snake_head': '#4ecdc4',
    'snake_body': '#2ecc71',
    'food': '#ff6b6b',
    'grid': '#16213e',
    'text': '#ffffff'
}

class SnakeGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("貪食蛇")
        self.root.resizable(False, False)
        
        # 遊戲畫布
        self.canvas = tk.Canvas(self.root, width=GAME_WIDTH, height=GAME_HEIGHT, 
                                bg=COLORS['bg'], highlightthickness=0)
        self.canvas.pack()
        
        # 分數顯示
        self.score_label = tk.Label(self.root, text="分數: 0", font=('Arial', 14, 'bold'),
                                     bg=COLORS['bg'], fg=COLORS['text'])
        self.score_label.pack(pady=5)
        
        # 遊戲狀態
        self.snake = [(GRID_SIZE // 2, GRID_SIZE // 2)]  # 蛇身座標
        self.direction = (0, -1)  # 初始方向：向上
        self.next_direction = (0, -1)
        self.food = self.generate_food()
        self.score = 0
        self.game_over = False
        self.paused = False
        
        # 遊戲速度 (毫秒)
        self.speed = 150
        self.after_id = None
        
        # 綁定鍵盤事件
        self.root.bind('<Up>', lambda e: self.change_direction(0, -1))
        self.root.bind('<Down>', lambda e: self.change_direction(0, 1))
        self.root.bind('<Left>', lambda e: self.change_direction(-1, 0))
        self.root.bind('<Right>', lambda e: self.change_direction(1, 0))
        self.root.bind('<space>', self.toggle_pause)
        self.root.bind('<r>', lambda e: self.reset_game())
        
        # 確保視窗獲得焦點
        self.canvas.focus_set()
        self.canvas.bind('<Up>', lambda e: self.change_direction(0, -1))
        self.canvas.bind('<Down>', lambda e: self.change_direction(0, 1))
        self.canvas.bind('<Left>', lambda e: self.change_direction(-1, 0))
        self.canvas.bind('<Right>', lambda e: self.change_direction(1, 0))
        
        # 開始遊戲
        self.draw_game()
        self.start_game_loop()
        
        # 顯示開始提示
        self.show_start_hint()
        
        self.root.mainloop()
    
    def generate_food(self):
        """生成食物，確保不在蛇身上"""
        while True:
            x = random.randint(0, GRID_SIZE - 1)
            y = random.randint(0, GRID_SIZE - 1)
            if (x, y) not in self.snake:
                return (x, y)
    
    def change_direction(self, dx, dy):
        """改變方向（不能反向）"""
        if self.game_over or self.paused:
            return
        
        # 防止蛇直接反向
        if (dx, dy) != (-self.direction[0], -self.direction[1]):
            self.next_direction = (dx, dy)
    
    def move(self):
        """移動蛇"""
        if self.game_over or self.paused:
            return
        
        # 更新方向
        self.direction = self.next_direction
        
        # 計算新頭部位置
        head = self.snake[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])
        
        # 檢查是否吃到食物
        if new_head == self.food:
            # 吃到食物：增加蛇身（不刪除尾部）
            self.snake.insert(0, new_head)
            self.score += 10
            self.update_score()
            self.food = self.generate_food()
            
            # 每100分增加速度
            if self.score % 100 == 0 and self.speed > 80:
                self.speed = max(80, self.speed - 5)
                self.restart_game_loop()
        else:
            # 沒吃到食物：移動蛇（加入頭部，刪除尾部）
            self.snake.insert(0, new_head)
            self.snake.pop()
        
        # 檢查碰撞
        if self.check_collision():
            self.game_over = True
            self.show_game_over()
            return
    
    def check_collision(self):
        """檢查碰撞（牆壁或自身）"""
        head = self.snake[0]
        
        # 檢查牆壁碰撞
        if head[0] < 0 or head[0] >= GRID_SIZE or head[1] < 0 or head[1] >= GRID_SIZE:
            return True
        
        # 檢查自身碰撞（頭部碰到身體）
        if head in self.snake[1:]:
            return True
        
        return False
    
    def update_score(self):
        """更新分數顯示"""
        self.score_label.config(text=f"分數: {self.score}")
    
    def draw_game(self):
        """繪製遊戲畫面"""
        self.canvas.delete("all")
        
        # 繪製網格
        for i in range(GRID_SIZE):
            self.canvas.create_line(i * CELL_SIZE, 0, i * CELL_SIZE, GAME_HEIGHT,
                                    fill=COLORS['grid'], width=1)
            self.canvas.create_line(0, i * CELL_SIZE, GAME_WIDTH, i * CELL_SIZE,
                                    fill=COLORS['grid'], width=1)
        
        # 繪製食物
        fx, fy = self.food
        x1 = fx * CELL_SIZE
        y1 = fy * CELL_SIZE
        x2 = x1 + CELL_SIZE
        y2 = y1 + CELL_SIZE
        self.canvas.create_oval(x1 + 2, y1 + 2, x2 - 2, y2 - 2, 
                                fill=COLORS['food'], outline='')
        # 食物光暈效果
        self.canvas.create_oval(x1 + 5, y1 + 5, x2 - 5, y2 - 5, 
                                fill='#ff9999', outline='')
        
        # 繪製蛇
        for i, (x, y) in enumerate(self.snake):
            x1 = x * CELL_SIZE
            y1 = y * CELL_SIZE
            x2 = x1 + CELL_SIZE
            y2 = y1 + CELL_SIZE
            
            # 蛇頭和蛇身不同顏色
            if i == 0:
                color = COLORS['snake_head']
                # 蛇頭眼睛
                eye_size = CELL_SIZE // 6
                if self.direction == (0, -1):  # 向上
                    eye1 = (x1 + CELL_SIZE * 0.3, y1 + CELL_SIZE * 0.3)
                    eye2 = (x1 + CELL_SIZE * 0.7, y1 + CELL_SIZE * 0.3)
                elif self.direction == (0, 1):  # 向下
                    eye1 = (x1 + CELL_SIZE * 0.3, y1 + CELL_SIZE * 0.7)
                    eye2 = (x1 + CELL_SIZE * 0.7, y1 + CELL_SIZE * 0.7)
                elif self.direction == (-1, 0):  # 向左
                    eye1 = (x1 + CELL_SIZE * 0.3, y1 + CELL_SIZE * 0.3)
                    eye2 = (x1 + CELL_SIZE * 0.3, y1 + CELL_SIZE * 0.7)
                else:  # 向右
                    eye1 = (x1 + CELL_SIZE * 0.7, y1 + CELL_SIZE * 0.3)
                    eye2 = (x1 + CELL_SIZE * 0.7, y1 + CELL_SIZE * 0.7)
                
                self.canvas.create_oval(eye1[0] - eye_size, eye1[1] - eye_size,
                                       eye1[0] + eye_size, eye1[1] + eye_size,
                                       fill='white', outline='')
                self.canvas.create_oval(eye2[0] - eye_size, eye2[1] - eye_size,
                                       eye2[0] + eye_size, eye2[1] + eye_size,
                                       fill='white', outline='')
                self.canvas.create_oval(eye1[0] - eye_size//2, eye1[1] - eye_size//2,
                                       eye1[0] + eye_size//2, eye1[1] + eye_size//2,
                                       fill='black', outline='')
                self.canvas.create_oval(eye2[0] - eye_size//2, eye2[1] - eye_size//2,
                                       eye2[0] + eye_size//2, eye2[1] + eye_size//2,
                                       fill='black', outline='')
            else:
                color = COLORS['snake_body']
            
            # 圓角矩形效果
            self.canvas.create_rectangle(x1 + 1, y1 + 1, x2 - 1, y2 - 1,
                                         fill=color, outline='', width=0)
            self.canvas.create_rectangle(x1 + 2, y1 + 2, x2 - 2, y2 - 2,
                                         fill=color, outline='')
        
        # 顯示暫停文字
        if self.paused and not self.game_over:
            self.canvas.create_text(GAME_WIDTH // 2, GAME_HEIGHT // 2,
                                   text="暫停\n按 空白鍵 繼續",
                                   fill=COLORS['text'], font=('Arial', 24, 'bold'),
                                   justify='center')
    
    def show_start_hint(self):
        """顯示開始提示"""
        self.canvas.create_text(GAME_WIDTH // 2, GAME_HEIGHT // 2 + 100,
                               text="使用方向鍵移動\n按 R 重新開始",
                               fill=COLORS['text'], font=('Arial', 14),
                               justify='center', tags="hint")
        self.root.after(3000, lambda: self.canvas.delete("hint"))
    
    def show_game_over(self):
        """顯示遊戲結束畫面"""
        self.canvas.create_text(GAME_WIDTH // 2, GAME_HEIGHT // 2 - 30,
                               text="GAME OVER",
                               fill='#ff6b6b', font=('Arial', 32, 'bold'))
        self.canvas.create_text(GAME_WIDTH // 2, GAME_HEIGHT // 2 + 30,
                               text=f"最終分數: {self.score}",
                               fill=COLORS['text'], font=('Arial', 18))
        self.canvas.create_text(GAME_WIDTH // 2, GAME_HEIGHT // 2 + 80,
                               text="按 R 重新開始",
                               fill=COLORS['text'], font=('Arial', 14))
    
    def toggle_pause(self, event=None):
        """暫停/繼續遊戲"""
        if not self.game_over:
            self.paused = not self.paused
            if not self.paused:
                self.start_game_loop()
            self.draw_game()
    
    def start_game_loop(self):
        """開始遊戲循環"""
        if not self.game_over and not self.paused:
            self.move()
            self.draw_game()
            self.after_id = self.root.after(self.speed, self.start_game_loop)
    
    def restart_game_loop(self):
        """重新啟動遊戲循環（改變速度時使用）"""
        if self.after_id:
            self.root.after_cancel(self.after_id)
        if not self.game_over and not self.paused:
            self.after_id = self.root.after(self.speed, self.start_game_loop)
    
    def reset_game(self):
        """重置遊戲"""
        if self.after_id:
            self.root.after_cancel(self.after_id)
        
        # 重置狀態
        self.snake = [(GRID_SIZE // 2, GRID_SIZE // 2)]
        self.direction = (0, -1)
        self.next_direction = (0, -1)
        self.food = self.generate_food()
        self.score = 0
        self.game_over = False
        self.paused = False
        self.speed = 150
        
        self.update_score()
        self.draw_game()
        self.start_game_loop()

if __name__ == "__main__":
    game = SnakeGame()