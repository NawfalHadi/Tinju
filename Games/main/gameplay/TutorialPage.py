import os

import pygame
import socket
import threading
import subprocess

from main.helper.constants import *
from main.helper.ui_elements.TextBox import TextBox
from main.helper.ui_elements.button import Button

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Padworks')

class TutorialPage:
    def __init__(self) -> None:
        self.screen = screen
        self.running = True

        "=== CONTROLLER ==="
        self.controller_process = None
        self.isPaused = False
        self.player_action = ACTIONS[0]

        "=== STEPS ==="
        self.inTutorialMenu = True
        self.inTutorialOffensse = False
        self.inTutorialGuard = False
        self.inTutorialDuck = False

        "=== TUTORIAL OFFENSE ==="
        self.isTutorialOffenseFinish = False
        self.tutorial_offense = ["Everytime you throw an offense, pull to guard,\n for throwing the same offense attack",
                                 "Give Me a 5 Jabs, Like this","Try Throw 5 Straigth",
                                 "Combine Left Hook and Right Hook 3 Times",
                                 "Here you throw uppercut, try left 3 times","then right uppercut 3 times also"]

        self.jab_counter = 0
        self.straigth_counter = 0
        self.leftHook_counter = 0
        self.rigthHook_counter = 0
        self.leftUppercut_counter = 0
        self.rigthUppercut_counter = 0

        "=== TUTORIAL GUARD ==="
        self.tutorial_guard = ["defense the face, guard like this", 
                               "keep the your hand up to cover your face",
                               "now guard your body like this", "i'll punch 3 times",
                               "try to slip to the left & rigth 3 times like this",
                               "nunduk sampai garis merah dibawah nya, keluar frame, untuk menghindar kebawah"]
        
        self.faceGuard_counter = 0
        self.bodyGuard_counter = 0
        self.slipLeft_counter = 0
        self.slipRigth_counter = 0
        self.duck_counter = 0

        "=== TUTORIAL BODY OFFENSE ==="
        self.tutorial_bodyOffense = ["Sambil menunduk lakukan gerakan offense seperti ini", 
                                     "Coba Jab sambil nunduk", "Lakukan straigth sambil nunduk",
                                     "Terus hook kanan sama kiri", "mantap, maju buat keluar dari tutorial"]
        
        self.lowJab_counter = 0
        self.lowStraigth_counter = 0
        self.lowLeftHook_counter = 0
        self.lowRigthHook_counter = 0

        "=== TEXT ==="
        self.explanation = ""

        self.draw_interface()
        # self.setup()

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
        self.text_dialog = TextBox(self.explanation, 0,
                                (self.screen.get_height() // 2) + 100,
                                self.screen.get_width(), (self.screen.get_height() // 2) - 100)
        
        self.pause_button = Button("Continue", (self.screen.get_width() // 2) - 300 // 2,
                                    (self.screen.get_height() // 2) - 100 // 2,
                                   300, 100, GRAY, FOREGROUND, self.next_tutorial)
    
    def step_menu(self):
        if self.inTutorialMenu:
            self.explanation = "Maju Kedepan Untuk Pause Permainan, untuk sekarang\n akan mempelihatkan tombol lanjutkan tutorial berikutnya"

            if self.isPaused:
                self.pause_button.draw(self.screen)

            self.draw_interface()

    def next_tutorial(self):
        self.isPaused = False
        self.inTutorialMenu = False
        self.inTutorialOffensse = True


    def step_offense(self):
        if self.inTutorialOffensse:
            self.explanation = self.tutorial_offense[0]
            self.draw_interface()
            print(self.player_action)


            if self.jab_counter < 5 :
                if self.player_action == "Jab":
                    self.jab_counter += 1

                if self.jab_counter >= 1 :
                    self.explanation = self.tutorial_offense[1]
                    self.draw_interface()
            
            elif self.straigth_counter <= 5:
                self.explanation = self.tutorial_offense[2]
                self.draw_interface()


                if self.player_action == "Straigth":
                    self.straigth_counter += 1

            elif self.leftHook_counter < 3 or self.rigthHook_counter < 3:
                self.explanation = self.tutorial_offense[3]
                self.draw_interface()

                if self.player_action == "Left Hook":
                    self.leftHook_counter += 1

                elif self.player_action == "Rigth Hook":
                    self.rigthHook_counter += 1

            elif self.leftUppercut_counter < 3:
                self.explanation = self.tutorial_offense[4]
                self.draw_interface()
                
                if self.player_action == "Left Uppercut":
                    self.leftUppercut_counter += 1
                
            elif self.rigthUppercut_counter < 4:
                self.explanation = self.tutorial_offense[5]
                self.draw_interface()

                if self.rigthUppercut_counter == 3:
                    self.explanation = "Once Again, and we move to guaard tutorial"

                if self.player_action == "Rigth Uppercut":
                    self.rigthUppercut_counter += 1

            else:
                self.inTutorialOffensse = False
                self.inTutorialGuard = True
                
    def step_guard(self):
        if self.inTutorialGuard:
            self.explanation = "Guard Offense"
            self.draw_interface()

    def step_duck(self):
        if self.inTutorialDuck:
            self.explanation = "Duck Offennse"
            self.draw_interface()

    def handle_key_press(self):
        # Temporary Function
        keys = pygame.key.get_pressed()  # Get a list of all pressed keys
        
        if keys[pygame.K_SPACE]:  # Check if the UP arrow key is pressed
            self.isPaused = True
        if keys[pygame.K_ESCAPE]:  # Check if the DOWN arrow key is pressed
            self.isPaused = False

        if keys[pygame.K_j]:  # Jab
            self.player_action = "Jab"
        if keys[pygame.K_s]:  # Straigth
            self.player_action = "Straigth"
        if keys[pygame.K_h]:  # Left Hook
            self.player_action = "Left Hook"
        if keys[pygame.K_a]:  # Rigth Hook
            self.player_action = "Rigth Hook"
        if keys[pygame.K_b]:  # Left Uppercut
            self.player_action = "Left Uppercut"
        if keys[pygame.K_c]:  # Rigth Uppercut
            self.player_action = "Rigth Uppercut"    

    def run(self):
        while self.running:
            self.screen.fill(BACKGROUND)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # self.controller_process.terminate()
                    self.running = False

                self.pause_button.is_clicked(event)

            self.handle_key_press()

            self.text_dialog.draw(screen)
            
            self.step_menu()
            self.step_offense()
            self.step_guard()
            self.step_duck()
            
            pygame.display.update()
            pygame.time.Clock().tick(60)
                    

