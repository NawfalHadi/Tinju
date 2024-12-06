import os

import pygame
import socket
import threading
import subprocess

from main.assets.ImagePath import *
from main.helper.constants import *
from main.helper.ui_elements.TextBox import TextBox
from main.helper.ui_elements.button import Button

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Padworks')

class TutorialPage:
    def __init__(self) -> None:
        self.screen = screen
        self.running = True
        self.isLoading = True

        "=== CONTROLLER ==="
        self.controller_process = None
        self.isPaused = False
        self.player_action = ACTIONS[0]

        "=== STEPS ==="
        self.inTutorialMenu = False
        self.inTutorialOffensse = False
        self.inTutorialGuard = False
        self.inTutorialLowOffence = False

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
        self.tutorial_guard = ["Lindungin muka pakai tangan kayak gini.", 
                               "Coba lempar pukulan apa saja, terus guard lagi",
                               "Untuk melindungi badan turunkan siku mu sampe ke perut \ncoba kanan dan kiri 3 kali",
                               "coba untuk menghindar ke kiri seperti ini, lalu ke kanan 3 kali",
                               "nunduk sampai garis merah dibawah ini, \nkeluar frame untuk menghindar kebawah",
                               "Lalu naik lagi dan turun lagi sampai 2 kali"]
        
        self.faceGuard_counter = 0
        self.bodyLeftGuard_counter = 0
        self.bodyRightGuard_counter = 0
        self.slipLeft_counter = 0
        self.slipRigth_counter = 0
        self.duck_counter = 0

        "=== TUTORIAL BODY OFFENSE ==="
        self.tutorial_bodyOffense = ["Sambil menunduk lakukan gerakan offense seperti ini", 
                                     "Coba Gunakan Jab 5 kali", "Lakukan straigth sambil nunduk 3 kali",
                                     "Terus hook kanan sama kiri masing masing 5 kali", "mantap terakhir, maju buat keluar dari tutorial"]
        
        self.lowJab_counter = 0
        self.lowStraigth_counter = 0
        self.lowLeftHook_counter = 0
        self.lowRigthHook_counter = 0

        "=== CHANGING VIEW ==="
        self.explanation = ""
        self.image = None

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
                            print(self.player_action)
                            self.counter_offense()
                            self.counter_defence()

                    except ConnectionResetError:
                        print("error")
        except :
            pass

    def start_controller(self):
        script_path = os.path.join("main", "gameplay", "PoseController.py")
        self.controller_process = subprocess.Popen(["python", script_path])

    def draw_interface(self):

        self.text_dialog_shadow = TextBox("", 40, self.screen.get_rect().bottom - 176, 950, 145, SHADOW_FOREGROUND)
        self.text_dialog = TextBox(self.explanation, 30, self.text_dialog_shadow.rect.top - 10, 950, 145)
        self.notes = Button("Notes", self.text_dialog.rect.left + 30, self.text_dialog.rect.top - 30, 210, 40, WHITE, WHITE, font=30)
        
        self.pause_button = Button("Continue", (self.screen.get_width() // 2) - 300 // 2,
                                    (self.screen.get_height() // 2) - 100 // 2,
                                   300, 100, GRAY, FOREGROUND, self.next_tutorial)
    
    def step_loading(self):
        if self.isLoading:
            self.image = pygame.image.load(TUTORIAL_WAIT_IMG)
            screen.blit(self.image, (327, 71))

            self.explanation = "Tunggu, Nyalain Pose Estimationnya Dulu"

            self.draw_interface()
        else:
            self.inTutorialMenu = True

    def step_menu(self):
        if self.inTutorialMenu:
            self.image = pygame.image.load(TUTORIAL_PAUSE_IMG)
            screen.blit(self.image, (327, 71))

            self.explanation = "Maju dekati kamera sampai garis yang ditunjuk pada gambar keluar\nframe untuk memberhentikan permainan, \ndan klik continue untuk tutorial berikutnya."

            if self.isPaused:
                self.pause_button.draw(self.screen)

            self.draw_interface()

    def next_tutorial(self):
        self.isPaused = False
        self.inTutorialMenu = False
        # self.inTutorialOffensse = True
        self.inTutorialGuard = True

    def step_offense(self):
        if self.inTutorialOffensse:
            self.explanation = self.tutorial_offense[0]
            screen.blit(self.image, (327, 71))

            self.draw_interface()

            if self.jab_counter < 5 :
                self.image = pygame.image.load(TUTORIAL_JAB_IMG)
                
                if self.jab_counter >= 1 :
                    self.explanation = self.tutorial_offense[1]
                    self.draw_interface()

                if self.jab_counter == 5:
                    self.straigth_counter = 0
            
            elif self.straigth_counter < 5:
                self.explanation = self.tutorial_offense[2]
                self.draw_interface()

                if self.straigth_counter == 5:
                    self.leftHook_counter = 0
                    self.rigthHook_counter = 0

            elif self.leftHook_counter < 3 or self.rigthHook_counter < 3:
                
                self.explanation = self.tutorial_offense[3]
                self.draw_interface()

                if self.leftHook_counter == 3 and self.rigthHook_counter == 3:
                    self.leftUppercut_counter = 0

            elif self.leftUppercut_counter < 3:
                self.explanation = self.tutorial_offense[4]
                self.draw_interface()
                
                if self.leftUppercut_counter == 3:
                    self.rigthUppercut_counter = 0
                
            elif self.rigthUppercut_counter < 4:
                self.explanation = self.tutorial_offense[5]
                self.draw_interface()

                if self.rigthUppercut_counter == 3:
                    self.explanation = "Once Again, and we move to guaard tutorial"

            else:
                self.inTutorialOffensse = False
                self.inTutorialGuard = True
                
    def counter_offense(self):
        if self.jab_counter < 5 :
            if self.player_action == "Jab":
                self.jab_counter += 1
        
        elif self.straigth_counter < 5:
            if self.player_action == "Straight":
                self.straigth_counter += 1
                print("Straight", self.straigth_counter)

        elif self.leftHook_counter < 3 or self.rigthHook_counter < 3:
            if self.player_action == "Left_Hook":
                self.leftHook_counter += 1
                print("Left Hook", self.leftHook_counter)

            elif self.player_action == "Right_Hook":
                self.rigthHook_counter += 1
                print("Right Hook", self.rigthHook_counter)

        elif self.leftUppercut_counter < 3:            
            if self.player_action == "Left_Uppercut":
                self.leftUppercut_counter += 1
                print("Left Uppercut", self.rigthHook_counter)
            
        elif self.rigthUppercut_counter < 4:
            if self.player_action == "Right_Uppercut":
                self.rigthUppercut_counter += 1
                print("Right Uppercut", self.rigthHook_counter)
    
    def step_guard(self):
        if self.inTutorialGuard:
            self.draw_interface()

            if self.faceGuard_counter < 3:
                # self.image = None
                self.explanation = self.tutorial_guard[0]
                self.draw_interface()

                if self.faceGuard_counter == 1:
                    self.explanation = self.tutorial_guard[1]
                    self.draw_interface()

            elif self.bodyLeftGuard_counter < 3 or self.bodyRightGuard_counter < 3:
                self.explanation = self.tutorial_guard[2]
                self.draw_interface()

                if self.bodyLeftGuard_counter == 1 or self.bodyRightGuard_counter == 1:
                    # Change Image to another side of bodyguard
                    pass
                

            elif self.slipLeft_counter < 3 or self.slipRigth_counter < 3:
                self.explanation = self.tutorial_guard[3]
                self.draw_interface()

                if self.slipLeft_counter == 1 or self.slipRigth_counter == 1:
                    # Change Image to another side of bodyguard
                    pass
                
            elif self.duck_counter < 3:
                self.explanation = self.tutorial_guard[4]
                self.draw_interface()

                if self.duck_counter == 1:
                    self.explanation = self.tutorial_guard[5]
                    self.draw_interface()
                
            else:
                self.inTutorialGuard = False
                self.inTutorialLowOffence = True

    def counter_defence(self):
        if self.inTutorialGuard:
            if self.faceGuard_counter < 3:
                if self.player_action == "Guard":
                    self.faceGuard_counter += 1

            elif self.bodyLeftGuard_counter < 3 or self.bodyRightGuard_counter < 3:
                if self.player_action == "Guard_LeftBody":
                    self.bodyLeftGuard_counter += 1
                    print("Guard Body Left:", self.bodyLeftGuard_counter)

                elif self.player_action == "Guard_RightBody":
                    self.bodyRightGuard_counter += 1
                    print("Guard Body Right:", self.bodyRightGuard_counter)

            elif self.slipLeft_counter < 3 or self.slipRigth_counter < 3:
                if self.player_action == "Slip_Left":
                    self.slipLeft_counter += 1
                    print("Slip Left:", self.slipLeft_counter)

                elif self.player_action == "Slip_Right":
                    self.slipRigth_counter += 1
                    print("Slip Right:", self.slipRigth_counter)

            elif self.duck_counter < 3:
                if self.player_action == "Duck":
                    self.duck_counter += 1
                    print("Duck:", self.duck_counter)

    def step_low_offence(self):
        if self.inTutorialLowOffence:
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
                    self.controller_process.terminate()
                    self.sock.close()
                    self.running = False

                self.pause_button.is_clicked(event)

            # self.handle_key_press()

            self.text_dialog_shadow.draw(screen)
            self.text_dialog.draw(screen)
            self.notes.draw(screen, font_color=FOREGROUND)
            
            self.step_loading()
            self.step_menu()
            self.step_offense()
            self.step_guard()
            self.step_low_offence()
            
            pygame.display.update()
            pygame.time.Clock().tick(60)
                    

