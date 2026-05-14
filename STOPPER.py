import pygame
import random


# הפונקציה החדשה: מחזירה False, את הזמן הסופי ואת ההפרש
def get_game_results(f_time, t_time):
    diff = abs(f_time - t_time)
    return False, diff


pygame.init()
screen = pygame.display.set_mode((800, 600))
font = pygame.font.SysFont("impact", 35)

running = True
state = "START"
target_time = random.randint(3000, 7000)
start_ticks = 0
final_time = 0
diff_value = 0

while running:
    screen.fill((225, 193, 110))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if state == "START":
                start_ticks = pygame.time.get_ticks()
                state = "RUNNING"

            elif state == "RUNNING":
                raw_final = pygame.time.get_ticks() - start_ticks
                # שימוש בפונקציה החדשה לקבלת הנתונים ועדכון מצב הריצה
                running, final_time, diff_value = get_game_results(raw_final, target_time)
                state = "STOPPED"

    target_text = font.render(f"Target: {target_time / 1000:.2f}s", True, (0, 0, 0))
    screen.blit(target_text, (300, 200))

    if state == "START":
        msg = font.render("Press SPACE to Start", True, (0, 0, 0))
        screen.blit(msg, (250, 300))

    elif state == "RUNNING":
        current_time = (pygame.time.get_ticks() - start_ticks) / 1000
        timer_text = font.render(f"{current_time:.3f}", True, (0, 0, 0))
        screen.blit(timer_text, (350, 300))

    if state == "STOPPED":
        score_text = font.render(f"Final: {final_time / 1000:.3f}s", True, (255, 255, 255))
        diff_text = font.render(f"Diff: {diff_value / 1000:.3f}s", True, (255, 100, 100))

        screen.blit(score_text, (300, 270))
        screen.blit(diff_text, (300, 320))

        pygame.display.flip()
        pygame.time.wait(3000)
        # הלולאה תסתיים כאן כי running הפך ל-False מהפונקציה

    pygame.display.flip()

pygame.quit()
