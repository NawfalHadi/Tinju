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
                                      SCREEN_MARGIN, 314, 258, RED, GRAY, self.start_game)
        self.coach_button = Button('As A Coach', self.training_button.rect.right + SCREEN_MARGIN,
                                   SCREEN_MARGIN, 314, 400, GREEN, GRAY, self.start_game)
        self.record_button = Button('1 / 1 / 0', SCREEN_MARGIN, self.start_button.rect.bottom + SCREEN_MARGIN,
                                   314, 116, BLUE, GRAY, self.start_game)
        self.padwork_button = Button("Padwork", self.record_button.rect.right + SCREEN_MARGIN,
                                     self.training_button.rect.bottom + SCREEN_MARGIN, 314, 258, GREEN, GRAY, self.start_game)
        self.resoulution_button = Button("1024 x 576", self.padwork_button.rect.right + SCREEN_MARGIN,
                                         self.coach_button.rect.bottom + SCREEN_MARGIN, 147, 116, BLUE, GRAY, self.start_game)
        self.exit_button = Button("Exit", self.resoulution_button.rect.right + SCREEN_MARGIN,
                                  self.coach_button.rect.bottom + SCREEN_MARGIN, 147, 116, RED, GRAY, self.start_game)

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
            self.record_button.draw(screen)
            self.padwork_button.draw(screen)
            
            self.resoulution_button.draw(screen)
            self.exit_button.draw(screen)
            

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
