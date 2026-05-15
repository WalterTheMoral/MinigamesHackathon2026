import pygame

pygame.init()


# -------------------------
# Base classes
# -------------------------
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
    pass


# -------------------------
# Title
# -------------------------
class Title(Scene):
    def __init__(self, screen):
        super().__init__(screen)

        self.font = pygame.font.SysFont("Arial", 75)

        self.title = self.font.render("Mario Party", True, (0, 0, 0))
        self.title_rect = self.title.get_rect(center=screen.get_rect().center).move(0, -200)

        self.join = self.font.render("JOIN", True, (0, 0, 0))
        self.join_rect = self.join.get_rect(center=screen.get_rect().center).move(-200, 200)

        self.host = self.font.render("HOST", True, (0, 0, 0))
        self.host_rect = self.host.get_rect(center=screen.get_rect().center).move(200, 200)

    def draw(self):
        self.screen.blit(self.title, self.title_rect)
        self.screen.blit(self.join, self.join_rect)
        self.screen.blit(self.host, self.host_rect)

    def handle_events(self, events):
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN:
                if self.join_rect.collidepoint(e.pos):
                    self.return_state = "join"
                elif self.host_rect.collidepoint(e.pos):
                    self.return_state = "host"


# -------------------------
# Join
# -------------------------
class JoinGame(Scene):
    def __init__(self, screen):
        super().__init__(screen)

        self.font = pygame.font.SysFont("Arial", 50)
        self.password = ""
        self.active = False

        self.box = pygame.Rect(500, 300, 400, 60)
        self.submit = pygame.Rect(550, 450, 300, 60)

    def draw(self):
        pygame.draw.rect(self.screen, (255, 255, 255), self.box)
        pygame.draw.rect(self.screen, (0, 0, 0), self.box, 2)

        txt = self.font.render(self.password, True, (0, 0, 0))
        self.screen.blit(txt, (self.box.x + 10, self.box.y + 10))

        pygame.draw.rect(self.screen, (0, 120, 255), self.submit)
        self.screen.blit(self.font.render("SUBMIT", True, (255, 255, 255)), (self.submit.x + 60, self.submit.y + 10))

    def handle_events(self, events):
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN:
                if self.box.collidepoint(e.pos):
                    self.active = True
                elif self.submit.collidepoint(e.pos):
                    self.return_state = f"submit:{self.password}"
                else:
                    self.active = False

            if e.type == pygame.KEYDOWN and self.active:
                if e.key == pygame.K_BACKSPACE:
                    self.password = self.password[:-1]
                else:
                    self.password += e.unicode

    def get_return_state(self):
        return self.return_state or ""


# -------------------------
# Waiting
# -------------------------
class Waiting(Scene):
    def __init__(self, screen, joined_count, has_started, password):
        super().__init__(screen)
        self.joined_count = joined_count
        self.has_started = has_started
        self.password = password

        self.font = pygame.font.SysFont("Arial", 60)

    def draw(self):
        txt1 = self.font.render(f"Lobby: {self.password}", True, (0, 0, 0))
        txt2 = self.font.render(f"Players: {self.joined_count()}", True, (0, 0, 0))

        self.screen.blit(txt1, (400, 200))
        self.screen.blit(txt2, (400, 300))

    def handle_events(self, events):
        self.return_state = self.has_started()


# -------------------------
# Host wait
# -------------------------
class HostWait(Waiting):
    def __init__(self, screen, joined_count, password):
        super().__init__(screen, joined_count, lambda: False, password)

        self.font = pygame.font.SysFont("Arial", 60)
        self.start_rect = pygame.Rect(550, 500, 300, 80)

    def draw(self):
        super().draw()
        pygame.draw.rect(self.screen, (0, 200, 0), self.start_rect)
        self.screen.blit(self.font.render("START", True, (255, 255, 255)), (600, 515))

    def handle_events(self, events):
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN:
                if self.start_rect.collidepoint(e.pos):
                    self.return_state = "start"


# -------------------------
# Start game
# -------------------------
class StartGame(Scene):
    def __init__(self, screen, game, leaderboard):
        super().__init__(screen)
        self.game = game
        self.leaderboard = leaderboard
        self.font = pygame.font.SysFont("Arial", 80)
        self.timer = 2.5

    def draw(self):
        self.timer -= 1 / 60
        txt = self.font.render(f"{self.game} starts in {int(self.timer)}", True, (0, 0, 0))
        self.screen.blit(txt, (400, 300))

    def handle_events(self, events):
        self.return_state = self.timer < 0


# -------------------------
# Wait between games
# -------------------------
class WaitBetweenGame(Scene):
    def __init__(self, screen, score, is_finished_waiting):
        super().__init__(screen)
        self.score = score
        self.is_finished_waiting = is_finished_waiting
        self.font = pygame.font.SysFont("Arial", 60)

    def draw(self):
        self.screen.blit(self.font.render(f"Score: {self.score}", True, (0, 0, 0)), (500, 300))
        self.screen.blit(self.font.render("Waiting...", True, (0, 0, 0)), (500, 400))

    def handle_events(self, events):
        self.return_state = self.is_finished_waiting()


