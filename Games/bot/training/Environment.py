import random
import os
import logging
import numpy as np
import time

import threading
import pygame
import pickle

from collections import defaultdict
from Actions import *

width, height = 1024, 576
window = pygame.display.set_mode((width, height))
pygame.font.init()
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

ACTION_EFFECT = ACTIONS_EFFECTS_OFFENSIVE
pygame.display.set_caption(f"Offensive")


class Environment:
    def __init__(self, action, step) -> None:
        self.screen = window
        self.isRunning = True
        self.action = action
        self.step = step
        
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
        self.total_seconds = 1.5 * 60
        self.isTimerFinish = False

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
            # self.player_action = random.choice(ACTIONS)
            # self.player_action = ACTIONS[0]

            if self.player_stm == 100:
                self.player_action = action
            elif self.player_stm < ACTION_EFFECT[self.player_action]["stamina_cost"]:
                self.player_action = ACTIONS[0]

            if self.player_stm >= ACTION_EFFECT[self.player_action]["stamina_cost"]:
                # Player
                self.player_stm -= ACTION_EFFECT[self.player_action]["stamina_cost"]
                self.player_hp += ACTION_EFFECT[self.player_action]["health_recovery"]
                self.player_stm += ACTION_EFFECT[self.player_action]["stamina_recovery"]

                if ACTION_EFFECT[self.player_action]["hit_damage"][self.bot_action] > 10:
                    self.player_successOffense += 1
                elif ACTION_EFFECT[self.player_action]["hit_damage"][self.bot_action] < 10:
                    self.player_successDefense += 1

                # Bot
                self.bot_hp -= ACTION_EFFECT[self.player_action]["hit_damage"][self.bot_action]

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
            return random.choice(range(len(ACTIONS) - 1)), "R :"  # Explore
        else:
            return np.argmax(self.Q[state]), "Q :"  # Exploit
        

    def update_q_table(self, state, action, reward, next_state):
        """Updates the Q-table using the Q-learning formula."""

        best_next_action = np.argmax(self.Q[next_state])
        td_target = reward + gamma * self.Q[next_state][best_next_action]
        td_error = td_target - self.Q[state][action]
        self.Q[state][action] += alpha * td_error

    def save_q_table(self, q_table, filename="../model/opponent/offensive_bot.pkl"):
        with open(filename, "wb") as f:
            pickle.dump(dict(q_table), f)

    def load_q_table(self, filename="../model/opponent/offensive_bot.pkl"):
        try:
            with open(filename, "rb") as f:
                return defaultdict(lambda: np.zeros(17), pickle.load(f))
        except FileNotFoundError:
            return defaultdict(lambda: np.zeros(17))

    def generate_bot_action(self):
        while self.player_hp > 0 and self.bot_hp > 0:
            state = self.get_state()
            get_action, get_chooce = self.choose_action(state)
            
            self.bot_action = ACTIONS[get_action]
            self.handle_bot_action()


            next_state = self.get_state()
            reward = self.calculate_reward()
            print(get_chooce, self.bot_action, "|| Reward :", reward)
            self.update_q_table(state, get_action, reward, next_state)

            time.sleep(0.2) 

    def calculate_reward(self):
        point = 0

        # if self.player_hp < self.bot_hp and self.bot_action != "Idle":
        #     point += 10
        # elif self.player_hp > self.bot_hp:
        #     point -= 10

        if self.player_action == ACTIONS[0] and ACTION_EFFECT[self.bot_action]["hit_damage"][self.player_action] > 0:
            point += 10

        if self.player_stm < 40 and ACTION_EFFECT[self.bot_action]["hit_damage"][self.player_action] > 0:
            point += 10

        if self.bot_stm < ACTION_EFFECT[self.bot_action]["stamina_cost"]:
            point -= 10

        if ACTION_EFFECT[self.bot_action]["hit_damage"][self.player_action] > 5:
            point += 10
        # elif ACTIONS_EFFECTS[self.bot_action]["hit_damage"][self.player_action] < 10 and ACTIONS_EFFECTS[self.bot_action]["hit_damage"][self.player_action] > 0:
        #     # Success Guard
        #     point += 20
        elif ACTION_EFFECT[self.bot_action]["hit_damage"][self.player_action] < 5:
            point -= 10

        action_reward = point + ACTION_EFFECT[self.bot_action]["point_training"][self.player_action]

        return action_reward

    def handle_bot_action(self):
        # Bot
        if self.bot_stm >= ACTION_EFFECT[self.bot_action]["stamina_cost"]:

            self.bot_stm -= ACTION_EFFECT[self.bot_action]["stamina_cost"]
            self.bot_hp += ACTION_EFFECT[self.bot_action]["health_recovery"]
            self.bot_stm += ACTION_EFFECT[self.bot_action]["stamina_recovery"]

            if ACTION_EFFECT[self.bot_action]["hit_damage"][self.player_action] > 10:
                self.bot_successOffense += 1
            elif ACTION_EFFECT[self.bot_action]["hit_damage"][self.player_action] < 10 and ACTION_EFFECT[self.bot_action]["hit_damage"][self.player_action] > 0:
                self.bot_successDefense += 1 
            
            # Player
            self.player_hp -= ACTION_EFFECT[self.bot_action]["hit_damage"][self.player_action]
        
        self.bot_hp = max(0, min(self.bot_maxHp, self.bot_hp))
        self.bot_stm = max(0, min(self.bot_maxStm, self.bot_stm))
        self.player_stm = max(0, min(self.player_maxHp, self.player_stm))
        self.player_hp = max(0, min(self.player_maxStm, self.player_hp))

    def start_timer(self):
        if self.total_seconds > 0:
            self.total_seconds -= 1 / 60
        else:
            self.isTimerFinish = True


        minutes = int(self.total_seconds) // 60
        seconds = int(self.total_seconds) % 60
        
        text = f"{minutes}:{seconds:02d}"
        font = pygame.font.Font(None, 60)

        self.screen.blit(font.render(text, True, BLACK), (50, 300))

        training_text = f"Episode Training {self.step} For {self.action}"
        self.screen.blit(font.render(training_text, True, BLACK), (50, 400))
        

    def run(self):
        while self.isRunning:
            self.screen.fill(WHITE)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.isRunning = False

            self.start_timer()

            if self.bot_hp == 0 or self.player_hp == 0:
                self.save_q_table(self.Q)
                print(f"Game Over : Bot Health: {self.bot_hp}, Player Health: {self.player_hp}")
                self.isRunning = False
                continue

            if self.isTimerFinish:
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
        elif self.bot_hp == 0:
            result_text = font.render("You Win! Bot Loses!", True, BLACK)
        elif self.isTimerFinish:
            if self.player_hp < self.bot_hp:
                result_text = font.render("You Lost! Bot Wins! By Anonymous Decision", True, BLACK)
            elif self.player_hp > self.bot_hp:
                result_text = font.render("You wIN! Bot Loses! By Anonymous Decision", True, BLACK)
            else:
                result_text = font.render("Error", True, BLACK)

        window.blit(result_text, (width // 2 - result_text.get_width() // 2, height // 2))

        pygame.display.update()
        pygame.time.Clock().tick(60)

        time.sleep(2)
        # pygame.quit()

# Main script
if __name__ == "__main__":
    runs = 50
    for action in ACTIONS:
        for i in range(runs):
            print(f"Training Cycle {i + 1}")

            pygame.init()

            env = Environment(action, i+1)
            env.run()

    pygame.quit()

    # num_runs = int(input("Enter the number of training cycles to run: "))
    # for i in range(num_runs):
    #     print(f"Training Cycle {i + 1}")
        
    #     # Re-initialize Pygame to ensure it's ready for each new training cycle
    #     pygame.init()

    #     # Create a new instance of the Environment class
    #     env = Environment()
    #     env.run()
        
    #     # Quit Pygame after each training cycle to ensure it's properly reset
    # pygame.quit()


            

    