# constants.py
import math
import pygame

# Базовые размеры
DEFAULT_SCREEN_WIDTH = 1200
DEFAULT_SCREEN_HEIGHT = 900
UI_PANEL_WIDTH = 300

class ScreenConfig:
    """Динамическая конфигурация экрана"""
    def __init__(self):
        self.width = DEFAULT_SCREEN_WIDTH
        self.height = DEFAULT_SCREEN_HEIGHT
        self.sim_width = self.width - UI_PANEL_WIDTH
        self.sim_height = self.height

    def update(self, width: int, height: int):
        self.width = max(800, width)
        self.height = max(600, height)
        self.sim_width = self.width - UI_PANEL_WIDTH
        self.sim_height = self.height

# Глобальный экземпляр конфигурации
screen_config = ScreenConfig()

# Константы (физика / размеры)
ROAD_SIZE = 400  # meters from center to edge (логическая размерность)
LANE_WIDTH = 15
NUM_LANES = 3
PED_SIZE_MIN = 1.5
PED_SIZE_MAX = 2.5
PED_SPEED_MIN = 4.0
PED_SPEED_MAX = 6.0
PED_GROUP_PROB = 0.3
PED_GROUP_SIZE = (2, 5)
PED_REPULSION = 5.0
PED_ATTRACTION = 0.5
INTERVAL_MIN = 1
INTERVAL_MAX = 10
PED_INTERVAL_MIN = 3
PED_INTERVAL_MAX = 10
SAFE_DIST = 10
SAFE_LANE_CHANGE_DIST = 20
VISIBILITY = 100
LIGHT_GREEN = 30
LIGHT_YELLOW = 3
LIGHT_RED = 30
MAX_CARS = 200
SPEED_MIN = 8.33  # m/s (30 km/h)
SPEED_MAX = 33.33  # m/s (120 km/h)
TURN_RADIUS = LANE_WIDTH * 1.5
SIDEWALK_WIDTH = 10
FPS = 60

# Colors (RGB)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (100, 100, 100)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (50, 50, 50)
UI_BG = (70, 70, 70)
UI_HOVER = (150, 150, 150)
UI_ACTIVE = (100, 100, 100)
UI_TEXT = (255, 255, 255)
UI_BORDER = (30, 30, 30)

# Directions and turns
DIR_INS = ['from_west', 'from_east', 'from_north', 'from_south']
TURN_PROBS = [0.6, 0.2, 0.2]  # [straight, right, left] (подбирается как в исходнике)

# Конфигурация поворотов (центры и углы) — используется для округления при поворотах
TURN_HEADINGS = {
    'from_west': (1, 0),
    'from_east': (-1, 0),
    'from_north': (0, 1),
    'from_south': (0, -1)
}

TURN_CENTERS = {
    'from_west': {1: (0, TURN_RADIUS), 2: (0, -TURN_RADIUS)},
    'from_east': {1: (0, -TURN_RADIUS), 2: (0, TURN_RADIUS)},
    'from_north': {1: (-TURN_RADIUS, 0), 2: (TURN_RADIUS, 0)},
    'from_south': {1: (TURN_RADIUS, 0), 2: (-TURN_RADIUS, 0)}
}

TURN_ANGLES = {
    'from_west': {0: None, 1: (math.pi, math.pi / 2), 2: (math.pi, 3 * math.pi / 2)},
    'from_east': {0: None, 1: (0, 3 * math.pi / 2), 2: (0, math.pi / 2)},
    'from_north': {0: None, 1: (math.pi / 2, math.pi), 2: (math.pi / 2, 0)},
    'from_south': {0: None, 1: (3 * math.pi / 2, 0), 2: (3 * math.pi / 2, math.pi)}
}
