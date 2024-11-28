import pygame

from main.helper.constants import *

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Padworks')

class TutorialPage:
    def __init__(self) -> None:
        self.screen = screen
        self.running = True

        "=== CONTROLLER ==="
        self.controller_process = None
        self.player_action = ACTIONS[0]

        "=== STEPS ==="
        self.tutorial_menu = True
        self.tutorial_offense = False
        self.tutorial_guard = False
        self.tutroial_duck = False

    def setup(self):
        # Starting the thread of controller

        # Socket

        # thread of data receive
        # thread of controller
        pass

    def receive_data(self):
        pass

    def start_controller(self):
        pass

    def step_menu(self):
        pass

    def step_offense(self):
        pass

    def step_guard(self):
        pass

    def step_duck(self):
        pass

    def run(self):
        while self.running:
            self.screen.fill(WHITE)

            for event in pygame.event.get():
                if event.type == pygame.QUIT():
                    self.running = False

            pygame.display.update()
            pygame.time.Clock(60)
                    

