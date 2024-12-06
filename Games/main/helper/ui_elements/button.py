import pygame

from helper.constants import *

pygame.font.init()

class Button:
    def __init__(self, text, x, y, width, height, color, hover_color, action=None) -> None:
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hover_color = hover_color
        self.action = action

    def draw(self, screen):
        font = pygame.font.Font(None, FONT_SIZE)

        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, self.hover_color, self.rect)
            text_surface = font.render(self.text, True, FOREGROUND)
        else:
            pygame.draw.rect(screen, self.color, self.rect)
            text_surface = font.render(self.text, True, WHITE)

        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                if self.action:
                    self.action()
