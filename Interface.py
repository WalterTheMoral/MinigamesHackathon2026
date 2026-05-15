import random
import re
import socket
import string
import threading
import time

import pygame

import LPM
import Perfect_Circle
import ReactionGame
import Rhythm
import Trivia
import Space_bar
import blink_counter
import colour_detector
from Scenes import *


SERVER_HOST = "10.13.244.168"
SERVER_PORT = 5555
MAX_PLAYERS = 5
REWARDS = [25, 20, 15, 10, 5]


class InterfaceClient:
    """Non-blocking Pygame client for the server.py text protocol."""

    PROMPTS = {
        "Welcome! Type 'HOST' or 'JOIN': ": "welcome",
        "Enter a password for your game: ": "host_password",
        "Enter Password: ": "join_password",
        "Wrong! Try again: ": "wrong_password",
    }

    def __init__(self, host=SERVER_HOST, port=SERVER_PORT):
        self.host = host
        self.port = port
        self.sock = None
        self.connected = False
        self.running = False
        self.lock = threading.Lock()

        self.prompt_events = {
            prompt_name: threading.Event()
            for prompt_name in self.PROMPTS.values()
        }

        self.is_host = False
        self.player_id = None
        self.joined_count = 0
        self.game_state = "disconnected"
        self.current_minigame = None
        self.round_id = 0
        self.leaderboard_data = ""
        self.coins = 0
        self.error = ""

    def connect(self):
        if self.connected:
            return True

        try:
            print(f"[INTERFACE] Connecting to {self.host}:{self.port}")
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            self.connected = True
            self.running = True
            self.game_state = "connected"
            threading.Thread(target=self._listen, daemon=True).start()
            return True
        except OSError as exc:
            self.error = f"Connection failed: {exc}"
            print(f"[INTERFACE] {self.error}")
            return False

    def host_game(self, password):
        self.is_host = True
        self.joined_count = 1
        if not self.connect():
            return False

        self._send("HOST")
        self._wait_for_prompt("host_password")
        self._send(password)
        self.game_state = "lobby"
        return True

    def join_game(self, password):
        self.is_host = False
        if not self.connect():
            return False

        self._send("JOIN")
        self._wait_for_prompt("join_password")
        self._send(password)
        self.game_state = "lobby"
        return True

    def send_start(self):
        print("[INTERFACE] Sending START")
        return self._send("START")

    def send_score(self, result):
        score, score_type = self._normalize_score(result)
        print(f"[INTERFACE] Sending score: {score},{score_type}")
        return self._send(f"{score},{score_type}")

    def close(self):
        self.running = False
        self.connected = False
        try:
            if self.sock:
                self.sock.close()
        except OSError:
            pass

    def _send(self, message):
        if not self.connected or not self.sock:
            print(f"[INTERFACE] Cannot send while disconnected: {message}")
            return False

        try:
            print(f"[INTERFACE -> SERVER] {message}")
            with self.lock:
                self.sock.sendall(str(message).encode("utf-8"))
            return True
        except OSError as exc:
            self.error = f"Send failed: {exc}"
            print(f"[INTERFACE] {self.error}")
            self.connected = False
            self.game_state = "disconnected"
            return False

    def _listen(self):
        buffer = ""
        while self.running:
            try:
                data = self.sock.recv(1024).decode("utf-8")
                if not data:
                    break
                buffer += data
                buffer = self._consume_prompts(buffer)

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self._handle_server_message(line.strip())
            except OSError as exc:
                if self.running:
                    self.error = f"Connection error: {exc}"
                    print(f"[INTERFACE] {self.error}")
                break

        self.connected = False
        if self.running:
            self.game_state = "disconnected"
            print("[INTERFACE] Disconnected from server.")

    def _consume_prompts(self, buffer):
        for prompt, prompt_name in self.PROMPTS.items():
            if prompt in buffer:
                print(f"[SERVER -> INTERFACE] {prompt}")
                self.prompt_events[prompt_name].set()
                if prompt_name == "wrong_password":
                    self.error = "Wrong password."
                buffer = buffer.replace(prompt, "")
        return buffer

    def _handle_server_message(self, message):
        if not message:
            return

        print(f"[SERVER -> INTERFACE] {message}")
        message = self._clean_server_message(message)

        if "YOUR_ID:" in message:
            message = self._consume_player_id(message)
            if not message:
                return

        if message.startswith("Game created."):
            self.joined_count = max(self.joined_count, 1)
            self.game_state = "lobby"

        elif message.startswith("Player joined!"):
            match = re.search(r"Total players:\s*(\d+)", message)
            if match:
                self.joined_count = int(match.group(1))
            self.game_state = "lobby"

        elif message.startswith("Not enough players"):
            self.error = message

        elif message.startswith("GAME STARTING NOW!"):
            self.game_state = "starting"

        elif message.startswith("START_GAME:"):
            self.current_minigame = message.split(":", 1)[1].strip().replace("'", "")
            self.round_id += 1
            self.game_state = "playing"

        elif message.startswith("LEADERBOARD:"):
            self.leaderboard_data = message.replace("LEADERBOARD:", "", 1).strip()
            self._apply_leaderboard_rewards()
            self.game_state = "leaderboard"

        elif message.startswith("PHASE:BUY"):
            self.game_state = "buy_phase"
            self._send(str(self.coins))

        elif message.startswith("FINAL_RESULTS:"):
            self.leaderboard_data = message.replace("FINAL_RESULTS:", "", 1).strip()
            self.game_state = "finished"

        elif message.startswith("DISCONNECT:"):
            self.game_state = "finished"
            self.close()

    def _consume_player_id(self, message):
        id_start = message.find("YOUR_ID:") + len("YOUR_ID:")
        start_game_idx = message.find("START_GAME:")

        if start_game_idx == -1:
            raw_id = message[id_start:].strip()
            rest = ""
        else:
            raw_id = message[id_start:start_game_idx].strip()
            rest = message[start_game_idx:].strip()

        try:
            self.player_id = int(raw_id)
            print(f"[INTERFACE] Assigned player ID: {self.player_id}")
        except ValueError:
            pass

        return rest

    def _apply_leaderboard_rewards(self):
        if self.player_id is None:
            return

        entries = [entry.strip() for entry in self.leaderboard_data.split("|")]
        for rank, entry in enumerate(entries):
            if entry.startswith(f"P{self.player_id}:") and rank < len(REWARDS):
                self.coins += REWARDS[rank]
                print(f"[INTERFACE] Coins after reward: {self.coins}")
                return

    def _wait_for_prompt(self, prompt_name, timeout=2.0):
        self.prompt_events[prompt_name].wait(timeout)

    def _clean_server_message(self, message):
        if message.startswith("b'") and message.endswith("'"):
            message = message[2:-1]
        if message.startswith('b"') and message.endswith('"'):
            message = message[2:-1]
        return message.replace("\\n", "").strip()

    def _normalize_score(self, result):
        score = result
        higher_is_better = True

        if isinstance(result, (tuple, list)):
            if result:
                score = result[0]
            if len(result) > 1:
                higher_is_better = bool(result[1])

        score_type = "score" if higher_is_better else "time"
        try:
            score = float(score)
        except (TypeError, ValueError):
            score = 0.0

        return f"{score:g}", score_type


