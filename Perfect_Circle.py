import pygame
import math
import statistics
import random
import os
from Scenes import Game


class PerfectCircleScene(Game):

    class Particle:
        def __init__(self, x, y, power=1, color=(100, 255, 100)):

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

    def __init__(self, screen):

        super().__init__(screen)

        self.WIDTH, self.HEIGHT = screen.get_size()

        self.CENTER = (
            self.WIDTH // 2,
            self.HEIGHT // 2
        )

        # -----------------------------
        # AUDIO
        # -----------------------------
        try:
            pygame.mixer.init()
            self.AUDIO = True

        except:
            self.AUDIO = False

        # -----------------------------
        # COLORS
        # -----------------------------
        self.WHITE = (255, 255, 255)
        self.RED = (255, 70, 70)
        self.GREEN = (100, 255, 100)
        self.YELLOW = (255, 255, 120)
        self.GOLD = (255, 215, 80)

        # -----------------------------
        # SOUNDS
        # -----------------------------
        self.sound_start = self.load_sound(
            "click_start.wav"
        )

        self.sound_release = self.load_sound(
            "release.wav"
        )

        self.sound_success = self.load_sound(
            "success.wav"
        )

        self.sound_perfect = self.load_sound(
            "perfect.wav"
        )

        # -----------------------------
        # STATE
        # -----------------------------
        self.drawing = False
        self.points = []

        self.score_return_time = None

        self.score = None
        self.display_score = 0.0

        self.perfect_circle = False

        self.shake_strength = 0

        self.particles = []

        self.last_point = None

        # -----------------------------
        # FONTS
        # -----------------------------
        self.score_font = pygame.font.SysFont(
            None,
            110
        )

        self.ui_font = pygame.font.SysFont(
            None,
            40
        )

    # ==================================================
    # AUDIO
    # ==================================================
    def load_sound(self, path):

        if self.AUDIO and os.path.exists(path):
            return pygame.mixer.Sound(path)

        return None

    def play(self, sound, volume=1.0):

        if sound:
            sound.set_volume(volume)
            sound.play()

    # ==================================================
    # HELPERS
    # ==================================================
    def distance(self, a, b):

        return math.hypot(
            a[0] - b[0],
            a[1] - b[1]
        )

    def total_rotation(self, points):

        total = 0

        prev = math.atan2(
            points[0][1] - self.CENTER[1],
            points[0][0] - self.CENTER[0]
        )

        for p in points[1:]:

            curr = math.atan2(
                p[1] - self.CENTER[1],
                p[0] - self.CENTER[0]
            )

            diff = math.degrees(curr - prev)

            if diff > 180:
                diff -= 360

            elif diff < -180:
                diff += 360

            total += abs(diff)

            prev = curr

        return total

    def circle_score(self, points):

        radii = [
            self.distance(p, self.CENTER)
            for p in points
        ]

        avg = sum(radii) / len(radii)

        std = (
            statistics.stdev(radii)
            if len(radii) > 1
            else 0
        )

        radius_score = 100 * math.exp(-std / 12)

        close = self.distance(
            points[0],
            points[-1]
        )

        close_score = 100 * math.exp(-close / 50)

        rot = self.total_rotation(points)

        rot_score = min(
            100,
            (rot / 360) * 100
        )

        size_penalty = abs(avg - 200)

        size_score = 100 * math.exp(
            -size_penalty / 80
        )

        final_score = (
            radius_score * 0.55 +
            rot_score * 0.2 +
            close_score * 0.15 +
            size_score * 0.1
        )

        return round(final_score, 2)

    def path_length(self, points):

        total = 0

        for i in range(len(points) - 1):

            total += self.distance(
                points[i],
                points[i + 1]
            )

        return total

    def lerp_color(self, a, b, t):

        return (
            int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t),
        )

    def is_too_close(self, points, pos, r=6):

        for p in points[:-20]:

            if self.distance(p, pos) < r:
                return True

        return False

    def live_quality(self, points):

        if len(points) < 10:
            return 0

        radii = [
            self.distance(p, self.CENTER)
            for p in points[-30:]
        ]

        std = (
            statistics.stdev(radii)
            if len(radii) > 1
            else 0
        )

        return max(
            0,
            min(1, 1 - std / 30)
        )

    # ==================================================
    # EVENTS
    # ==================================================
    def handle_events(self, events):

        for event in events:

            if event.type == pygame.QUIT:
                self.return_state = ("quit", None)


            # -----------------------------
            # START DRAW
            # -----------------------------
            if event.type == pygame.MOUSEBUTTONDOWN:

                self.play(
                    self.sound_start,
                    0.4
                )

                self.drawing = True

                self.points.clear()

                self.score = None
                self.display_score = 0.0

                self.perfect_circle = False

                self.last_point = None

            # -----------------------------
            # RELEASE DRAW
            # -----------------------------
            if event.type == pygame.MOUSEBUTTONUP:

                self.play(
                    self.sound_release,
                    0.4
                )

                self.drawing = False

                if len(self.points) < 50:
                    return

                if self.path_length(self.points) < 200:
                    return

                if self.total_rotation(self.points) < 320:
                    return

                self.score = self.circle_score(
                    self.points
                )

                self.score_return_time = pygame.time.get_ticks() + 2000

                # PERFECT
                if self.score >= 95:

                    self.perfect_circle = True

                    self.shake_strength = 18

                    self.play(
                        self.sound_perfect,
                        0.8
                    )

                    for _ in range(120):

                        self.particles.append(
                            self.Particle(
                                self.CENTER[0],
                                self.CENTER[1],
                                1.5,
                                self.GOLD
                            )
                        )

                # NORMAL SUCCESS
                else:

                    self.play(
                        self.sound_success,
                        0.6
                    )

                    for _ in range(60):

                        self.particles.append(
                            self.Particle(
                                self.CENTER[0],
                                self.CENTER[1],
                                self.score / 100,
                                self.GREEN
                            )
                        )

                if self.score >= 85:

                    self.shake_strength = max(
                        self.shake_strength,
                        10
                    )


    # ==================================================
    # UPDATE
    # ==================================================
    def update(self):

        # -----------------------------
        # SHAKE
        # -----------------------------
        self.offset_x = 0
        self.offset_y = 0

        if self.shake_strength > 0:

            self.offset_x = random.randint(
                -self.shake_strength,
                self.shake_strength
            )

            self.offset_y = random.randint(
                -self.shake_strength,
                self.shake_strength
            )

            self.shake_strength -= 1

        # -----------------------------
        # DRAW INPUT
        # -----------------------------
        if self.drawing:

            pos = pygame.mouse.get_pos()

            if self.last_point is None:

                self.points.append(pos)
                self.last_point = pos

            elif (
                self.distance(pos, self.last_point) > 2
                and not self.is_too_close(
                    self.points,
                    pos
                )
            ):

                self.points.append(pos)
                self.last_point = pos

        # -----------------------------
        # DELAYED RETURN
        # -----------------------------
        if (
                self.score is not None
                and self.score_return_time is not None
        ):

            if pygame.time.get_ticks() >= self.score_return_time:
                self.return_state = self.score

                self.score_return_time = None

        # -----------------------------
        # SCORE SMOOTHING
        # -----------------------------
        if self.score is not None:

            self.display_score += (
                self.score - self.display_score
            ) * 0.10

            if abs(
                self.display_score - self.score
            ) < 0.01:

                self.display_score = self.score

        # -----------------------------
        # PARTICLES
        # -----------------------------
        for p in self.particles[:]:

            p.update()

            if p.life <= 0:
                self.particles.remove(p)

    # ==================================================
    # DRAW
    # ==================================================
    def draw(self):

        self.update()

        # -----------------------------
        # BACKGROUND
        # -----------------------------
        base = self.display_score

        self.screen.fill((
            int(25 + base * 1.6),
            int(20 + base * 1.2),
            int(25 + base * 0.4)
        ))

        # -----------------------------
        # GLOW
        # -----------------------------
        glow_surface = pygame.Surface(
            (self.WIDTH, self.HEIGHT),
            pygame.SRCALPHA
        )

        glow_color = (
            self.GOLD
            if self.perfect_circle
            else (255, 90, 90)
        )

        for i in range(10, 0, -1):

            pygame.draw.circle(
                glow_surface,
                (*glow_color, 18 * i),
                (
                    self.CENTER[0] + self.offset_x,
                    self.CENTER[1] + self.offset_y
                ),
                8 + i * 3
            )

        self.screen.blit(glow_surface, (0, 0))

        pygame.draw.circle(
            self.screen,
            self.RED,
            (
                self.CENTER[0] + self.offset_x,
                self.CENTER[1] + self.offset_y
            ),
            8
        )

        # -----------------------------
        # DRAW LINE
        # -----------------------------
        if len(self.points) > 1:

            t = self.live_quality(
                self.points
            )

            color = self.lerp_color(
                (255, 80, 80),
                (80, 255, 120),
                t
            )

            shifted = [
                (
                    p[0] + self.offset_x,
                    p[1] + self.offset_y
                )
                for p in self.points
            ]

            pygame.draw.lines(
                self.screen,
                color,
                False,
                shifted,
                5
            )

        # -----------------------------
        # PARTICLES
        # -----------------------------
        for p in self.particles:
            p.draw(self.screen)

        # -----------------------------
        # SCORE TEXT
        # -----------------------------
        if self.score is not None:

            text = self.score_font.render(
                f"{self.display_score:.2f}%",
                True,
                self.GOLD
                if self.perfect_circle
                else self.GREEN
            )

            rect = text.get_rect(
                center=(
                    self.WIDTH // 2 + self.offset_x,
                    self.HEIGHT // 2 + self.offset_y
                )
            )

            self.screen.blit(text, rect)

        # -----------------------------
        # UI TEXT
        # -----------------------------
        top = self.ui_font.render(
            "Draw a perfect circle around the red dot",
            True,
            self.WHITE
        )

        bottom = self.ui_font.render(
            "Press and hold to start",
            True,
            self.WHITE
        )

        self.screen.blit(
            top,
            (
                self.WIDTH // 2
                - top.get_width() // 2,
                30
            )
        )

        self.screen.blit(
            bottom,
            (
                self.WIDTH // 2
                - bottom.get_width() // 2,
                self.HEIGHT - 60
            )
        )

        pygame.display.flip()