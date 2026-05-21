import pygame
import random
import time

# --- 初始化 ---
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Core Overload: 極速符號挑戰")
clock = pygame.time.Clock()

# 顏色定義
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
CYAN = (0, 255, 255)
RED = (255, 50, 50)
GOLD = (255, 215, 0)

# 字體
font_large = pygame.font.SysFont("arial", 72, bold=True)
font_small = pygame.font.SysFont("arial", 32)

# --- 遊戲變量 ---
target_keys = ["W", "A", "S", "D"]
current_target = random.choice(target_keys)
score = 0
combo = 0
time_limit = 1.5  # 每個按鍵的初始時間
start_time = time.time()

# 模擬音效函數 (如果你有 wav 文件，可以使用 pygame.mixer.Sound)
def play_feedback_sound(is_hit):
    # pygame.mixer.Sound("hit.wav").play() # 實際應用時取消註釋
    pass

def reset_target():
    global current_target, start_time, time_limit
    current_target = random.choice(target_keys)
    start_time = time.time()
    # 隨著分數增加，時間限制會稍微縮短，增加難度
    time_limit = max(0.6, 1.5 - (score / 5000))

# --- 主循環 ---
running = True
game_over = False

while running:
    screen.fill(BLACK)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN and not game_over:
            key_pressed = pygame.key.name(event.key).upper()
            
            if key_pressed == current_target.lower() or key_pressed == current_target:
                # 擊中邏輯
                combo += 1
                multiplier = 1 + (combo // 5) # 每 5 連擊倍率 +1
                score += 100 * multiplier
                play_feedback_sound(True)
                reset_target()
            else:
                # 按錯鍵
                combo = 0
                play_feedback_sound(False)

    if not game_over:
        # 計算剩餘時間
        elapsed = time.time() - start_time
        remaining_ratio = max(0, (time_limit - elapsed) / time_limit)
        
        if elapsed >= time_limit:
            # 時間到，Miss
            combo = 0
            reset_target()
            # 這裡可以加入扣血邏輯，為了簡化，我們先只重置連擊

        # --- 繪製界面 ---
        # 繪製時間條
        bar_color = CYAN if combo < 5 else GOLD
        pygame.draw.rect(screen, bar_color, (200, 450, 400 * remaining_ratio, 20))
        
        # 繪製當前目標
        target_text = font_large.render(current_target, True, WHITE)
        screen.blit(target_text, (WIDTH//2 - 30, HEIGHT//2 - 50))
        
        # 繪製 UI (分數與連擊)
        score_text = font_small.render(f"Score: {score}", True, WHITE)
        combo_text = font_small.render(f"Combo: {combo} (x{1 + combo//5})", True, bar_color)
        screen.blit(score_text, (20, 20))
        screen.blit(combo_text, (20, 60))
        
        # 提示文字
        hint_text = font_small.render("Press W, A, S, or D", True, (100, 100, 100))
        screen.blit(hint_text, (WIDTH//2 - 100, 500))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()