import pygame
import random

def simion():
    score = 0
    # הגדרות עיצוב
    BG_COLOR = (30, 30, 30)
    COLORS = [
        ((46, 204, 113), (120, 240, 170)),  # ירוק
        ((231, 76, 60), (255, 120, 110)),  # אדום
        ((241, 196, 15), (255, 240, 150)),  # צהוב
        ((52, 152, 219), (130, 210, 255))  # כחול
    ]

    WIDTH, HEIGHT = 600, 600
    FPS = 60


    class SimonGame:
        def __init__(self):
            pygame.init()
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
            pygame.display.set_caption("Simon - Fixed Sequence")
            self.clock = pygame.time.Clock()
            self.font = pygame.font.SysFont("Arial", 40, bold=True)

            self.buttons = [
                pygame.Rect(100, 100, 190, 190), pygame.Rect(310, 100, 190, 190),
                pygame.Rect(100, 310, 190, 190), pygame.Rect(310, 310, 190, 190)
            ]

            self.sequence = []
            self.player_seq = []
            self.state = "MENU"
            self.active_btn = -1
            self.timer = 0
            self.seq_idx = 0
            score = 0

        def draw(self):
            self.screen.fill(BG_COLOR)
            for i in range(4):
                # שימוש בצבע הבהיר במידה והכפתור פעיל
                color = COLORS[i][1] if self.active_btn == i else COLORS[i][0]
                pygame.draw.rect(self.screen, color, self.buttons[i], border_radius=15)

            if self.state == "MENU":
                self.draw_overlay("START GAME", (46, 204, 113))
            elif self.state == "GAMEOVER":
                self.draw_overlay(f"TRY AGAIN? (Score: {self.score})", (231, 76, 60))

            if self.state not in ["MENU", "GAMEOVER"]:
                txt = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
                self.screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, 30))

            pygame.display.flip()

        def draw_overlay(self, text, color):
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            btn_rect = pygame.Rect(WIDTH // 2 - 160, HEIGHT // 2 - 40, 320, 80)
            pygame.draw.rect(self.screen, color, btn_rect, border_radius=12)
            txt = self.font.render(text, True, (255, 255, 255))
            self.screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT // 2 - txt.get_height() // 2))

        def update(self):
            now = pygame.time.get_ticks()

            if self.state == "SHOWING":
                if self.active_btn == -1:
                    # רווח זמן בין הבהובים (מגן על כך שהשלב הראשון לא יעלם)
                    if now > self.timer + 300:
                        if self.seq_idx < len(self.sequence):
                            self.active_btn = self.sequence[self.seq_idx]
                            self.timer = now + 500  # משך ההבהוב
                        else:
                            self.state = "PLAYING"
                            self.player_seq = []
                else:
                    if now > self.timer:
                        self.active_btn = -1
                        self.timer = now
                        self.seq_idx += 1

            elif self.active_btn != -1 and now > self.timer:
                self.active_btn = -1

        def handle_click(self, pos):
            if self.state in ["MENU", "GAMEOVER"]:
                self.start_new_game()
                return

            if self.state == "PLAYING" and self.active_btn == -1:
                for i, rect in enumerate(self.buttons):
                    if rect.collidepoint(pos):
                        self.active_btn = i
                        self.timer = pygame.time.get_ticks() + 250
                        self.player_seq.append(i)
                        self.check_step()

        def check_step(self):
            idx = len(self.player_seq) - 1
            if self.player_seq[idx] != self.sequence[idx]:
                self.state = "GAMEOVER"
            elif len(self.player_seq) == len(self.sequence):
                self.score += 1
                self.add_to_sequence()

        def start_new_game(self):
            self.score = 0
            self.sequence = []
            self.add_to_sequence()

        def add_to_sequence(self):
            self.sequence.append(random.randint(0, 3))
            self.seq_idx = 0
            self.state = "SHOWING"
            # המתנה של חצי שנייה לפני תחילת ההצגה כדי שהמשתמש יהיה מוכן
            self.timer = pygame.time.get_ticks() + 500
            self.active_btn = -1

        def run(self):
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT: return
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self.handle_click(event.pos)
                self.update()
                self.draw()
                self.clock.tick(FPS)
    return score, True

