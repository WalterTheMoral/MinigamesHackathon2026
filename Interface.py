import pygame
from Scenes import *
import Space_bar

pygame.init()

screen = pygame.display.set_mode((1400, 800))
pygame.display.set_caption("Mario Party")

# 3. Clock to control frame rate
clock = pygame.time.Clock()
running = True


activeScene = Title(screen)

def joined_count():
    return 1 # TODO: With Comms

def has_started():
    return True # TODO: With Comms

def get_password():
    return "321"

def get_game():
    return "space"

def is_finished_waiting():
    return True

game_scenes = {
    "None": Scene(screen),
    "space": Space_bar.ClickSpeedTestScene(screen)
}

while running:
    if pygame.event.get(pygame.QUIT):
        running = False
        break

    screen.fill((225, 193, 110))
    activeScene.handle_events(pygame.event.get())
    activeScene.draw()

    # print(activeScene.get_return_state())
    if activeScene.__class__ == Title:
        if activeScene.get_return_state() == 'join':
            activeScene = JoinGame(screen)
        elif activeScene.get_return_state() == 'host':
            activeScene = HostWait(screen, joined_count, get_password())
    if activeScene.__class__ == HostWait:
        if activeScene.get_return_state() == "start":
            activeScene = StartGame(screen, get_game(), [2, 3, 5,1])
    if activeScene.__class__ == StartGame:
        if activeScene.get_return_state():
            activeScene = game_scenes[get_game()]

    if activeScene.__class__ == JoinGame:
        print(activeScene.get_return_state())
        if activeScene.get_return_state() and "submit" in activeScene.get_return_state():
            password = activeScene.get_return_state().split(":")[1]
            activeScene = Waiting(screen, joined_count, has_started, password)

    if isinstance(activeScene, Game):
        print(activeScene.get_return_state())
        if activeScene.get_return_state():
            print(activeScene.get_return_state())
            activeScene = WaitBetweenGame(screen, activeScene.get_return_state(), is_finished_waiting)


    pygame.display.flip()

    clock.tick(60)

pygame.quit()