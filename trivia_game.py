import pygame
import json
import time


def run_trivia_game(screen, clock):

    # -----------------------------
    # LOAD QUESTIONS
    # -----------------------------
    with open("questions.json", "r") as f:
        questions = json.load(f)

    # -----------------------------
    # SCREEN
    # -----------------------------
    WIDTH, HEIGHT = screen.get_size()

    # -----------------------------
    # COLORS
    # -----------------------------
    WHITE = (255, 255, 255)
    BLACK = (25, 25, 30)

    RED = (255, 80, 80)
    BLUE = (80, 160, 255)
    GREEN = (80, 220, 120)
    YELLOW = (255, 220, 80)

    GRAY = (60, 60, 70)

    colors = [RED, BLUE, YELLOW, GREEN]

    # -----------------------------
    # FONTS
    # -----------------------------
    question_font = pygame.font.SysFont(None, 50)
    answer_font = pygame.font.SysFont(None, 40)
    timer_font = pygame.font.SysFont(None, 80)
    result_font = pygame.font.SysFont(None, 100)

    # -----------------------------
    # SCORE
    # -----------------------------
    total_score = 0

    # -----------------------------
    # GAME LOOP
    # -----------------------------
    for q_index, q in enumerate(questions):

        answered = False
        answer_correct = False

        start_time = time.time()

        while not answered:

            clock.tick(120)

            elapsed = time.time() - start_time
            remaining = max(0, 30 - elapsed)

            # timeout
            if remaining <= 0:
                answered = True
                break

            # -----------------------------
            # EVENTS
            # -----------------------------
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    return total_score

                if event.type == pygame.MOUSEBUTTONDOWN:

                    mx, my = pygame.mouse.get_pos()

                    # answer boxes
                    for i, rect in enumerate(answer_rects):

                        if rect.collidepoint(mx, my):

                            answered = True

                            # correct answer
                            if i == q["correct"]:
                                answer_correct = True

                                gained = int(remaining * 8)
                                total_score += gained

            # -----------------------------
            # DRAW
            # -----------------------------
            screen.fill(BLACK)

            # -----------------------------
            # QUESTION
            # -----------------------------
            question_text = question_font.render(
                q["question"],
                True,
                WHITE
            )

            screen.blit(
                question_text,
                (
                    WIDTH // 2 - question_text.get_width() // 2,
                    80
                )
            )

            # -----------------------------
            # TIMER
            # -----------------------------
            timer_color = RED if remaining < 10 else WHITE

            timer_text = timer_font.render(
                str(int(remaining)),
                True,
                timer_color
            )

            screen.blit(
                timer_text,
                (
                    WIDTH // 2 - timer_text.get_width() // 2,
                    170
                )
            )

            # -----------------------------
            # ANSWERS
            # -----------------------------
            answer_rects = []

            positions = [
                (100, 320),
                (520, 320),
                (100, 500),
                (520, 500)
            ]

            for i, ans in enumerate(q["answers"]):

                rect = pygame.Rect(
                    positions[i][0],
                    positions[i][1],
                    380,
                    120
                )

                answer_rects.append(rect)

                color = colors[i]

                # hover effect
                if rect.collidepoint(pygame.mouse.get_pos()):
                    color = (
                        min(color[0] + 40, 255),
                        min(color[1] + 40, 255),
                        min(color[2] + 40, 255)
                    )

                pygame.draw.rect(screen, color, rect, border_radius=20)

                text = answer_font.render(ans, True, WHITE)

                screen.blit(
                    text,
                    (
                        rect.centerx - text.get_width() // 2,
                        rect.centery - text.get_height() // 2
                    )
                )

            pygame.display.flip()

        # -----------------------------
        # FEEDBACK SCREEN
        # -----------------------------
        feedback_start = time.time()

        while time.time() - feedback_start < 1.2:

            clock.tick(120)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return total_score

            screen.fill(BLACK)

            feedback = "CORRECT!" if answer_correct else "WRONG!"

            feedback_color = GREEN if answer_correct else RED

            text = result_font.render(
                feedback,
                True,
                feedback_color
            )

            screen.blit(
                text,
                (
                    WIDTH // 2 - text.get_width() // 2,
                    HEIGHT // 2 - text.get_height() // 2
                )
            )

            pygame.display.flip()

    # -----------------------------
    # FINAL SCORE SCREEN
    # -----------------------------
    while True:

        clock.tick(120)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return total_score

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return total_score

        screen.fill(BLACK)

        final_text = result_font.render(
            f"FINAL SCORE: {total_score}",
            True,
            YELLOW
        )

        hint = answer_font.render(
            "Press ESC to continue",
            True,
            WHITE
        )

        screen.blit(
            final_text,
            (
                WIDTH // 2 - final_text.get_width() // 2,
                260
            )
        )

        screen.blit(
            hint,
            (
                WIDTH // 2 - hint.get_width() // 2,
                400
            )
        )

        pygame.display.flip()