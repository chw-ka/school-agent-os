import pygame
import random
import sys

# --- 遊戲配置 ---
WIDTH, HEIGHT = 400, 600
FPS = 60
GRAVITY = 0.4        # 重力：每幀向下增加的速度
FLAP_STRENGTH = -7   # 翅膀拍打：按鍵時向上的瞬時速度
PIPE_SPEED = 3       # 水管向左移動速度
PIPE_GAP = 150       # 上下水管之間的間隙大小

# 顏色
WHITE = (255, 255, 255)
SKY_BLUE = (135, 206, 235)
BIRD_YELLOW = (255, 255, 0)
PIPE_GREEN = (34, 139, 34)

class Bird:
    def __init__(self):
        self.x = 50
        self.y = HEIGHT // 2
        self.vel = 0
        self.rect = pygame.Rect(self.x, self.y, 34, 24)

    def update(self):
        # 物理模擬
        self.vel += GRAVITY
        self.y += self.vel
        self.rect.y = self.y

    def flap(self):
        self.vel = FLAP_STRENGTH

    def draw(self, screen):
        pygame.draw.rect(screen, BIRD_YELLOW, self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2) # 邊框

class Pipe:
    def __init__(self, x):
        self.x = x
        self.top_height = random.randint(50, HEIGHT - PIPE_GAP - 50)
        self.passed = False
        # 上半部水管
        self.top_rect = pygame.Rect(self.x, 0, 50, self.top_height)
        # 下半部水管
        self.bottom_rect = pygame.Rect(self.x, self.top_height + PIPE_GAP, 50, HEIGHT)

    def update(self):
        self.x -= PIPE_SPEED
        self.top_rect.x = self.x
        self.bottom_rect.x = self.x

    def draw(self, screen):
        pygame.draw.rect(screen, PIPE_GREEN, self.top_rect)
        pygame.draw.rect(screen, PIPE_GREEN, self.bottom_rect)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Flappy Bird Python")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 32, bold=True)

    bird = Bird()
    pipes = [Pipe(WIDTH + 100)]
    score = 0
    game_over = False

    while True:
        screen.fill(SKY_BLUE)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if game_over:
                        return main() # 重新開始
                    bird.flap()

        if not game_over:
            bird.update()
            
            # 檢查是否觸碰邊界
            if bird.y < 0 or bird.y > HEIGHT:
                game_over = True

            # 水管邏輯
            if pipes[-1].x < WIDTH - 200: # 每隔一段距離生成新水管
                pipes.append(Pipe(WIDTH))

            for pipe in pipes[:]:
                pipe.update()
                # 碰撞檢測
                if bird.rect.colliderect(pipe.top_rect) or bird.rect.colliderect(pipe.bottom_rect):
                    game_over = True
                
                # 計分
                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    score += 1
                
                # 移除畫面外的水管
                if pipe.x < -50:
                    pipes.remove(pipe)

        # --- 繪圖 ---
        bird.draw(screen)
        for pipe in pipes:
            pipe.draw(screen)

        # 顯示分數
        score_surf = font.render(str(score), True, WHITE)
        screen.blit(score_surf, (WIDTH // 2 - 10, 50))

        if game_over:
            over_surf = font.render("GAME OVER", True, (255, 0, 0))
            screen.blit(over_surf, (WIDTH // 2 - 80, HEIGHT // 2 - 20))
            hint_surf = pygame.font.SysFont("Arial", 20).render("Press SPACE to Restart", True, (0, 0, 0))
            screen.blit(hint_surf, (WIDTH // 2 - 85, HEIGHT // 2 + 30))

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()