import pygame

from main.helper.constants import *
from main.helper.ui_elements.button import Button

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Choose Bot Difficulty")

class ChooseBotPage:
    def __init__(self):
        self.screen = screen
        self.isRunning = True
    
    def draw_interface(self):
        self.offensiveBot_card, self.offensive_button = self.create_card("Frequently\nOffensive", 20, 20, self.choose_offensive_diff)
        self.defensiveBot_card, self.defensive_button = self.create_card("Frequently\nDefensive", self.offensiveBot_card.right + 20, self.offensiveBot_card.top, self.choose_defensive_diff)
        self.balancedBot_card, self.balanced_button = self.create_card("Balanced\nTraining", self.defensiveBot_card.right + 20, self.defensiveBot_card.top, self.choose_balance_diff)    
    

    def create_card(self, text, rightOf, bottomOf, event):
        rect = pygame.Rect(rightOf, bottomOf, 315, 536)
        pygame.draw.rect(self.screen, FOREGROUND, rect)

        font = pygame.font.Font(None, 36)
        lines = text.split('\n')
        
        line_height = font.size("Tg")[1]  # Approximate height of one line
        total_text_height = line_height * len(lines)
        
        start_y = rect.top + (rect.height - total_text_height) // 2

        for i, line in enumerate(lines):
            text_surface = font.render(line, True, WHITE)
            text_rect = text_surface.get_rect(center=(rect.centerx, start_y + i * line_height))
            
            self.screen.blit(text_surface, text_rect)

        button = Button("Fight It!", rect.left + 20, rect.bottom - 90,
                        275, 70, FOREGROUND_2, WHITE, event)
        
        button.draw(self.screen)

        return rect, button        


    def choose_offensive_diff(self):
        model = "main/bot/bot_offensive.pkl"
        
        from main.gameplay.VersusBotPage import VersusBotPage
        VersusBotPage(model).run()
        
    def choose_defensive_diff(self):
        model = "main/bot/bot_defensive.pkl"

        from main.gameplay.VersusBotPage import VersusBotPage
        VersusBotPage(model).run()

    def choose_balance_diff(self):
        model = "main/bot/bot_balanced.pkl"

        from main.gameplay.VersusBotPage import VersusBotPage
        VersusBotPage(model).run()

    def run(self):
        while self.isRunning:
            self.screen.fill(BACKGROUND)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.isRunning = False

                self.offensive_button.is_clicked(event)
                self.defensive_button.is_clicked(event)
                self.balanced_button.is_clicked(event)

            self.draw_interface()

            pygame.display.update()
            pygame.time.Clock().tick(60)