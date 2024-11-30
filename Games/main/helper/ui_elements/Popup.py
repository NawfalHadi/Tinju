import pygame

pygame.font.init()

class Popup:
    def __init__(self, title, x, y, width, height, color) -> None:
        self.title = title
        self.rect = pygame.Rect(x,y, width, height)
        self.color = color

    def draw(self, screen):
        font = pygame.font.Font
        
        transparent_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)  # Use SRCALPHA for alpha channel
        transparent_surface.fill(self.color)  # Fill with the RGBA color
        
        # Blit the transparent surface
        screen.blit(transparent_surface, (self.rect.x, self.rect.y))