# constants.py

# ====== SCREEN DIMENSION 1=======
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 576

SCREEN_MARGIN = 20
BUTTON_MARGIN = 40
# =================================

# ====== COLORS =======
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)

BACKGROUND = (32, 40, 105)
FOREGROUND = (237, 57, 98)


# ====== FONTS =======
FONT_SIZE = 40

# ====== SOCKET =======
SERVER_ADDRESS = 'localhost'
SERVER_PORT = 12345

# ====== GAMES =====
"""
- Attribtues games are store in here
- actions : the action that are available in this games
- coach_ask : the randomize coach ask for padwork
- model : anything that realated to bot models
"""
# ====== ATTRIBUTES =====
MAX_HP = 100
MAX_STM = 100

# ====== ACTIONS =====
# ACTION = ["no_guard", "guard", "jab", "straigth", "left_hook", "right_hook"]
ACTIONS  = ["Idle","Jab", "Guard"]


# ======= COACHES =====
C_ASKPOSE = ["Give me a ", "Throw the ", "Show me your ", "I want see your "]

# ======= BOT MODELS =====

ALPHA = 0.1  # Learning rate
GAMMA = 0.9  # Discount factor
EPSILON = 0.1  # Exploration factor