import pygame
import time
import random
"""
# הגדרות מסך וצבעים
WIDTH, HEIGHT = 1100, 400
WHITE = (255, 255, 255)
GRAY = (0,0,0)
GREEN = (0, 150, 0)
RED = (255, 50, 50)
BG_COLOR = (225, 193, 110)


class TypingGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Monkeytype Clone")
        self.font = pygame.font.SysFont("impact", 42)
        self.result_font = pygame.font.SysFont("impact", 70)

        self.sentences = [
            "THE ANSWER IS ALWAYS A POINTER!!!",
            "THEY'RE TAKING THE HOBBITS TO ISENGARD!",
            "TONIGHT we touch kremer"
        ]
        self.reset_game()

    def reset_game(self):
        self.target_text = random.choice(self.sentences)
        self.user_text = ""
        self.start_time = None
        self.end_time_stamp = None
        self.active = True
        self.final_score = 0

    def get_wpm(self):
        if not self.start_time: return 0
        end = self.end_time_stamp if self.end_time_stamp else time.time()
        elapsed = (end - self.start_time) / 60
        if elapsed <= 0: return 0
        # חישוב WPM לפי נוסחת 5 תווים למילה
        return True,round((len(self.user_text) / 5) / elapsed)

    def draw_text(self):
        self.screen.fill(BG_COLOR)
        start_x, start_y = 50, 180

        # ציור טקסט המטרה באפור
        full_target_surf = self.font.render(self.target_text, True, GRAY)
        self.screen.blit(full_target_surf, (start_x, start_y))

        # ציור הטקסט שהוקלד מעל
        for i in range(len(self.user_text)):
            color = GREEN if self.user_text[i] == self.target_text[i] else RED
            char_surf = self.font.render(self.user_text[i], True, color)
            current_pos_x = self.font.size(self.target_text[:i])[0]
            self.screen.blit(char_surf, (start_x + current_pos_x, start_y))

        # הצגת WPM
        wpm_val = self.get_wpm()
        wpm_surf = self.font.render(f"WPM: {wpm_val}", True, (0, 0, 0))
        self.screen.blit(wpm_surf, (50, 50))

        if not self.active:
            self.display_final_results()

        pygame.display.flip()

    def display_final_results(self):
        self.screen.fill(GRAY)
        res_text = f"FINAL WPM: {self.final_score}"
        res_surf = self.result_font.render(res_text, True, (0,0,0))
        exit_surf = self.font.render("PRESS ESC TO EXIT", True, (50, 50, 50))

        res_rect = res_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
        exit_rect = exit_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))

        self.screen.blit(res_surf, res_rect)
        self.screen.blit(exit_surf, exit_rect)

    def run(self):
        running = True
        while running:
            self.draw_text()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if self.active:
                        # מחיקת תו תמיד מותרת
                        if event.key == pygame.K_BACKSPACE:
                            self.user_text = self.user_text[:-1]

                        # הוספת תו חדש
                        elif len(self.user_text) < len(self.target_text):
                            # בדיקה: האם מה שהוקלד עד עכשיו תקין?
                            # אם יש טעות בתו האחרון, לא ניתן להוסיף תווים חדשים
                            is_correct_so_far = self.user_text == self.target_text[:len(self.user_text)]

                            if is_correct_so_far and event.unicode:
                                if self.start_time is None:
                                    self.start_time = time.time()
                                self.user_text += event.unicode.upper()

                        # בדיקת סיום
                        if self.user_text == self.target_text:
                            self.end_time_stamp = time.time()
                            self.final_score = self.get_wpm()
                            self.active = False
                    else:
                        if event.key == pygame.K_ESCAPE:
                            running = False
        pygame.quit()


if __name__ == "__main__":
    game = TypingGame()
    game.run()
"""

import pygame
import time
import random


# Reusing the Scene/Game structure from your second snippet
class Scene:
    def __init__(self, screen):
        self.screen = screen
        self.return_state = None

    def draw(self):
        pass

    def handle_events(self, events):
        pass

    def get_return_state(self):
        return self.return_state


class Game(Scene):
    """Parent class for mini-games"""
    pass


class TypingGameScene(Game):
    def __init__(self, screen):
        super().__init__(screen)

        # Colors & Fonts
        self.GRAY = (50, 50, 50)
        self.GREEN = (0, 150, 0)
        self.RED = (255, 50, 50)
        self.TEXT_COLOR = (0, 0, 0)

        self.font = pygame.font.SysFont("impact", 42)

        # Game Data
        self.sentences = [
            "THE ANSWER IS ALWAYS A POINTER!!!",
            "THEY'RE TAKING THE HOBBITS TO ISENGARD!",
            "TONIGHT WE TOUCH KREMER"
        ]

        # Game State
        self.target_text = random.choice(self.sentences)
        self.user_text = ""
        self.start_time = None
        self.end_time_stamp = None
        self.active = True
        self.final_score = 0

    def get_wpm(self):
        if not self.start_time:
            return 0
        end = self.end_time_stamp if self.end_time_stamp else time.time()
        elapsed = (end - self.start_time) / 60
        if elapsed <= 0:
            return 0
        # WPM formula: (chars / 5) / minutes
        return round((len(self.user_text) / 5) / elapsed)

    def draw(self):
        # The background fill is handled by your main loop,
        # but we draw the game elements here.
        start_x, start_y = 100, 400  # Adjusted for your 1400x800 screen

        # 1. Draw Target Text (Shadow/Guide)
        target_surf = self.font.render(self.target_text, True, self.GRAY)
        self.screen.blit(target_surf, (start_x, start_y))

        # 2. Draw Typed Text with color feedback
        for i in range(len(self.user_text)):
            color = self.GREEN if self.user_text[i] == self.target_text[i] else self.RED
            char_surf = self.font.render(self.user_text[i], True, color)

            # Calculate offset based on previous characters
            offset_x = self.font.size(self.target_text[:i])[0]
            self.screen.blit(char_surf, (start_x + offset_x, start_y))

        # 3. Draw UI (WPM)
        wpm_val = self.get_wpm()
        ui_surf = self.font.render(f"WPM: {wpm_val}", True, self.TEXT_COLOR)
        self.screen.blit(ui_surf, (100, 100))

    def handle_events(self, events):
        if not self.active:
            return

        for event in events:
            if event.type == pygame.KEYDOWN:
                # Start timer on first keypress
                if self.start_time is None:
                    self.start_time = time.time()

                if event.key == pygame.K_BACKSPACE:
                    self.user_text = self.user_text[:-1]

                elif len(self.user_text) < len(self.target_text):
                    # Logic: Only allow typing if the current string is correct
                    # (Monkeytype style strict mode)
                    is_correct_so_far = self.user_text == self.target_text[:len(self.user_text)]

                    if is_correct_so_far and event.unicode:
                        self.user_text += event.unicode.upper()

                # Check for win condition
                if self.user_text == self.target_text:
                    self.end_time_stamp = time.time()
                    self.final_score = self.get_wpm()
                    self.active = False
                    # This triggers the transition to WaitBetweenGame in your main loop
                    self.return_state = self.final_score