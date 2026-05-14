import pygame
import cv2


pygame.init()

screen = pygame.display.set_mode((1400, 800))
pygame.display.set_caption("Mario Party")

# 3. Clock to control frame rate
clock = pygame.time.Clock()
running = True

class Scene:
    def __init__(self):
        self.return_state = None

    def draw(self):
        pass

    def handle_events(self, events):
        pass

    def get_return_state(self):
        return self.return_state

class Title(Scene):
    def __init__(self):
        super().__init__()

        self.title_font = pygame.font.SysFont("Arial", 75)
        self.title = self.title_font.render("Mario Party (Change Name)", True, (0,0,0), (255, 255, 255))
        self.title_rect = self.title.get_rect(center=screen.get_rect().center).move(0, -200)

        self.join_text = self.title_font.render("JOIN GAME", True, (0, 0, 0), (255, 255, 255))
        self.join_rect = self.join_text.get_rect(center = screen.get_rect().center).move(-200, 200)

        self.host_text = self.title_font.render("HOST GAME", True, (0, 0, 0), (255, 255, 255))
        self.host_rect = self.host_text.get_rect(center = screen.get_rect().center).move(200, 200)

        self.return_state = None

    def draw(self):
        screen.blit(self.title, self.title_rect)
        screen.blit(self.host_text, self.host_rect)
        screen.blit(self.join_text, self.join_rect)

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
    def __init__(self):
        super().__init__()

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
            center=screen.get_rect().center
        ).move(0, -220)

        # Textbox
        self.input_rect = pygame.Rect(0, 0, 400, 60)
        self.input_rect.center = screen.get_rect().center

        self.password = ""
        self.active = False

        # Submit button
        self.submit_text = self.ui_font.render(
            "SUBMIT",
            True,
            (0, 0, 0)
        )

        self.submit_rect = pygame.Rect(0, 0, 220, 70)
        self.submit_rect.center = screen.get_rect().center
        self.submit_rect.move_ip(0, 120)

    def draw(self):
        # Title
        screen.blit(self.title, self.title_rect)

        # Textbox
        pygame.draw.rect(
            screen,
            (255, 255, 255),
            self.input_rect
        )

        pygame.draw.rect(
            screen,
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

        screen.blit(
            text_surface,
            (self.input_rect.x + 10, self.input_rect.y + 10)
        )

        # Submit button
        pygame.draw.rect(
            screen,
            (220, 220, 220),
            self.submit_rect
        )

        pygame.draw.rect(
            screen,
            (0, 0, 0),
            self.submit_rect,
            3
        )

        submit_text_rect = self.submit_text.get_rect(
            center=self.submit_rect.center
        )

        screen.blit(self.submit_text, submit_text_rect)

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

                    # Example password check
                    if self.password == "secret":
                        self.return_state = self.password

            # Keyboard typing
            if event.type == pygame.KEYDOWN and self.active:

                # Backspace
                if event.key == pygame.K_BACKSPACE:
                    self.password = self.password[:-1]

                # Enter key
                elif event.key == pygame.K_RETURN:
                    print("Submitted password:", self.password)

                    if self.password == "secret":
                        self.return_state = self.password

                # Normal typing
                else:
                    self.password += event.unicode

    def get_return_state(self):
        return "submit:" + self.return_state


class Waiting(Scene):
    def __init__(self, joined_count, has_started):
        super().__init__()

        self.waiting_font = pygame.font.SysFont("Arial", 75)
        self.waiting_text = self.waiting_font.render("Waiting for Others to Join", True, (0,0,0))
        self.waiting_rect = self.waiting_text.get_rect(center=screen.get_rect().center).move(0,-100)

        self.joined_count = joined_count
        self.has_started = has_started

    def draw(self):
        self.joined_count_text = self.waiting_font.render(f"Joined: {self.joined_count()} / 5", True, (0,0,0))
        self.joined_count_rect = self.joined_count_text.get_rect(center=screen.get_rect().center).move(0, 100)

        screen.blit(self.waiting_text, self.waiting_rect)
        screen.blit(self.joined_count_text, self.joined_count_rect)

    def get_return_state(self):
        return self.has_started()

class HostWait(Waiting):
    def __init__(self, joined_count):
        super().__init__(joined_count)

        self.start_text = self.waiting_font.render("START GAME", True, (0, 0, 0), (255, 255, 255))
        self.start_rect = self.start_text.get_rect(center = screen.get_rect().center).move(0, 250)

    def draw(self):
        super().draw()
        screen.blit(self.start_text, self.start_rect)

    def handle_events(self, events):
        for event in events:
            if event == pygame.MOUSEBUTTONDOWN:
                if self.start_rect.collidepoint(pygame.mouse.get_pos()):
                    self.return_state = "start"

activeScene = Title()

def joined_count():
    return 1 # TODO: With Comms

def has_started():
    return True # TODO: With Comms

def get_game():
    return ""

while running:
    if pygame.event.get(pygame.QUIT):
        running = False
        break

    screen.fill((225, 193, 110))
    activeScene.handle_events(pygame.event.get())
    activeScene.draw()

    if activeScene.get_return_state() == 'join':
        activeScene = JoinGame()
    elif activeScene.get_return_state() == 'host':
        activeScene = HostWait(joined_count)
    elif activeScene.get_return_state() and "submit" in activeScene.get_return_state():
        password = activeScene.get_return_state().split(":")[1]
        activeScene = Waiting(joined_count, has_started)
    elif activeScene.get_return_state() == "start":
        activeScene = Start(get_game())

    pygame.display.flip()

    clock.tick(60)

pygame.quit()