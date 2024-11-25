import pygame

from main.helper.constants import *
from main.helper.ui_elements.Attribute import *

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Main Menu Example')

class VersusBot:
    def __init__(self):
        self.screen = screen
        self.draw_interface()
        self.running = True

    def draw_interface(self):
        self.player_hp = Attributes(SCREEN_MARGIN, SCREEN_MARGIN, 400, 40, RED)
        self.player_stamina = Attributes(SCREEN_MARGIN,
                                         self.player_hp.rect.bottom, 350, 20, BLUE)

        self.bot_hp = Attributes(self.screen.get_width() - (400 + SCREEN_MARGIN), SCREEN_MARGIN, 400, 40, RED) 
        self.bot_stamina = Attributes(self.bot_hp.rect.left + 50, self.bot_hp.rect.bottom,
                                      350, 20, BLUE)

    def start_timer(self):
        text = "3:00"
        font = pygame.font.Font(None, 60)
        self.timer = screen.blit(font.render(text, True, BLACK),
                    (self.player_hp.rect.right + 55, SCREEN_MARGIN + 15))
        



    def run(self):
        while self.running:
            self.screen.fill(WHITE)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            
            self.start_timer()
            
            self.player_hp.draw(screen, corner_bottomRight=15)
            self.player_stamina.draw(screen, corner_bottomRight=15)
            self.bot_hp.draw(screen, corner_bottomLeft=15)
            self.bot_stamina.draw(screen, corner_bottomLeft=15)

            pygame.display.update()


                    