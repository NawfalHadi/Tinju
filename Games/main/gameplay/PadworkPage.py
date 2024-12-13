import time
import os
import random
import csv

import pygame
import socket
import threading
import subprocess

from main.assets.ImagePath import *
from main.helper.constants import *
from main.helper.ui_elements.button import *
from main.helper.ui_elements.Attribute import *

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

        self.padworks = []
        self.read_padworks_csv()

        "=== PREVIEW ==="
        self.title = "Title \nPadworks"
        self.timer = "00:00:00"

        "=== SCROLL SETTINGS ==="
        self.scroll_pos = 0
        self.scroll_speed = 20
        self.scroll_max = len(self.padworks) * ITEM_HEIGHT - 430

        self.create_button()

    def read_padworks_csv(self):
        with open("main/information/padworks.csv") as padworks_csv:
            reader = csv.DictReader(padworks_csv)

            for row in reader:
                name = row["name"]
                seq = row["sequences"].split(", ")
                rec = row["record"]

                self.padworks.append([name, seq, rec])


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

        for i, item in enumerate(self.padworks[start_idx:end_idx], start=start_idx):
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
                action=lambda i=i: self.start_padwork(self.padworks[i]),
                action_hover=lambda i=i: self.button_hover(self.padworks[i][0], self.padworks[i][2])
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
        pygame.event.post(pygame.event.Event(pygame.QUIT))

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
        self.totalCountdown = 4
        self.isCountdownFinish = False
        self.countdownText = "" 

        self.start_time = 0
        self.elapsed_time = 0

        "=== PADWORKS ==="
        self.padworks = data
        self.list_pose = len(data[1])
        self.current_pose = None
        self.current_image = pygame.image.load(PADWROKS_ACTIONS_IMAGE["Jab"][0])
        self.next_pose = None
        self.isPadworkFinish = False
        
        "=== INTERFACE ==="
        self.draw_interface()

        self.start_padwork()
    
    def format_time(self, time_string):
        minutes, seconds, milliseconds = map(int, time_string.split(':'))
        return minutes, seconds, milliseconds
        

    def start_padwork(self):
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

                    except ConnectionResetError:
                        print("Connection Reset")
        except :
            pass

    def draw_interface(self):
        center_x = (SCREEN_WIDTH - 250) // 2 
        self.pose_requirement_shadow = Attributes(center_x, 20, 250, 50, SHADOW_FOREGROUND)
        self.pose_requirement = Button(str(self.current_pose), center_x + 5, self.pose_requirement_shadow.rect.top + 10, 250, 50, FOREGROUND, FOREGROUND)
        
    def update_interface(self):
        # Constant Changin Interface Put Here
        center_x = (SCREEN_WIDTH - 250) // 2
        self.pose_requirement_shadow = Attributes(center_x, 20, 250, 50, SHADOW_FOREGROUND)
        self.pose_requirement = Button(str(self.countdownText), center_x + 5, self.pose_requirement_shadow.rect.top + 10, 250, 50, FOREGROUND, FOREGROUND)


        # Text Requirements
        font = pygame.font.Font(None, 48)  # Font and size
        text = self.current_pose
        text_surface = font.render(text, True, WHITE)
        text_rect = text_surface.get_rect(center=(self.screen.get_width() // 2, self.pose_requirement.rect.bottom + 48))

        self.screen.blit(text_surface, text_rect)

    def update_padwork(self):
        padwork_list = self.padworks[1]

        try:
            if not self.isPadworkFinish:
                if self.list_pose > 0:
                
                    index = len(padwork_list) - self.list_pose
                    self.current_pose = padwork_list[index]
                    self.current_image = pygame.image.load(PADWROKS_ACTIONS_IMAGE[self.current_pose][0])
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
                old_time = self.format_time(self.padworks[2])
                current_time = self.format_time(self.countdownText)
                
                if old_time < current_time or old_time == (0, 0, 0):
                    self.save_record(current_time)
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
                else:
                    print("Faster BRUV")
                        
        except Exception as e:
            print("List Pose", e)

    def save_record(self, record):

        filename = "main/information/padworks.csv" 
        with open(filename, 'r') as file:
            reader = csv.reader(file)
            rows = list(reader)

        for row in rows:
            if row[0] == self.padworks[0]:
                row[2] = f"{record[0]:02d}:{record[1]:02d}:{record[2]:02d}"
                break
        
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(rows)

    
    def no_function(self):
        print("test")
        pass

    def pause(self):
        pass

    def start_countdown(self):
        if not self.isCountdownFinish:
            if self.totalCountdown > 0:
                self.totalCountdown -= 1 / 60
            else:
                self.isCountdownFinish = True

            minutes = int(self.totalCountdown) // 60
            seconds = int(self.totalCountdown) % 60

            self.countdownText = f"{minutes:02d}:{seconds:02d}"

    def stopwatch(self):
        if self.isCountdownFinish:
            self.totalCountdown += 1 / 60

            minutes = int(self.totalCountdown) // 60
            seconds = int(self.totalCountdown) % 60
            milliseconds = int((self.totalCountdown % 1) * 1000)

            self.countdownText = f"{minutes:02d}:{seconds:02d}:{milliseconds:02d}"
            
    
    def run(self):
        while self.running:
            self.screen.fill(WHITE)
            screen.blit(self.image, (0, 0))
            screen.blit(self.current_image, (119, 139))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.controller_process.terminate()
                    self.running = False
                    self.sock.close()

            if not self.show_loading:
                self.pose_requirement_shadow.draw(screen)
                self.pose_requirement.draw(screen)
                self.update_interface()
                if not self.isCountdownFinish:
                    self.start_countdown()
                else:
                    self.stopwatch()
                    self.update_padwork()


            pygame.display.update()
            pygame.time.Clock().tick(60)
        


