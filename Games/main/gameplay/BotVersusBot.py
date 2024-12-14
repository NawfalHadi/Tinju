import numpy as np
import pickle
import random
import time

from collections import defaultdict

import pygame
import threading

from main.helper.constants import *
from main.helper.Actions import *
from main.assets.ImagePath import *
from main.helper.ui_elements.Attribute import * 


screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Bot Versus Bot')

class BotVersusBot:
    def __init__(self, player_bot_path, opponent_bot_path):
        self.screen = screen
        self.image_bg = pygame.image.load(PLACE_RING)
        self.isRunning = True

        self.draw_interface()

        self.initialize_attribute_opponents_bot(opponent_bot_path)
        self.initialize_attribute_players_bot(player_bot_path)

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
        self.isLoading = False
        self.sock = None

        self.start_game()

    def start_game(self):
        threading.Thread(target=self.generate_player_bot_actions, daemon=True).start()
        threading.Thread(target=self.genereate_opp_bot_actions, daemon=True).start()

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
    
    def draw_interface(self):
        self.player_hp_bg = Attributes(SCREEN_MARGIN, SCREEN_MARGIN, 400, 40, GRAY)
        self.player_stamina_bg = Attributes(SCREEN_MARGIN,
                                         self.player_hp_bg.rect.bottom, 350, 20, GRAY)

        self.bot_hp_bg = Attributes(self.screen.get_width() - (400 + SCREEN_MARGIN), SCREEN_MARGIN, 400, 40, GRAY) 
        self.bot_stamina_bg = Attributes(self.bot_hp_bg.rect.left + 50, self.bot_hp_bg.rect.bottom,
                                      350, 20, GRAY)

    def update_interface(self):
        bot_hp = ((self.bot_hp) / 100 * 400)
        bot_stm = ((self.bot_stamina) / 100 * 350)
        

        player_hp = ((self.player_hp) / 100 * 400)
        player_stm = ((self.player_stamina) / 100 * 350)

        Attributes(self.screen.get_width() - (bot_hp + SCREEN_MARGIN), SCREEN_MARGIN, bot_hp, 40, RED).draw(screen, corner_bottomLeft = 15)
        Attributes(self.bot_hp_bg.rect.left + 50, self.bot_hp_bg.rect.bottom, bot_stm, 20, BLUE).draw(screen, corner_bottomLeft = 15)

        Attributes(SCREEN_MARGIN, SCREEN_MARGIN, player_hp, 40, RED).draw(screen, corner_bottomRight = 15)
        Attributes(SCREEN_MARGIN, self.player_hp_bg.rect.bottom, player_stm, 20, BLUE).draw(screen, corner_bottomRight = 15)

    def load_bots(self, filename):
        with open(filename, "rb") as f:
            return defaultdict(lambda: np.zeros(17), pickle.load(f)), True

    def choose_action(self, state, q):
        if random.uniform(0, 1) < EPSILON:
            print("Random")
            return random.choice(range(17))  # Explore
        else:
            print("Q_Check")
            return np.argmax(q[state])
        
    def genereate_opp_bot_actions(self):
        while self.isRunning and self.isBotQLoaded:
            state = (self.bot_hp, self.player_hp, self.bot_stamina, self.player_stamina, ACTIONS.index(self.player_action))
            try:
                action_state = self.choose_action(state, self.bot_Q)
                self.bot_action = ACTIONS[action_state]

                print("Bot :", self.bot_action)
            except Exception as e:
                self.bot_action = ACTIONS[0]
                
            time.sleep(0.2)

    def generate_player_bot_actions(self):
        while self.isRunning and self.isPlayerQLoaded:
            state = (self.player_hp, self.bot_hp, self.player_stamina, self.bot_stamina, ACTIONS.index(self.bot_action))

            try:
                action_state = self.choose_action(state, self.player_Q)
                self.player_action = ACTIONS[action_state]
                print("Player :", self.player_action)
            except Exception as e:
                # print("Except P:", e)
                self.player_action = ACTIONS[0]

            time.sleep(0.2)
    
    def calculation_opp_bot_actions(self):
        if self.bot_stamina >= ACTIONS_EFFECTS[self.bot_action]["stamina_cost"]:
            self.bot_stamina -= ACTIONS_EFFECTS[self.bot_action]["stamina_cost"]
            self.bot_hp += ACTIONS_EFFECTS[self.bot_action]["health_recovery"]
            self.bot_stamina += ACTIONS_EFFECTS[self.bot_action]["stamina_recovery"]

            if ACTIONS_EFFECTS[self.bot_action]["hit_damage"][self.player_action] > 10:
                self.bot_offenseRate += 1
            elif ACTIONS_EFFECTS[self.bot_action]["hit_damage"][self.player_action] < 10 and ACTIONS_EFFECTS[self.bot_action]["hit_damage"][self.player_action] > 0:
                self.bot_defenseRate += 1 
            
            # Player
            self.player_hp -= ACTIONS_EFFECTS[self.bot_action]["hit_damage"][self.player_action]

        # self.bot_img = pygame.image.load(random.choice(ACTIONS_IMAGE[self.bot_action]))

        self.bot_hp = max(0, min(self.bot_maxhp, self.bot_hp))
        self.bot_stamina = max(0, min(MAX_STM, self.bot_stamina))
        self.player_hp = max(0, min(self.player_maxHp, self.player_hp))
        self.player_stamina = max(0, min(MAX_STM, self.player_stamina))

    def calculation_player_bot_actions(self):
        if self.player_stamina >= ACTIONS_EFFECTS[self.player_action]["stamina_cost"]:
            # Player
            self.player_stamina -= ACTIONS_EFFECTS[self.player_action]["stamina_cost"]
            self.player_hp += ACTIONS_EFFECTS[self.player_action]["health_recovery"]
            self.player_stamina += ACTIONS_EFFECTS[self.player_action]["stamina_recovery"]

            if ACTIONS_EFFECTS[self.player_action]["hit_damage"][self.bot_action] > 10:
                self.player_offenseRate += 1
            elif ACTIONS_EFFECTS[self.player_action]["hit_damage"][self.bot_action] < 10:
                self.player_defenseRate += 1

            # Bot
            self.bot_hp -= ACTIONS_EFFECTS[self.player_action]["hit_damage"][self.bot_action]

        self.bot_hp = max(0, min(self.bot_maxhp, self.bot_hp))
        self.bot_stamina = max(0, min(MAX_STM, self.bot_stamina))
        self.player_hp = max(0, min(self.player_maxHp, self.player_hp))
        self.player_stamina = max(0, min(MAX_STM, self.player_stamina))

        # Open 2 Threads Your Bot & Opponents Bot
        pass

    def run(self):
        while self.isRunning:
            self.screen.fill(WHITE)
            self.screen.blit(self.image_bg, (0, 0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.isRunning = False

            if not self.isLoading and not self.isTimerFinish and (self.isPlayerQLoaded and self.isBotQLoaded):
                self.player_hp_bg.draw(screen, corner_bottomRight=15)
                self.player_stamina_bg.draw(screen, corner_bottomRight=15)
                
                self.bot_hp_bg.draw(screen, corner_bottomLeft=15)
                self.bot_stamina_bg.draw(screen, corner_bottomLeft=15)
                
                self.update_interface()
                self.calculation_opp_bot_actions()
                self.calculation_player_bot_actions()

            if self.isTimerFinish:
                pass
            
            pygame.display.update()

            