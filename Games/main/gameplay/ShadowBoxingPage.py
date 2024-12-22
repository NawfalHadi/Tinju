import time
import os
import random
import csv

import pygame
import socket
import threading
import subprocess

from main.helper.Actions import *
from main.assets.ImagePath import *
from main.helper.constants import *
from main.helper.ui_elements.button import *
from main.helper.ui_elements.Attribute import *


screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Shadow Boxing')

class ShadowBoxingPage:
    def __init__(self) -> None:
        self.screen = screen
        self.running = True
        self.isPaused = False
        self.img = self.image = pygame.image.load(PLACE_RING_SIDE)
        self.player_image = pygame.image.load(BOT_IDLE_IMG[0])

        "=== CONTROLLER ==="
        self.controller_process = None
        self.player_action = ACTIONS[0]

        "=== SOCKET ==="
        self.show_loading = True
        self.sock = None
        
        "=== INTERFACE ==="
        self.setup_pose_est()
        

    def setup_pose_est(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((SERVER_ADDRESS, SERVER_PORT))
        self.sock.listen()

        print(f"Server listening on {SERVER_ADDRESS}:{SERVER_PORT}")
        threading.Thread(target=self.receive_data, daemon=True).start()
        threading.Thread(target=self.start_controller, daemon=True).start()

    def start_controller(self):
        script_path = os.path.join("main", "gameplay", "PoseController.py")
        self.controller_process = subprocess.Popen(["python", script_path])

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
                            print(self.player_action)
                            if data != "Pause":
                                self.player_image = pygame.image.load(ACTIONS_IMAGE[data][0])
                                self.isPaused = False
                            elif data == "Pause":
                                self.isPaused = True

                    except ConnectionResetError:
                        print("Connection Reset")
        except :
            pass

    def show_pause_screen(self):
        self.pause_screen = pygame.draw.rect(self.screen, FOREGROUND, pygame.Rect(50, 50, 924, 476))

        font = pygame.font.Font(None, 48) 
        text = "Mundur Untuk Melanjutkan" 
        text_surface = font.render(text, True, WHITE)

        text_rect = text_surface.get_rect(center=(512, 288))
        self.screen.blit(text_surface, text_rect)

        self.quit_button = Button("Quit", 462, 350, 150, 50, BACKGROUND, FOREGROUND, self.quit)
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
                
                if self.isPaused:
                    self.quit_button.is_clicked(event)

            if not self.show_loading and not self.isPaused:
                screen.blit(self.player_image, (-80, 180))
            elif self.isPaused:
                self.show_pause_screen()
    
            pygame.display.update()
            pygame.time.Clock().tick(60)