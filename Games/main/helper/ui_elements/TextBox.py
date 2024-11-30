import pygame

from main.helper.constants import *

pygame.font.init()

class TextBox:
    def __init__(self, text, x, y, width, height, color = FOREGROUND) -> None:
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color

    def draw(self, screen):
        font = pygame.font.Font(None, FONT_SIZE)
        pygame.draw.rect(screen, self.color, self.rect)
        
        text_surface = font.render(self.text, True,  WHITE)
        text_rect = text_surface.get_rect(topleft=(self.rect.left + 20, self.rect.top + 20))
        screen.blit(text_surface, text_rect)
        
        