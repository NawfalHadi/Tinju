import random
import os
import logging
import numpy as np
import time

import threading
import pygame
import pickle

from collections import defaultdict

ACTIONS = [
    "Idle", "Guard", "Jab", "Low_Jab", "Straight", "Low_Straight",
    "Left_Hook", "Right_Hook", "Left_BodyHook", "Right_BodyHook",
    "Left_Uppercut", "Right_Uppercut", "Slip_Left", "Slip_Right", 
    "Guard_LeftBody", "Guard_RightBody", "Duck"
]

ACTIONS_EFFECTS = {
    "Idle": {
        "stamina_cost": 0,
        "health_recovery": 0.5,
        "stamina_recovery": 10,
        "hit_damage": {
            "Idle": 0, "Jab": 0, "Low_Jab": 0, "Straight": 0, "Low_Straight": 0, 
            "Left_Hook": 0, "Left_BodyHook": 0, "Right_Hook": 0, "Right_BodyHook": 0, 
            "Left_Uppercut": 0, "Right_Uppercut": 0, "Guard": 0, "Slip_Left": 0, 
            "Slip_Right": 0, "Duck":0, "Guard_LeftBody": 0, "Guard_RightBody": 0

        },
        "point_training": {
            "Idle": 20, "Jab": -10, "Low_Jab": -12, "Straight": -10, "Low_Straight": -12,
            "Left_Hook": -15, "Left_BodyHook": -15, "Right_Hook": -15, "Right_BodyHook": -15,
            "Left_Uppercut": 20, "Right_Uppercut": -20, "Guard": 20, "Slip_Left": 20,
            "Slip_Right": 20, "Duck": 30, "Guard_LeftBody": 30, "Guard_RightBody": 30
        },
    },
    "Jab": {
        "stamina_cost": 20,
        "health_recovery": 0,
        "stamina_recovery": 0,
        "hit_damage": {
            "Idle": 5, "Jab": 8, "Low_Jab": 3, "Straight": 0, "Low_Straight": 3, 
            "Left_Hook": 3, "Left_BodyHook": 0, "Right_Hook": 5, "Right_BodyHook": 0, 
            "Left_Uppercut": 7, "Right_Uppercut": 8, "Guard": 1, "Slip_Left": 3, 
            "Slip_Right": 0, "Duck":0, "Guard_LeftBody": 5, "Guard_RightBody": 1
        },
        "point_training": {
            "Idle": 10, "Jab": 5, "Low_Jab": 8, "Straight": 5, "Low_Straight": 8,
            "Left_Hook": 5, "Left_BodyHook": -10, "Right_Hook": 5, "Right_BodyHook": -10,
            "Left_Uppercut": 3, "Right_Uppercut": 3, "Guard": 5, "Slip_Left": -5,
            "Slip_Right": 3, "Duck": -3, "Guard_LeftBody": 2, "Guard_RightBody": 10
        },
    },
    "Low_Jab": {
        "stamina_cost": 25,
        "health_recovery": 0,
        "stamina_recovery": 0,
        "hit_damage": {
            "Idle": 4, "Jab": 8, "Low_Jab": 5, "Straight": 7, "Low_Straight": 4, 
            "Left_Hook": 5, "Left_BodyHook": 8, "Right_Hook": 5, "Right_BodyHook": 8, 
            "Left_Uppercut": 3, "Right_Uppercut": 3, "Guard": 5, "Slip_Left": 3, 
            "Slip_Right": 1, "Duck":5, "Guard_LeftBody": 1, "Guard_RightBody": 5
        },
        "point_training": {
            "Idle": 5, "Jab": 15, "Low_Jab": 15, "Straight": 5, "Low_Straight": 15,
            "Left_Hook": 5, "Left_BodyHook": -15, "Right_Hook": 5, "Right_BodyHook": -15,
            "Left_Uppercut": 15, "Right_Uppercut": 15, "Guard": 15, "Slip_Left": 5,
            "Slip_Right": 10, "Duck": 15, "Guard_LeftBody": 20, "Guard_RightBody": 20
        },
    },
    "Straight": {
        "stamina_cost": 30,
        "health_recovery": 0,
        "stamina_recovery": 0,
        "hit_damage": {
            "Idle": 7, "Jab": 10, "Low_Jab": 0, "Straight": 8, "Low_Straight": 0, 
            "Left_Hook": 5, "Left_BodyHook": 0, "Right_Hook": 5, "Right_BodyHook": 0, 
            "Left_Uppercut": 10, "Right_Uppercut": 10, "Guard": 3, "Slip_Left": 0, 
            "Slip_Right": 3, "Duck":0, "Guard_LeftBody": 3, "Guard_RightBody": 10
        },
        "point_training": {
            "Idle": 10, "Jab": -10, "Low_Jab": -10, "Straight": -15, "Low_Straight": 5,
            "Left_Hook": -15, "Left_BodyHook": 5, "Right_Hook": -15, "Right_BodyHook": 5,
            "Left_Uppercut": 10, "Right_Uppercut": 10, "Guard": 8, "Slip_Left": 5,
            "Slip_Right": -5, "Duck": -10, "Guard_LeftBody": 10, "Guard_RightBody": 2
        },
    },
    "Low_Straight": {
        "stamina_cost": 35,
        "health_recovery": 0,
        "stamina_recovery": 0,
        "hit_damage": {
            "Idle": 6, "Jab": 10, "Low_Jab": 10, "Straight": 10, "Low_Straight": 10, 
            "Left_Hook": 10, "Left_BodyHook": 6, "Right_Hook": 8, "Right_BodyHook": 6, 
            "Left_Uppercut": 8, "Right_Uppercut": 8, "Guard": 7, "Slip_Left": 0, 
            "Slip_Right": 5, "Duck":0, "Guard_LeftBody": 7, "Guard_RightBody": 3
        },
        "point_training": {
            "Idle": 5, "Jab": 10, "Low_Jab": 10, "Straight": 15, "Low_Straight": 15,
            "Left_Hook": 15, "Left_BodyHook": -5, "Right_Hook": 10, "Right_BodyHook": -15,
            "Left_Uppercut": 10, "Right_Uppercut": 20, "Guard": 25, "Slip_Left": 15,
            "Slip_Right": -5, "Duck": 15, "Guard_LeftBody": 20, "Guard_RightBody": 20
        },
    },
    "Left_Hook": {
        "stamina_cost": 30,
        "health_recovery": 0,
        "stamina_recovery": 0,
        "hit_damage": {
            "Idle": 8, "Jab": 12, "Low_Jab": 0, "Straight": 10, "Low_Straight": 0, 
            "Left_Hook": 7, "Left_BodyHook": 0, "Right_Hook": 7, "Right_BodyHook": 0, 
            "Left_Uppercut": 10, "Right_Uppercut": 10, "Guard": 5, "Slip_Left": 5, 
            "Slip_Right": 5, "Duck":0, "Guard_LeftBody": 3, "Guard_RightBody": 8
        },
        "point_training": {
            "Idle": 15, "Jab": 5, "Low_Jab": 15, "Straight": 10, "Low_Straight": 15,
            "Left_Hook": -5, "Left_BodyHook": 5, "Right_Hook": -15, "Right_BodyHook": 5,
            "Left_Uppercut": 20, "Right_Uppercut": 15, "Guard": 10, "Slip_Left": 2,
            "Slip_Right": -5, "Duck": -10, "Guard_LeftBody": 5, "Guard_RightBody": 5
        },
    },
    "Left_BodyHook":{
        "stamina_cost": 40,
        "health_recovery": 0,
        "stamina_recovery": 0,
        "hit_damage": {
            "Idle": 7, "Jab": 13, "Low_Jab": 15, "Straight": 15, "Low_Straight": 10, 
            "Left_Hook": 7, "Left_BodyHook": 15, "Right_Hook": 10, "Right_BodyHook": 15, 
            "Left_Uppercut": 15, "Right_Uppercut": 10, "Guard": 10, "Slip_Left": 10, 
            "Slip_Right": 3, "Duck":0, "Guard_LeftBody": 10, "Guard_RightBody": 7
        },
        "point_training": {
            "Idle": 5, "Jab": 15, "Low_Jab": 5, "Straight": -10, "Low_Straight": -15,
            "Left_Hook": 5, "Left_BodyHook": 15, "Right_Hook": -10, "Right_BodyHook": 5,
            "Left_Uppercut": 10, "Right_Uppercut": -15, "Guard": 5, "Slip_Left": 10,
            "Slip_Right": 2, "Duck": -5, "Guard_LeftBody": 20, "Guard_RightBody": 5
        },
    },
    "Right_Hook": {
        "stamina_cost": 40,
        "health_recovery": 0,
        "stamina_recovery": 0,
        "hit_damage": {
            "Idle": 10, "Jab": 15, "Low_Jab": 0, "Straight": 15, "Low_Straight": 0, 
            "Left_Hook": 15, "Left_BodyHook": 15, "Right_Hook": 7, "Right_BodyHook": 0, 
            "Left_Uppercut": 10, "Right_Uppercut": 7, "Guard": 5, "Slip_Left": 5, 
            "Slip_Right": 3, "Duck":0, "Guard_LeftBody": 10, "Guard_RightBody": 5
        },
        "point_training": {
            "Idle": 5, "Jab": 5, "Low_Jab": 5, "Straight": -15, "Low_Straight": 5,
            "Left_Hook": -15, "Left_BodyHook": -10, "Right_Hook": 10, "Right_BodyHook": -20,
            "Left_Uppercut": 15, "Right_Uppercut": 5, "Guard": 10, "Slip_Left": 3,
            "Slip_Right": -5, "Duck": 5, "Guard_LeftBody": 2, "Guard_RightBody": 10
        },
    },
    "Right_BodyHook" : {
        "stamina_cost": 45,
        "health_recovery": 0,
        "stamina_recovery": 0,
        "hit_damage": {
            "Idle": 9, "Jab": 17, "Low_Jab": 15, "Straight": 20, "Low_Straight": 15, 
            "Left_Hook": 15, "Left_BodyHook": 10, "Right_Hook": 20, "Right_BodyHook": 15, 
            "Left_Uppercut": 15, "Right_Uppercut": 15, "Guard": 10, "Slip_Left": 7, 
            "Slip_Right": 10, "Duck":0, "Guard_LeftBody": 5, "Guard_RightBody": 10
        },
        "point_training": {
            "Idle": 5, "Jab": 10, "Low_Jab": 5, "Straight": -10, "Low_Straight": 5,
            "Left_Hook": -10, "Left_BodyHook": 10, "Right_Hook": 5, "Right_BodyHook": 20,
            "Left_Uppercut": -15, "Right_Uppercut": 15, "Guard": 5, "Slip_Left": 3,
            "Slip_Right": -10, "Duck": 10, "Guard_LeftBody": 5, "Guard_RightBody": 15
        },
    },
    "Left_Uppercut": {
        "stamina_cost": 50,
        "health_recovery": 0,
        "stamina_recovery": 0,
        "hit_damage": {
            "Idle": 20, "Jab": 18, "Low_Jab": 0, "Straight": 15, "Low_Straight": 0, 
            "Left_Hook": 15, "Left_BodyHook": 0, "Right_Hook": 15, "Right_BodyHook": 0, 
            "Left_Uppercut": 15, "Right_Uppercut": 15, "Guard": 8, "Slip_Left": 0, 
            "Slip_Right": 0, "Duck":0, "Guard_LeftBody": 5, "Guard_RightBody": 5
        },
        "point_training": {
            "Idle": 30, "Jab": 15, "Low_Jab": 15, "Straight": 10, "Low_Straight": 10,
            "Left_Hook": 15, "Left_BodyHook": 15, "Right_Hook": 10, "Right_BodyHook": -5,
            "Left_Uppercut": 25, "Right_Uppercut": 10, "Guard": 3, "Slip_Left": -5,
            "Slip_Right": -5, "Duck": -5, "Guard_LeftBody": 3, "Guard_RightBody": -5
        },
    },
    "Right_Uppercut":{
        "stamina_cost": 50,
        "health_recovery": 0,
        "stamina_recovery": 0,
        "hit_damage": {
            "Idle": 30, "Jab": 25, "Low_Jab": 0, "Straight": 25, "Low_Straight": 0, 
            "Left_Hook": 25, "Left_BodyHook": 0, "Right_Hook": 20, "Right_BodyHook": 0, 
            "Left_Uppercut": 20, "Right_Uppercut": 20, "Guard": 10, "Slip_Left": 0, 
            "Slip_Right": 0, "Duck":0, "Guard_LeftBody": 10, "Guard_RightBody": 10
        },
        "point_training": {
            "Idle": 30, "Jab": 10, "Low_Jab": 15, "Straight": 5, "Low_Straight": -5,
            "Left_Hook": 15, "Left_BodyHook": 10, "Right_Hook": 10, "Right_BodyHook": 5,
            "Left_Uppercut": 15, "Right_Uppercut": 25, "Guard": 3, "Slip_Left": -5,
            "Slip_Right": -5, "Duck": -5, "Guard_LeftBody": 3, "Guard_RightBody": 15
        },        
    },
    "Guard" : {
        "stamina_cost": 0,
        "health_recovery": 0.1,
        "stamina_recovery": 5,
        "hit_damage": {
            "Idle": 0, "Jab": 0, "Low_Jab": 0, "Straight": 0, "Low_Straight": 0, 
            "Left_Hook": 0, "Left_BodyHook": 0, "Right_Hook": 0, "Right_BodyHook": 0, 
            "Left_Uppercut": 0, "Right_Uppercut": 0, "Guard": 0, "Slip_Left": 0, 
            "Slip_Right": 0, "Duck":0, "Guard_LeftBody": 0, "Guard_RightBody": 0
        },
        "point_training": {
            "Idle": 15, "Jab": 10, "Low_Jab": -10, "Straight": 10, "Low_Straight": -10,
            "Left_Hook": 5, "Left_BodyHook": -15, "Right_Hook": 5, "Right_BodyHook": -15,
            "Left_Uppercut": 2, "Right_Uppercut": 2, "Guard": 20, "Slip_Left": 25,
            "Slip_Right": 25, "Duck": 30, "Guard_LeftBody": 30, "Guard_RightBody": 30
        },
    },
    "Slip_Left" : {
        "stamina_cost": 5,
        "health_recovery": 0,
        "stamina_recovery": 0,
        "hit_damage": {
            "Idle": 0, "Jab": 0, "Low_Jab": 0, "Straight": 0, "Low_Straight": 0, 
            "Left_Hook": 0, "Left_BodyHook": 0, "Right_Hook": 0, "Right_BodyHook": 0, 
            "Left_Uppercut": 0, "Right_Uppercut": 0, "Guard": 0, "Slip_Left": 0, 
            "Slip_Right": 0, "Duck":0, "Guard_LeftBody": 0, "Guard_RightBody": 0
        },
        "point_training": {
            "Idle": 5, "Jab": 15, "Low_Jab": 5, "Straight": -5, "Low_Straight": 5,
            "Left_Hook": 5, "Left_BodyHook": -15, "Right_Hook": -3, "Right_BodyHook": -10,
            "Left_Uppercut": 10, "Right_Uppercut": 10, "Guard": 5, "Slip_Left": 10,
            "Slip_Right": 10, "Duck": 10, "Guard_LeftBody": 10, "Guard_RightBody": 10
        },
    },
    "Slip_Right" : {
        "stamina_cost": 5,
        "health_recovery": 0,
        "stamina_recovery": 0,
        "hit_damage": {
            "Idle": 0, "Jab": 0, "Low_Jab": 0, "Straight": 0, "Low_Straight": 0, 
            "Left_Hook": 0, "Left_BodyHook": 0, "Right_Hook": 0, "Right_BodyHook": 0, 
            "Left_Uppercut": 0, "Right_Uppercut": 0, "Guard": 0, "Slip_Left": 0, 
            "Slip_Right": 0, "Duck":0, "Guard_LeftBody": 0, "Guard_RightBody": 0
        },
        "point_training": {
            "Idle": 5, "Jab": 15, "Low_Jab": 5, "Straight": 5, "Low_Straight": 5,
            "Left_Hook": -5, "Left_BodyHook": -10, "Right_Hook": -3, "Right_BodyHook": -15,
            "Left_Uppercut": 10, "Right_Uppercut": 10, "Guard": 5, "Slip_Left": 10,
            "Slip_Right": 10, "Duck": 10, "Guard_LeftBody": 10, "Guard_RightBody": 10
        },
    },
    "Duck" : {
        "stamina_cost": 5,
        "health_recovery": 0,
        "stamina_recovery": 0,
        "hit_damage": {
            "Idle": 0, "Jab": 0, "Low_Jab": 0, "Straight": 0, "Low_Straight": 0, 
            "Left_Hook": 0, "Left_BodyHook": 0, "Right_Hook": 0, "Right_BodyHook": 0, 
            "Left_Uppercut": 0, "Right_Uppercut": 0, "Guard": 0, "Slip_Left": 0, 
            "Slip_Right": 0, "Duck":0, "Guard_LeftBody": 0, "Guard_RightBody": 0
        },
        "point_training": {
            "Idle": 5, "Jab": 15, "Low_Jab": -5, "Straight": 15, "Low_Straight": -5,
            "Left_Hook": 20, "Left_BodyHook": -10, "Right_Hook": 20, "Right_BodyHook": -10,
            "Left_Uppercut": 25, "Right_Uppercut": 25, "Guard": 5, "Slip_Left": 5,
            "Slip_Right": 5, "Duck": 3, "Guard_LeftBody": 3, "Guard_RightBody": 3
        },
    },
    "Guard_LeftBody" : {
        "stamina_cost": 5,
        "health_recovery": 0,
        "stamina_recovery": 0,
        "hit_damage": {
            "Idle": 0, "Jab": 0, "Low_Jab": 0, "Straight": 0, "Low_Straight": 0, 
            "Left_Hook": 0, "Left_BodyHook": 0, "Right_Hook": 0, "Right_BodyHook": 0, 
            "Left_Uppercut": 0, "Right_Uppercut": 0, "Guard": 0, "Slip_Left": 0, 
            "Slip_Right": 0, "Duck":0, "Guard_LeftBody": 0, "Guard_RightBody": 0
        },
        "point_training": {
            "Idle": 5, "Jab": 5, "Low_Jab": -5, "Straight": -10, "Low_Straight": 10,
            "Left_Hook": 10, "Left_BodyHook": -10, "Right_Hook": -15, "Right_BodyHook": 15,
            "Left_Uppercut": 3, "Right_Uppercut": 3, "Guard": 5, "Slip_Left": 5,
            "Slip_Right": 5, "Duck": 5, "Guard_LeftBody": 3, "Guard_RightBody": 3
        },
    },
    "Guard_RightBody" : {
        "stamina_cost": 5,
        "health_recovery": 0,
        "stamina_recovery": 0,
        "hit_damage": {
            "Idle": 0, "Jab": 0, "Low_Jab": 0, "Straight": 0, "Low_Straight": 0, 
            "Left_Hook": 0, "Left_BodyHook": 0, "Right_Hook": 0, "Right_BodyHook": 0, 
            "Left_Uppercut": 0, "Right_Uppercut": 0, "Guard": 0, "Slip_Left": 0, 
            "Slip_Right": 0, "Duck":0, "Guard_LeftBody": 0, "Guard_RightBody": 0
        },
        "point_training": {
            "Idle": 5, "Jab": -5, "Low_Jab": 5, "Straight": 5, "Low_Straight": -10,
            "Left_Hook": -10, "Left_BodyHook": 10, "Right_Hook": 15, "Right_BodyHook": -15,
            "Left_Uppercut": 3, "Right_Uppercut": 3, "Guard": 5, "Slip_Left": 5,
            "Slip_Right": 5, "Duck": 5, "Guard_LeftBody": 3, "Guard_RightBody": 3
        },
    },
      
}

