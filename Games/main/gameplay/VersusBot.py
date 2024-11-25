import os
import numpy as np
import random

import pygame
import threading
import pickle


from collections import defaultdict

from main.helper.constants import *
from main.helper.ui_elements.Attribute import *

model_path = "main/bot/q_table.pkl"

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Main Menu Example')

class VersusBot:
    def __init__(self):
        self.screen = screen
        self.draw_interface()
        self.loading = True
        self.running = True

        "=== BOT ATTRIBUTES ==="
        self.load_bots(model_path)
        self.bot_action = ACTIONS[0]
        self.bot_hp = 100
        self.bot_stamina = 100

        "=== PLAYER ATTRIBUTES ==="
        self.player_action = ACTIONS[0]
        self.player_hp = 100
        self.player_stamina = 100

        self.start_games()

    
    def start_games(self):
        "The thread for generating action from bot"
        threading.Thread(target=self.generate_bot_actions, daemon=True).start()

    def load_bots(self, filename):
        with open(filename, "rb") as f:
            self.Q = defaultdict(lambda: np.zeros(3), pickle.load(f))

    def choose_action(self, state):
        """Chooses an action based on epsilon-greedy policy."""
        if random.uniform(0, 1) < EPSILON:
            return random.choice(range(3))  # Explore
        else:
            return np.argmax(self.Q[state])  # Exploit

    def generate_bot_actions(self):
        while self.running:
            state = (self.bot_hp, self.player_hp, 
                    self.bot_stamina, self.player_stamina,
                    ACTIONS.index(self.player_action))
            
            action_state = self.choose_action(state)
            self.bot_action = ACTIONS[action_state]
            
            print(self.bot_action)


    def start_server(self):
        pass

    def draw_interface(self):
        self.player_hp_ui = Attributes(SCREEN_MARGIN, SCREEN_MARGIN, 400, 40, RED)
        self.player_stamina_ui = Attributes(SCREEN_MARGIN,
                                         self.player_hp_ui.rect.bottom, 350, 20, BLUE)

        self.bot_hp_ui = Attributes(self.screen.get_width() - (400 + SCREEN_MARGIN), SCREEN_MARGIN, 400, 40, RED) 
        self.bot_stamina_ui = Attributes(self.bot_hp_ui.rect.left + 50, self.bot_hp_ui.rect.bottom,
                                      350, 20, BLUE)

    def start_timer(self):
        text = "3:00"
        font = pygame.font.Font(None, 60)
        self.timer = screen.blit(font.render(text, True, BLACK),
                    (self.player_hp_ui.rect.right + 55, SCREEN_MARGIN + 15))
        
    def run(self):
        while self.running:
            self.screen.fill(WHITE)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            
            self.start_timer()
            
            self.player_hp_ui.draw(screen, corner_bottomRight=15)
            self.player_stamina_ui.draw(screen, corner_bottomRight=15)
            self.bot_hp_ui.draw(screen, corner_bottomLeft=15)
            self.bot_stamina_ui.draw(screen, corner_bottomLeft=15)

            pygame.display.update()


                    