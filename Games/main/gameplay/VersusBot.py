import os
import numpy as np
import random
import time

import socket
import pygame
import threading
import subprocess
import pickle


from collections import defaultdict

from main.helper.constants import *
from main.helper.ui_elements.Attribute import *

bot_model = "main/bot/q_table.pkl"
controller = "main/gameplay/controller.py"

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Main Menu Example')

class VersusBot:
    def __init__(self):
        self.screen = screen
        "=== THREADING ==="
        self.controller_process = None

        "=== BOT ATTRIBUTES ==="
        self.load_bots(bot_model)
        self.bot_action = ACTIONS[0]
        self.bot_action_hit = True
        self.bot_hp = 100
        self.bot_stamina = 100

        "=== PLAYER ATTRIBUTES ==="
        self.player_action = ACTIONS[0]
        self.player_action_hit = True
        self.player_hp = 100
        self.player_stamina = 100

        self.draw_interface()
        self.loading = True
        self.running = True
        
        "=== SOCKET ==="
        self.show_loading = True
        self.sock = None

        self.start_games()

    def start_controller(self):
        # script_path = os.system(f'python "{os.path.join("main","gameplay","Controller.py")}"')
        script_path = os.path.join("main", "gameplay", "Controller.py")
        self.controller_process = subprocess.Popen(["python", script_path],)
    
    def start_games(self):
        "The thread for generating action from bot"
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((SERVER_ADDRESS, SERVER_PORT))
        self.sock.listen()

        print(f"Server listening on {SERVER_ADDRESS}:{SERVER_PORT}")

        threading.Thread(target=self.receive_data, daemon=True).start()
        threading.Thread(target=self.start_controller, daemon=True).start()
        
        # Bisa diganti dengan countdown 3-2-1, and kinda like that
        
        threading.Thread(target=self.generate_bot_actions, daemon=True).start()

        # threading.Thread(target=)

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

            time.sleep(0.2)
            
            # print(self.bot_action)
            
            # if(not self.show_loading):
            #     print("test")
            

    def receive_data(self):
        try : 
            conn, addr = self.sock.accept()
            print(f"Connected by {addr}")
            self.show_loading = False
        except:
            pass 
        
        try:
            with conn:
                while self.running:
                    try:
                        data = conn.recv(1024).decode()

                        if data:
                            self.player_action = data

                    except ConnectionResetError:
                        print("error")
        except :
            pass

    def draw_interface(self):
        player_hp = ((self.player_hp) / 100 * 400)
        bot_hp = ((self.bot_hp) / 100 * 400)

        self.player_hp_bg = Attributes(SCREEN_MARGIN, SCREEN_MARGIN, 400, 40, GRAY)
        self.player_stamina_ui = Attributes(SCREEN_MARGIN,
                                         self.player_hp_bg.rect.bottom, 350, 20, BLUE)

        self.bot_hp_bg = Attributes(self.screen.get_width() - (400 + SCREEN_MARGIN), SCREEN_MARGIN, 400, 40, GRAY) 
        self.bot_stamina_ui = Attributes(self.bot_hp_bg.rect.left + 50, self.bot_hp_bg.rect.bottom,
                                      350, 20, BLUE)
        
    def update_interface(self):
        player_hp = ((self.player_hp) / 100 * 400)
        bot_hp = ((self.bot_hp) / 100 * 400)

        Attributes(SCREEN_MARGIN, SCREEN_MARGIN, player_hp, 40, RED).draw(screen, corner_bottomRight = 15)
        Attributes(self.screen.get_width() - (bot_hp + SCREEN_MARGIN), SCREEN_MARGIN, bot_hp, 40, RED).draw(screen, corner_bottomLeft = 15)

        font = pygame.font.Font(None, 60)
        screen.blit(font.render(self.bot_action, True, BLACK), (self.player_stamina_ui.rect.left, self.player_stamina_ui.rect.bottom))

    def start_timer(self):
        text = "3:00"
        font = pygame.font.Font(None, 60)
        self.timer = screen.blit(font.render(text, True, BLACK),
                    (self.player_hp_bg.rect.right + 55, SCREEN_MARGIN + 15))
                    
        
    def player_action_calculation(self):
        if self.player_action == "Jab":
            if self.player_stamina >= 20:
                self.player_stamina -= 25
                if self.bot_action == "Idle":
                    self.bot_hp -= 2
                elif self.bot_action == "Guard":
                    self.bot_hp -= 1
                elif self.bot_action == "Jab":
                    self.bot_hp -= 3
        
        elif self.player_action == "Guard":
            self.player_stamina += 1
            self.player_hp += 0.002
            if self.bot_action == "Jab":
                self.player_stamina += 2
        
        elif self.player_action == "Idle":
            self.player_stamina += 2
            self.player_hp += 0.01
            if self.bot_action == "Jab":
                self.player_stamina += 4

        self.bot_hp = max(0, min(MAX_HP, self.bot_hp))
        self.bot_stamina = max(0, min(MAX_STM, self.bot_stamina))
        self.player_hp = max(0, min(MAX_HP, self.player_hp))
        self.player_stamina = max(0, min(MAX_STM, self.player_stamina))

    def bot_action_calculation(self):
        if self.bot_action == "Jab":
            if self.bot_stamina >= 20:
                self.bot_stamina -= 25
                if self.player_action == "Idle":
                    self.player_hp -= 2
                elif self.player_action == "Guard":
                    self.player_hp -= 1
                elif self.player_action == "Jab":
                    self.player_hp -= 3
        
        elif self.bot_action == "Guard":
            self.bot_stamina += 1
            self.bot_hp += 0.002
            if self.player_action == "Jab":
                self.bot_stamina += 2
        
        elif self.bot_action == "Idle":
            self.bot_stamina += 2
            self.bot_hp += 0.01
            if self.player_action == "Jab":
                self.bot_stamina += 4

        self.bot_hp = max(0, min(MAX_HP, self.bot_hp))
        self.bot_stamina = max(0, min(MAX_STM, self.bot_stamina))
        self.player_hp = max(0, min(MAX_HP, self.player_hp))
        self.player_stamina = max(0, min(MAX_STM, self.player_stamina))
        
        
        
    def run(self):
        while self.running:
            self.screen.fill(WHITE)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.controller_process.terminate()
                    self.running = False
                    self.sock.close()
            
            self.start_timer()
            
            self.player_hp_bg.draw(screen, corner_bottomRight=15)
            self.player_stamina_ui.draw(screen, corner_bottomRight=15)
            
            self.bot_hp_bg.draw(screen, corner_bottomLeft=15)
            self.bot_stamina_ui.draw(screen, corner_bottomLeft=15)

            if (not self.show_loading):    
                self.update_interface()
                self.bot_action_calculation()
                self.player_action_calculation()

            pygame.display.update()
            pygame.time.Clock().tick(60)


                    