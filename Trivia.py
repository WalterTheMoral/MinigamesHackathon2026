import pygame
import json
import time
from Scenes import Game

class TriviaGame(Game):

    # ==================================================
    # INIT
    # ==================================================
    def __init__(self, screen):

        super().__init__(screen)

        # -----------------------------
        # LOAD QUESTIONS
        # -----------------------------
        with open("questions.json", "r") as f:

            self.questions = json.load(f)

        # -----------------------------
        # SCREEN
        # -----------------------------
        self.WIDTH, self.HEIGHT = (
            screen.get_size()
        )

        # -----------------------------
        # COLORS
        # -----------------------------
        self.WHITE = (255, 255, 255)
        self.BLACK = (25, 25, 30)

        self.RED = (255, 80, 80)
        self.BLUE = (80, 160, 255)
        self.GREEN = (80, 220, 120)
        self.YELLOW = (255, 220, 80)

        self.GRAY = (60, 60, 70)

        self.colors = [
            self.RED,
            self.BLUE,
            self.YELLOW,
            self.GREEN
        ]

        # -----------------------------
        # FONTS
        # -----------------------------
        self.question_font = (
            pygame.font.SysFont(
                None,
                50
            )
        )

        self.answer_font = (
            pygame.font.SysFont(
                None,
                40
            )
        )

        self.timer_font = (
            pygame.font.SysFont(
                None,
                80
            )
        )

        self.result_font = (
            pygame.font.SysFont(
                None,
                100
            )
        )

        # -----------------------------
        # GAME STATE
        # -----------------------------
        self.total_score = 0

        self.question_index = 0

        self.current_question = (
            self.questions[
                self.question_index
            ]
        )

        self.question_start_time = (
            time.time()
        )

        self.answered = False

        self.answer_correct = False

        self.feedback_start = None

        self.state = "QUESTION"

        # QUESTION
        # FEEDBACK
        # FINAL

        self.answer_rects = []

    # ==================================================
    # HELPERS
    # ==================================================
    def next_question(self):

        self.question_index += 1

        # -----------------------------
        # FINISHED
        # -----------------------------
        if (
            self.question_index
            >= len(self.questions)
        ):

            self.state = "FINAL"

            return

        # -----------------------------
        # NEXT QUESTION
        # -----------------------------
        self.current_question = (
            self.questions[
                self.question_index
            ]
        )

        self.question_start_time = (
            time.time()
        )

        self.answered = False

        self.answer_correct = False

        self.feedback_start = None

        self.state = "QUESTION"

    # ==================================================
    # EVENTS
    # ==================================================
    def handle_events(self, events):

        for event in events:

            # -----------------------------
            # QUIT
            # -----------------------------
            if event.type == pygame.QUIT:

                self.return_state = (
                    "quit",
                    self.total_score
                )

            # -----------------------------
            # KEYS
            # -----------------------------
            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:

                    self.return_state = (self.total_score, True)

            # -----------------------------
            # ANSWER CLICK
            # -----------------------------
            if (
                self.state == "QUESTION"
                and event.type
                == pygame.MOUSEBUTTONDOWN
            ):

                mx, my = pygame.mouse.get_pos()

                for i, rect in enumerate(
                    self.answer_rects
                ):

                    if rect.collidepoint(mx, my):

                        self.answered = True

                        # correct
                        if (
                            i
                            == self.current_question[
                                "correct"
                            ]
                        ):

                            self.answer_correct = True

                            remaining = max(
                                0,
                                30 - (
                                    time.time()
                                    - self.question_start_time
                                )
                            )

                            gained = int(
                                remaining * 8
                            )

                            self.total_score += (
                                gained
                            )

                        self.feedback_start = (
                            time.time()
                        )

                        self.state = "FEEDBACK"

    # ==================================================
    # UPDATE
    # ==================================================
    def update(self):

        # -----------------------------
        # QUESTION TIMER
        # -----------------------------
        if self.state == "QUESTION":

            elapsed = (
                time.time()
                - self.question_start_time
            )

            remaining = max(
                0,
                30 - elapsed
            )

            # timeout
            if remaining <= 0:

                self.answered = True

                self.answer_correct = False

                self.feedback_start = (
                    time.time()
                )

                self.state = "FEEDBACK"

        # -----------------------------
        # FEEDBACK TIMER
        # -----------------------------
        elif self.state == "FEEDBACK":

            if (
                time.time()
                - self.feedback_start
                >= 1.2
            ):

                self.next_question()

    # ==================================================
    # DRAW QUESTION
    # ==================================================
    def draw_question(self):

        q = self.current_question

        elapsed = (
            time.time()
            - self.question_start_time
        )

        remaining = max(
            0,
            30 - elapsed
        )

        # -----------------------------
        # QUESTION
        # -----------------------------
        question_text = (
            self.question_font.render(
                q["question"],
                True,
                self.WHITE
            )
        )

        self.screen.blit(
            question_text,
            (
                self.WIDTH // 2
                - question_text.get_width()
                // 2,
                80
            )
        )

        # -----------------------------
        # TIMER
        # -----------------------------
        timer_color = (
            self.RED
            if remaining < 10
            else self.WHITE
        )

        timer_text = (
            self.timer_font.render(
                str(int(remaining)),
                True,
                timer_color
            )
        )

        self.screen.blit(
            timer_text,
            (
                self.WIDTH // 2
                - timer_text.get_width()
                // 2,
                170
            )
        )

        # -----------------------------
        # ANSWERS
        # -----------------------------
        self.answer_rects = []

        positions = [
            (self.WIDTH // 2 - 420, self.HEIGHT // 2 - 100),
            (self.WIDTH // 2 + 40, self.HEIGHT // 2 - 100),
            (self.WIDTH // 2 - 420, self.HEIGHT // 2 + 80),
            (self.WIDTH // 2 + 40, self.HEIGHT // 2 + 80),
        ]

        for i, ans in enumerate(
            q["answers"]
        ):

            rect = pygame.Rect(
                positions[i][0],
                positions[i][1],
                380,
                120
            )

            self.answer_rects.append(
                rect
            )

            color = self.colors[i]

            # hover
            if rect.collidepoint(
                pygame.mouse.get_pos()
            ):

                color = (
                    min(color[0] + 40, 255),
                    min(color[1] + 40, 255),
                    min(color[2] + 40, 255)
                )

            pygame.draw.rect(
                self.screen,
                color,
                rect,
                border_radius=20
            )

            text = self.answer_font.render(
                ans,
                True,
                self.WHITE
            )

            self.screen.blit(
                text,
                (
                    rect.centerx
                    - text.get_width() // 2,

                    rect.centery
                    - text.get_height() // 2
                )
            )

    # ==================================================
    # DRAW FEEDBACK
    # ==================================================
    def draw_feedback(self):

        feedback = (
            "CORRECT!"
            if self.answer_correct
            else "WRONG!"
        )

        feedback_color = (
            self.GREEN
            if self.answer_correct
            else self.RED
        )

        text = self.result_font.render(
            feedback,
            True,
            feedback_color
        )

        self.screen.blit(
            text,
            (
                self.WIDTH // 2
                - text.get_width() // 2,

                self.HEIGHT // 2
                - text.get_height() // 2
            )
        )

    # ==================================================
    # DRAW FINAL
    # ==================================================
    def draw_final(self):

        final_text = (
            self.result_font.render(
                f"FINAL SCORE: "
                f"{self.total_score}",
                True,
                self.YELLOW
            )
        )

        hint = self.answer_font.render(
            "Press ESC to continue",
            True,
            self.WHITE
        )

        self.screen.blit(
            final_text,
            (
                self.WIDTH // 2
                - final_text.get_width()
                // 2,
                260
            )
        )

        self.screen.blit(
            hint,
            (
                self.WIDTH // 2
                - hint.get_width()
                // 2,
                400
            )
        )

    # ==================================================
    # DRAW
    # ==================================================
    def draw(self):
        self.update()

        # -----------------------------
        # QUESTION
        # -----------------------------
        if self.state == "QUESTION":
            self.draw_question()

        # -----------------------------
        # FEEDBACK
        # -----------------------------
        elif self.state == "FEEDBACK":
            self.draw_feedback()

        # -----------------------------
        # FINAL
        # -----------------------------
        elif self.state == "FINAL":
            self.draw_final()