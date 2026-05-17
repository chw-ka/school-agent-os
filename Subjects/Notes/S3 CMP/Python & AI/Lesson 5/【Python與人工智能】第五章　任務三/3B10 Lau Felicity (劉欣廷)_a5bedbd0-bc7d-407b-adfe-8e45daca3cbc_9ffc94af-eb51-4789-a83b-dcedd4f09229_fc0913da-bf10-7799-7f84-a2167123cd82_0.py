import pygame
import random
import math

# 初始化 Pygame
pygame.init()
pygame.mixer.init()

# 螢幕設定
WIDTH, HEIGHT = 600, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pixel Dodger: Overdrive")

# 顏色定義
WHITE = (255, 255, 255)
BLACK = (20, 20, 25)
PLAYER_COLOR = (50, 255, 50)
ENEMY_COLOR = (255, 50, 50)
COMBO_COLOR = (255, 200, 0)

# 遊戲變數
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 32)
large_font = pygame.font.SysFont("Arial", 64)

def run_game():
    player_size = 40
    player_x = WIDTH // 2
    player_y = HEIGHT - 100
    player_speed = 8

    enemies = []
    enemy_speed = 5
    spawn_timer = 0

    score = 0
    combo = 0
    max_combo = 0
    shake_timer = 0
    running = True

    while running:
        screen.fill(BLACK)
        
        # 螢幕震動邏輯
        offset_x, offset_y = 0, 0
        if shake_timer > 0:
            offset_x = random.randint(-5, 5)
            offset_y = random.randint(-5, 5)
            shake_timer -= 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 玩家移動
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < WIDTH - player_size:
            player_x += player_speed

        # 生成敵人
        spawn_timer += 1
        if spawn_timer > max(10, 30 - int(score/500)): # 難度隨分數提升
            enemy_w = random.randint(40, 100)
            enemies.append([random.randint(0, WIDTH-enemy_w), -50, enemy_w, 30])
            spawn_timer = 0

        # 更新敵人位置
        for enemy in enemies[:]:
            enemy[1] += enemy_speed + (score / 1000) # 速度隨分數提升
            
            # 碰撞檢測
            player_rect = pygame.Rect(player_x + offset_x, player_y + offset_y, player_size, player_size)
            enemy_rect = pygame.Rect(enemy[0], enemy[1], enemy[2], enemy[3])
            
            if player_rect.colliderect(enemy_rect):
                shake_timer = 15
                combo = 0 # 撞到就斷 Combo
                score -= 100 # 懲罰
                enemies.remove(enemy)
                if score < 0: score = 0
            
            elif enemy[1] > HEIGHT:
                enemies.remove(enemy)
                combo += 1
                score += 10 * (1 + combo // 5) # 連擊加成
                if combo > max_combo: max_combo = combo

        # 繪製玩家
        pygame.draw.rect(screen, PLAYER_COLOR, (player_x + offset_x, player_y + offset_y, player_size, player_size))

        # 繪製敵人
        for enemy in enemies:
            pygame.draw.rect(screen, ENEMY_COLOR, (enemy[0], enemy[1], enemy[2], enemy[3]))

        # 顯示 UI
        score_text = font.render(f"Score: {int(score)}", True, WHITE)
        combo_text = font.render(f"Combo: {combo}x", True, COMBO_COLOR if combo > 5 else WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(combo_text, (10, 50))
        
        if combo > 10:
            overdrive_text = font.render("OVERDRIVE!", True, (255, 0, 0))
            screen.blit(overdrive_text, (WIDTH//2 - 50, 10))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    run_game()