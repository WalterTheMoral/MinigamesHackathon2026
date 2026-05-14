import pygame
from trivia_game import run_trivia_game

pygame.init()

screen = pygame.display.set_mode((1000, 700))
clock = pygame.time.Clock()

run_trivia_game(screen, clock)