pygame.init()

screen = pygame.display.set_mode((1400, 800))
pygame.display.set_caption("Mario Party")
clock = pygame.time.Clock()

client = InterfaceClient()
# activeScene = BettingScene(screen, 10, [4, 1, 2, 5])
activeScene = Title(screen)
last_started_round = 0
running = True


def make_game_scene(game_name):
    game_scenes = {
        "space": lambda: Space_bar.ClickSpeedTestScene(screen),
        "circle": lambda: Perfect_Circle.PerfectCircleScene(screen),
        "colour": lambda: colour_detector.ColourDetectorScene(screen, "red"),
        "blink": lambda: blink_counter.BlinkCounterScene(screen),
        "rhythm": lambda: Rhythm.RhythmGame(screen),
        "reaction": lambda: ReactionGame.ReactionTimeGame(screen),
        "trivia": lambda: Trivia.TriviaGame(screen),
        "speed": lambda: LPM.TypingGame(screen),
    }
    return game_scenes.get(game_name, lambda: Scene(screen))()


def score_value(result):
    if isinstance(result, (tuple, list)) and result:
        return result[0]
    return result


while running:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False

    if not running:
        break

    screen.fill((225, 193, 110))
    activeScene.handle_events(events)
    activeScene.draw()

    if isinstance(activeScene, Title):
        choice = activeScene.get_return_state()
        if choice == "join":
            activeScene = JoinGame(screen)
        elif choice == "host":
            password = "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
            if client.host_game(password):
                activeScene = HostWait(screen, lambda: client.joined_count, password)
            else:
                activeScene = Title(screen)

    elif isinstance(activeScene, HostWait):
        if activeScene.get_return_state() == "start":
            client.send_start()
            activeScene.return_state = None

    elif isinstance(activeScene, JoinGame):
        result = activeScene.get_return_state()
        if result and result.startswith("submit:"):
            password = result.split(":", 1)[1].strip()
            if client.join_game(password):
                activeScene = Waiting(
                    screen,
                    lambda: client.joined_count,
                    lambda: client.game_state == "playing",
                    password,
                )
            else:
                activeScene = JoinGame(screen)

    if client.game_state == "playing" and client.round_id != last_started_round:
        activeScene = StartGame(screen, client.current_minigame, [])
        last_started_round = client.round_id

    if isinstance(activeScene, StartGame) and activeScene.get_return_state():
        activeScene = make_game_scene(client.current_minigame)

    if isinstance(activeScene, Game):
        result = activeScene.get_return_state()
        if result:
            client.send_score(result)
            activeScene = WaitBetweenGame(
                screen,
                score_value(result),
                lambda: client.game_state == "playing",
            )

    if client.game_state == "finished" and not isinstance(activeScene, Title):
        print(f"[INTERFACE] Final results: {client.leaderboard_data}")
        activeScene = Title(screen)

    pygame.display.flip()
    clock.tick(60)

client.close()
pygame.quit()