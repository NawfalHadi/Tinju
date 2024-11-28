import os

import pygame
import socket
import threading
import subprocess

from main.helper.constants import *
from main.helper.ui_elements.TextBox import TextBox

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Padworks')

class TutorialPage:
    def __init__(self) -> None:
        self.screen = screen
        self.running = True

        "=== CONTROLLER ==="
        self.controller_process = None
        self.player_action = ACTIONS[0]

        "=== STEPS ==="
        self.tutorial_menu = True
        self.tutorial_offense = False
        self.tutorial_guard = False
        self.tutroial_duck = False

        "=== TEXT ==="
        self.explanation = ""

        self.draw_interface()
        self.setup()

    def setup(self):
        # Starting the thread of controller

        # Socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((SERVER_ADDRESS, SERVER_PORT))
        self.sock.listen()

        print(f"Server listening on {SERVER_ADDRESS}:{SERVER_PORT}")

        threading.Thread(target=self.receive_data, daemon=True).start()
        threading.Thread(target=self.start_controller, daemon=True).start()

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

                    except ConnectionResetError:
                        print("error")
        except :
            pass

    def start_controller(self):
        script_path = os.path.join("main", "gameplay", "Controller.py")
        self.controller_process = subprocess.Popen(["python", script_path])

    def draw_interface(self):
        self.text_dialog = TextBox("Halo Coy, Selamat Pagi", 0,
                                (self.screen.get_height() // 2) + 100,
                                self.screen.get_width(), (self.screen.get_height() // 2) - 100)

    def step_menu(self):
        pass

    def step_offense(self):
        pass

    def step_guard(self):
        pass

    def step_duck(self):
        pass

    def run(self):
        while self.running:
            self.screen.fill(BACKGROUND)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.controller_process.terminate()
                    self.running = False

            self.text_dialog.draw(screen)

            pygame.display.update()
            pygame.time.Clock().tick(60)
                    

