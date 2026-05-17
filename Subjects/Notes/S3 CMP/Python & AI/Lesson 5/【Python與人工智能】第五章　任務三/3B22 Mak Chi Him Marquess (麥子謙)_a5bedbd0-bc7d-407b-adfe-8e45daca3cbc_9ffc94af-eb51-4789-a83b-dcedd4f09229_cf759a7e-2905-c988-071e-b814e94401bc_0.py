import pygame
import random

# 初始化
pygame.init()
pygame.mixer.init()

# 視窗設定
WIDTH, HEIGHT = 600, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("世界計畫風格 - 判定優化版")

# 載入音樂 (請確保檔案在同資料夾，若無檔案則會以無聲運行)
try:
    pygame.mixer.music.load("bgm.mp3") 
    pygame.mixer.music.play(-1)
    hit_sound = pygame.mixer.Sound("hit.wav")
except:
    hit_sound = None

# 顏色定義
BLACK = (10, 10, 15)
WHITE = (255, 255, 255)
PERFECT_COLOR = (0, 255, 255) # 青色
GOOD_COLOR = (50, 255, 50)    # 綠色
MISS_COLOR = (200, 200, 200)  # 灰色

# 設定
LANES = 4
LANE_WIDTH = 100
LANE_START_X = (WIDTH - (LANES * LANE_WIDTH)) // 2
JUDGE_LINE_Y = 700  # 判定線的高度
NOTE_SPEED = 12     # 音符下落速度
KEYS = [pygame.K_d, pygame.K_f, pygame.K_j, pygame.K_k]

class Note:
    def __init__(self, lane):
        self.lane = lane
        self.x = LANE_START_X + lane * LANE_WIDTH + 5
        self.y = -50
        self.active = True
        self.judged = False # 是否已經被判定過

    def move(self):
        self.y += NOTE_SPEED

    def draw(self):
        if self.active:
            pygame.draw.rect(screen, PERFECT_COLOR, (self.x, self.y, LANE_WIDTH-10, 25), border_radius=5)
            pygame.draw.rect(screen, WHITE, (self.x+5, self.y+5, LANE_WIDTH-20, 15), border_radius=2)

class RhythmGame:
    def __init__(self):
        self.notes = []
        self.score = 0
        self.combo = 0
        self.feedback = ""
        self.feedback_color = WHITE
        self.feedback_timer = 0
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 40, bold=True)
        self.spawn_timer = 0

    def check_hit(self, lane_index):
        # 只找該軌道中，還沒被判定過且最靠近底部的音符
        available_notes = [n for n in self.notes if n.lane == lane_index and n.active]
        if not available_notes:
            return

        # 抓取該軌道最下面的一顆
        target_note = available_notes[0]
        dist = abs(target_note.y - JUDGE_LINE_Y)

        if dist < 35: # 完美判定範圍
            self.trigger_judgment("PERFECT", PERFECT_COLOR, 100, target_note)
        elif dist < 70: # 好判定範圍
            self.trigger_judgment("GOOD", GOOD_COLOR, 50, target_note)
        elif dist < 120: # 勉強碰到
            self.trigger_judgment("BAD", MISS_COLOR, 10, target_note)

    def trigger_judgment(self, text, color, score_add, note):
        note.active = False
        self.feedback = text
        self.feedback_color = color
        self.feedback_timer = 20
        self.score += score_add
        self.combo += 1
        if hit_sound: hit_sound.play()

    def run(self):
        running = True
        while running:
            screen.fill(BLACK)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key in KEYS:
                        self.check_hit(KEYS.index(event.key))

            # 生成音符 (根據速度調整生成頻率)
            self.spawn_timer += 1
            if self.spawn_timer > 25:
                self.notes.append(Note(random.randint(0, 3)))
                self.spawn_timer = 0

            # 繪製軌道
            for i in range(LANES + 1):
                x = LANE_START_X + i * LANE_WIDTH
                pygame.draw.line(screen, (40, 40, 60), (x, 0), (x, HEIGHT), 2)
            
            # 判定線下方發光效果
            pygame.draw.rect(screen, (30, 30, 50), (LANE_START_X, JUDGE_LINE_Y-10, LANES*LANE_WIDTH, 20))
            pygame.draw.line(screen, WHITE, (LANE_START_X, JUDGE_LINE_Y), 
                             (LANE_START_X + LANES * LANE_WIDTH, JUDGE_LINE_Y), 4)

            # 音符邏輯
            for note in self.notes[:]:
                note.move()
                note.draw()
                
                # MISS 判定：如果音符超過判定線太遠還沒按
                if note.y > JUDGE_LINE_Y + 80 and note.active:
                    note.active = False
                    self.feedback = "MISS"
                    self.feedback_color = MISS_COLOR
                    self.feedback_timer = 20
                    self.combo = 0 # 斷 Combo
                
                if note.y > HEIGHT:
                    self.notes.remove(note)

            # UI 顯示
            score_surf = self.font.render(f"{self.score:06d}", True, WHITE)
            combo_surf = self.font.render(f"{self.combo} COMBO", True, PERFECT_COLOR)
            screen.blit(score_surf, (WIDTH - 180, 20))
            if self.combo > 0:
                screen.blit(combo_surf, (WIDTH // 2 - 70, 100))

            if self.feedback_timer > 0:
                f_surf = self.font.render(self.feedback, True, self.feedback_color)
                # 讓文字有一點點向上飄的動畫感
                screen.blit(f_surf, (WIDTH // 2 - 60, JUDGE_LINE_Y - 150 - (20 - self.feedback_timer)))
                self.feedback_timer -= 1

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    RhythmGame().run()