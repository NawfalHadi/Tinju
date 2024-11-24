import pygame

class Button:
    def __init__(self, text, x, y, width, height, color, hover_color, action=None) -> None:
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hover_color = hover_color
        self.action = action

    def draw(self, screen):
        pass