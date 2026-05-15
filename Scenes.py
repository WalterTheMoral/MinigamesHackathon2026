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
        self.score_text = self.score_font.render(f"You got {self.score} points", True, (0,0,0))

        self.waiting_text = self.score_font.render("Waiting for others to finish...", True, (0,0,0))

    def draw(self):
        self.screen.blit(self.score_text, self.score_text.get_rect(center=self.screen.get_rect().center).move(0,-100))
        self.screen.blit(self.waiting_text, self.waiting_text.get_rect(center=self.screen.get_rect().center).move(0,100))

    def get_return_state(self):
        return self.is_finished_waiting()

    class BettingScene(Scene):
        def __init__(self, screen, total_points, leaderboard):
            super().__init__(screen)

            self.total_points = total_points
            self.leaderboard = leaderboard
            self.num_players = len(leaderboard)

            self.selected_place = 1
            self.bid_amount = 0

            self.screen_width = screen.get_width()
            self.screen_height = screen.get_height()

            # ===== FONTS =====
            self.title_font = pygame.font.SysFont(None, 64)
            self.font = pygame.font.SysFont(None, 40)
            self.small_font = pygame.font.SysFont(None, 34)

            # ===== MAIN AREA POSITIONING =====
            # Slightly left of center
            self.main_center_x = self.screen_width // 2 - 180

            # ===== SLIDER =====
            self.slider_rect = pygame.Rect(
                self.main_center_x - 300,
                220,
                600,
                12
            )

            self.slider_handle_radius = 18
            self.dragging_slider = False

            # ===== PLACE BUTTONS =====
            self.place_buttons = []

            button_width = 95
            button_height = 75
            spacing = 20

            total_width = (
                    self.num_players * button_width
                    + (self.num_players - 1) * spacing
            )

            start_x = self.main_center_x - total_width // 2

            for i in range(self.num_players):
                rect = pygame.Rect(
                    start_x + i * (button_width + spacing),
                    390,
                    button_width,
                    button_height
                )

                self.place_buttons.append((i + 1, rect))

            # ===== SUBMIT BUTTON =====
            self.submit_button = pygame.Rect(
                self.main_center_x - 120,
                560,
                240,
                85
            )

            # ===== LEADERBOARD =====
            self.leaderboard_rect = pygame.Rect(
                self.screen_width - 360,
                100,
                300,
                520
            )

        def draw(self):
            self.screen.fill((28, 28, 38))

            # ===== TITLE =====
            title = self.title_font.render(
                "PLACE YOUR BET",
                True,
                (255, 255, 255)
            )

            title_rect = title.get_rect(
                center=(self.main_center_x, 90)
            )

            self.screen.blit(title, title_rect)

            # ===== BID TEXT =====
            bid_text = self.font.render(
                f"Bid Amount: {self.bid_amount} / {self.total_points}",
                True,
                (240, 240, 240)
            )

            bid_rect = bid_text.get_rect(
                center=(self.main_center_x, 170)
            )

            self.screen.blit(bid_text, bid_rect)

            # ===== SLIDER =====
            pygame.draw.rect(
                self.screen,
                (90, 90, 90),
                self.slider_rect,
                border_radius=10
            )

            handle_x = self.get_slider_handle_x()

            pygame.draw.circle(
                self.screen,
                (0, 210, 255),
                (handle_x, self.slider_rect.centery),
                self.slider_handle_radius
            )

            # ===== PLACE TEXT =====
            place_text = self.font.render(
                "Select Final Placement",
                True,
                (255, 255, 255)
            )

            place_rect = place_text.get_rect(
                center=(self.main_center_x, 320)
            )

            self.screen.blit(place_text, place_rect)

            # ===== PLACE BUTTONS =====
            for place, rect in self.place_buttons:
                color = (
                    (0, 180, 80)
                    if place == self.selected_place
                    else (70, 70, 85)
                )

                pygame.draw.rect(
                    self.screen,
                    color,
                    rect,
                    border_radius=14
                )

                text = self.font.render(
                    str(place),
                    True,
                    (255, 255, 255)
                )

                text_rect = text.get_rect(center=rect.center)

                self.screen.blit(text, text_rect)

            # ===== SUBMIT BUTTON =====
            pygame.draw.rect(
                self.screen,
                (220, 120, 20),
                self.submit_button,
                border_radius=16
            )

            submit_text = self.font.render(
                "SUBMIT",
                True,
                (255, 255, 255)
            )

            submit_rect = submit_text.get_rect(
                center=self.submit_button.center
            )

            self.screen.blit(submit_text, submit_rect)

            # ===== LEADERBOARD PANEL =====
            pygame.draw.rect(
                self.screen,
                (45, 45, 60),
                self.leaderboard_rect,
                border_radius=18
            )

            leaderboard_title = self.font.render(
                "Leaderboard",
                True,
                (255, 255, 255)
            )

            title_rect = leaderboard_title.get_rect(
                center=(
                    self.leaderboard_rect.centerx,
                    self.leaderboard_rect.y + 40
                )
            )

            self.screen.blit(leaderboard_title, title_rect)

            # Sort descending by score
            sorted_players = sorted(
                enumerate(self.leaderboard),
                key=lambda x: x[1],
                reverse=True
            )

            y = self.leaderboard_rect.y + 100

            for rank, (player_id, points) in enumerate(sorted_players, start=1):
                row_text = (
                    f"{rank}. Player {player_id}"
                    f"   {points} pts"
                )

                text_surface = self.small_font.render(
                    row_text,
                    True,
                    (235, 235, 235)
                )

                self.screen.blit(
                    text_surface,
                    (self.leaderboard_rect.x + 25, y)
                )

                y += 55

        def handle_events(self, events):
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()

                    # Slider
                    if self.is_mouse_on_slider(mouse_pos):
                        self.dragging_slider = True
                        self.update_slider(mouse_pos[0])

                    # Placement buttons
                    for place, rect in self.place_buttons:
                        if rect.collidepoint(mouse_pos):
                            self.selected_place = place

                    # Submit button
                    if self.submit_button.collidepoint(mouse_pos):
                        self.return_state = {
                            "bid_amount": self.bid_amount,
                            "predicted_place": self.selected_place
                        }

                elif event.type == pygame.MOUSEBUTTONUP:
                    self.dragging_slider = False

                elif event.type == pygame.MOUSEMOTION:
                    if self.dragging_slider:
                        self.update_slider(event.pos[0])

        def get_slider_handle_x(self):
            ratio = self.bid_amount / max(1, self.total_points)

            return int(
                self.slider_rect.x
                + ratio * self.slider_rect.width
            )

        def update_slider(self, mouse_x):
            relative_x = mouse_x - self.slider_rect.x

            relative_x = max(
                0,
                min(relative_x, self.slider_rect.width)
            )

            ratio = relative_x / self.slider_rect.width

            self.bid_amount = int(
                ratio * self.total_points
            )

        def is_mouse_on_slider(self, mouse_pos):
            slider_hitbox = pygame.Rect(
                self.slider_rect.x,
                self.slider_rect.y - 25,
                self.slider_rect.width,
                50
            )

            return slider_hitbox.collidepoint(mouse_pos)

        def get_return_state(self):
            return self.return_state