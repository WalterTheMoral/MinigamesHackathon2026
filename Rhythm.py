import pygame
import time
import random
import os

pygame.init()

WIDTH, HEIGHT = 1400, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rhythm Game - Final Polish")

clock = pygame.time.Clock()
FONT = pygame.font.SysFont("Arial", 42, bold=True)
BIG = pygame.font.SysFont("Arial", 90, bold=True)

LANES = 4
lane_width = WIDTH // LANES
hit_y = HEIGHT - 140

LANE_KEYS = {
    pygame.K_LEFT: 0, pygame.K_a: 0,
    pygame.K_DOWN: 1, pygame.K_s: 1,
    pygame.K_UP: 2, pygame.K_w: 2,
    pygame.K_RIGHT: 3, pygame.K_d: 3
}

COLORS = [(255,80,80),(80,255,140),(80,180,255),(255,220,80)]
ARROWS = ["←","↓","↑","→"]

# ---------------- MUSIC ----------------
MUSIC_FILE = "song.mp3"

if not os.path.exists(MUSIC_FILE):
    print("Missing song.mp3")
    exit()

pygame.mixer.init()
pygame.mixer.music.load(MUSIC_FILE)
pygame.mixer.music.set_volume(0.7)

# ---------------- NOTE ----------------
class Note:
    def __init__(self, lane, speed):
        self.lane = lane
        self.x = lane * lane_width + lane_width // 2
        self.y = -60
        self.speed = speed
        self.hit = False

    def update(self):
        self.y += self.speed

    def draw(self):
        if self.hit:
            return
        pygame.draw.circle(screen, COLORS[self.lane], (self.x, int(self.y)), 42)
        pygame.draw.circle(screen, (255,255,255), (self.x, int(self.y)), 42, 2)

        txt = FONT.render(ARROWS[self.lane], True, (0,0,0))
        screen.blit(txt, (self.x-12, self.y-25))


notes = []

score = 0
streak = 0
max_streak = 0

# ---------------- GAME STATE ----------------
state = "COUNTDOWN"
countdown_start = time.time()
go_time = None
game_start_time = None

last_spawn = 0
game_over = False
final_return = None

feedback = ""
feedback_time = 0


running = True

while running:
    screen.fill((10,10,18))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if state == "PLAYING" and not game_over:
            if event.type == pygame.KEYDOWN:
                if event.key in LANE_KEYS:
                    lane = LANE_KEYS[event.key]

                    best = None
                    best_dist = 999

                    for n in notes:
                        if n.lane == lane and not n.hit:
                            dist = abs(n.y - hit_y)
                            if dist < best_dist:
                                best = n
                                best_dist = dist

                    if best:
                        if best_dist < 60:
                            base = 150
                            feedback = "PERFECT"
                            streak += 1
                        elif best_dist < 100:
                            base = 100
                            feedback = "GOOD"
                            streak += 1
                        else:
                            base = 0
                            feedback = "MISS"
                            streak = max(0, streak - 3)

                        best.hit = True

                        multiplier = 1 + streak * 0.04
                        score += int(base * multiplier)

                        max_streak = max(max_streak, streak)
                        feedback_time = time.time()

                    else:
                        streak = max(0, streak - 4)
                        feedback = "MISS"
                        feedback_time = time.time()

    # ---------------- COUNTDOWN ----------------
    if state == "COUNTDOWN":
        t = time.time() - countdown_start

        if t < 1:
            text = "3"
        elif t < 2:
            text = "2"
        elif t < 3:
            text = "1"
        else:
            text = "GO!"
            if go_time is None:
                pygame.mixer.music.play()
                go_time = time.time()
                game_start_time = go_time
                state = "PLAYING"

        big = BIG.render(text, True, (255,255,255))
        screen.blit(big, (WIDTH//2 - 60, HEIGHT//2 - 80))

        pygame.display.flip()
        clock.tick(60)
        continue

    # ---------------- TIMER ----------------
    elapsed = time.time() - game_start_time

    if elapsed >= 30 and not game_over:
        game_over = True

        # 🎵 STOP MUSIC ON TIME UP (FIX YOU REQUESTED)
        pygame.mixer.music.stop()

        # 📤 return value support
        final_return = (score, True)

    # ---------------- GAMEPLAY ----------------
    if state == "PLAYING" and not game_over:

        difficulty = min((streak * 0.15) + (elapsed * 0.02), 6)

        note_speed = 3 + difficulty * 1.8
        spawn_delay = max(1.2 - difficulty * 0.18, 0.25)

        if time.time() - last_spawn > spawn_delay:
            lane = random.randint(0, 3)
            notes.append(Note(lane, note_speed))
            last_spawn = time.time()

        for n in notes:
            n.speed = note_speed
            n.update()

        notes = [n for n in notes if n.y < HEIGHT + 100 and not n.hit]

        # lanes
        for i in range(LANES):
            x = i * lane_width
            pygame.draw.rect(screen, COLORS[i], (x, 0, 5, HEIGHT))
            pygame.draw.rect(screen, COLORS[i], (x, hit_y - 5, lane_width, 10))

        for n in notes:
            n.draw()

        ui = FONT.render(f"SCORE {score}  STREAK {streak}", True, (255,255,255))
        screen.blit(ui, (20,20))

        if time.time() - feedback_time < 0.4:
            fb = BIG.render(feedback, True, (255,255,255))
            screen.blit(fb, (WIDTH//2 - 140, HEIGHT//2))

    # ---------------- END SCREEN (HAPPIER) ----------------
    else:
        title = BIG.render("GOOD RUN! 🎉", True, (255,255,255))
        score_text = FONT.render(f"Final Score: {score}", True, (255,255,255))
        streak_text = FONT.render(f"Max Streak: {max_streak}", True, (255,255,255))
        msg = FONT.render("Nice rhythm control — try again for a higher score!", True, (200,200,200))

        screen.blit(title, (WIDTH//2 - 220, HEIGHT//2 - 160))
        screen.blit(score_text, (WIDTH//2 - 240, HEIGHT//2 - 40))
        screen.blit(streak_text, (WIDTH//2 - 220, HEIGHT//2 + 20))
        screen.blit(msg, (WIDTH//2 - 380, HEIGHT//2 + 90))

        # return value visible in console
        if final_return:
            print("RESULT:", final_return)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()