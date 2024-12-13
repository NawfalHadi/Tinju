import numpy as np
import pickle

from collections import defaultdict

import pygame

from main.helper.constants import *
from main.assets.ImagePath import *


screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Bot Versus Bot')

class BotVersusBot:
    def __init__(self):
        self.screen = screen
        self.image_bg = pygame.image.load(PLACE_RING)
        self.isRunning = True

        self.draw_interface()

        self.initialize_attribute_opponents_bot()
        self.initialize_attribute_players_bot()

        "=== JUDGES SYSTEM ==="
        self.judges_hp = [[10, 10], [10, 10], [10, 10]]
        self.judges_def = [[10, 10], [10, 10], [10, 10]]
        self.judges_off = [[10, 10], [10, 10], [10, 10]]

        "=== GAME SYSTEM ==="
        self.isTimerFinish = False
        self.scoring_round = 1
        self.current_rounds = 1
        self.total_second = 3 * 60

        "=== SOCKET ==="
        self.isLoading = True
        self.sock = None

        self.start_game()

    def initialize_attribute_opponents_bot(self, model_path):
        self.bot_Q, self.isBotQLoaded= self.load_bots(model_path)

        self.bot_action = ACTIONS[0]
        self.bot_img = pygame.image.load(ACTIONS_IMAGE["Idle"][0])

        self.bot_maxhp = 100
        self.bot_hp = self.bot_maxhp

        self.bot_maxStm = 100
        self.bot_stamina = self.bot_maxStm

        self.bot_offenseRate = 0
        self.bot_defenseRate = 0

    def initialize_attribute_players_bot(self, model_path):
        self.player_Q, self.isPlayerQLoaded= self.load_bots(model_path)
        
        self.player_action = ACTIONS[0]
        self.player_img = None

        self.player_maxHp = 100
        self.player_hp = self.player_maxHp

        self.player_maxStm = 100
        self.player_stamina = self.player_maxStm

        self.player_offenseRate = 0
        self.player_defenseRate = 0
    
    def load_bots(self, filename):
        with open(filename, "rb") as f:
            return defaultdict(lambda: np.zeros(3), pickle.load(f)), True

    def start_game(self):
        # Open 2 Threads Your Bot & Opponents Bot
        pass

    def run(self):
        while self.isRunning:
            self.screen.fill(WHITE)
            self.screen.blit(self.image_bg, (0, 0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.isRunning = False

            