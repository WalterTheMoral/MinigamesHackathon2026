import pygame
import sys

# הגדרות מערכת
WIDTH, HEIGHT = 800, 600
LEVEL_WIDTH = 20000
FPS = 60
GRAVITY = 0.9

# צבעים
PS_BLUE = (0, 55, 145)
WHITE = (255, 255, 255)
GOLD = (255, 215, 0)


# פונקציית עזר לטעינה (ללא שינוי)
def load_res(path, size, color):
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, size)
    except:
        s = pygame.Surface(size);
        s.fill(color);
        return s


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = load_res('frog_idle.png', (45, 45), (0, 255, 0))
        self.rect = self.image.get_rect(midbottom=(100, 500))
        self.direction = pygame.math.Vector2(0, 0)
        self.speed = 8
        self.on_ground = False
        self.jump_count = 0

    def update(self):
        keys = pygame.key.get_pressed()
        self.direction.x = 1 if keys[pygame.K_RIGHT] else -1 if keys[pygame.K_LEFT] else 0

    def jump(self):
        if self.on_ground:
            self.direction.y = -20
            self.jump_count = 1
            self.on_ground = False
        elif self.jump_count < 2:
            self.direction.y = -17
            self.jump_count += 1


class Block(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, is_goal=False):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill((30, 30, 30))
        if is_goal: self.image.fill(GOLD)
        self.rect = self.image.get_rect(topleft=(x, y))


# אתחול
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 30, bold=True)
big_font = pygame.font.SysFont("Arial", 60, bold=True)


def reset_game():
    global player, platforms, goal, scroll, won, start_time, final_time
    player = Player()
    platforms = pygame.sprite.Group()
    scroll = 0
    won = False
    start_time = pygame.time.get_ticks()  # איפוס זמן התחלה
    final_time = 0

    # המבנה החדש שביקשת (X, Y, W, H)
    layout = [
        (0, 550, 800, 50), (1100, 450, 150, 40), (1500, 350, 150, 40),
        (1900, 250, 150, 40), (2300, 500, 1000, 50), (3600, 400, 200, 40),
        (4100, 300, 100, 40), (4500, 200, 100, 40), (4900, 450, 800, 40),
        (6000, 350, 200, 200), (6500, 550, 2000, 50), (8800, 450, 150, 40),
        (9200, 350, 100, 40), (9600, 250, 80, 40), (10000, 150, 60, 40),
        (10500, 500, 1200, 50), (12000, 400, 300, 40), (12600, 300, 300, 40),
        (13500, 550, 5000, 60), (19000, 300, 200, 400)
    ]
    for x, y, w, h in layout:
        platforms.add(Block(x, y, w, h))
    goal = Block(19100, 200, 50, 400, is_goal=True)


reset_game()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and not won:
            player.jump()

    if not won:
        # חישוב הזמן הנוכחי בשניות
        current_ticks = pygame.time.get_ticks() - start_time
        seconds = int((current_ticks / 1000) % 60)
        minutes = int((current_ticks / (1000 * 60)) % 60)
        time_str = f"Time: {minutes:02}:{seconds:02}"

        player.update()
        player.rect.x += player.direction.x * player.speed
        for s in platforms:
            if s.rect.colliderect(player.rect):
                if player.direction.x > 0:
                    player.rect.right = s.rect.left
                else:
                    player.rect.left = s.rect.right

        player.direction.y += GRAVITY
        player.rect.y += player.direction.y
        player.on_ground = False
        for s in platforms:
            if s.rect.colliderect(player.rect):
                if player.direction.y > 0:
                    player.rect.bottom = s.rect.top
                    player.direction.y, player.on_ground, player.jump_count = 0, True, 0
                elif player.direction.y < 0:
                    player.rect.top = s.rect.bottom
                    player.direction.y = 0

        if player.rect.top > HEIGHT: reset_game()
        if player.rect.colliderect(goal.rect):
            won = True
            final_time = time_str  # שמירת הזמן ברגע הניצחון

        if player.rect.centerx > WIDTH // 2:
            scroll = max(scroll, player.rect.centerx - WIDTH // 2)
        scroll = min(scroll, LEVEL_WIDTH - WIDTH)

    # ציור
    screen.fill(PS_BLUE)
    for p in platforms: screen.blit(p.image, (p.rect.x - scroll, p.rect.y))
    screen.blit(player.image, (player.rect.x - scroll, player.rect.y))

    # הצגת הטיימר בזמן אמת
    if not won:
        timer_surf = font.render(time_str, True, WHITE)
        screen.blit(timer_surf, (20, 20))
    else:
        # מסך ניצחון עם הזמן הסופי
        win_surf = big_font.render("VICTORY!", True, WHITE)
        time_res_surf = font.render(f"Final Time: {final_time}", True, GOLD)
        screen.blit(win_surf, (WIDTH // 2 - 120, HEIGHT // 2 - 50))
        screen.blit(time_res_surf, (WIDTH // 2 - 100, HEIGHT // 2 + 20))

    pygame.display.update()
    clock.tick(FPS)