width, height = 1024, 576
window = pygame.display.set_mode((width, height))
pygame.font.init()
pygame.display.set_caption("Bot Environment Training")
font = pygame.font.Font(None, 36)

# Q-learning parameters
alpha = 0.1  # Learning rate
gamma = 0.9  # Discount factor
epsilon = 0.1  # Exploration 

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)

class Environment:
    def __init__(self) -> None:
        self.screen = window
        self.isRunning = True
        
        self.bot_action = ACTIONS[0]
        self.bot_maxHp = 100
        self.bot_hp = self.bot_maxHp
        self.bot_maxStm = 100
        self.bot_stm = self.bot_maxStm
        self.bot_successOffense = 0
        self.bot_successDefense = 0
        
        self.player_action = ACTIONS[0]
        self.player_maxHp = 100
        self.player_hp = self.player_maxHp
        self.player_maxStm = 100
        self.player_stm = self.player_maxStm
        self.player_successOffense = 0
        self.player_successDefense = 0
        
        "=== TIMER ==="
        self.total_seconds = 3 * 1

        "=== TRAINING VARIABLE ==="
        self.Q = self.load_q_table()
        self.start_thread()

    def start_thread(self):
        threading.Thread(target=self.handle_user_actions, daemon=True).start()
        threading.Thread(target=self.generate_bot_action, daemon=True).start()

    def handle_key_pressed(self, keys):
    # Jab variations
        if keys[pygame.K_j]:
            if keys[pygame.K_DOWN]:
                self.player_action = "Low_Jab"
            else:
                self.player_action = "Jab"

        # Straight punch variations
        elif keys[pygame.K_s]:
            if keys[pygame.K_DOWN]:
                self.player_action = "Low_Straight"
            else:
                self.player_action = "Straight"

        # Hook variations
        elif keys[pygame.K_h]:
            if keys[pygame.K_LEFT]:
                if keys[pygame.K_DOWN]:
                    self.player_action = "Left_BodyHook"
                else:
                    self.player_action = "Left_Hook"
            elif keys[pygame.K_RIGHT]:
                if keys[pygame.K_DOWN]:
                    self.player_action = "Right_BodyHook"
                else:
                    self.player_action = "Right_Hook"

        # Uppercut variations
        elif keys[pygame.K_u]:
            if keys[pygame.K_LEFT]:
                self.player_action = "Left_Uppercut"
            elif keys[pygame.K_RIGHT]:
                self.player_action = "Right_Uppercut"

        # Guard variations
        elif keys[pygame.K_g]:
            if keys[pygame.K_DOWN]:
                self.player_action = "Guard_Body"
            else:
                self.player_action = "Guard"

        # Default to Idle if no specific action is pressed
        else:
            self.player_action = "Idle"
    
    def handle_user_actions(self):
        while self.player_hp > 0 and self.bot_hp > 0:
            # keys = pygame.key.get_pressed()
            # self.handle_key_pressed(keys)
            self.player_action = random.choice(ACTIONS)


            if self.player_stm >= ACTIONS_EFFECTS[self.player_action]["stamina_cost"]:
                # Player
                self.player_stm -= ACTIONS_EFFECTS[self.player_action]["stamina_cost"]
                self.player_hp += ACTIONS_EFFECTS[self.player_action]["health_recovery"]
                self.player_stm += ACTIONS_EFFECTS[self.player_action]["stamina_recovery"]

                if ACTIONS_EFFECTS[self.player_action]["hit_damage"][self.bot_action] > 10:
                    self.player_successOffense += 1
                elif ACTIONS_EFFECTS[self.player_action]["hit_damage"][self.bot_action] < 10:
                    self.player_successDefense += 1

                # Bot
                self.bot_hp -= ACTIONS_EFFECTS[self.player_action]["hit_damage"][self.bot_action]

            self.bot_hp = max(0, min(self.bot_maxHp, self.bot_hp))
            self.bot_stm = max(0, min(self.bot_maxStm, self.bot_stm))
            self.player_stm = max(0, min(self.player_maxHp, self.player_stm))
            self.player_hp = max(0, min(self.player_maxStm, self.player_hp))

            time.sleep(0.2)
    
    def get_state(self):

        return (
            self.bot_hp,
            self.player_hp,
            self.bot_stm,
            self.player_stm,
            ACTIONS.index(self.player_action),
        )
    
    def choose_action(self, state):
        if random.uniform(0, 1) < epsilon:
            return random.choice(range(len(ACTIONS) - 1))  # Explore
        else:
            return np.argmax(self.Q[state])  # Exploit

    def update_q_table(self, state, action, reward, next_state):
        """Updates the Q-table using the Q-learning formula."""

        best_next_action = np.argmax(self.Q[next_state])
        td_target = reward + gamma * self.Q[next_state][best_next_action]
        td_error = td_target - self.Q[state][action]
        self.Q[state][action] += alpha * td_error

    def save_q_table(self, q_table, filename="../model/q_table.pkl"):
        with open(filename, "wb") as f:
            pickle.dump(dict(q_table), f)

    def load_q_table(self, filename="../model/q_table.pkl"):
        try:
            with open(filename, "rb") as f:
                return defaultdict(lambda: np.zeros(17), pickle.load(f))
        except FileNotFoundError:
            return defaultdict(lambda: np.zeros(17))

    def generate_bot_action(self):
        while self.player_hp > 0 and self.bot_hp > 0:
            state = self.get_state()
            get_action = self.choose_action(state)
            
            self.bot_action = ACTIONS[get_action]
            self.handle_bot_action()

            next_state = self.get_state()
            reward = self.calculate_reward()
            self.update_q_table(state, get_action, reward, next_state)

            time.sleep(0.2) 

    def calculate_reward(self):
        point = 0

        if self.player_hp < self.bot_hp:
            point += 20
        elif self.player_hp > self.bot_hp:
            point -= 20

        if self.bot_stm < ACTIONS_EFFECTS[self.bot_action]["stamina_cost"]:
            point -= 20

        if ACTIONS_EFFECTS[self.bot_action]["hit_damage"][self.player_action] > 10:
            point += 10
        elif ACTIONS_EFFECTS[self.bot_action]["hit_damage"][self.player_action] < 10 and ACTIONS_EFFECTS[self.bot_action]["hit_damage"][self.player_action] > 0:
            # Success Guard
            point += 20

        action_reward = point + ACTIONS_EFFECTS[self.bot_action]["point_training"][self.player_action]

        return action_reward

    def handle_bot_action(self):
        # Bot
        if self.bot_stm >= ACTIONS_EFFECTS[self.bot_action]["stamina_cost"]:

            self.bot_stm -= ACTIONS_EFFECTS[self.bot_action]["stamina_cost"]
            self.bot_hp += ACTIONS_EFFECTS[self.bot_action]["health_recovery"]
            self.bot_stm += ACTIONS_EFFECTS[self.bot_action]["stamina_recovery"]

            if ACTIONS_EFFECTS[self.bot_action]["hit_damage"][self.player_action] > 10:
                self.bot_successOffense += 1
            elif ACTIONS_EFFECTS[self.bot_action]["hit_damage"][self.player_action] < 10 and ACTIONS_EFFECTS[self.bot_action]["hit_damage"][self.player_action] > 0:
                self.bot_successDefense += 1 
            
            # Player
            self.player_hp -= ACTIONS_EFFECTS[self.bot_action]["hit_damage"][self.player_action]
        
        self.bot_hp = max(0, min(self.bot_maxHp, self.bot_hp))
        self.bot_stm = max(0, min(self.bot_maxStm, self.bot_stm))
        self.player_stm = max(0, min(self.player_maxHp, self.player_stm))
        self.player_hp = max(0, min(self.player_maxStm, self.player_hp))

    def run(self):
        while self.isRunning:
            self.screen.fill(WHITE)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.isRunning = False

            if self.bot_hp == 0 or self.player_hp == 0:
                self.save_q_table(self.Q)
                print(f"Game Over : Bot Health: {self.bot_hp}, Player Health: {self.player_hp}")
                self.isRunning = False
                continue

            text1 = font.render(f"Bot Thread: {self.bot_action}", True, BLACK)
            text2 = font.render(f"User Action: {self.player_action}", True, BLACK)

            window.blit(text1, (50, 150))
            window.blit(text2, (50, 250))

            # Draw health bars
            pygame.draw.rect(window, RED, (50, 50, 200, 25))  # Bot health background
            pygame.draw.rect(window, GREEN, (50, 50, 2 * self.bot_hp, 25))  # Bot health foreground

            pygame.draw.rect(window, RED, (50, 100, 200, 25))  # Player health background
            pygame.draw.rect(window, GREEN, (50, 100, 2 * self.player_hp, 25))  # Player health foreground

            # Draw stamina bars
            pygame.draw.rect(window, RED, (350, 50, 200, 25))  # Bot stamina background
            pygame.draw.rect(window, BLUE, (350, 50, 2 * self.bot_stm, 25))  # Bot stamina foreground

            pygame.draw.rect(window, RED, (350, 100, 200, 25))  # Player stamina background
            pygame.draw.rect(window, BLUE, (350, 100, 2 * self.player_stm, 25))

            pygame.display.update()
            pygame.time.Clock().tick(60)
        
        self.screen.fill(WHITE)
        if self.player_hp == 0:
            result_text = font.render("You Lost! Bot Wins!", True, BLACK)
        else:
            result_text = font.render("You Win! Bot Loses!", True, BLACK)

        window.blit(result_text, (width // 2 - result_text.get_width() // 2, height // 2))

        pygame.display.update()
        pygame.time.Clock().tick(60)

        time.sleep(2)
        # pygame.quit()

# Main script
if __name__ == "__main__":
    num_runs = int(input("Enter the number of training cycles to run: "))
    for i in range(num_runs):
        print(f"Training Cycle {i + 1}")
        
        # Re-initialize Pygame to ensure it's ready for each new training cycle
        pygame.init()

        # Create a new instance of the Environment class
        env = Environment()
        env.run()
        
        # Quit Pygame after each training cycle to ensure it's properly reset
    pygame.quit()


            

    