import pygame
import sys

# הגדרות בסיסיות
WIDTH, HEIGHT = 800, 600
LEVEL_WIDTH = 12000  # שלב ארוך ומפרך
FPS = 60
GRAVITY = 1.0  # כבידה חזקה יותר לנחיתה מהירה

# נתיבי Sprites
SPRITE_FILES = {
    'player': 'mario.png',
    'enemy': 'goomba.png',
    'ground': 'tile.png',
    'goal': 'flag.png'
}


def get_sprite(key, size, fallback_color):
    try:
        img = pygame.image.load(SPRITE_FILES[key]).convert_alpha()
        return pygame.transform.scale(img, size)
    except:
        s = pygame.Surface(size);
        s.fill(fallback_color);
        return s


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = get_sprite('player', (35, 50), (255, 0, 0))  # שחקן מעט קטן יותר לדיוק
        self.rect = self.image.get_rect(midbottom=(100, HEIGHT - 100))
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


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, platform_rect):
        super().__init__()
        self.image = get_sprite('enemy', (40, 40), (0, 0, 0))
        self.rect = self.image.get_rect(bottomleft=(x, y))
        self.speed = 5  # מהירות גבוהה יותר
        self.platform = platform_rect

    def update(self):
        self.rect.x += self.speed
        if self.rect.right > self.platform.right or self.rect.left < self.platform.left:
            self.speed *= -1


class Block(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, is_goal=False):
        super().__init__()
        color = (255, 215, 0) if is_goal else (50, 50, 50)
        self.image = get_sprite('goal' if is_goal else 'ground', (w, h), color)
        self.rect = self.image.get_rect(topleft=(x, y))


# אתחול
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()


def reset_game():
    global player, platforms, enemies, goal, scroll, won
    player = Player()
    platforms = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    scroll, won = 0, False

    # בניית שלב מאתגר במיוחד
    # פורמט: (X, Y, W, H)
    layout = [
        (0, 560, 800, 40),  # התחלה בטוחה
        (1000, 450, 200, 40),  # קפיצה ראשונה (קטנה)
        (1400, 350, 200, 40),  # מדרגה באוויר
        (1800, 560, 600, 40),  # רצפה עם אויב מהיר
        (2600, 450, 150, 40),  # פלטפורמה צרה
        (3000, 350, 150, 40),  # פלטפורמה צרה נוספת
        (3400, 250, 150, 40),  # גבוה מאוד
        (3800, 560, 2000, 40),  # קטע ריצה ארוך ומלא אויבים
        (6000, 400, 100, 40),  # קפיצת אמונה 1
        (6300, 300, 100, 40),  # קפיצת אמונה 2
        (6600, 450, 100, 40),  # נפילה מבוקרת
        (7000, 560, 800, 40),  # רצפה יציבה
        (8000, 400, 1500, 40),  # פלטפורמה ארוכה בגובה
        (9800, 560, 2000, 40)  # קטע סיום רחב
    ]

    for x, y, w, h in layout:
        b = Block(x, y, w, h)
        platforms.add(b)
        if w > 100:  # אויבים כמעט על כל פלטפורמה
            enemies.add(Enemy(x + 10, y, b.rect))
            if w > 1000:  # תוספת אויבים לקטעים ארוכים
                enemies.add(Enemy(x + 500, y, b.rect))
                enemies.add(Enemy(x + 900, y, b.rect))

    goal = Block(11500, 260, 40, 300, is_goal=True)


reset_game()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not won: player.jump()

    if not won:
        player.update()

        # תנועה אופקית והתנגשות קירות
        player.rect.x += player.direction.x * player.speed
        for s in platforms:
            if s.rect.colliderect(player.rect):
                if player.direction.x > 0:
                    player.rect.right = s.rect.left
                else:
                    player.rect.left = s.rect.right

        # תנועה אנכית ופיזיקה
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

        # עדכון אויבים (פסילה קשוחה - אין רחמים)
        enemies.update()
        for e in enemies:
            if e.rect.colliderect(player.rect):
                # מריו חייב ליפול בחוזקה על האויב כדי להרוג אותו
                if player.direction.y > 8 and player.rect.bottom < e.rect.centery + 10:
                    e.kill();
                    player.direction.y = -15
                else:
                    reset_game()

                # נפילה או סיום
        if player.rect.top > HEIGHT: reset_game()
        if player.rect.colliderect(goal.rect): won = True

        # מצלמה מהירה
        if player.rect.centerx > WIDTH // 2:
            scroll = max(scroll, player.rect.centerx - WIDTH // 2)
        scroll = min(scroll, LEVEL_WIDTH - WIDTH)

    # רינדור (צבע רקע כהה יותר לאווירה מאתגרת)
    screen.fill((50, 80, 150))

    for p in platforms: screen.blit(p.image, (p.rect.x - scroll, p.rect.y))
    for e in enemies: screen.blit(e.image, (e.rect.x - scroll, e.rect.y))
    screen.blit(goal.image, (goal.rect.x - scroll, goal.rect.y))
    screen.blit(player.image, (player.rect.x - scroll, player.rect.y))

    if won:
        f = pygame.font.SysFont("Arial", 80, True)
        screen.blit(f.render("IMPOSSIBLE CLEAR!", True, (255, 255, 255)), (100, 250))

    pygame.display.update()
    clock.tick(FPS)
