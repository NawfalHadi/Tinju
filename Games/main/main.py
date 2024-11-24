import pygame
import sys

from helper.ui_elements.button import *

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Main Menu Example')

class MainMenu:
    def __init__(self):
        self.create_button()
        self.running = True

    def create_button(self):
        self.start_button = Button('Start Game', SCREEN_MARGIN, SCREEN_MARGIN,
                                    314, 400, RED, GRAY, self.start_game)
        self.training_button = Button('Tutorial', self.start_button.rect.right + SCREEN_MARGIN,
                                      SCREEN_MARGIN, 314, 250, RED, GRAY, self.start_game)
        self.coach_button = Button('As A Coach', self.training_button.rect.right + SCREEN_MARGIN,
                                   SCREEN_MARGIN, 314, 350, GREEN, GRAY, self.start_game)
        self.padwork_button = 0
        self.exit_button = 0

    def start_game(self):
        pass

    def run(self):
        while self.running:
            screen.fill(WHITE)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            # Rest Code
            
            self.start_button.draw(screen)
            self.training_button.draw(screen)
            self.coach_button.draw(screen)
            

            pygame.display.flip()

    def run_menu(self):
        while self.running:
            screen.fill(WHITE)

# Run the game
if __name__ == "__main__":
    main_menu = MainMenu()
    main_menu.run()
    pygame.quit()
    sys.exit()
