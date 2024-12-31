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

from main.assets.ImagePath import *
from main.helper.constants import *
from main.helper.Actions import *
from main.helper.ui_elements.Attribute import *
from main.helper.ui_elements.button import *
from main.assets.AudioPath import *

controller = "main/gameplay/PoseController.py"

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Main Menu Example')

pygame.mixer.init()

class VersusBotPage:
    def __init__(self, bot_model):
        self.screen = screen
        self.image = pygame.image.load(PLACE_RING)
        self.isPaused = False

        "=== JUDGES & GAME SYSTEM==="
        self.isTimerFinish = False
        self.scoring_round = 1
        self.current_rounds = 1

        self.judges_hp = [[10, 10], [10, 10], [10, 10]]
        self.judges_def = [[10, 10], [10, 10], [10, 10]]
        self.judges_off = [[10, 10], [10, 10], [10, 10]] 

        "=== KO SYSTEM ==="
        self.ko_target_speed = 10
        self.ko_target_size = 600
        self.ko_seconds = 0
        self.min_pos = 400
        self.max_pos = 0
        self.cur_pos = 400
        self.isGoLeft = False

        "=== THREADING ==="
        self.controller_process = None

        "=== TIMER ==="
        self.total_seconds = 1 * 30


        self.start_round_seconds = 0
        self.isRoundStart = False

        "=== BOT ATTRIBUTES ==="
        self.load_bots(bot_model)

        self.bot_action = ACTIONS[0]
        self.bot_img = pygame.image.load(ACTIONS_IMAGE["Idle"][0])
        self.bot_action_hit = True

        self.bot_maxhp = 100
        self.bot_hp = self.bot_maxhp

        self.bot_maxStm = 100
        self.bot_stamina = self.bot_maxStm

        self.isBotKO = False
        self.isBotTKO = False
        self.bot_recover_square = 0
        self.bot_round_ko = 0
        self.bot_total_ko = 0

        self.bot_offenseRate = 0
        self.bot_defenseRate = 0
        "=============================="

        "=== PLAYER ATTRIBUTES ==="
        self.player_action = ACTIONS[0]
        self.player_action_hit = True

        self.player_maxHp = 1
        self.player_hp = self.player_maxHp

        self.player_maxStm = 100
        self.player_stamina = self.player_maxStm

        self.isPlayerKO = False
        self.isPlayerTKO = False
        self.player_recover_square = 0
        self.player_round_ko = 0
        self.player_total_ko = 0

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
        script_path = os.path.join("main", "gameplay", "PoseController.py")
        self.controller_process = subprocess.Popen(["python", script_path])
    
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
            self.Q = defaultdict(lambda: np.zeros(17), pickle.load(f))

    def choose_action(self, state):
        """Chooses an action based on epsilon-greedy policy."""
        if random.uniform(0, 1) < EPSILON:
            return random.choice(range(17))  # Explore
        else:
            return np.argmax(self.Q[state])  # Exploit

    def generate_bot_actions(self):
        while self.running:
            if self.player_action != "Pause":
                state = (self.bot_hp, self.player_hp, 
                        self.bot_stamina, self.player_stamina,
                        ACTIONS.index(self.player_action))
                try:
                    action_state = self.choose_action(state)
                    self.bot_action = ACTIONS[action_state]
                except Exception as e:
                    self.bot_action = ACTIONS[0]


                time.sleep(0.2)
                     
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
                            if (not self.isLoading and not self.isTimerFinish) :
                                self.player_action = data

                                if data == "Pause":
                                    self.isPaused = True
                                else:
                                    self.isPaused = False
                                    print(self.player_action)
                                    self.player_action_calculation()

                    except ConnectionResetError:
                        print("Connection Reset")
        except :
            pass

    def draw_interface(self):
        bot_hp = ((self.bot_hp) / 100 * 400)


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

        font = pygame.font.Font(None, 60)
        screen.blit(font.render(self.bot_action, True, BLACK), (self.bot_stamina_bg.rect.left, self.bot_stamina_bg.rect.bottom))

        self.bot_img = pygame.image.load(ACTIONS_IMAGE[self.bot_action][0])


    def start_timer(self):
        if self.total_seconds > 0:
            self.total_seconds -= 1 / 60
        else:
            self.isTimerFinish = True
            if self.current_rounds == self.scoring_round:
                self.scoring_system()
                self.hitpoint_stamina_calculation() 
            
        
        minutes = int(self.total_seconds) // 60
        seconds = int(self.total_seconds) % 60

        text = f"{minutes}:{seconds:02d}"
        font = pygame.font.Font(None, 60)
        self.timer = screen.blit(font.render(text, True, BLACK),
                    (self.player_hp_bg.rect.right + 55, SCREEN_MARGIN + 15))         
 
    def knockout_check(self):
        if self.player_hp <= 0:
            self.player_round_ko += 1
            self.player_total_ko += 1
            if self.player_round_ko == 3:
                self.isPlayerTKO = True
                self.total_seconds = 0
            else:
                self.isPlayerKO = True
                self.knockout_speed(self.player_total_ko)
        elif self.bot_hp <= 0:
            self.bot_round_ko += 1
            self.bot_total_ko += 1
            if self.bot_round_ko == 3:
                self.isBotTKO = True
                self.total_seconds = 0
            else:
                self.isBotKO = True
                self.knockout_speed(self.bot_total_ko)
    
    def knockout_speed(self, total_ko):
        if total_ko == 1:
            self.ko_target_speed = 10
            self.ko_target_size = 600
        elif total_ko == 2:
            self.ko_target_speed = 20
            self.ko_target_size = 500
        elif total_ko == 3 or total_ko == 4:
            self.ko_target_speed = 40
            self.ko_target_size = 350
        else:
            self.ko_target_size = 200
            self.ko_target_speed = 50

    def knockout_interface(self):        
        self.knockout_frame = Attributes((SCREEN_WIDTH // 2) - 400, (SCREEN_HEIGHT // 2) + 200, 800, 50, WHITE).draw(self.screen)
        
        if self.cur_pos == self.min_pos:
            self.cur_pos -= self.ko_target_speed
            self.isGoLeft = False
        elif self.cur_pos == self.max_pos:
            self.cur_pos += self.ko_target_speed
            self.isGoLeft = self.ko_target_speed
        else:
            if self.isGoLeft:
                self.cur_pos += self.ko_target_speed
            elif not self.isGoLeft:
                self.cur_pos -= self.ko_target_speed

        self.knockout_target = Attributes((SCREEN_WIDTH // 2) - self.cur_pos, (SCREEN_HEIGHT // 2) + 202, self.ko_target_size, 46, FOREGROUND)
        self.knockout_target.draw(self.screen)

        left_target, right_target = self.knockout_target.rect.left, self.knockout_target.rect.right
        
        if self.isPlayerKO:
            self.player_recover_square = max(-400, min(400, self.player_recover_square))
            recovery_square = self.player_recover_square

            if self.player_action == "Guard":
                self.player_recover_square += 5
            elif self.player_action == "Idle":
                self.player_recover_square -= 5

        elif self.isBotKO:
            
            bot_action = random.choice("Guard", "Idle")

            if bot_action == "Guard":
                self.bot_recover_square += 5
            elif bot_action == "Idle":
                self.bot_recover_square -= 5

            self.bot_recover_square = max(-400, min(400, self.bot_recover_square))
            recovery_square = self.bot_recover_square
                
        self.knockout_square = Attributes((SCREEN_WIDTH // 2) - recovery_square, (SCREEN_HEIGHT // 2) + 202, 10, 46, BLACK)
        self.knockout_square.draw(self.screen)

        if left_target < self.knockout_square.rect.centerx and self.knockout_square.rect.centerx < right_target:
            if self.isPlayerKO:
                self.player_hp += 0.2
            elif self.isBotKO:
                self.bot_hp += 0.2

        if self.player_hp >= 100:
            self.player_hp = self.player_maxHp * 0.75
            self.isPlayerKO = False
            self.ko_seconds = 0
        elif self.bot_hp >= 100:
            self.bot_hp = self.bot_maxhp * 0.75
            self.isBotKO = False
            self.ko_seconds = 0

        self.player_hp = max(0, min(self.player_maxHp, self.player_hp))
        self.bot_hp = max(0, min(self.bot_maxhp, self.bot_hp))

    def knockout_timer(self):
        seconds = int(self.ko_seconds) % 60

        if self.ko_seconds < 10:
            self.ko_seconds += 1 / 60

            if int(self.ko_seconds) != seconds:
                try:
                    pygame.mixer.Sound.play(pygame.mixer.Sound(AUDIO_COUNTER[round(self.ko_seconds)]))
                except KeyError:
                    pass
            font = pygame.font.Font(None, 150)
            text = font.render(str(seconds), True, (FOREGROUND))

            screen.blit(text, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        else:
            if self.isPlayerKO:
                self.isPlayerTKO = True
            elif self.isBotKO:
                self.isBotTKO = True
                
            self.total_seconds = 0

    def start_round_timer(self):
        seconds = int(self.start_round_seconds) % 60

        if self.start_round_seconds < 3:
            self.start_round_seconds += 1 / 60

            if int(self.start_round_seconds) != seconds:
                try:
                    pygame.mixer.Sound.play(pygame.mixer.Sound(AUDIO_COUNTER[round(self.start_round_seconds)]))
                except KeyError:
                    pass
            font = pygame.font.Font(None, 150)
            text = font.render(str(seconds), True, (FOREGROUND))

            screen.blit(text, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        else:
            self.isRoundStart = True


    def scoring_system(self):
        bot_ko = self.bot_round_ko
        player_ko = self.player_round_ko

        if self.player_hp < self.bot_hp:
            self.judges_hp[self.current_rounds - 1][0] -= 1
        elif self.player_hp > self.bot_hp:
            self.judges_hp[self.current_rounds - 1][1] -= 1

        if self.player_offenseRate < self.bot_offenseRate:
            self.judges_off[self.current_rounds - 1][0] -= 1 
        elif self.player_offenseRate > self.bot_offenseRate:
            self.judges_off[self.current_rounds - 1][1] -= 1

        if self.player_defenseRate < self.bot_defenseRate:
            self.judges_def[self.current_rounds - 1][0] -= 1
        elif self.player_defenseRate > self.bot_defenseRate:
            self.judges_def[self.current_rounds - 1][1] -= 1

        self.judges_hp[self.current_rounds - 1][0] -= player_ko
        self.judges_hp[self.current_rounds - 1][1] -= bot_ko
        self.judges_off[self.current_rounds - 1][0] -= player_ko
        self.judges_off[self.current_rounds - 1][1] -= bot_ko
        self.judges_def[self.current_rounds - 1][0] -= player_ko
        self.judges_def[self.current_rounds - 1][1] -= bot_ko
        
        self.scoring_round += 1
            
    def hitpoint_stamina_calculation(self):
        if self.current_rounds >= 1:    
            self.player_maxHp = min(self.player_hp * 0.30 + self.player_hp, 100)
            self.player_maxStm = min(self.player_stamina * 0.90 + self.player_stamina, 100)

            self.bot_maxhp = min(self.bot_hp * 0.30 + self.bot_hp, 100)
            self.bot_maxStm = min(self.bot_stamina * 0.90 + self.bot_stamina, 100)
        elif self.current_rounds >= 2:
            self.player_maxHp = min(self.player_hp * 0.20 + self.player_hp, 100)
            self.player_maxStm = min(self.player_stamina * 0.80 + self.player_stamina, 100)

            self.bot_maxhp = min(self.bot_hp * 0.20 + self.bot_hp, 100)
            self.bot_maxStm = min(self.bot_stamina * 0.80 + self.bot_stamina, 100)
        elif self.current_rounds >= 3:
            self.player_maxHp = min(self.player_hp * 0.15 + self.player_hp, 100)
            self.player_maxStm = min(self.player_stamina * 0.75 + self.player_stamina, 100)

            self.bot_maxhp = min(self.bot_hp * 0.15 + self.bot_hp, 100)
            self.bot_maxStm = min(self.bot_stamina * 0.75 + self.bot_stamina, 100)

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
        if self.current_rounds >= 1:
            self.first_r1 = self.draw_round_score(self.judges_hp[0][0], self.judges_hp[0][1], self.first_round.left, self.first_judges.top, BACKGROUND)
        if self.current_rounds >= 2:
            self.first_r2 = self.draw_round_score(self.judges_hp[1][0], self.judges_hp[1][1], self.second_round.left, self.first_judges.top, BACKGROUND)
        if self.current_rounds >= 3:
            self.first_r3 = self.draw_round_score(self.judges_hp[2][0], self.judges_hp[2][1], self.third_round.left, self.first_judges.top, BACKGROUND)
        
            hpPlayer_scoring = sum(sublist[0] for sublist in self.judges_hp)
            hpBot_scoring = sum(sublist[1] for sublist in self.judges_hp)
            
            self.first_total = self.draw_round_score(hpPlayer_scoring, hpBot_scoring, self.total_round.left, self.first_judges.top, BACKGROUND)

        "=== Second Judges Scoring ==="
        self.second_judges = self.draw_player_name(self.first_judges.bottom + 20, BACKGROUND)
        if self.current_rounds >= 1:
            self.second_r1 = self.draw_round_score(self.judges_off[0][0], self.judges_off[0][1], self.first_round.left, self.second_judges.top, BACKGROUND) 
        if self.current_rounds >= 2:
            self.second_r2 = self.draw_round_score(self.judges_off[1][0], self.judges_off[1][1], self.second_round.left, self.second_judges.top, BACKGROUND) 
        if self.current_rounds >= 3:
            self.second_r3 = self.draw_round_score(self.judges_off[2][0], self.judges_off[2][1], self.third_round.left, self.second_judges.top, BACKGROUND) 
        
            offPlayer_scoring = sum(sublist[0] for sublist in self.judges_off)
            offBot_scoring = sum(sublist[1] for sublist in self.judges_off)
            
            self.second_total = self.draw_round_score(offPlayer_scoring, offBot_scoring, self.total_round.left, self.second_judges.top, BACKGROUND) 

        "=== Third Judges Scoring ==="
        self.third_judges = self.draw_player_name(self.second_judges.bottom + 20, BACKGROUND)
        if self.current_rounds >= 1:
            self.third_r1 = self.draw_round_score(self.judges_def[0][0], self.judges_def[0][1], self.first_round.left, self.third_judges.top, BACKGROUND)
        if self.current_rounds >= 2:
            self.third_r2 = self.draw_round_score(self.judges_def[1][0], self.judges_def[1][1], self.second_round.left, self.third_judges.top, BACKGROUND)
        if self.current_rounds >= 3:
            self.third_r3 = self.draw_round_score(self.judges_def[2][0], self.judges_def[2][1], self.third_round.left, self.third_judges.top, BACKGROUND)
        
            defPlayer_scoring = sum(sublist[0] for sublist in self.judges_def)
            defBot_scoring = sum(sublist[1] for sublist in self.judges_def)

            self.third_total = self.draw_round_score(defPlayer_scoring, defBot_scoring, self.total_round.left, self.third_judges.top, BACKGROUND)

        self.next_button = Button("Continue >>", self.total_round.left, self.third_judges.bottom + 20, 150, 100, GRAY, FOREGROUND, self.continue_round)

    def continue_round(self):
        self.isTimerFinish = False
        self.total_seconds = 3 * 10

        hpPlayer_scoring = sum(sublist[0] for sublist in self.judges_hp)
        hpBot_scoring = sum(sublist[1] for sublist in self.judges_hp)

        offPlayer_scoring = sum(sublist[0] for sublist in self.judges_off)
        offBot_scoring = sum(sublist[1] for sublist in self.judges_off)

        defPlayer_scoring = sum(sublist[0] for sublist in self.judges_def)
        defBot_scoring = sum(sublist[1] for sublist in self.judges_def)

        playerScore = hpPlayer_scoring + offPlayer_scoring + defPlayer_scoring
        botScore = hpBot_scoring + offBot_scoring + defBot_scoring
            
        if self.isPlayerTKO:
            print("Bot Win by Technical Knockout")
            self.save_record("Bot")
            time.sleep(1)
            pygame.event.post(pygame.event.Event(pygame.QUIT))

        elif self.isBotTKO:
            print("Player Win by Technical Knockout")
            self.save_record("Player")
            time.sleep(1)
            pygame.event.post(pygame.event.Event(pygame.QUIT))
        
        elif self.current_rounds < 3:
            self.current_rounds += 1

            self.bot_round_ko = 0
            self.player_round_ko = 0

            self.bot_offenseRate = 0
            self.bot_defenseRate = 0
            self.player_offenseRate = 0
            self.player_defenseRate = 0
            
        elif self.current_rounds == 3:
            if playerScore > botScore:
                print("Player Win by Anonimous Decision")
                self.save_record("Player")
            elif playerScore == botScore:
                print("Draw")
                self.save_record("Draw")
            elif playerScore < botScore:
                print("Bot Win by Anonimous Decision")
                self.save_record("Bot")
            
            time.sleep(1)
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def save_record(self, winner):
        data_file = "main/information/your_info.csv"  # Update with your actual data file path
        temp_lines = []

        with open(data_file, "r") as file:
            for line in file:
                if line.startswith("nawfal"):  # Find the line for this bot
                    parts = line.strip().split(",")
                    
                    print(type(parts[2]))
                    # if winner == "Bot":
                    #     parts[2] = str(int([parts[2]]) + 1)
                    # elif winner == "Player":
                    #     parts[1] = str(int([parts[1]]) + 1)
                    # elif winner == "Draw":
                    #     parts[3] = str(int(parts[3]) + 1) 

                    # temp_lines.append(",".join(parts) + "\n")
                else:
                    temp_lines.append(line)

        with open(data_file, "w") as file:
            file.writelines(temp_lines)

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

        # self.bot_img = pygame.image.load(random.choice(ACTIONS_IMAGE[self.bot_action]))

        self.bot_hp = max(0, min(self.bot_maxhp, self.bot_hp))
        self.bot_stamina = max(0, min(MAX_STM, self.bot_stamina))
        self.player_hp = max(0, min(self.player_maxHp, self.player_hp))
        self.player_stamina = max(0, min(MAX_STM, self.player_stamina))
         
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

    
    def run(self):
        while self.running:
            self.screen.fill(WHITE)
            screen.blit(self.image, (0, 0))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT or event.type == pygame.USEREVENT + 1:
                    self.controller_process.terminate()
                    self.running = False
                    self.sock.close()

                if self.isTimerFinish:
                    self.next_button.is_clicked(event)

                if self.isPaused:
                    self.quit_button.is_clicked(event)
            
            if (not self.isLoading and not self.isTimerFinish):
                
                if not self.isRoundStart:
                    self.start_round_timer()
                elif not self.isPaused:
                    self.player_hp_bg.draw(screen, corner_bottomRight=15)
                    self.player_stamina_bg.draw(screen, corner_bottomRight=15)
                    
                    self.bot_hp_bg.draw(screen, corner_bottomLeft=15)
                    self.bot_stamina_bg.draw(screen, corner_bottomLeft=15)

                    if self.isBotKO or self.isPlayerKO:
                        self.knockout_interface()
                        self.knockout_timer()
                    else:    
                        self.bot_action_calculation()
                        screen.blit(self.bot_img, (119, 139))

                        # if self.player_action == "Idle":
                        #     self.player_action_calculation()

                        self.knockout_check()
                        self.update_interface()
                    self.start_timer()
                elif self.isPaused:
                    self.show_pause_screen()  
                
            if self.isTimerFinish:
                self.show_roundboard()
                self.next_button.draw(screen)

            
            pygame.display.update()
            pygame.time.Clock().tick(60)


                    