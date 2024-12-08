import pygame

from main.assets.ImagePath import *
from main.helper.constants import *

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Shadow Boxing')

class ShadowBoxing:
    def __init__(self):
        self.background_image = pygame.image.load(PLACE_RING_SIDE)
        self.screen = screen
        self.isRunning = True

        self.setup()

    def setup(self):
        pass

    def run(self):
        while self.isRunning:
            self.screen.fill(WHITE)
            screen.blit(self.background_image, (0, 0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.isRunning = False

            pygame.display.update()
            pygame.time.Clock().tick(60)    
