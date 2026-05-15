import pygame
import time
import random
import os
import glob
from Scenes import Game


class RhythmGame(Game):

    class Note:

        def __init__(self, lane, speed, lane_width):

            self.lane = lane

            self.x = (
                lane * lane_width
                + lane_width // 2
            )

            self.y = -60

            self.speed = speed
            self.hit = False

        def update(self):

            self.y += self.speed

        def draw(
            self,
            screen,
            colors,
            arrows,
            font
        ):

            if self.hit:
                return

            pygame.draw.circle(
                screen,
                colors[self.lane],
                (self.x, int(self.y)),
                42
            )

            pygame.draw.circle(
                screen,
                (255, 255, 255),
                (self.x, int(self.y)),
                42,
                2
            )

            txt = font.render(
                arrows[self.lane],
                True,
                (0, 0, 0)
            )

            screen.blit(
                txt,
                (self.x - 12, self.y - 25)
            )

    # ==================================================
    # INIT
    # ==================================================
    def __init__(self, screen):

        super().__init__(screen)

        # ---------------- SCREEN ----------------
        self.WIDTH, self.HEIGHT = (
            screen.get_size()
        )

        # ---------------- FONTS ----------------
        self.FONT = pygame.font.SysFont(
            "Arial",
            42,
            bold=True
        )

        self.BIG = pygame.font.SysFont(
            "Arial",
            90,
            bold=True
        )

        # ---------------- LANES ----------------
        self.LANES = 4

        self.lane_width = (
            self.WIDTH // self.LANES
        )

        self.hit_y = self.HEIGHT - 140

        self.LANE_KEYS = {
            pygame.K_LEFT: 0,
            pygame.K_a: 0,

            pygame.K_DOWN: 1,
            pygame.K_s: 1,

            pygame.K_UP: 2,
            pygame.K_w: 2,

            pygame.K_RIGHT: 3,
            pygame.K_d: 3
        }

        self.COLORS = [
            (255, 80, 80),
            (80, 255, 140),
            (80, 180, 255),
            (255, 220, 80)
        ]

        self.ARROWS = [
            "←",
            "↓",
            "↑",
            "→"
        ]

        # ---------------- MUSIC ----------------
        self.SONG_FOLDER = "songs"

        self.songs = glob.glob(
            os.path.join(
                self.SONG_FOLDER,
                "*.mp3"
            )
        )

        if not self.songs:

            self.return_state = (
                "error",
                "No mp3 files found"
            )

            return

        self.MUSIC_FILE = random.choice(
            self.songs
        )

        pygame.mixer.init()

        pygame.mixer.music.load(
            self.MUSIC_FILE
        )

        pygame.mixer.music.set_volume(0.7)

        # ---------------- NOTES ----------------
        self.notes = []

        # ---------------- SCORE ----------------
        self.score = 0
        self.streak = 0
        self.max_streak = 0

        # ---------------- GAME STATE ----------------
        self.state = "COUNTDOWN"

        self.countdown_start = time.time()

        self.go_time = None
        self.game_start_time = None

        self.last_spawn = 0

        self.game_over = False

        self.feedback = ""
        self.feedback_time = 0

        self.GAME_TIME = 25

        # result delay
        self.result_time = None

    # ==================================================
    # EVENTS
    # ==================================================
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.mixer.music.stop()
                    self.return_state = (self.score, True)

            # ---------------- INPUT ----------------
            if (
                self.state == "PLAYING"
                and not self.game_over
            ):

                if event.type == pygame.KEYDOWN:

                    if event.key in self.LANE_KEYS:

                        lane = self.LANE_KEYS[
                            event.key
                        ]

                        best = None
                        best_dist = 999

                        for n in self.notes:

                            if (
                                n.lane == lane
                                and not n.hit
                            ):

                                dist = abs(
                                    n.y - self.hit_y
                                )

                                if dist < best_dist:

                                    best = n
                                    best_dist = dist

                        if best:

                            if best_dist < 60:

                                base = 150
                                self.feedback = "PERFECT"

                                self.streak += 1

                            elif best_dist < 100:

                                base = 100
                                self.feedback = "GOOD"

                                self.streak += 1

                            else:

                                base = 0
                                self.feedback = "MISS"

                                self.streak = max(
                                    0,
                                    self.streak - 3
                                )

                            best.hit = True

                            multiplier = (
                                1
                                + self.streak * 0.04
                            )

                            self.score += int(
                                base * multiplier
                            )

                            self.max_streak = max(
                                self.max_streak,
                                self.streak
                            )

                            self.feedback_time = (
                                time.time()
                            )

                        else:

                            self.streak = max(
                                0,
                                self.streak - 4
                            )

                            self.feedback = "MISS"

                            self.feedback_time = (
                                time.time()
                            )

    # ==================================================
    # UPDATE
    # ==================================================
    def update(self):

        # ---------------- COUNTDOWN ----------------
        if self.state == "COUNTDOWN":

            t = (
                time.time()
                - self.countdown_start
            )

            if t >= 3 and self.go_time is None:

                pygame.mixer.music.play()

                self.go_time = time.time()

                self.game_start_time = (
                    self.go_time
                )

                self.state = "PLAYING"

            return

        # ---------------- TIMER ----------------
        elapsed = (
            time.time()
            - self.game_start_time
        )

        if (
            elapsed >= self.GAME_TIME
            and not self.game_over
        ):

            self.game_over = True

            pygame.mixer.music.stop()

            self.result_time = (
                pygame.time.get_ticks()
                + 3000
            )

        # ---------------- RETURN DELAY ----------------
        if (
            self.game_over
            and self.result_time is not None
        ):

            if (
                pygame.time.get_ticks()
                >= self.result_time
            ):
                self.return_state = (self.score, True)

                self.result_time = None

        # ---------------- GAMEPLAY ----------------
        if (
            self.state == "PLAYING"
            and not self.game_over
        ):

            difficulty = min(
                (
                    self.streak * 0.15
                ) + (
                    elapsed * 0.02
                ),
                6
            )

            note_speed = (
                3 + difficulty * 1.8
            )

            spawn_delay = max(
                1.2 - difficulty * 0.18,
                0.25
            )

            if (
                time.time()
                - self.last_spawn
                > spawn_delay
            ):

                lane = random.randint(0, 3)

                self.notes.append(
                    self.Note(
                        lane,
                        note_speed,
                        self.lane_width
                    )
                )

                self.last_spawn = time.time()

            for n in self.notes:

                n.speed = note_speed
                n.update()

            self.notes = [

                n for n in self.notes

                if (
                    n.y < self.HEIGHT + 100
                    and not n.hit
                )
            ]

    # ==================================================
    # DRAW
    # ==================================================
    def draw(self):

        self.update()

        self.screen.fill((10, 10, 18))

        # ---------------- COUNTDOWN ----------------
        if self.state == "COUNTDOWN":

            t = (
                time.time()
                - self.countdown_start
            )

            if t < 1:
                text = "3"

            elif t < 2:
                text = "2"

            elif t < 3:
                text = "1"

            else:
                text = "GO!"

            big = self.BIG.render(
                text,
                True,
                (255, 255, 255)
            )

            self.screen.blit(
                big,
                (
                    self.WIDTH // 2 - 60,
                    self.HEIGHT // 2 - 80
                )
            )

            pygame.display.flip()

            return

        # ---------------- LANES ----------------
        for i in range(self.LANES):

            x = i * self.lane_width

            pygame.draw.rect(
                self.screen,
                self.COLORS[i],
                (x, 0, 5, self.HEIGHT)
            )

            pygame.draw.rect(
                self.screen,
                self.COLORS[i],
                (
                    x,
                    self.hit_y - 5,
                    self.lane_width,
                    10
                )
            )

        # ---------------- NOTES ----------------
        for n in self.notes:

            n.draw(
                self.screen,
                self.COLORS,
                self.ARROWS,
                self.FONT
            )

        # ---------------- UI ----------------
        ui = self.FONT.render(

            f"SCORE {self.score}  "
            f"STREAK {self.streak}",

            True,
            (255, 255, 255)
        )

        self.screen.blit(ui, (20, 20))

        # ---------------- FEEDBACK ----------------
        if (
            time.time()
            - self.feedback_time
            < 0.4
        ):

            fb = self.BIG.render(
                self.feedback,
                True,
                (255, 255, 255)
            )

            self.screen.blit(
                fb,
                (
                    self.WIDTH // 2 - 140,
                    self.HEIGHT // 2
                )
            )

        # ---------------- END SCREEN ----------------
        if self.game_over:

            title = self.BIG.render(
                "GOOD RUN! 🎉",
                True,
                (255, 255, 255)
            )

            score_text = self.FONT.render(
                f"Final Score: {self.score}",
                True,
                (255, 255, 255)
            )

            streak_text = self.FONT.render(
                f"Max Streak: {self.max_streak}",
                True,
                (255, 255, 255)
            )

            msg = self.FONT.render(
                "Nice! Try again for a higher score!",
                True,
                (200, 200, 200)
            )

            self.screen.blit(
                title,
                (
                    self.WIDTH // 2 - 240,
                    self.HEIGHT // 2 - 160
                )
            )

            self.screen.blit(
                score_text,
                (
                    self.WIDTH // 2 - 240,
                    self.HEIGHT // 2 - 40
                )
            )

            self.screen.blit(
                streak_text,
                (
                    self.WIDTH // 2 - 220,
                    self.HEIGHT // 2 + 20
                )
            )

            self.screen.blit(
                msg,
                (
                    self.WIDTH // 2 - 360,
                    self.HEIGHT // 2 + 90
                )
            )

        pygame.display.flip()