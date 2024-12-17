import os

import pygame
import socket
import threading
import subprocess
import time

from main.assets.ImagePath import *
from main.helper.constants import *
from main.helper.ui_elements.TextBox import TextBox
from main.helper.ui_elements.button import Button
from main.helper.ui_elements.Attribute import Attributes

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Tutorial')

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
        self.inTutorialKnockout = False

        "=== TUTORIAL OFFENSE ==="
        self.isTutorialOffenseFinish = False
        self.tutorial_offense = ["Setiap kali memukul tarik lagi pukulan ke guard,\nUntuk melakukan serangan yang sama",
                                 "Lemparkan 5 pukulan jabs, seperti yang \nada digambar","Sekarang gunakan tangan kanan untuk \nStraight",
                                 "Lemparkan 5 kali pukulan hook kiri dan kanan \nmasing masing 3 kali pukulan",
                                 "Lakukan Uppercut Kiri 3 Kali ","Sekarang coba Uppercut Kanan 3 Kali juga"]

        self.jab_counter = 0
        self.straigth_counter = 0
        self.leftHook_counter = 0
        self.rigthHook_counter = 0
        self.leftUppercut_counter = 0
        self.rigthUppercut_counter = 0

        "=== TUTORIAL GUARD ==="
        self.tutorial_guard = ["Lindungin muka pakai tangan seperti ini untuk \nmelakukan gerakan guard.", 
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
        self.tutorial_bodyOffense = ["Sambil menunduk lakukan gerakan jab seperti ini", 
                                     "Coba Gunakan Jab 5 kali", "Lakukan straight 5 kali",
                                     "Terus hook kanan sama kiri masing masing 3 kali", "mantap terakhir, maju buat keluar dari tutorial"]
        
        self.lowJab_counter = 0
        self.lowStraigth_counter = 0
        self.lowLeftHook_counter = 0
        self.lowRigthHook_counter = 0

        "=== TUTORIAL KNOCKOUT ==="
        self.tutorial_knockout = "Pastikan garis hitam berada antara kotak pink"

        "=== KO SYSTEM ==="
        self.ko_target_speed = 10
        self.ko_target_size = 600
        self.ko_progress = 0
        self.min_pos = 400
        self.max_pos = 0
        self.cur_pos = 400

        self.isGoLeft = False

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
                            self.counter_low_offence()

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
        if self.image:
            screen.blit(self.image, (327, 71))
        else:
            pass
    
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
        # self.inTutorialGuard = True
        # self.inTutorialLowOffence = True
        self.inTutorialKnockout = True

    def step_offense(self):
        if self.inTutorialOffensse:
            self.explanation = self.tutorial_offense[0]
            screen.blit(self.image, (327, 71))

            self.draw_interface()

            if self.jab_counter < 5 :
                self.image = pygame.image.load(TUTORIAL_JAB_IMG)
                self.draw_interface()
                
                if self.jab_counter >= 1 :
                    self.explanation = self.tutorial_offense[1]
                    self.draw_interface()

                if self.jab_counter == 5:
                    self.straigth_counter = 0
            
            elif self.straigth_counter < 5:
                self.image = pygame.image.load(TUTORIAL_STRAIGHT_IMG)
                self.explanation = self.tutorial_offense[2]
                self.draw_interface()

                if self.straigth_counter == 5:
                    self.leftHook_counter = 0
                    self.rigthHook_counter = 0

            elif self.leftHook_counter < 3 or self.rigthHook_counter < 3:
                self.image = pygame.image.load(TUTORIAL_LEFT_HOOK_IMG)
                self.explanation = self.tutorial_offense[3]
                self.draw_interface()

                if self.leftHook_counter == 2:
                    self.image = pygame.image.load(TURORIAL_RIGHT_HOOK_IMG)

                if self.leftHook_counter == 3 and self.rigthHook_counter == 3:
                    self.leftUppercut_counter = 0

            elif self.leftUppercut_counter < 3:
                self.image = pygame.image.load(TUTORIAL_LEFT_UPP_IMG)
                self.explanation = self.tutorial_offense[4]
                self.draw_interface()
                
                if self.leftUppercut_counter == 3:
                    self.rigthUppercut_counter = 0
                
            elif self.rigthUppercut_counter < 4:
                self.image = pygame.image.load(TUTORIAL_RIGHT_UPP_IMG)
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
                self.image = pygame.image.load(TUTORIAL_GUARD_IMG)
                self.explanation = self.tutorial_guard[0]
                self.draw_interface()

                if self.faceGuard_counter == 1:
                    self.explanation = self.tutorial_guard[1]
                    self.draw_interface()

            elif self.bodyLeftGuard_counter < 3 or self.bodyRightGuard_counter < 3:
                self.image = pygame.image.load(TUTORIAL_GUARD_BODY_LEFT_IMG)
                self.explanation = self.tutorial_guard[2]
                self.draw_interface()

                if self.bodyLeftGuard_counter == 1 or self.bodyRightGuard_counter == 1:
                    self.image = pygame.image.load(TUTORIAL_GUARD_BODY_RIGHT_IMG)
                    pass
                

            elif self.slipLeft_counter < 3 or self.slipRigth_counter < 3:
                self.image = pygame.image.load(TUTORIAL_SLIP_LEFT_IMG)
                self.explanation = self.tutorial_guard[3]
                self.draw_interface()

                if self.slipLeft_counter == 1 or self.slipRigth_counter == 1:
                    self.image = pygame.image.load(TUTORIAL_SLIP_RIGHT_IMG)
                    pass
                
            elif self.duck_counter < 3:
                self.image = pygame.image.load(TUTORIAL_DUCK_1_IMG)
                self.explanation = self.tutorial_guard[4]
                self.draw_interface()

                if self.duck_counter == 1:
                    self.image = pygame.image.load(TUTORIAL_DUCK_2_IMG)
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
            self.draw_interface()

            if self.lowJab_counter < 5:
                # self.image = pygame.image.load(BOT_LJ_IMG)
                self.explanation = self.tutorial_bodyOffense[0]
                self.draw_interface()
                if self.lowJab_counter == 1:
                    self.explanation = self.tutorial_bodyOffense[1]
                    self.draw_interface()

            elif self.lowStraigth_counter < 5:
                # self.image = pygame.image.load(BOT_LS_IMG)
                self.explanation = self.tutorial_bodyOffense[2]
                self.draw_interface()
            
            elif self.lowLeftHook_counter < 3 or self.lowRigthHook_counter < 3:
                self.explanation = self.tutorial_bodyOffense[3]
                self.draw_interface()    
            
    def counter_low_offence(self):
        if self.lowJab_counter < 5:
            if self.player_action == "Low_Jab":
                self.lowJab_counter += 1
                print("Low Jab:", self.lowJab_counter)

        elif self.lowStraigth_counter < 5:
            if self.player_action == "Low_Straight":
                self.lowStraigth_counter += 1
                print("Low Straight:", self.lowStraigth_counter)
        
        elif self.lowLeftHook_counter < 3 or self.lowRigthHook_counter < 3:
            if self.player_action == "Left_BodyHook" :
                print("Left Body Hook:", self.lowLeftHook_counter)
                self.lowLeftHook_counter += 1
            
            elif self.player_action == "Right_BodyHook" :
                self.lowRigthHook_counter += 1
                print("Right Body Hook:", self.lowRigthHook_counter)
    
    def step_knockout(self):
        if self.inTutorialKnockout:
            if self.ko_progress == 100:
                self.image = pygame.image.load(TUTORIAL_DONE_IMG)
                self.explanation = "Mantap, Sekarang coba lah permainan nya"
                self.draw_interface()

                try:
                    pygame.event.post(pygame.event.Event(pygame.USEREVENT + 1))
                except Exception as e:
                    print(e)
            else:
                self.explanation = self.tutorial_knockout
                self.image = None
                self.draw_interface()
                
                self.knockout_frame = Attributes((SCREEN_WIDTH // 2) - 400, (SCREEN_HEIGHT // 2), 800, 50, WHITE).draw(self.screen)
                self.knockout_target = Attributes((SCREEN_WIDTH // 2) - self.cur_pos, (SCREEN_HEIGHT // 2) + 2, self.ko_target_size, 46, FOREGROUND)
                self.knockout_target.draw(self.screen)

                self.knockout_square = Attributes((SCREEN_WIDTH // 2) - 0, (SCREEN_HEIGHT // 2) + 2, 10, 46, BLACK)
                self.knockout_square.draw(self.screen)

                ko_progress = ((self.ko_progress) / 100 * 800)

                self.knockout_bg_progress = Attributes((SCREEN_WIDTH // 2) - 400, (SCREEN_HEIGHT // 2) - 100, 800, 50, WHITE).draw(self.screen)
                self.knockout_value_progress = Attributes((SCREEN_WIDTH // 2) - 400, (SCREEN_HEIGHT // 2) - 99, ko_progress, 49, GREEN).draw(self.screen)
                self.update_knockout()



    def update_knockout(self):
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

        left_target, right_target = self.knockout_target.rect.left, self.knockout_target.rect.right
        if left_target < self.knockout_square.rect.centerx and self.knockout_square.rect.centerx < right_target:
            self.ko_progress += 0.5

        self.ko_progress = max(0, min(100, self.ko_progress))

        


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
                if event.type == pygame.QUIT or event.type == pygame.USEREVENT + 1:
                    print("Quit")
                    time.sleep(2)
                    self.controller_process.terminate()
                    self.sock.close()
                    self.running = False

                self.pause_button.is_clicked(event)

            # self.handle_key_press()

            self.text_dialog_shadow.draw(screen)
            self.text_dialog.draw(screen)
            self.notes.draw(screen, font_color=FOREGROUND)

            if self.player_action == "Pause":
                self.isPaused = True
            else:
                self.isPaused = False
            
            self.step_loading()
            self.step_menu()
            self.step_offense()
            self.step_guard()
            self.step_low_offence()
            self.step_knockout()

            
            
            pygame.display.update()
            pygame.time.Clock().tick(60)
                    