# -------------------------
# 🔥 NEW: Bidding Scene
# -------------------------
class BidScene(Scene):
    def __init__(self, screen, get_max_bid, get_button_count):
        super().__init__(screen)

        self.screen = screen
        self.max_value = get_max_bid()
        self.button_count = get_button_count()

        self.font = pygame.font.SysFont("Arial", 40)

        # slider
        self.slider = pygame.Rect(300, 200, 800, 8)
        self.value = 0
        self.dragging = False

        # options
        self.selected = None
        self.options = [
            pygame.Rect(300, 300 + i * 70, 300, 50)
            for i in range(self.button_count)
        ]

        # submit
        self.submit = pygame.Rect(550, 600, 300, 60)

        self.return_state = None

    def draw(self):
        self.screen.fill((240, 240, 240))

        # -------- slider line --------
        pygame.draw.rect(self.screen, (0, 0, 0), self.slider)

        ratio = self.value / self.max_value if self.max_value else 0
        knob_x = self.slider.x + int(ratio * self.slider.width)
        knob_y = self.slider.y + self.slider.height // 2

        pygame.draw.circle(self.screen, (200, 0, 0), (knob_x, knob_y), 12)

        # 🔥 SHOW VALUE (FIX #1)
        value_text = self.font.render(f"Value: {int(self.value)}", True, (0, 0, 0))
        self.screen.blit(value_text, (300, 120))

        # -------- options --------
        for i, r in enumerate(self.options):
            color = (0, 200, 0) if i == self.selected else (180, 180, 180)
            pygame.draw.rect(self.screen, color, r)

            text = self.font.render(f"Option {i+1}", True, (0, 0, 0))
            self.screen.blit(text, (r.x + 10, r.y + 10))

        # -------- submit --------
        pygame.draw.rect(self.screen, (0, 120, 255), self.submit)
        txt = self.font.render("SUBMIT", True, (255, 255, 255))
        self.screen.blit(txt, (self.submit.x + 80, self.submit.y + 10))

    def handle_events(self, events):
        for e in events:

            if e.type == pygame.MOUSEBUTTONDOWN:

                # submit FIRST (important)
                if self.submit.collidepoint(e.pos):
                    self.return_state = {
                        "bid": int(self.value),
                        "choice": self.selected
                    }
                    return  # 🔥 stop here

                # options
                for i, r in enumerate(self.options):
                    if r.collidepoint(e.pos):
                        self.selected = i

                # slider click
                if self.slider.collidepoint(e.pos):
                    self.update_slider(e.pos[0])

            # drag support (FIX usability)
            elif e.type == pygame.MOUSEMOTION:
                if pygame.mouse.get_pressed()[0]:
                    if self.slider.collidepoint(e.pos):
                        self.update_slider(e.pos[0])

    def update_slider(self, mouse_x):
        ratio = (mouse_x - self.slider.x) / self.slider.width
        ratio = max(0, min(1, ratio))

        self.value = ratio * self.max_value

    def get_return_state(self):
        return self.return_state
    def __init__(self, screen, get_max_bid, get_button_count):
        super().__init__(screen)

        self.screen = screen
        self.max_value = get_max_bid()
        self.button_count = get_button_count()

        self.font = pygame.font.SysFont("Arial", 40)

        # slider
        self.slider = pygame.Rect(300, 200, 800, 8)
        self.value = 0

        # options
        self.selected = None
        self.options = [
            pygame.Rect(300, 300 + i * 70, 300, 50)
            for i in range(self.button_count)
        ]

        # submit
        self.submit = pygame.Rect(550, 600, 300, 60)

    def draw(self):
        self.screen.fill((240, 240, 240))

        # slider
        pygame.draw.rect(self.screen, (0, 0, 0), self.slider)

        value_text = self.font.render(str(int(self.value)), True, (0, 0, 0))
        self.screen.blit(value_text, (self.slider.x, self.slider.y - 50))

        ratio = self.value / self.max_value if self.max_value else 0
        x = self.slider.x + int(ratio * self.slider.width)

        pygame.draw.circle(self.screen, (200, 0, 0), (x, self.slider.y), 12)

        # options
        for i, r in enumerate(self.options):
            color = (0, 200, 0) if i == self.selected else (180, 180, 180)
            pygame.draw.rect(self.screen, color, r)
            self.screen.blit(self.font.render(f"Option {i+1}", True, (0, 0, 0)), (r.x + 10, r.y + 10))

        # submit
        pygame.draw.rect(self.screen, (0, 120, 255), self.submit)
        self.screen.blit(self.font.render("SUBMIT", True, (255, 255, 255)), (self.submit.x + 80, self.submit.y + 10))

    def handle_events(self, events):
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN:

                # slider
                if self.slider.collidepoint(e.pos):
                    ratio = (e.pos[0] - self.slider.x) / self.slider.width
                    self.value = max(0, min(self.max_value, ratio * self.max_value))

                # options
                for i, r in enumerate(self.options):
                    if r.collidepoint(e.pos):
                        self.selected = i

                # submit
                if self.submit.collidepoint(e.pos):
                    self.return_state = {
                        "bid": int(self.slider_value),
                        "choice": self.selected_button
                    }