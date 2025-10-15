# constants.py
import pygame
import math

# --------- Параметры симуляции ----------
DEFAULT_SCREEN_WIDTH = 900
DEFAULT_SCREEN_HEIGHT = 900
UI_PANEL_WIDTH = 300
FPS = 60

class ScreenConfig:
    """Динамическая конфигурация экрана"""
    def __init__(self):
        self.width = DEFAULT_SCREEN_WIDTH
        self.height = DEFAULT_SCREEN_HEIGHT
        self.sim_width = self.width - UI_PANEL_WIDTH
        self.sim_height = self.height

    def update(self, width, height):
        self.width = max(800, width)
        self.height = max(600, height)
        self.sim_width = self.width - UI_PANEL_WIDTH
        self.sim_height = self.height

# Глобальный экземпляр конфигурации
screen_config = ScreenConfig()

# Размер перекрестка и полос
LANE_WIDTH = 28
LANES_PER_DIR = 2
ROAD_HALF = 220  # от центра до начала полосы
NUM_LANES = LANES_PER_DIR * 2  # Совместимость с старым кодом
LANES_PER_DIRECTION = LANES_PER_DIR  # Совместимость с старым кодом

# Конвертация скорости: км/ч -> пикселей/сек (приближённо)
KMH_TO_PPS = 1000/3600  # m/s per km/h; but we'll treat 1 m = 1 px roughly
SPEED_SCALE = 0.8  # подгонка визуальной скорости

MIN_KMH, MAX_KMH = 30, 120
SPEED_MIN = MIN_KMH * KMH_TO_PPS * SPEED_SCALE  # Совместимость
SPEED_MAX = MAX_KMH * KMH_TO_PPS * SPEED_SCALE  # Совместимость

# Спавн
SPAWN_INTERVAL_MEAN = 1.2  # сек
SPAWN_JITTER = 0.8

# Безопасная дистанция (в пикселях)
SAFE_DISTANCE = 36
SAFE_DIST = SAFE_DISTANCE  # Совместимость

# Светофор: статический конфиг (можно расширить до динамического)
GREEN_DURATION = 8
YELLOW_DURATION = 2
RED_DURATION = GREEN_DURATION + YELLOW_DURATION  # для противоположного направления

LIGHT_GREEN = GREEN_DURATION  # Совместимость
LIGHT_YELLOW = YELLOW_DURATION  # Совместимость
LIGHT_RED = RED_DURATION  # Совместимость

# Старые константы для совместимости
ROAD_SIZE = ROAD_HALF
INTERSECTION_SIZE = LANES_PER_DIR * LANE_WIDTH * 2
TURN_RADIUS = LANE_WIDTH * 1.5
SIDEWALK_WIDTH = 10
VISIBILITY = 100
CAR_VISIBILITY_RANGE = 150
MAX_CARS = 200

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
SAFE_LANE_CHANGE_DIST = 20

# Подходы для waypoint системы: 'N' (сверху вниз), 'S', 'W', 'E'
DIRECTIONS = ['N', 'S', 'W', 'E']
# Colors
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (100, 100, 100)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (50, 50, 50)
UI_BG = (70, 70, 70)  # Darker background for UI
UI_HOVER = (150, 150, 150)
UI_ACTIVE = (100, 100, 100)
UI_TEXT = (255, 255, 255)
UI_BORDER = (30, 30, 30)
FPS = 60

# Directions and turns for vehicles - теперь двунаправленные дороги
DIR_INS = ['from_west', 'from_east', 'from_north', 'from_south', 'to_west', 'to_east', 'to_north', 'to_south']
TURN_PROBS = [0.6, 0.2, 0.2]

# Маппинг направлений движения
DIRECTION_MAPPINGS = {
    # Основные направления (въезд на перекресток)
    'from_west': {'heading': (1, 0), 'opposite': 'to_west'},
    'from_east': {'heading': (-1, 0), 'opposite': 'to_east'}, 
    'from_north': {'heading': (0, 1), 'opposite': 'to_north'},
    'from_south': {'heading': (0, -1), 'opposite': 'to_south'},
    # Обратные направления (выезд с перекрестка)  
    'to_west': {'heading': (-1, 0), 'opposite': 'from_west'},
    'to_east': {'heading': (1, 0), 'opposite': 'from_east'},
    'to_north': {'heading': (0, -1), 'opposite': 'from_north'},
    'to_south': {'heading': (0, 1), 'opposite': 'from_south'}
}

TURN_HEADINGS = {
    'from_west': {0: (1, 0), 1: (0, 1), 2: (0, -1)},
    'from_east': {0: (-1, 0), 1: (0, -1), 2: (0, 1)},
    'from_north': {0: (0, 1), 1: (-1, 0), 2: (1, 0)},
    'from_south': {0: (0, -1), 1: (1, 0), 2: (-1, 0)}
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

# Turn direction constants
TURN_STRAIGHT = 'straight'
TURN_LEFT = 'left'
TURN_RIGHT = 'right'

# IDM (Intelligent Driver Model) constants
IDM_ACCELERATION_EXPONENT = 4  # Степень для свободного ускорения
IDM_SAFE_DECELERATION = 8.0  # Максимальное аварийное торможение (м/с²)
VISIBILITY_RANGE = 200  # Дальность видимости для IDM (м)
TRAFFIC_LIGHT_STOP_DISTANCE = 5  # Расстояние от стоп-линии до светофора (м)