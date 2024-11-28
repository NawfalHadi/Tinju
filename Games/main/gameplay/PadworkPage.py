import pygame

from main.helper.constants import *

padworks = [
    [1, 5, ["jab", "straight", "guard", "duck", "jab"], "00:00:00"],
    [2, 6, ["jab", "straight", "jab", "straight", "jab", "guard", "jab"], "00:00:00"]
]

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Padworks')

class PadworkList:
    def __init__(self) -> None:
        self.screen = screen
        self.running = True

    def run(self):
        while self.running:
            self.screen.fill(WHITE)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            pygame.display.update()

class PadworkPage:
    def __init__(self) -> None:
        pass