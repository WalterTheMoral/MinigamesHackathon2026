import pygame
import random
import time


def run_click_speed_test(screen, clock):

    # -----------------------------
    # CONSTANTS
    # -----------------------------
    WIDTH, HEIGHT = screen.get_size()
    duration = 15

    WHITE = (255, 255, 255)
    BLACK = (20, 20, 25)
    RED = (255, 80, 80)
    GREEN = (120, 255, 120)
    YELLOW = (255, 230, 120)

    # -----------------------------
    # STATE
    # -----------------------------
    clicks = 0
    running = True
    game_active = False
    finished = False
    start_time = 0

    shake = 0
    particles = []

    # -----------------------------
    # PARTICLES
    # -----------------------------
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

        def draw(self):
            if self.life > 0:
                pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), self.size)

    # -----------------------------
    # LOOP
    # -----------------------------
    while running:

        clock.tick(120)

        # -----------------------------
        # TIMER END
        # -----------------------------
        if game_active and not finished:
            elapsed = time.time() - start_time

            if elapsed >= duration:
                game_active = False
                finished = True

                cps = clicks / duration

                shake = 20 if cps >= 6 else 10 if cps >= 4 else 5

                for _ in range(100):
                    particles.append(Particle(WIDTH // 2, HEIGHT // 2))

        # -----------------------------
        # EVENTS
        # -----------------------------
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False
                finished = True

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_SPACE:

                    if not game_active and not finished:
                        game_active = True
                        start_time = time.time()
                        clicks = 1
                    elif game_active:
                        clicks += 1

                if event.key == pygame.K_r:
                    return run_click_speed_test(screen, clock)

                if event.key == pygame.K_ESCAPE:
                    running = False
                    finished = True

        # -----------------------------
        # SHAKE
        # -----------------------------
        offset_x = random.randint(-shake, shake) if shake > 0 else 0
        offset_y = random.randint(-shake, shake) if shake > 0 else 0
        shake = max(0, shake - 1)

        # -----------------------------
        # DRAW BACKGROUND
        # -----------------------------
        screen.fill(BLACK)

        # -----------------------------
        # TIME
        # -----------------------------
        if game_active:
            time_left = max(0, duration - (time.time() - start_time))
        else:
            time_left = duration

        # -----------------------------
        # FONTS
        # -----------------------------
        font_big = pygame.font.SysFont(None, 120)
        font_small = pygame.font.SysFont(None, 50)

        # -----------------------------
        # GAME SCREEN
        # -----------------------------
        if not finished:

            screen.blit(
                font_small.render("SPACE as fast as possible", True, WHITE),
                (WIDTH//2 - 200, 50)
            )

            screen.blit(
                font_big.render(f"{time_left:.1f}", True, RED),
                (WIDTH//2 - 60, 180)
            )

            screen.blit(
                font_big.render(str(clicks), True, GREEN),
                (WIDTH//2 - 40, 350)
            )

        # -----------------------------
        # RESULT SCREEN (NO LOOP INSIDE LOOP)
        # -----------------------------
        else:

            cps = clicks / duration

            color = GREEN if cps >= 5 else YELLOW if cps >= 3 else RED

            screen.blit(
                font_big.render(f"{clicks}", True, color),
                (WIDTH//2 - 60, 220)
            )

            screen.blit(
                font_small.render(f"{cps:.2f} CPS", True, WHITE),
                (WIDTH//2 - 60, 350)
            )

            screen.blit(
                font_small.render("R = retry | ESC = exit", True, WHITE),
                (WIDTH//2 - 120, 500)
            )

        # -----------------------------
        # PARTICLES
        # -----------------------------
        for p in particles[:]:
            p.update()
            p.draw()
            if p.life <= 0:
                particles.remove(p)

        pygame.display.flip()

    # return final score to main system
    return clicks, clicks / duration