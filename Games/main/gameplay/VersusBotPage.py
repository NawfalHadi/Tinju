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
from main.helper.ui_elements.button import *

bot_model = "main/bot/q_table.pkl"
controller = "main/gameplay/controller.py"

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Main Menu Example')

class VersusBotPage:
    def __init__(self):
        self.screen = screen
        "=== JUDGES ==="
        self.isTimerFinish = False
        self.judges_hp = [0, 0, 0]
        self.judges_def = [0, 0, 0]
        self.judges_off = [0, 0, 0] 
        
        "=== THREADING ==="
        self.controller_process = None

        "=== TIMER ==="
        self.clock = pygame.time.Clock()
        # self.total_seconds = 3 * 60
        self.total_seconds = 1 * 1
        
        "=== BOT ATTRIBUTES ==="
        self.load_bots(bot_model)

        self.bot_action = ACTIONS[0]
        self.bot_action_hit = True
        self.bot_hp = 100
        self.bot_stamina = 100

        self.bot_offenseRate = 0
        self.bot_defenseRate = 0
        "=============================="

        "=== PLAYER ATTRIBUTES ==="
        self.player_action = ACTIONS[0]
        self.player_action_hit = True
        self.player_hp = 100
        self.player_stamina = 100
        # Stamina helps recovery

        self.player_offenseRate = 0
        self.player_defenseRate = 0
        "============================="

        self.draw_interface()
        self.loading = True
        self.running = True
        
        "=== SOCKET ==="
        self.isLoading = True
        self.sock = None

        self.start_games()

    def start_controller(self):
        # script_path = os.system(f'python "{os.path.join("main","gameplay","Controller.py")}"')
        script_path = os.path.join("main", "gameplay", "Controller.py")
        self.controller_process = subprocess.Popen(["python", script_path],)
    
    def start_games(self):
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
            self.isLoading = False
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
        if self.total_seconds > 0:
            self.total_seconds -= 1 / 60
        else:
            self.isTimerFinish = True
        
        minutes = int(self.total_seconds) // 60
        seconds = int(self.total_seconds) % 60

        text = f"{minutes}:{seconds:02d}"
        font = pygame.font.Font(None, 60)
        self.timer = screen.blit(font.render(text, True, BLACK),
                    (self.player_hp_bg.rect.right + 55, SCREEN_MARGIN + 15))          

    def show_roundboard(self):
        self.roundboard = pygame.draw.rect(self.screen, FOREGROUND, pygame.Rect(50, 50, 924, 476)) 

        # Round
        self.rect_roundNumber = pygame.draw.rect(self.screen, WHITE, pygame.Rect(
            self.roundboard.left + 20, self.roundboard.top + 20, 884, 50
        ))

        self.empty_space = self.draw_rounds("PLAYER", self.rect_roundNumber.left + 20, self.rect_roundNumber.top, WHITE)
        self.first_round = self.draw_rounds("R1", self.empty_space.right + 20, self.rect_roundNumber.top)
        self.second_round = self.draw_rounds("R2", self.first_round.right + 20, self.rect_roundNumber.top)
        self.third_round = self.draw_rounds("R3", self.second_round.right + 20, self.rect_roundNumber.top)
        self.total_round = self.draw_rounds("TOTAL", self.third_round.right + 20, self.rect_roundNumber.top)


        self.rect_playerName = pygame.draw.rect(self.screen, WHITE, pygame.Rect(
            self.rect_roundNumber.left, self.rect_roundNumber.bottom + 20, 150, 366
        ))

        "=== First Judges Scoring ==="
        self.first_judges = self.draw_player_name(self.empty_space.bottom + 20, BACKGROUND)
        self.first_r1 = self.draw_round_score(10, 10, self.first_round.left, self.first_judges.top, BACKGROUND)
        self.first_r2 = self.draw_round_score(10, 9, self.second_round.left, self.first_judges.top, BACKGROUND)
        self.first_r3 = self.draw_round_score(9, 10, self.third_round.left, self.first_judges.top, BACKGROUND)
        self.first_total = self.draw_round_score(29, 29, self.total_round.left, self.first_judges.top, BACKGROUND)

        "=== Second Judges Scoring ==="
        self.second_judges = self.draw_player_name(self.first_judges.bottom + 20, BACKGROUND)
        self.second_r1 = self.draw_round_score(10, 10, self.first_round.left, self.second_judges.top, BACKGROUND) 
        self.second_r2 = self.draw_round_score(10, 10, self.second_round.left, self.second_judges.top, BACKGROUND) 
        self.second_r3 = self.draw_round_score(10, 10, self.third_round.left, self.second_judges.top, BACKGROUND) 
        self.second_total = self.draw_round_score(10, 10, self.total_round.left, self.second_judges.top, BACKGROUND) 

        "=== Third Judges Scoring ==="
        self.third_judges = self.draw_player_name(self.second_judges.bottom + 20, BACKGROUND)
        self.third_r1 = self.draw_round_score(10, 10, self.first_round.left, self.third_judges.top, BACKGROUND)
        self.third_r2 = self.draw_round_score(10, 10, self.second_round.left, self.third_judges.top, BACKGROUND)
        self.third_r3 = self.draw_round_score(10, 10, self.third_round.left, self.third_judges.top, BACKGROUND)
        self.third_total = self.draw_round_score(10, 10, self.total_round.left, self.third_judges.top, BACKGROUND)

        self.next_button = Button("Continue >>", self.total_round.left, self.third_judges.bottom + 20, 150, 100, GRAY, FOREGROUND, self.continue_round).draw(self.screen)

    def continue_round(self):
        print("test")
        total_round = 1
        if total_round == 3:
            print("finish")
        else:
            print("next round")

    def draw_rounds(self, text, rightOf, bottomOf, color = BACKGROUND):
        # Draw the rectangle
        rect = pygame.Rect(rightOf, bottomOf, 152, 50)
        pygame.draw.rect(self.screen, color, rect)

        font = pygame.font.Font(None, 36) 
        text_surface = font.render(text, True, (0, 0, 0))  
        text_rect = text_surface.get_rect(center=rect.center) 

        self.screen.blit(text_surface, text_rect)

        return rect

    def draw_player_name(self, bottomOf, color = BACKGROUND):
        rect = pygame.Rect(self.rect_playerName.left, bottomOf, 150, 76)
        pygame.draw.rect(self.screen, color, rect)

        # Initialize the font
        font = pygame.font.Font(None, 36)  # Adjust font size as needed

        # Render the "Player" text
        player_text_surface = font.render("Player", True, (WHITE))  # Black color for text
        player_text_rect = player_text_surface.get_rect(center=(rect.centerx, rect.top + 15))  # Position near the top

        # Render the "Bot" text
        bot_text_surface = font.render("Bot", True, (WHITE))  # Black color for text
        bot_text_rect = bot_text_surface.get_rect(center=(rect.centerx, rect.bottom - 15))  # Position near the bottom

        # Blit the text onto the screen
        self.screen.blit(player_text_surface, player_text_rect)
        self.screen.blit(bot_text_surface, bot_text_rect)

        return rect
    
    def draw_round_score(self, point_player, point_bot, rightOf, bottomOf, color= BACKGROUND):
        rect = pygame.Rect(rightOf, bottomOf, 150, 76)
        pygame.draw.rect(self.screen, color, rect)

        font = pygame.font.Font(None, 36)

        player_point_surface = font.render(str(point_player), True, (WHITE))  # Black color for text
        player_point_rect = player_point_surface.get_rect(center=(rect.centerx, rect.top + 15))  # Position near the top

        bot_point_surface = font.render(str(point_bot), True, (WHITE))  # Black color for text
        bot_point_rect = bot_point_surface.get_rect(center=(rect.centerx, rect.bottom - 15))  # Position near the bottom

        self.screen.blit(player_point_surface, player_point_rect)
        self.screen.blit(bot_point_surface, bot_point_rect)

        return rect
        
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
            
            
            self.player_hp_bg.draw(screen, corner_bottomRight=15)
            self.player_stamina_ui.draw(screen, corner_bottomRight=15)
            
            self.bot_hp_bg.draw(screen, corner_bottomLeft=15)
            self.bot_stamina_ui.draw(screen, corner_bottomLeft=15)

            if (not self.isLoading and not self.isTimerFinish) :    
                self.update_interface()
                self.bot_action_calculation()
                self.player_action_calculation()
                self.start_timer()

            if self.isTimerFinish:
                self.show_roundboard()

            
            pygame.display.update()
            pygame.time.Clock().tick(60)


                    