import tkinter as tk
import random

# 遊戲視窗設定
WIDTH = 400
HEIGHT = 400
GRID = 20
SPEED = 120

# 主視窗
root = tk.Tk()
root.title("貪吃蛇遊戲")
root.resizable(False, False)

# 畫布
canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="#1a1a1a")
canvas.pack()

# 全域變數
snake = []
food = None
dir_x = GRID
dir_y = 0
game_over = False
score = 0

# 初始化遊戲
def init_game():
    global snake, dir_x, dir_y, game_over, score
    canvas.delete("all")
    snake = [[100, 100], [80, 100], [60, 100]]
    dir_x = GRID
    dir_y = 0
    game_over = False
    score = 0
    create_food()
    draw_snake()
    root.after(SPEED, game_loop)

# 產生食物
def create_food():
    global food
    while True:
        x = random.randrange(0, WIDTH, GRID)
        y = random.randrange(0, HEIGHT, GRID)
        if [x, y] not in snake:
            break
    food = [x, y]
    canvas.create_rectangle(x, y, x+GRID, y+GRID, fill="#ff4757", outline="")

# 畫蛇
def draw_snake():
    canvas.delete("snake")
    for idx, (x, y) in enumerate(snake):
        color = "#2ed573" if idx == 0 else "#7bed9f"
        canvas.create_rectangle(x, y, x+GRID, y+GRID, fill=color, tag="snake", outline="")

# 移動蛇
def move_snake():
    head_x, head_y = snake[0]
    new_head = [head_x + dir_x, head_y + dir_y]
    snake.insert(0, new_head)

    # 吃到食物
    if new_head == food:
        create_food()
        global score
        score += 10
    else:
        snake.pop()

# 碰撞偵測
def check_collision():
    head = snake[0]
    # 撞牆
    if head[0] < 0 or head[0] >= WIDTH or head[1] < 0 or head[1] >= HEIGHT:
        return True
    # 撞自己
    if head in snake[1:]:
        return True
    return False

# 遊戲迴圈
def game_loop():
    global game_over
    if game_over:
        return
    
    move_snake()
    if check_collision():
        game_over = True
        canvas.create_text(WIDTH//2, HEIGHT//2, fill="white", font=("微軟正黑體", 24, "bold"),
                           text=f"遊戲結束\n得分：{score}")
        canvas.create_text(WIDTH//2, HEIGHT//2+50, fill="#aaa", font=("微軟正黑體", 14),
                           text="按 R 重新開始")
        return
    
    draw_snake()
    root.after(SPEED, game_loop)

# 方向控制
def key_control(event):
    global dir_x, dir_y
    key = event.keysym
    # 防止原地回頭
    if key == "Up" and dir_y != GRID:
        dir_x = 0
        dir_y = -GRID
    elif key == "Down" and dir_y != -GRID:
        dir_x = 0
        dir_y = GRID
    elif key == "Left" and dir_x != GRID:
        dir_x = -GRID
        dir_y = 0
    elif key == "Right" and dir_x != -GRID:
        dir_x = GRID
        dir_y = 0
    # 重新開始
    elif key == "r" or key == "R":
        init_game()

# 綁定按鍵
root.bind_all("<Key>", key_control)

# 啟動遊戲
init_game()
root.mainloop()