import os
import random
import time
import numpy as np

import pygame
import pickle
import socket
import threading
import subprocess

from collections import defaultdict

from main.helper.Actions import *
from main.assets.ImagePath import *
from main.helper.constants import *
from main.helper.ui_elements.Attribute import Attributes
from main.helper.ui_elements.button import Button

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
ACTION_EFFECT = ACTIONS_EFFECTS_OFFENSIVE
pygame.display.set_caption('Bot Training')  

class BotTraining:
    def __init__(self, bot_info):
        self.background_img = pygame.image.load(PLACE_RING)
        self.data = bot_info
        self.model_path = bot_info["model_path"]
        self.screen = screen
        self.isRunning = True
        self.isPaused = False

        self.Q = self.load_bots(self.model_path)
        self.setup_bot()
        self.setup_player()

        "=== CONTROLLER ==="
        self.controller_process = None

        "=== SOCKET ==="
        self.isLoading = True
        self.sock = None

        "=== TIMER ==="
        self.total_seconds = 1 * 30
        self.isTimerFinish = False

        "=== INTERFACE ==="
        self.draw_interface()

        "=== INTERFACE ==="
        self.setup_pose_est()

    def setup_player(self):
        self.player_action = ACTIONS[0]

        self.player_maxHp = 100
        self.player_hp = self.player_maxHp

        self.player_maxStm = 100
        self.player_stamina = self.player_maxStm

        self.isPlayerKO = False
        self.isPlayerTKO = False

        self.player_offenseRate = 0
        self.player_defenseRate = 0

    def setup_bot(self):
        self.bot_action = ACTIONS[1]
        self.bot_img = pygame.image.load(ACTIONS_IMAGE["Idle"][0])
        

        self.bot_maxhp = 100
        self.bot_hp = self.bot_maxhp

        self.bot_maxStm = 100
        self.bot_stamina = self.bot_maxStm

        self.isBotKO = False
        self.isBotTKO = False

        self.bot_offenseRate = 0
        self.bot_defenseRate = 0

    def setup_pose_est(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((SERVER_ADDRESS, SERVER_PORT))
        self.sock.listen()

        print(f"Server listening on {SERVER_ADDRESS}:{SERVER_PORT}")
        threading.Thread(target=self.receive_data, daemon=True).start()
        threading.Thread(target=self.start_controller, daemon=True).start()
        threading.Thread(target=self.generate_bot_actions, daemon=True).start()

    def start_controller(self):
        script_path = os.path.join("main", "gameplay", "PoseController.py")
        self.controller_process = subprocess.Popen(["python", script_path])

    def receive_data(self):
        try : 
            conn, addr = self.sock.accept()
            print(f"Connected by {addr}")
            self.isLoading = False
        except:
            pass 
        
        try:
            with conn:
                while self.isRunning:
                    try:
                        data = conn.recv(1024).decode()
                        if data:
                            self.player_action = data
                            print(self.player_action)

                            if data == "Pause":
                                self.isPaused = True
                            else:
                                self.isPaused = False
                                self.player_action_calculation()
                                print(self.player_action)


                    except ConnectionResetError:
                        print("Connection Reset")
        except :
            pass

    def draw_interface(self):
        self.player_hp_bg = Attributes(SCREEN_MARGIN, SCREEN_MARGIN, 400, 40, GRAY)
        self.player_stamina_bg = Attributes(SCREEN_MARGIN,
                                         self.player_hp_bg.rect.bottom, 350, 20, GRAY)

        self.bot_hp_bg = Attributes(self.screen.get_width() - (400 + SCREEN_MARGIN), SCREEN_MARGIN, 400, 40, GRAY) 
        self.bot_stamina_bg = Attributes(self.bot_hp_bg.rect.left + 50, self.bot_hp_bg.rect.bottom,
                                      350, 20, GRAY)
        
    def update_interface(self):
        player_hp = ((self.player_hp) / 100 * 400)
        player_stm = ((self.player_stamina) / 100 * 350)
        player_maxHp = ((self.player_maxHp) / 100 * 400)
        
        bot_hp = ((self.bot_hp) / 100 * 400)
        bot_stm = ((self.bot_stamina) / 100 * 350)
        bot_maxHp = ((self.bot_maxhp) / 100 * 400)

        Attributes(SCREEN_MARGIN, SCREEN_MARGIN, player_maxHp, 40, BLACK).draw(screen, corner_bottomRight=15)
        Attributes(SCREEN_MARGIN, SCREEN_MARGIN, player_hp, 40, RED).draw(screen, corner_bottomRight = 15)
        Attributes(SCREEN_MARGIN, self.player_hp_bg.rect.bottom, player_stm, 20, BLUE).draw(screen, corner_bottomRight = 15)

        Attributes(self.screen.get_width() - (bot_maxHp + SCREEN_MARGIN), SCREEN_MARGIN, bot_maxHp, 40, BLACK).draw(screen, corner_bottomLeft = 15)
        Attributes(self.screen.get_width() - (bot_hp + SCREEN_MARGIN), SCREEN_MARGIN, bot_hp, 40, RED).draw(screen, corner_bottomLeft = 15)
        Attributes(self.bot_hp_bg.rect.left + 50, self.bot_hp_bg.rect.bottom, bot_stm, 20, BLUE).draw(screen, corner_bottomLeft = 15)

    "== BOT FUNCTION =="

    def load_bots(self, filename):
        try:
            with open(filename, "rb") as f:
                return defaultdict(lambda: np.zeros(17), pickle.load(f))
        except FileNotFoundError:
            return defaultdict(lambda: np.zeros(17))

    def choose_action(self, state):
        """Chooses an action based on epsilon-greedy policy."""
        if random.uniform(0, 1) < EPSILON:
            return random.choice(range(17))  # Explore
        else:
            return np.argmax(self.Q[state])  # Exploit
        
    def get_state(self):
        return (self.bot_hp, 
                self.player_hp, 
                self.bot_stamina, 
                self.player_stamina,
                ACTIONS.index(self.player_action)
                )
    
    def generate_bot_actions(self):
        while self.isRunning:
            while self.player_hp > 0 and self.bot_hp > 0:
                state = self.get_state()
                
                try:
                    action_state = self.choose_action(state)
                    self.bot_action = ACTIONS[action_state]

                    next_state = self.get_state()
                    reward = self.calculate_reward()
                    self.update_q_table(state, action_state, reward, next_state)

                except Exception as e:
                    self.bot_action = ACTIONS[0]

                time.sleep(0.2)
        
    "== PLAYER FUNCTION =="


    "== GAME SYSTEM - TIMER=="
    def start_timer(self):
        if self.total_seconds > 0:
            self.total_seconds -= 1 / 60
        else:
            self.isTimerFinish = True

        minutes = int(self.total_seconds) // 60
        seconds = int(self.total_seconds) % 60

        text = f"{minutes}:{seconds:02d}"
        font = pygame.font.Font(None, 60)
        self.timer = screen.blit(font.render(text, True, WHITE),
                    (self.player_hp_bg.rect.right + 55, SCREEN_MARGIN + 15))
        
        text_trn = f"Training : {self.data['training']}x"
        font_trn = pygame.font.Font(None, 45)

        self.train_eps = screen.blit(font_trn.render(text_trn, True, WHITE),
                    (self.player_hp_bg.rect.right + 0, SCREEN_MARGIN + 50))          
        

    "== GAME SYSTEM - REALTIME CALCULATION =="
    def player_action_calculation(self):
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
    
    def bot_action_calculation(self):

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

        self.bot_img = pygame.image.load(ACTIONS_IMAGE[self.bot_action][0])

        self.bot_hp = max(0, min(self.bot_maxhp, self.bot_hp))
        self.bot_stamina = max(0, min(MAX_STM, self.bot_stamina))
        self.player_hp = max(0, min(self.player_maxHp, self.player_hp))
        self.player_stamina = max(0, min(MAX_STM, self.player_stamina))
    
    "== DATA SAVING =="

    def calculate_reward(self):
        point = 0

        if self.player_action == ACTIONS[0] and ACTION_EFFECT[self.bot_action]["hit_damage"][self.player_action] > 0:
            point += 10
        if self.player_stamina < 40 and ACTION_EFFECT[self.bot_action]["hit_damage"][self.player_action] > 0:
            point += 10
        if self.bot_stamina < ACTION_EFFECT[self.bot_action]["stamina_cost"]:
            point -= 10

        if ACTION_EFFECT[self.bot_action]["hit_damage"][self.player_action] > 5:
            point += 10

        elif ACTION_EFFECT[self.bot_action]["hit_damage"][self.player_action] < 5:
            point -= 10

        action_reward = point + ACTION_EFFECT[self.bot_action]["point_training"][self.player_action]
        return action_reward

    def update_q_table(self, state, action, reward, next_state):
        best_next_action = np.argmax(self.Q[next_state])
        td_target = reward + GAMMA * self.Q[next_state][best_next_action]
        td_error = td_target - self.Q[state][action]
        self.Q[state][action] += ALPHA * td_error

    def save_q_table(self, q_table):
        with open(self.model_path, "wb") as f:
            pickle.dump(dict(q_table), f)

        data_file = "main/information/your_bots.csv"  # Update with your actual data file path
        temp_lines = []

        with open(data_file, "r") as file:
            for line in file:
                if line.startswith(self.data["name"]):  # Find the line for this bot
                    parts = line.strip().split(",")
                    parts[3] = str(int(parts[3]) + 1)  # Increment the training value
                    temp_lines.append(",".join(parts) + "\n")
                else:
                    temp_lines.append(line)

        with open(data_file, "w") as file:
            file.writelines(temp_lines)

    def check_game_over(self):
        if self.bot_hp == 0 or self.player_hp == 0:
            self.save_q_table(self.Q)
            print(f"Game Over : Bot Health: {self.bot_hp}, Player Health: {self.player_hp}")
            pygame.event.post(pygame.event.Event(pygame.USEREVENT + 1))

        if self.isTimerFinish:
            self.save_q_table(self.Q)
            print(f"Game Over : Bot Health: {self.bot_hp}, Player Health: {self.player_hp}")
            pygame.event.post(pygame.event.Event(pygame.USEREVENT + 1))

    "== Pause =="

    def show_pause_screen(self):
        self.pause_screen = pygame.draw.rect(self.screen, FOREGROUND, pygame.Rect(50, 50, 924, 476))

        font = pygame.font.Font(None, 48) 
        text = "Mundur Untuk Melanjutkan" 
        text_surface = font.render(text, True, WHITE)

        text_rect = text_surface.get_rect(center=(512, 288))
        self.screen.blit(text_surface, text_rect)

        self.quit_button = Button("Quit", 462, 350, 150, 50, WHITE, FOREGROUND, self.quit)
        self.quit_button.draw(self.screen)

    def quit(self):
        pygame.event.post(pygame.event.Event(pygame.USEREVENT + 1))


    "========================="
    def run(self):
        while self.isRunning:
            self.screen.fill(WHITE)
            self.screen.blit(self.background_img, (0, 0))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT or event.type == pygame.USEREVENT + 1:
                    self.controller_process.terminate()
                    self.isRunning = False
                    self.sock.close()

                if self.isPaused:
                    self.quit_button.is_clicked(event)

            if not self.isLoading and not self.isPaused:
                # Only the hp and stamina bar background
                self.player_hp_bg.draw(screen, corner_bottomRight=15)
                self.player_stamina_bg.draw(screen, corner_bottomRight=15)
                self.bot_hp_bg.draw(screen, corner_bottomLeft=15)
                self.bot_stamina_bg.draw(screen, corner_bottomLeft=15)

                self.bot_action_calculation()
                screen.blit(self.bot_img, (119, 139))

                self.update_interface()
                self.start_timer()
                self.check_game_over()
            elif self.isPaused:
                self.show_pause_screen()

            pygame.display.update()
            pygame.time.Clock().tick(60)
            