import pygame
import random
import time
from Scenes import Game

class ClickSpeedTestScene(Game):

    class Particle:
        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.vx = random.uniform(-4, 4)
            self.vy = random.uniform(-4, 4)
            self.life = random.randint(25, 50)
            self.size = random.randint(2, 5)

        def update(self):
            self.vy += 0.12
            self.x += self.vx
            self.y += self.vy
            self.life -= 1

        def draw(self, screen, color):
            if self.life > 0:
                pygame.draw.circle(
                    screen,
                    color,
                    (int(self.x), int(self.y)),
                    self.size
                )

    def __init__(self, screen):
        super().__init__(screen)

        # -----------------------------
        # CONSTANTS
        # -----------------------------
        self.WIDTH, self.HEIGHT = screen.get_size()
        self.duration = 10

        self.WHITE = (255, 255, 255)
        self.BLACK = (20, 20, 25)
        self.RED = (255, 80, 80)
        self.GREEN = (120, 255, 120)
        self.YELLOW = (255, 230, 120)

        # -----------------------------
        # STATE
        # -----------------------------
        self.clicks = 0
        self.game_active = False
        self.finished = False
        self.start_time = 0

        self.shake = 0
        self.particles = []

        # -----------------------------
        # FONTS
        # -----------------------------
        self.font_big = pygame.font.SysFont(None, 120)
        self.font_small = pygame.font.SysFont(None, 50)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not self.game_active and not self.finished:
                        self.game_active = True
                        self.start_time = time.time()
                        self.clicks = 1

                    elif self.game_active:
                        self.clicks += 1

                if event.key == pygame.K_r:
                    self.__init__(self.screen)

                if event.key == pygame.K_ESCAPE:
                    print("esc")
                    cps = self.clicks / self.duration
                    self.return_state = (self.clicks, True)

    def update(self):

        # -----------------------------
        # TIMER END
        # -----------------------------
        if self.game_active and not self.finished:

            elapsed = time.time() - self.start_time

            if elapsed >= self.duration:

                self.game_active = False
                self.finished = True

                cps = self.clicks / self.duration

                self.shake = (
                    20 if cps >= 6 else
                    10 if cps >= 4 else
                    5
                )

                for _ in range(100):
                    self.particles.append(
                        self.Particle(
                            self.WIDTH // 2,
                            self.HEIGHT // 2
                        )
                    )

        # -----------------------------
        # PARTICLES
        # -----------------------------
        for p in self.particles[:]:
            p.update()

            if p.life <= 0:
                self.particles.remove(p)

        # -----------------------------
        # SHAKE DECAY
        # -----------------------------
        self.shake = max(0, self.shake - 1)

    def draw(self):

        self.update()

        # -----------------------------
        # SHAKE
        # -----------------------------
        offset_x = random.randint(-self.shake, self.shake) if self.shake > 0 else 0
        offset_y = random.randint(-self.shake, self.shake) if self.shake > 0 else 0

        # -----------------------------
        # DRAW BACKGROUND
        # -----------------------------
        self.screen.fill(self.BLACK)

        # -----------------------------
        # TIME
        # -----------------------------
        if self.game_active:
            time_left = max(
                0,
                self.duration - (time.time() - self.start_time)
            )
        else:
            time_left = self.duration

        # -----------------------------
        # GAME SCREEN
        # -----------------------------
        if not self.finished:

            self.screen.blit(
                self.font_small.render(
                    "SPACE as fast as possible",
                    True,
                    self.WHITE
                ),
                (self.WIDTH // 2 - 200 + offset_x, 50 + offset_y)
            )

            self.screen.blit(
                self.font_big.render(
                    f"{time_left:.1f}",
                    True,
                    self.RED
                ),
                (self.WIDTH // 2 - 60 + offset_x, 180 + offset_y)
            )

            self.screen.blit(
                self.font_big.render(
                    str(self.clicks),
                    True,
                    self.GREEN
                ),
                (self.WIDTH // 2 - 40 + offset_x, 350 + offset_y)
            )

        # -----------------------------
        # RESULT SCREEN
        # -----------------------------
        else:

            cps = self.clicks / self.duration

            color = (
                self.GREEN if cps >= 5 else
                self.YELLOW if cps >= 3 else
                self.RED
            )

            self.screen.blit(
                self.font_big.render(
                    f"{self.clicks}",
                    True,
                    color
                ),
                (self.WIDTH // 2 - 60 + offset_x, 220 + offset_y)
            )

            self.screen.blit(
                self.font_small.render(
                    f"{cps:.2f} CPS",
                    True,
                    self.WHITE
                ),
                (self.WIDTH // 2 - 60 + offset_x, 350 + offset_y)
            )

            self.screen.blit(
                self.font_small.render(
                    "R = retry | ESC = exit",
                    True,
                    self.WHITE
                ),
                (self.WIDTH // 2 - 120 + offset_x, 500 + offset_y)
            )

        # -----------------------------
        # DRAW PARTICLES
        # -----------------------------
        for p in self.particles:
            p.draw(self.screen, self.YELLOW)

        pygame.display.flip()