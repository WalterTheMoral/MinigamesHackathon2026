import pygame
import math
import statistics
import random
import os

# -----------------------------
# INIT
# -----------------------------
pygame.init()

# -----------------------------
# AUDIO
# -----------------------------
try:
    pygame.mixer.init()
    AUDIO = True
except:
    AUDIO = False

# -----------------------------
# SCREEN
# -----------------------------
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Perfect Circle")

clock = pygame.time.Clock()

CENTER = (WIDTH // 2, HEIGHT // 2)

# -----------------------------
# LOAD SOUNDS
# -----------------------------
def load_sound(path):
    if AUDIO and os.path.exists(path):
        return pygame.mixer.Sound(path)
    return None

sound_start = load_sound("click_start.wav")
sound_release = load_sound("release.wav")
sound_success = load_sound("success.wav")
sound_perfect = load_sound("perfect.wav")

def play(sound, volume=1.0):
    if sound:
        sound.set_volume(volume)
        sound.play()

# -----------------------------
# COLORS
# -----------------------------
WHITE = (255, 255, 255)
RED = (255, 70, 70)
GREEN = (100, 255, 100)
YELLOW = (255, 255, 120)
GOLD = (255, 215, 80)

# -----------------------------
# GLOBAL STATE
# -----------------------------
drawing = False
points = []
score = None
display_score = 0.0
perfect_circle = False
shake_strength = 0

# -----------------------------
# PARTICLES
# -----------------------------
particles = []

class Particle:

    def __init__(self, x, y, power=1, color=GREEN):
        self.x = x
        self.y = y

        self.vx = random.uniform(-3, 3) * power
        self.vy = random.uniform(-3, 3) * power

        self.life = random.randint(40, 80)
        self.size = random.randint(2, 5)

        self.color = color

    def update(self):
        self.vy += 0.05

        self.x += self.vx
        self.y += self.vy

        self.life -= 1

    def draw(self, surf):

        if self.life > 0:
            pygame.draw.circle(
                surf,
                self.color,
                (int(self.x), int(self.y)),
                self.size
            )

# -----------------------------
# HELPERS
# -----------------------------
def distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

def total_rotation(points):

    total = 0

    prev = math.atan2(
        points[0][1] - CENTER[1],
        points[0][0] - CENTER[0]
    )

    for p in points[1:]:

        curr = math.atan2(
            p[1] - CENTER[1],
            p[0] - CENTER[0]
        )

        diff = math.degrees(curr - prev)

        if diff > 180:
            diff -= 360

        elif diff < -180:
            diff += 360

        total += abs(diff)

        prev = curr

    return total

def circle_score(points):

    radii = [distance(p, CENTER) for p in points]

    avg = sum(radii) / len(radii)

    std = statistics.stdev(radii) if len(radii) > 1 else 0

    radius_score = 100 * math.exp(-std / 12)

    close = distance(points[0], points[-1])
    close_score = 100 * math.exp(-close / 50)

    rot = total_rotation(points)
    rot_score = min(100, (rot / 360) * 100)

    size_penalty = abs(avg - 200)
    size_score = 100 * math.exp(-size_penalty / 80)

    final_score = (
        radius_score * 0.55 +
        rot_score * 0.2 +
        close_score * 0.15 +
        size_score * 0.1
    )

    return round(final_score, 2)

def path_length(points):

    total = 0

    for i in range(len(points) - 1):
        total += distance(points[i], points[i + 1])

    return total

def lerp_color(a, b, t):

    return (
        int(a[0] + (b[0] - a[0]) * t),
        int(a[1] + (b[1] - a[1]) * t),
        int(a[2] + (b[2] - a[2]) * t),
    )

def is_too_close(points, pos, r=6):

    for p in points[:-20]:

        if distance(p, pos) < r:
            return True

    return False

def live_quality(points):

    if len(points) < 10:
        return 0

    radii = [distance(p, CENTER) for p in points[-30:]]

    std = statistics.stdev(radii) if len(radii) > 1 else 0

    return max(0, min(1, 1 - std / 30))

# -----------------------------
# MAIN GAME FUNCTION
# -----------------------------
def run_perfect_circle():

    global drawing
    global points
    global score
    global display_score
    global perfect_circle
    global shake_strength

    running = True
    last_point = None

    while running:

        clock.tick(120)

        offset_x = 0
        offset_y = 0

        # -----------------------------
        # SHAKE
        # -----------------------------
        if shake_strength > 0:

            offset_x = random.randint(
                -shake_strength,
                shake_strength
            )

            offset_y = random.randint(
                -shake_strength,
                shake_strength
            )

            shake_strength -= 1

        # -----------------------------
        # EVENTS
        # -----------------------------
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            # START DRAW
            if event.type == pygame.MOUSEBUTTONDOWN:

                play(sound_start, 0.4)

                drawing = True

                points.clear()

                score = None
                display_score = 0.0

                perfect_circle = False

                last_point = None

            # RELEASE DRAW
            if event.type == pygame.MOUSEBUTTONUP:

                play(sound_release, 0.4)

                drawing = False

                if len(points) < 50:
                    continue

                if path_length(points) < 200:
                    continue

                if total_rotation(points) < 320:
                    continue

                score = circle_score(points)

                # PERFECT
                if score >= 95:

                    perfect_circle = True

                    shake_strength = 18

                    play(sound_perfect, 0.8)

                    for _ in range(120):

                        particles.append(
                            Particle(
                                CENTER[0],
                                CENTER[1],
                                1.5,
                                GOLD
                            )
                        )

                # NORMAL SUCCESS
                else:

                    play(sound_success, 0.6)

                    for _ in range(60):

                        particles.append(
                            Particle(
                                CENTER[0],
                                CENTER[1],
                                score / 100,
                                GREEN
                            )
                        )

                if score >= 85:
                    shake_strength = max(shake_strength, 10)

        # -----------------------------
        # DRAWING INPUT
        # -----------------------------
        if drawing:

            pos = pygame.mouse.get_pos()

            if last_point is None:

                points.append(pos)
                last_point = pos

            elif (
                distance(pos, last_point) > 2
                and not is_too_close(points, pos)
            ):

                points.append(pos)
                last_point = pos

        # -----------------------------
        # SCORE SMOOTHING
        # -----------------------------
        if score is not None:

            display_score += (
                score - display_score
            ) * 0.10

            if abs(display_score - score) < 0.01:
                display_score = score

        # -----------------------------
        # BACKGROUND
        # -----------------------------
        base = display_score

        screen.fill((
            int(25 + base * 1.6),
            int(20 + base * 1.2),
            int(25 + base * 0.4)
        ))

        # -----------------------------
        # GLOW
        # -----------------------------
        glow_surface = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA
        )

        glow_color = GOLD if perfect_circle else (255, 90, 90)

        for i in range(10, 0, -1):

            pygame.draw.circle(
                glow_surface,
                (*glow_color, 18 * i),
                (
                    CENTER[0] + offset_x,
                    CENTER[1] + offset_y
                ),
                8 + i * 3
            )

        screen.blit(glow_surface, (0, 0))

        pygame.draw.circle(
            screen,
            RED,
            (
                CENTER[0] + offset_x,
                CENTER[1] + offset_y
            ),
            8
        )

        # -----------------------------
        # DRAW LINE
        # -----------------------------
        if len(points) > 1:

            t = live_quality(points)

            color = lerp_color(
                (255, 80, 80),
                (80, 255, 120),
                t
            )

            shifted = [
                (p[0] + offset_x, p[1] + offset_y)
                for p in points
            ]

            pygame.draw.lines(
                screen,
                color,
                False,
                shifted,
                5
            )

        # -----------------------------
        # PARTICLES
        # -----------------------------
        for p in particles[:]:

            p.update()
            p.draw(screen)

            if p.life <= 0:
                particles.remove(p)

        # -----------------------------
        # SCORE TEXT
        # -----------------------------
        if score is not None:

            font = pygame.font.SysFont(None, 110)

            text = font.render(
                f"{display_score:.2f}%",
                True,
                GOLD if perfect_circle else GREEN
            )

            rect = text.get_rect(
                center=(
                    WIDTH // 2 + offset_x,
                    HEIGHT // 2 + offset_y
                )
            )

            screen.blit(text, rect)

        # -----------------------------
        # UI TEXT
        # -----------------------------
        ui_font = pygame.font.SysFont(None, 40)

        top = ui_font.render(
            "Draw a perfect circle around the red dot",
            True,
            WHITE
        )

        bottom = ui_font.render(
            "Press and hold to start",
            True,
            WHITE
        )

        screen.blit(
            top,
            (
                WIDTH // 2 - top.get_width() // 2,
                30
            )
        )

        screen.blit(
            bottom,
            (
                WIDTH // 2 - bottom.get_width() // 2,
                HEIGHT - 60
            )
        )

        pygame.display.flip()

    pygame.quit()

    return score

# -----------------------------
# TEST RUN
# -----------------------------
if __name__ == "__main__":

    result = run_perfect_circle()

    print("Player scored:", result)