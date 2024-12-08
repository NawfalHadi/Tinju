import time
import os

import pygame
import socket
import threading
import subprocess

from main.assets.ImagePath import *
from main.helper.constants import *
from main.helper.ui_elements.button import *

padworks = [
    ["Offensive \nPadworks", ["jab", "straight", "guard", "duck", "jab"], "00:00:00"],
    ["Defensive \nPadworks", ["guard", "straigth", "jab", "straigth", "jab", "guard", "jab"], "00:50:21"],
    ["First Padworks", ["jab", "straigth", "jab", "straigth", "jab", "guard", "jab"], "00:00:00"],
    ["Long Padworks", ["jab", "straigth", "jab", "straigth", "jab", "guard", "jab"], "00:00:12"],
    ["Short Padworks", ["jab", "straigth", "jab", "straigth", "jab", "guard", "jab"], "00:00:20"],
    ["Jab Straight \nPadworks", ["jab", "straigth", "jab", "straigth", "jab", "guard", "jab"], "00:00:00"],
    ["Anu Padworks", ["jab", "straigth", "jab", "straigth", "jab", "guard", "jab"], "00:00:32"],
    ["Selebeew \nPadworks", ["jab", "straigth", "jab", "straigth", "jab", "guard", "jab"], "00:00:00"],
    ["Laufey", ["jab", "straigth", "jab", "straigth", "jab", "guard", "jab"], "00:00:31"],
    ["Nawfal \nHadi", ["jab", "straigth", "jab", "straigth", "jab", "guard", "jab"], "10:00:00"],
]

# Scroll settings
SCROLL_SPEED = 20
ITEM_HEIGHT = 100

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Padworks')

font = pygame.font.Font(None, 36)


class PadworkList:
    def __init__(self) -> None:
        self.screen = screen
        self.running = True
        "=== PREVIEW ==="
        self.title = "Title \nPadworks"
        self.timer = "00:00:00"

        "=== SCROLL SETTINGS ==="
        self.scroll_pos = 0
        self.scroll_speed = 20
        self.scroll_max = len(padworks) * ITEM_HEIGHT - 430

        self.create_button()

    def draw_interface(self):
        self.padwork_preview = self.create_card(f"{self.title}", 20, 20)
        
        list_rect = pygame.Rect(self.padwork_preview.right + 20, self.padwork_preview.top,
                                590, 430)
        self.create_list(list_rect)
        
    def create_list(self, list_rect):
        pygame.draw.rect(self.screen, BACKGROUND, list_rect)

        # Render visible portion of list
        start_idx = self.scroll_pos // ITEM_HEIGHT
        end_idx = (self.scroll_pos + list_rect.height) // ITEM_HEIGHT + 1
        
        self.buttons = []

        for i, item in enumerate(padworks[start_idx:end_idx], start=start_idx):
            item_y = list_rect.y + (i * ITEM_HEIGHT - self.scroll_pos)
            
            # text = font.render(str(item[0]), True, BLACK)
            # self.screen.blit(text, (list_rect.x + 5, item_y))

            button = ButtonList(
                text=str(item[0]),
                x=self.padwork_preview.right + 20,
                y=item_y,
                width=595, height=65,
                color = WHITE,
                hover_color= FOREGROUND,
                action=lambda i=i: self.start_padwork(padworks[i]),
                action_hover=lambda i=i: self.button_hover(padworks[i][0], padworks[i][2])
                )
            self.buttons.append(button)
        
        for button in self.buttons:
            button.draw(self.screen, font_color=FOREGROUND, font_hover=WHITE)
    
    def button_hover(self, title, times):
        self.title = title
        self.timer = times

    def create_card(self, text, rightOf, bottomOf):
        rect = pygame.Rect(rightOf, bottomOf, 315, 536)
        pygame.draw.rect(self.screen, FOREGROUND, rect)

        rect_2 = pygame.Rect(rect.left + 20, rect.top + 20, 275, 275)
        pygame.draw.rect(self.screen, FOREGROUND_2, rect_2)

        font = pygame.font.Font(None, 36)
        lines = text.split('\n')
        
        line_height = font.size("Tg")[1]  # Approximate height of one line
        total_text_height = line_height * len(lines)
        
        start_y = rect_2.top + (rect_2.height - total_text_height) // 2

        for i, line in enumerate(lines):
            text_surface = font.render(line, True, WHITE)
            text_rect = text_surface.get_rect(center=(rect_2.centerx, start_y + i * line_height))
            
            self.screen.blit(text_surface, text_rect)

        button = Button(self.timer, rect.left + 20, rect.bottom - 90,
                        275, 70, FOREGROUND_2, WHITE)
        
        button.draw(self.screen)

        return rect  
    
    def create_button(self):
        self.exit_button = Button('Menu', screen.get_width() - (200 + SCREEN_MARGIN),
                                   screen.get_rect().bottom - (50 + SCREEN_MARGIN), 200, 50, GRAY, RED, self.exit_page)
    
    def start_padwork(self, padworks):
        PadworkPage(padworks).run()
        pass

    def exit_page(self):
        self.running = False

    def run(self):
        while self.running:
            self.screen.fill(BACKGROUND)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 4:
                        self.scroll_pos = max(self.scroll_pos - SCROLL_SPEED, 0)
                    elif event.button == 5:
                        self.scroll_pos = min(self.scroll_pos + SCROLL_SPEED, self.scroll_max)

                for button in self.buttons:
                    if button.is_clicked(event):
                        break
                    if button.is_hover():
                        continue
                
                self.exit_button.is_clicked(event)

            self.exit_button.draw(screen)  
            self.draw_interface()            
            pygame.display.update()

class PadworkPage:
    def __init__(self, data) -> None:
        self.screen = screen
        self.running = True
        self.img = self.image = pygame.image.load(PLACE_RING)

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
            screen.blit(self.image, (0, 0))

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
        


