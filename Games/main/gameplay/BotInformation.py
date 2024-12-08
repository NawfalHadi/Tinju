import pygame

from main.helper.constants import *
from main.helper.ui_elements.button import Button

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Bot Information')  

class BotInformation:
    def __init__(self):
        self.screen = screen
        self.isRunning = True

    def draw_interface(self):
        self.bot_information, self.bot_training = self.create_card("Yours Bot", 20, 20)

    def create_card(self, text, rightOf, bottomOf):
        rect = pygame.Rect(rightOf, bottomOf, 315, 536)
        pygame.draw.rect(self.screen, FOREGROUND, rect)

        rect_2 = pygame.Rect(rect.left + 20, rect.top + 20, 275, 275)
        pygame.draw.rect(self.screen, FOREGROUND_2, rect_2)

        font = pygame.font.Font(None, 36)
        lines = text.split('\n')
        
        line_height = font.size("Tg")[1]  # Approximate height of one line
        total_text_height = line_height * len(lines)
        
        start_y = rect_2.top + (rect_2.height - total_text_height) // 2

        for i, line in enumerate(lines):
            text_surface = font.render(line, True, WHITE)
            text_rect = text_surface.get_rect(center=(rect_2.centerx, start_y + i * line_height))
            
            self.screen.blit(text_surface, text_rect)

        button = Button("Training : 1x", rect.left + 20, rect.bottom - 90,
                        275, 70, FOREGROUND_2, WHITE, font=32)
        
        button.draw(self.screen)

        return rect, button

    def run(self):
        while self.isRunning:
            self.screen.fill(BACKGROUND) 

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.isRunning = False

            self.draw_interface()

            pygame.display.update()
            pygame.time.Clock().tick(60)

