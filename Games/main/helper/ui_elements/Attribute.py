import pygame
from main.helper.constants import *

class Attributes:
    def __init__(self, x, y, width, height, color) -> None:
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        
    def draw(self, screen, corner_bottomLeft=0, corner_bottomRight=0):
        
        pygame.draw.rect(screen, self.color, self.rect,
                         border_bottom_left_radius=corner_bottomLeft,
                         border_bottom_right_radius=corner_bottomRight)
