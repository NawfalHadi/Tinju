import pygame
import os, csv


from main.helper.constants import *
from main.assets.ImagePath import *
from main.helper.ui_elements.button import Button

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Bot Information')  

new_row = ["Jubaer", "main/bot/yours/Jubaer.pkl", "1/0/0", "1"]

class BotInformation:
    def __init__(self):
        self.screen = screen
        self.isRunning = True
        self.bot_info = "main/information/your_bots.csv"
        self.q_points_info = pygame.image.load(INFO_Q_POINTS_MIN)

        "=== BOT INFORMATION ==="
        self.bot_name = ""
        self.bot_path = ""
        self.bot_record = ""
        self.bot_trng = 0 

        self.check_information(self.bot_info)

    def check_information(self, file_name):
        # Check if the file exists
        if os.path.exists(file_name):
            # Read the existing data to see if the row already exists
            with open(file_name, mode='r') as file:
                reader = csv.reader(file)
                data = list(reader)
            
            # Check if the row already exists (excluding the header)
            if len(data) > 1:
                self.update_bot_info()
            else:
                print("The file exists but contains no data rows. Adding a new row.")
                with open(file_name, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(new_row)
                    print("New row added.")
        else:
            with open(file_name, mode='w', newline='') as file:
                writer = csv.writer(file)
                # Define the header
                header = ["name", "model_path", "record", "training"]
                writer.writerow(header)
                writer.writerow(new_row)
                print("File created and row added.")

    def update_bot_info(self):
        with open(self.bot_info, mode='r') as file:
            reader = csv.DictReader(file)
            first_row = next(reader, None)  # Get the first row or None if the file is empty

        if first_row:
            print(first_row)
            self.bot_name = first_row["name"]          # Access by column name
            self.bot_path = first_row["model_path"]    # Access by column name
            self.bot_record = first_row["record"]      # Access by column name
            self.bot_trng = first_row["training"]      # Access by column name

    def draw_interface(self):
        self.bot_information, self.bot_training = self.create_card(self.bot_name, 20, 20)
        self.bot_sparring_btn = Button("Simulate My Bot Versus Bot", self.bot_information.right + 10, 392, self.q_points_info.get_rect().width, 50, FOREGROUND, WHITE, None, 32)
        self.bot_training_btn = Button("Train The Bot", self.bot_information.right + 10, self.bot_sparring_btn.rect.bottom + 20, self.q_points_info.get_rect().width, 50, FOREGROUND, WHITE, self.start_training, 32)

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

        button = Button(f"Training : {self.bot_trng}x", rect.left + 20, rect.bottom - 90,
                        275, 70, FOREGROUND_2, WHITE, action=self.start_training, font=32)
        
        button.draw(self.screen)

        return rect, button

    def start_training(self):
        model = self.bot_path
        
        from main.gameplay.BotTraining import BotTraining
        BotTraining(model).run()

    def start_fight(self):
        # Your bot vs default bot
        pass

    def run(self):
        while self.isRunning:
            self.screen.fill(BACKGROUND)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.isRunning = False

                self.bot_training.is_clicked(event)
                self.bot_training_btn.is_clicked(event)

            self.draw_interface()
            self.screen.blit(pygame.image.load(INFO_Q_POINTS_MIN), (self.bot_information.right + 10, self.bot_information.top)) 
            self.bot_sparring_btn.draw(screen)
            self.bot_training_btn.draw(screen)

            pygame.display.update()
            pygame.time.Clock().tick(60)

