import pygame
import random
import time
from Scenes import Game

class ReactionTimeGame(Game):

    def __init__(self, screen):

        super().__init__(screen)

        self.WIDTH, self.HEIGHT = (
            screen.get_size()
        )

        # -----------------------------
        # COLORS
        # -----------------------------
        self.WHITE = (255, 255, 255)
        self.BLACK = (20, 20, 20)
        self.RED = (220, 60, 60)
        self.GREEN = (60, 220, 100)
        self.ORANGE = (255, 170, 60)
        self.CYAN = (80, 240, 255)

        # -----------------------------
        # FONTS
        # -----------------------------
        self.FONT = pygame.font.SysFont(
            "Arial",
            52,
            bold=True
        )

        self.SMALL = pygame.font.SysFont(
            "Arial",
            32,
            bold=True
        )

        # -----------------------------
        # GAME STATE
        # -----------------------------
        self.tries = 0
        self.max_tries = 2

        self.scores = []

        self.state = "IDLE"

        # IDLE
        # WAITING
        # READY
        # RESULT
        # DONE

        self.message = "Click to Start\n(2 Tries)"

        self.bg_color = self.WHITE

        self.start_time = 0

        self.green_time = None

        self.finish_return_time = None

    # ==================================================
    # EVENTS
    # ==================================================
    def handle_events(self, events):

        for event in events:

            if event.type == pygame.QUIT:

                self.return_state = (
                    "quit",
                    None
                )

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:

                    self.return_state = (
                        "exit",
                        self.get_total_score()
                    )

            # -----------------------------
            # CLICK
            # -----------------------------
            if event.type == pygame.MOUSEBUTTONDOWN:

                self.handle_click()

    # ==================================================
    # CLICK LOGIC
    # ==================================================
    def handle_click(self):

        # -----------------------------
        # GAME COMPLETE
        # -----------------------------
        if self.state == "DONE":
            return

        # -----------------------------
        # START WAITING
        # -----------------------------
        if self.state in ("IDLE", "RESULT"):

            self.message = "Wait for Green..."

            self.bg_color = self.RED

            self.state = "WAITING"

            delay = random.randint(
                2000,
                5000
            )

            self.green_time = (
                pygame.time.get_ticks()
                + delay
            )

            return

        # -----------------------------
        # TOO EARLY
        # -----------------------------
        if self.state == "WAITING":

            self.message = (
                "TOO EARLY!\n"
                "Click to try again"
            )

            self.bg_color = self.ORANGE

            self.state = "RESULT"

            return

        # -----------------------------
        # SUCCESSFUL CLICK
        # -----------------------------
        if self.state == "READY":

            end_time = time.time()

            result = int(
                (
                    end_time
                    - self.start_time
                ) * 1000
            )

            self.scores.append(result)

            self.tries += 1

            # -----------------------------
            # MORE TRIES LEFT
            # -----------------------------
            if self.tries < self.max_tries:

                self.message = (
                    f"{result} ms\n"
                    f"Click for Try "
                    f"{self.tries + 1}"
                )

                self.bg_color = self.WHITE

                self.state = "RESULT"

            # -----------------------------
            # FINISHED
            # -----------------------------
            else:

                total = self.get_total_score()

                self.message = (
                    f"DONE!\n"
                    f"Total Sum: {total} ms"
                )

                self.bg_color = self.CYAN

                self.state = "DONE"

                self.finish_return_time = (
                    pygame.time.get_ticks()
                    + 2000
                )

    # ==================================================
    # HELPERS
    # ==================================================
    def get_total_score(self):

        return sum(self.scores)

    # ==================================================
    # UPDATE
    # ==================================================
    def update(self):

        now = pygame.time.get_ticks()

        # -----------------------------
        # TURN GREEN
        # -----------------------------
        if (
            self.state == "WAITING"
            and self.green_time is not None
        ):

            if now >= self.green_time:

                self.bg_color = self.GREEN

                self.message = "CLICK NOW!"

                self.start_time = time.time()

                self.state = "READY"

                self.green_time = None

        # -----------------------------
        # FINISH RETURN
        # -----------------------------
        if (
            self.state == "DONE"
            and self.finish_return_time
            is not None
        ):

            if now >= self.finish_return_time:

                self.return_state = (
                    "finished",
                    self.get_total_score()
                )

                self.finish_return_time = None

    # ==================================================
    # DRAW
    # ==================================================
    def draw(self):

        self.update()

        self.screen.fill(self.bg_color)

        lines = self.message.split("\n")

        total_height = (
            len(lines) * 70
        )

        start_y = (
            self.HEIGHT // 2
            - total_height // 2
        )

        for i, line in enumerate(lines):

            text = self.FONT.render(
                line,
                True,
                self.BLACK
            )

            rect = text.get_rect(
                center=(
                    self.WIDTH // 2,
                    start_y + i * 70
                )
            )

            self.screen.blit(text, rect)

        # -----------------------------
        # TRY COUNTER
        # -----------------------------
        counter = self.SMALL.render(

            f"Try {min(self.tries + 1, self.max_tries)}"
            f"/{self.max_tries}",

            True,
            self.BLACK
        )

        self.screen.blit(counter, (20, 20))

        pygame.display.flip()