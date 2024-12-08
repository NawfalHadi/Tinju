import pygame

from main.assets.ImagePath import *
from main.helper.constants import *

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Bot Training')  

class BotTraining:
    def __init__(self, model_path):
        self.background_img = pygame.image.load(PLACE_RING)
        self.screen = screen
        self.isRunning = True

    def run(self):
        while self.isRunning:
            self.screen.fill(WHITE)
            self.screen.blit(self.background_img, (0, 0))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.isRunning = False

            pygame.display.update()
            pygame.time.Clock().tick(60)
            