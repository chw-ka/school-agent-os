import pygame
import random

# --- 初始化 ---
pygame.init()
WIDTH, HEIGHT = 800, 450
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("極速跑酷：怪物襲來")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 24)

# --- 顏色與參數 ---
WHITE, BLACK, RED = (255, 255, 255), (0, 0, 0), (255, 50, 50)
SKY_BLUE = (135, 206, 235)
GROUND_Y = HEIGHT - 50
GRAVITY = 0.7

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((35, 50))
        self.image.fill((255, 100, 0))
        self.rect = self.image.get_rect(midbottom=(100, GROUND_Y))
        self.vel_y = 0
        self.jump_count = 0

    def jump(self):
        if self.jump_count < 2:
            self.vel_y = -13
            self.jump_count += 1

    def update(self, platforms):
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y

        if self.rect.bottom >= GROUND_Y:
            self.rect.bottom = GROUND_Y
            self.vel_y = 0
            self.jump_count = 0

        # 平台碰撞
        if self.vel_y > 0:
            hits = pygame.sprite.spritecollide(self, platforms, False)
            if hits:
                if self.rect.bottom <= hits[0].rect.bottom + 10:
                    self.rect.bottom = hits[0].rect.top
                    self.vel_y = 0
                    self.jump_count = 0

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, speed):
        super().__init__()
        self.image = pygame.Surface((width, 20))
        self.image.fill((50, 150, 50))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = speed

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()

class Mob(pygame.sprite.Sprite):
    """ 會在平台上或地面來回移動的怪物 """
    def __init__(self, platform, speed):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill((150, 0, 255)) # 紫色怪物
        self.platform = platform # 怪物綁定的平台
        
        # 初始位置在平台上方
        self.rect = self.image.get_rect(midbottom=(platform.rect.centerx, platform.rect.top))
        self.move_speed = random.choice([-2, 2]) # 左右巡邏速度

    def update(self):
        # 隨平台移動
        self.rect.x -= self.platform.speed
        # 自身巡邏移動
        self.rect.x += self.move_speed

        # 邊緣偵測：如果快要掉出平台，就轉向
        if self.rect.left < self.platform.rect.left or self.rect.right > self.platform.rect.right:
            self.move_speed *= -1
            
        if self.platform.rect.right < 0: # 平台消失，怪物也消失
            self.kill()

# --- 初始化群組 ---
all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()
mobs = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

game_speed = 6
score = 0
timer = 0
running = True

while running:
    clock.tick(60)
    timer += 1
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE: player.jump()

    # 生成邏輯
    if timer % 90 == 0:
        # 生成二樓平台
        p_width = random.randint(200, 400)
        p = Platform(WIDTH, GROUND_Y - 120, p_width, game_speed)
        all_sprites.add(p); platforms.add(p)
        
        # 50% 機率在平台上生成一隻怪物
        if random.random() > 0.5:
            m = Mob(p, game_speed)
            all_sprites.add(m); mobs.add(m)

    # 更新邏輯
    player.update(platforms)
    platforms.update()
    mobs.update()
    
    # 碰撞怪物死亡
    if pygame.sprite.spritecollide(player, mobs, False):
        running = False
    
    score += 1
    if score % 1000 == 0: game_speed += 1

    # 繪製
    screen.fill(SKY_BLUE)
    pygame.draw.rect(screen, (100, 50, 0), (0, GROUND_Y, WIDTH, 50))
    all_sprites.draw(screen)
    
    score_txt = font.render(f"Distance: {score//10}m", True, BLACK)
    screen.blit(score_txt, (20, 20))
    pygame.display.flip()

pygame.quit()