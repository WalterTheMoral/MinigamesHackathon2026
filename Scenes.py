import pygame

pygame.init()

def has_started():
    return True # TODO: With Comms

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

class Title(Scene):
    def __init__(self, screen):
        super().__init__(screen)

        self.title_font = pygame.font.SysFont("Arial", 75)
        self.title = self.title_font.render("Mario Party (Change Name)", True, (0,0,0), (255, 255, 255))
        self.title_rect = self.title.get_rect(center=screen.get_rect().center).move(0, -200)

        self.join_text = self.title_font.render("JOIN GAME", True, (0, 0, 0), (255, 255, 255))
        self.join_rect = self.join_text.get_rect(center = screen.get_rect().center).move(-200, 200)

        self.host_text = self.title_font.render("HOST GAME", True, (0, 0, 0), (255, 255, 255))
        self.host_rect = self.host_text.get_rect(center = screen.get_rect().center).move(200, 200)

        self.return_state = None

    def draw(self):
        self.screen.blit(self.title, self.title_rect)
        self.screen.blit(self.host_text, self.host_rect)
        self.screen.blit(self.join_text, self.join_rect)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.host_rect.collidepoint(pygame.mouse.get_pos()):
                    self.return_state = "host"
                elif self.join_rect.collidepoint(pygame.mouse.get_pos()):
                    self.return_state = "join"

    def get_return_state(self):
        return self.return_state


class JoinGame(Scene):
    def __init__(self, screen):
        super().__init__(screen)

        self.title_font = pygame.font.SysFont("Arial", 75)
        self.ui_font = pygame.font.SysFont("Arial", 40)

        # Title
        self.title = self.title_font.render(
            "Join Game",
            True,
            (0, 0, 0),
            (255, 255, 255)
        )
        self.title_rect = self.title.get_rect(
            center=self.screen.get_rect().center
        ).move(0, -220)

        # Textbox
        self.input_rect = pygame.Rect(0, 0, 400, 60)
        self.input_rect.center = self.screen.get_rect().center

        self.password = ""
        self.active = False

        # Submit button
        self.submit_text = self.ui_font.render(
            "SUBMIT",
            True,
            (0, 0, 0)
        )

        self.submit_rect = pygame.Rect(0, 0, 220, 70)
        self.submit_rect.center = self.screen.get_rect().center
        self.submit_rect.move_ip(0, 120)

    def draw(self):
        # Title
        self.screen.blit(self.title, self.title_rect)

        # Textbox
        pygame.draw.rect(
            self.screen,
            (255, 255, 255),
            self.input_rect
        )

        pygame.draw.rect(
            self.screen,
            (0, 0, 0),
            self.input_rect,
            3
        )

        # Hide password characters
        hidden_text = self.password
        text_surface = self.ui_font.render(
            hidden_text,
            True,
            (0, 0, 0)
        )

        self.screen.blit(
            text_surface,
            (self.input_rect.x + 10, self.input_rect.y + 10)
        )

        # Submit button
        pygame.draw.rect(
            self.screen,
            (220, 220, 220),
            self.submit_rect
        )

        pygame.draw.rect(
            self.screen,
            (0, 0, 0),
            self.submit_rect,
            3
        )

        submit_text_rect = self.submit_text.get_rect(
            center=self.submit_rect.center
        )

        self.screen.blit(self.submit_text, submit_text_rect)

    def handle_events(self, events):
        for event in events:

            # Mouse clicks
            if event.type == pygame.MOUSEBUTTONDOWN:

                # Activate textbox
                if self.input_rect.collidepoint(event.pos):
                    self.active = True
                else:
                    self.active = False

                # Submit button
                if self.submit_rect.collidepoint(event.pos):
                    print("Submitted password:", self.password)

                    self.return_state = self.password

            # Keyboard typing
            if event.type == pygame.KEYDOWN and self.active:

                # Backspace
                if event.key == pygame.K_BACKSPACE:
                    self.password = self.password[:-1]

                # Enter key
                elif event.key == pygame.K_RETURN:
                    print("Submitted password:", self.password)

                    self.return_state = self.password

                # Normal typing
                else:
                    self.password += event.unicode

    def get_return_state(self):
        return ("submit:" + self.return_state) if self.return_state else ""


