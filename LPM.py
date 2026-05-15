import pygame
import time
import random
from Scenes import Game

WIDTH, HEIGHT = 1100, 400

WHITE = (255, 255, 255)
GRAY = (0, 0, 0)

GREEN = (0, 150, 0)
RED = (255, 50, 50)

BG_COLOR = (225, 193, 110)


class TypingGame(Game):

    # ==================================================
    # INIT
    # ==================================================
    def __init__(self, screen):

        super().__init__(screen)

        self.font = pygame.font.SysFont(
            "impact",
            42
        )

        self.result_font = pygame.font.SysFont(
            "impact",
            70
        )

        self.sentences = [

            "THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG",

            "PYTHON PROGRAMMING IS FAST AND POWERFUL",

            "TYPE AS FAST AS YOU CAN TO WIN"
        ]

        self.reset_game()

    # ==================================================
    # RESET
    # ==================================================
    def reset_game(self):

        self.target_text = random.choice(
            self.sentences
        )

        self.user_text = ""

        self.start_time = None
        self.end_time_stamp = None

        self.active = True

        self.final_score = 0

        self.return_delay = None

    # ==================================================
    # WPM
    # ==================================================
    def get_wpm(self):

        if not self.start_time:
            return 0

        end = (
            self.end_time_stamp
            if self.end_time_stamp
            else time.time()
        )

        elapsed = (
            end - self.start_time
        ) / 60

        if elapsed <= 0:
            return 0

        return round(
            (
                len(self.user_text) / 5
            ) / elapsed
        )

    # ==================================================
    # EVENTS
    # ==================================================
    def handle_events(self, events):

        for event in events:
            # -----------------------------
            # KEYS
            # -----------------------------
            if event.type == pygame.KEYDOWN:

                # exit result screen
                if (
                    not self.active
                    and event.key
                    == pygame.K_ESCAPE
                ):

                    self.return_state = (
                        self.final_score,
                        True
                    )

                # typing
                if self.active:

                    # delete
                    if (
                        event.key
                        == pygame.K_BACKSPACE
                    ):

                        self.user_text = (
                            self.user_text[:-1]
                        )

                    # add character
                    elif (
                        len(self.user_text)
                        < len(self.target_text)
                    ):

                        is_correct_so_far = (

                            self.user_text

                            ==

                            self.target_text[
                                :len(
                                    self.user_text
                                )
                            ]
                        )

                        if (
                            is_correct_so_far
                            and event.unicode
                        ):

                            if (
                                self.start_time
                                is None
                            ):

                                self.start_time = (
                                    time.time()
                                )

                            self.user_text += (
                                event.unicode.upper()
                            )

                    # finish
                    if (
                        self.user_text
                        == self.target_text
                    ):

                        self.end_time_stamp = (
                            time.time()
                        )

                        self.final_score = (
                            self.get_wpm()
                        )

                        self.active = False

                        self.return_delay = (
                            pygame.time.get_ticks()
                            + 2000
                        )

    # ==================================================
    # UPDATE
    # ==================================================
    def update(self):

        if (
            not self.active
            and self.return_delay
            is not None
        ):

            if (
                pygame.time.get_ticks()
                >= self.return_delay
            ):

                self.return_state = (
                    self.final_score,
                    True
                )

                self.return_delay = None

    # ==================================================
    # DRAW ACTIVE GAME
    # ==================================================
    def draw_game(self):

        self.screen.fill(BG_COLOR)

        start_x = 50
        start_y = 180

        # target text
        target_surface = self.font.render(
            self.target_text,
            True,
            GRAY
        )

        self.screen.blit(
            target_surface,
            (start_x, start_y)
        )

        # typed text
        for i in range(len(self.user_text)):

            color = (

                GREEN

                if (
                    self.user_text[i]
                    ==
                    self.target_text[i]
                )

                else RED
            )

            char_surface = self.font.render(
                self.user_text[i],
                True,
                color
            )

            current_x = self.font.size(
                self.target_text[:i]
            )[0]

            self.screen.blit(

                char_surface,

                (
                    start_x + current_x,
                    start_y
                )
            )

        # WPM
        wpm_surface = self.font.render(

            f"WPM: {self.get_wpm()}",

            True,

            (0, 0, 0)
        )

        self.screen.blit(
            wpm_surface,
            (50, 50)
        )

    # ==================================================
    # DRAW RESULTS
    # ==================================================
    def draw_results(self):

        self.screen.fill(GRAY)

        result_text = (
            f"FINAL WPM: "
            f"{self.final_score}"
        )

        result_surface = (
            self.result_font.render(
                result_text,
                True,
                WHITE
            )
        )

        exit_surface = self.font.render(
            "PRESS ESC TO EXIT",
            True,
            (120, 120, 120)
        )

        result_rect = (
            result_surface.get_rect(
                center=(
                    WIDTH // 2,
                    HEIGHT // 2 - 40
                )
            )
        )

        exit_rect = (
            exit_surface.get_rect(
                center=(
                    WIDTH // 2,
                    HEIGHT // 2 + 40
                )
            )
        )

        self.screen.blit(
            result_surface,
            result_rect
        )

        self.screen.blit(
            exit_surface,
            exit_rect
        )

    # ==================================================
    # DRAW
    # ==================================================
    def draw(self):

        self.update()

        if self.active:

            self.draw_game()

        else:

            self.draw_results()

        pygame.display.flip()