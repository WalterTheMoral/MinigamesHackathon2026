import pygame
import sys
import time


def platfrom():
    # הגדרות בסיסיות
    WIDTH, HEIGHT = 800, 600
    LEVEL_WIDTH = 12000  # שלב ארוך ומפרך
    FPS = 60
    GRAVITY = 1.0  # כבידה חזקה יותר לנחיתה מהירה
    TIMER = 0
    current_time=time.time()

    # נתיבי Sprites
    SPRITE_FILES = {
        'player': 'img_5.png',
        'jump': 'img_7.png',
        'enemy': 'img-4.png',
        'ground': 'img_6.png',
        'goal': 'flag.png',
        'bg': 'img.png'
    }


    def get_sprite(key, size, fallback_color):
        try:
            img = pygame.image.load(SPRITE_FILES[key]).convert_alpha()
            return pygame.transform.scale(img, size)
        except:
            s = pygame.Surface(size);
            s.fill(fallback_color);
            return s
    def load_res(path, size, color):
        """
        path: שם הקובץ (למשל 'frog_jump.png')
        size: הגודל הרצוי בפיקסלים (למשל (50, 50))
        color: צבע לגיבוי אם התמונה לא נמצאה (RGB)
        """
        try:
            # ניסיון טעינת התמונה מהתיקייה
            img = pygame.image.load(path).convert_alpha()
            # שינוי גודל התמונה לגודל המדויק שהגדרנו
            return pygame.transform.scale(img, size)
        except:
            # אם יש שגיאה (קובץ חסר), יצירת ריבוע צבעוני במקום
            print(f"Warning: Could not load image at {path}. Using fallback color.")
            s = pygame.Surface(size)
            s.fill(color)
            return s


    class Player(pygame.sprite.Sprite):
        def __init__(self):
            super().__init__()
            # טעינת התמונות השונות
            self.idle_img = load_res('img_5.png', (70, 70), (0, 255, 0))
            self.jump_img = load_res('img_7.png', (70, 70), (0, 200, 0))
            # תמונות לריצה (אופציונלי - אם יש לך קבצים בשם frog_run1/2)
            self.run_frames = [
                load_res('img_5.png', (50, 50), (0, 255, 0)),
                load_res('img_5.png', (50, 50), (0, 255, 0))
            ]

            self.image = self.idle_img
            self.rect = self.image.get_rect(midbottom=(100, 500))
            self.direction = pygame.math.Vector2(0, 0)
            self.speed = 8
            self.jump_count = 0
            self.on_ground = True
            self.facing_right = True
            self.frame_index = 0  # לניהול מהירות האנימציה בריצה

        def animate(self):
            # 1. אם השחקן באוויר -> תמונת קפיצה
            if not self.on_ground:
                self.image = self.jump_img

            # 2. אם השחקן זז על הקרקע -> אנימציית ריצה
            elif self.direction.x != 0:
                self.frame_index += 0.15
                if self.frame_index >= len(self.run_frames): self.frame_index = 0
                self.image = self.run_frames[int(self.frame_index)]

            # 3. אם השחקן עומד -> תמונת עמידה
            else:
                self.image = self.idle_img

            # היפוך תמונה לפי כיוון ההליכה (Flip)
            if not self.facing_right:
                self.image = pygame.transform.flip(self.image, True, False)

        def update(self):
            keys = pygame.key.get_pressed()

            self.direction.x = 1 if keys[pygame.K_RIGHT] else -1 if keys[pygame.K_LEFT] else 0

            # עדכון כיוון המבט
            if self.direction.x > 0:
                self.facing_right = True
            elif self.direction.x < 0:
                self.facing_right = False

            # הפעלת מערכת האנימציה
            self.animate()

        def jump(self):
            if self.on_ground:
                self.direction.y = -20
                self.jump_count = 1
                self.on_ground = False
            elif self.jump_count < 2:
                self.direction.y = -17
                self.jump_count += 1

        def apply_animation(self):
            # אם השחקן לא על הקרקע - הצג תמונת קפיצה
            if not self.on_ground:
                self.image = self.jump_img
            else:
                self.image = self.idle_img

        def update(self):
            # עדכון תנועה
            keys = pygame.key.get_pressed()
            if keys[pygame.K_RIGHT]:
                self.direction.x = 1
            elif keys[pygame.K_LEFT]:
                self.direction.x = -1
            else:
                self.direction.x = 0

            # הפעלת האנימציה
            self.apply_animation()

        def jump(self):
            if self.on_ground:
                self.direction.y = -18
                self.jump_count = 1
                self.on_ground = False
            elif self.jump_count < 2:
                self.direction.y = -16
                self.jump_count += 1

        # def update(self):
        #     keys = pygame.key.get_pressed()
        #     self.direction.x = 1 if keys[pygame.K_RIGHT] else -1 if keys[pygame.K_LEFT] else 0

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
            # השורה הזו טוענת את התמונה. וודא ש monster.png נמצא בתיקייה!
            try:
                self.image = pygame.image.load('img_4.png').convert_alpha()
                self.image = pygame.transform.scale(self.image, (50, 50))
            except:
                # אם התמונה לא נמצאה, הוא יצבע בצהוב כדי שתראה שמשהו השתנה
                self.image = pygame.Surface((40, 40))
                self.image = pygame.Surface((40, 40), pygame.SRCALPHA)

                self.image.fill((0, 0, 0, 0))  # ארבעה אפסים: אדום, ירוק, כחול ושקיפות

            self.rect = self.image.get_rect(bottomleft=(x, y))
            self.speed = 5
            self.platform = platform_rect

        def update(self):
            self.rect.x += self.speed
            if self.rect.right > self.platform.right or self.rect.left < self.platform.left:
                self.speed *= -1
            TIMER = time.time() - current_time
            if TIMER > 180:
                return 0
                exit()

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
            (0, 550, 800, 50),  # 1. אזור התחלה בטוח
            (1100, 450, 150, 40),  # 2. קפיצת היכרות
            (1500, 350, 150, 40),  # 3. עלייה בגובה
            (1900, 250, 150, 40),  # 4. גבוה מאוד
            (2300, 500, 1000, 50),  # 5. רצפה ארוכה (אזור אויבים 1)
            (3600, 400, 200, 40),  # 6. קפיצה מעל בור
            (4100, 300, 100, 40),  # 7. פלטפורמה צרה
            (4500, 200, 100, 40),  # 8. שיא הגובה
            (4900, 450, 800, 40),  # 9. נחיתה למטה
            (6000, 350, 200, 200),  # 10. קיר חוסם (דורש קפיצה כפולה מדויקת)
            (6500, 550, 2000, 50),  # 11. מישור ריצה מהיר (אזור אויבים 2)
            (8800, 450, 150, 40),  # 12. תחילת סדרת קפיצות "פיקסל"
            (9200, 350, 100, 40),  # 13.
            (9600, 250, 80, 40),  # 14.
            (10000, 150, 60, 40),  # 15. הקפיצה הכי קשה בשלב
            (10500, 500, 1200, 50),  # 16. אזור נחיתה והתאוששות
            (12000, 400, 300, 40),  # 17. מדרגות רחבות
            (12600, 300, 300, 40),  # 18.
            (13500, 550, 5000, 60),  # 19. קטע ספרינט סופי (מרתון אויבים)
            (19000, 300, 200, 400)# קו סיום
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
        # מצא את החלק הזה (בתוך לולאת ה-while True):
        screen.fill((107, 140, 255))  # מחק או שים בסימן # את השורה הזו

        # והוסף את השורות האלו במקומה:
        bg_img = pygame.image.load(SPRITE_FILES['bg']).convert()
        bg_img = pygame.transform.scale(bg_img, (800, 600))
        screen.blit(bg_img, (0, 0))  # זה מצייר את התמונה שלך כרקע

        for p in platforms: screen.blit(p.image, (p.rect.x - scroll, p.rect.y))
        for e in enemies: screen.blit(e.image, (e.rect.x - scroll, e.rect.y))
        screen.blit(goal.image, (goal.rect.x - scroll, goal.rect.y))
        screen.blit(player.image, (player.rect.x - scroll, player.rect.y))

        if won:
            f = pygame.font.SysFont("Arial", 80, True)
            screen.blit(f.render("IMPOSSIBLE CLEAR!", True, (255, 255, 255)), (100, 250))
            return 1

        pygame.display.update()
        clock.tick(FPS)