class Waiting(Scene):
    def __init__(self, screen, joined_count, has_started, password="123"):
        super().__init__(screen)

        self.waiting_font = pygame.font.SysFont("Arial", 75)
        self.waiting_text = self.waiting_font.render("Waiting for Others to Join...", True, (0,0,0))
        self.waiting_rect = self.waiting_text.get_rect(center=self.screen.get_rect().center).move(0,-300)

        self.lobby_key = self.waiting_font.render(f"Lobby Key: {password}", True, (0,0,0))
        self.lobby_key_rect = self.lobby_key.get_rect(center=self.screen.get_rect().center).move(0, -100)

        self.joined_count = joined_count
        self.has_started = has_started

    def draw(self):
        self.joined_count_text = self.waiting_font.render(f"Joined: {self.joined_count()} / 5", True, (0,0,0))
        self.joined_count_rect = self.joined_count_text.get_rect(center=self.screen.get_rect().center).move(0, 100)

        self.screen.blit(self.lobby_key, self.lobby_key_rect)
        self.screen.blit(self.waiting_text, self.waiting_rect)
        self.screen.blit(self.joined_count_text, self.joined_count_rect)

    def handle_events(self, events):
        self.return_state = self.has_started()


class HostWait(Waiting):
    def __init__(self, screen, joined_count, password):
        super().__init__(screen, joined_count, has_started, password)

        self.start_text = self.waiting_font.render("START GAME", True, (0, 0, 0), (255, 255, 255))
        self.start_rect = self.start_text.get_rect(center = self.screen.get_rect().center).move(0, 250)

    def draw(self):
        super().draw()
        self.screen.blit(self.start_text, self.start_rect)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                print("Press")
                if self.start_rect.collidepoint(event.pos):
                    print("Press Start")
                    self.return_state = "start"

    def has_started(self):
        return self.return_state == "start"

class StartGame(Scene):
    def __init__(self, screen, game, leaderboard=None):
        super().__init__(screen)

        self.game = game
        self.leaderboard = leaderboard if leaderboard else []

        self.start_font = pygame.font.SysFont("Arial", 90)
        self.time = 1 #TODO self.time = 3.99

        self.leaderboard_font = pygame.font.SysFont("Arial", 60)
        print(enumerate(self.leaderboard))
        self.leaderboard_text = self.leaderboard_font.render(
            self.leaderboard_to_string(leaderboard),
            True,
            (0,0,0)
        )

    def draw(self):
        self.start_text = self.start_font.render(f"{self.game} Starting in {int(self.time)}", True, (0,0,0))
        self.time -= (1.0/60.0)

        self.screen.blit(self.start_text, self.start_text.get_rect(center=self.screen.get_rect().center).move(0,-100))
        self.screen.blit(self.leaderboard_text, self.leaderboard_text.get_rect(midtop=self.screen.get_rect().center).move(0,100))

    def handle_events(self, events):
        self.return_state = self.time < 0

    def leaderboard_to_string(self, leaderboard):
        sorted_leaderboard = sorted(enumerate(leaderboard), key=lambda score: score[1], reverse=True)
        return "\n".join(" : ".join([str(s) for s in score]) for score in sorted_leaderboard)

class WaitBetweenGame(Scene):
    def __init__(self, screen, score, is_finished_waiting):
        super().__init__(screen)
        self.score = score
        self.is_finished_waiting = is_finished_waiting

        self.score_font = pygame.font.SysFont("Arial", 90)
        self.score_text = self.score_font.render(f"You got {self.score} gold", True, (0,0,0))

        self.waiting_text = self.score_font.render("Waiting for others to finish...", True, (0,0,0))

    def draw(self):
        self.screen.blit(self.score_text, self.score_text.get_rect(center=self.screen.get_rect().center).move(0,-100))
        self.screen.blit(self.waiting_text, self.waiting_text.get_rect(center=self.screen.get_rect().center).move(0,100))

    def get_return_state(self):
        return self.is_finished_waiting()
