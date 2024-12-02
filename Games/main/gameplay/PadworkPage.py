import time
import os

import pygame
import socket
import threading
import subprocess

from main.helper.constants import *
from main.helper.ui_elements.button import *

padworks = [
    [1, ["jab", "straight", "guard", "duck", "jab"], "00:00:00"],
    [2, ["jab", "straigth", "jab", "straigth", "jab", "guard", "jab"], "00:00:00"]
]

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Padworks')

class PadworkList:
    def __init__(self) -> None:
        self.screen = screen
        self.running = True

        self.create_button()
    def create_button(self):
        self.exit_button = Button('Back', screen.get_width() - (200 + SCREEN_MARGIN),
                                   SCREEN_MARGIN, 200, 100, GRAY, RED, self.start_padwork)
        
    
    def start_padwork(self):
        PadworkPage(padworks[1]).run()
        pass

    def exit_page(self):
        self.running = False

    def run(self):
        while self.running:
            self.screen.fill(WHITE)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                self.exit_button.is_clicked(event)

            self.exit_button.draw(screen)            
            pygame.display.update()

class PadworkPage:
    def __init__(self, data) -> None:
        self.screen = screen
        self.running = True

        "=== CONTROLLER ==="
        self.controller_process = None
        self.player_action = ACTIONS[0]

        "=== SOCKET ==="
        self.show_loading = True
        self.sock = None
        

        "=== TIMER ==="
        self.isCountdownFinish = False

        "=== PADWORKS ==="
        self.padworks = data
        self.list_pose = len(data[1])
        self.current_pose = None
        self.next_pose = None
        self.isPadworkFinish = False
        
        "=== INTERFACE ==="
        self.draw_interface()

        self.start_padwork()

    def start_padwork(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((SERVER_ADDRESS, SERVER_PORT))
        self.sock.listen()

        print(f"Server listening on {SERVER_ADDRESS}:{SERVER_PORT}")
        threading.Thread(target=self.receive_data, daemon=True).start()
        threading.Thread(target=self.start_controller, daemon=True).start()

    def start_controller(self):
        script_path = os.path.join("main", "gameplay", "Controller.py")
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

                    except ConnectionResetError:
                        print("error")
        except :
            pass

    def draw_interface(self):
        self.pose_requirement = Button(str(self.current_pose), 50, 50, 250, 100, RED, RED, self.no_function)
        

    def update_interface(self):
        # Constant Changin Interface Put Here
        self.pose_requirement = Button(str(self.current_pose), 50, 50, 100, 50, GRAY, GRAY, self.no_function)

    def update_padwork(self):
        padwork_list = self.padworks[1]

        try:
            if not self.isPadworkFinish:
                if self.list_pose > 0:
                
                    index = len(padwork_list) - self.list_pose
                    self.current_pose = padwork_list[index]
                    try:
                        self.next_pose = padwork_list[index + 1]
                    except Exception as e:
                        self.isPadworkFinish = True
                        pass
                    
                    if self.player_action == self.current_pose.capitalize():
                        self.list_pose -= 1
                        if self.isPadworkFinish:
                            self.current_pose = "Done"
                        else:
                            self.current_pose = self.next_pose
            else:
                print("Padworks Done")

                        
                        
        except Exception as e:
            print("List Pose", e)


    
    def no_function(self):
        print("test")
        pass

    def pause(self):
        pass

    def timer(self):
        font = pygame.font.Font(None, 100)
        
        self.isCountdownFinish = True

        # for i in range (3, 0, -1):
        #     text = font.render(str(i), True, BLACK)
        #     text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

        #     screen.blit(text, text_rect)
            

        #     screen.fill(WHITE)            

        # else:
        #     print("Countdown Finish")

    def stopwatch(self):
        pass

    
    def run(self):
        while self.running:
            self.screen.fill(WHITE)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.controller_process.terminate()
                    self.running = False
                    self.sock.close()

            if not self.show_loading:
                self.pose_requirement.draw(screen)
                self.update_interface()
                if not self.isCountdownFinish:
                    self.timer()
                else:
                    self.stopwatch()
                    self.update_padwork()


            pygame.display.update()
            pygame.time.Clock().tick(60)
        


