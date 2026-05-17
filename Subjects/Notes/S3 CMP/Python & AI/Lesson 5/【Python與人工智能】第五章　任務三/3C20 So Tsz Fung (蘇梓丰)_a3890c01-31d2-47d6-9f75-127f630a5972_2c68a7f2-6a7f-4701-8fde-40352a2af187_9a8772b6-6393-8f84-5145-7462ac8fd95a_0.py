import pygame
import random
import time

# 初始化 Pygame
pygame.init()

# 遊戲視窗設定
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("極速方塊：連擊風暴 - Task3_3X99")

# 顏色定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 80, 80)
GOLD = (255, 215, 0)

# 遊戲變數
score = 0
combo = 0
time_left = 30.0  # 初始時間
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 32)
big_font = pygame.font.SysFont("arial", 64)

# 目標物設定
target_rect = pygame.Rect(0, 0, 50, 50)
target_rect.center = (WIDTH // 2, HEIGHT // 2)
target_color = RED

def spawn_target():
    target_rect.x = random.randint(50, WIDTH - 50)
    target_rect.y = random.randint(50, HEIGHT - 50)
    return (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))

# 遊戲主迴圈
running = True
game_over = False

while running:
    dt = clock.tick(60) / 1000.0  # 取得幀間時間（秒）

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
            if target_rect.collidepoint(event.pos):
                # 擊中目標！
                combo += 1
                points = 10 * combo
                score += points
                time_left += 0.5  # 獎勵時間
                target_color = spawn_target()
                # 這裡可以加入音效：pygame.mixer.Sound('hit.wav').play()
            else:
                # 點空了，連擊中斷
                combo = 0
        
        if event.type == pygame.KEYDOWN and game_over:
            if event.key == pygame.K_r:  # 按 R 重新開始
                score = 0
                combo = 0
                time_left = 30.0
                game_over = False

    if not game_over:
        time_left -= dt
        if time_left <= 0:
            time_left = 0
            game_over = True

    # 繪製畫面
    screen.fill(BLACK)
    
    if not game_over:
        # 繪製目標
        pygame.draw.rect(screen, target_color, target_rect)
        
        # 顯示 UI
        score_text = font.render(f"Score: {score}", True, WHITE)
        combo_text = font.render(f"Combo: x{combo}", True, GOLD)
        time_text = font.render(f"Time: {time_left:.1f}s", True, RED if time_left < 5 else WHITE)
        
        screen.blit(score_text, (20, 20))
        screen.blit(combo_text, (20, 60))
        screen.blit(time_text, (WIDTH - 180, 20))
    else:
        # 結束畫面
        over_text = big_font.render("GAME OVER", True, RED)
        final_score = font.render(f"Final Score: {score}", True, WHITE)
        retry_text = font.render("Press 'R' to Restart", True, GOLD)
        
        screen.blit(over_text, (WIDTH // 2 - 150, HEIGHT // 2 - 100))
        screen.blit(final_score, (WIDTH // 2 - 100, HEIGHT // 2))
        screen.blit(retry_text, (WIDTH // 2 - 120, HEIGHT // 2 + 60))

    pygame.display.flip()

pygame.quit()