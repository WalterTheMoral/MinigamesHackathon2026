import pygame
import time
import random

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
            "THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG",
            "PYTHON PROGRAMMING IS FAST AND POWERFUL",
            "TYPE AS FAST AS YOU CAN TO WIN"
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
