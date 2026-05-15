import pygame

import LPM
import Perfect_Circle
import ReactionGame
import Rhythm
import Trivia
from Scenes import *
import Space_bar
import colour_detector
import blink_counter

pygame.init()

screen = pygame.display.set_mode((1400, 800))
pygame.display.set_caption("Mario Party")

clock = pygame.time.Clock()
running = True

activeScene = Title(screen)


# -------------------------
# Dummy functions
# -------------------------
def joined_count():
    return 1

def has_started():
    return True

def get_password():
    return "321"

def get_game():
    return "colour"

def is_finished_waiting():
    return True

def get_max_bid():
    return 100

def get_button_count():
    return 4


# -------------------------
# Scenes dictionary
# -------------------------
game_scenes = {
    "None": Scene(screen),
    "space": Space_bar.ClickSpeedTestScene(screen),
    "circle": Perfect_Circle.PerfectCircleScene(screen),
    "colour": colour_detector.ColourDetectorScene(screen, "red"),
    "blink": blink_counter.BlinkCounterScene(screen),
    "rhythm": Rhythm.RhythmGame(screen),
    "reaction": ReactionGame.ReactionTimeGame(screen),
    "trivia": Trivia.TriviaGame(screen),
    "speed": LPM.TypingGame(screen),
    "bidding": BidScene(screen, get_max_bid, get_button_count)
}


# -------------------------
# Main loop
# -------------------------
while running:

    events = pygame.event.get()

    for event in events:
        if event.type == pygame.QUIT:
            running = False

    screen.fill((225, 193, 110))

    activeScene.handle_events(events)
    activeScene.draw()

    # -------------------------
    # ORIGINAL FLOW (UNCHANGED)
    # -------------------------

    if activeScene.__class__ == Title:
        state = activeScene.get_return_state()
        if state == 'join':
            activeScene = JoinGame(screen)
        elif state == 'host':
            activeScene = HostWait(screen, joined_count, get_password())

    elif activeScene.__class__ == HostWait:
        if activeScene.get_return_state() == "start":
            activeScene = StartGame(screen, get_game(), [2, 3, 5, 1])

    elif activeScene.__class__ == StartGame:
        if activeScene.get_return_state():
            activeScene = game_scenes[get_game()]

    elif activeScene.__class__ == JoinGame:
        state = activeScene.get_return_state()
        if state and "submit" in state:
            password = state.split(":")[1]
            activeScene = Waiting(screen, joined_count, has_started, password)

    elif isinstance(activeScene, Game):
        if activeScene.get_return_state():
            activeScene = WaitBetweenGame(
                screen,
                activeScene.get_return_state(),
                is_finished_waiting
            )

    # -------------------------
    # 🔥 ONLY ADDITION: AFTER WAIT BETWEEN GAME
    # -------------------------
    elif isinstance(activeScene, WaitBetweenGame):
        if activeScene.get_return_state():
            activeScene = game_scenes["bidding"]

    pygame.display.flip()
    clock.tick(60)

pygame.quit()