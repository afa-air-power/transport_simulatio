import pygame

DEFAULT_SCREEN_WIDTH = 1280
DEFAULT_SCREEN_HEIGHT = 720
UI_PANEL_WIDTH = 300


class ScreenConfig:

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


screen_config = ScreenConfig()
SCREEN_WIDTH = screen_config.width
SCREEN_HEIGHT = screen_config.height
SIM_WIDTH = screen_config.sim_width
SIM_HEIGHT = screen_config.sim_height
ROAD_SIZE = 400
LANE_WIDTH = 20
NUM_LANES = 4
LANES_PER_DIRECTION = 2
PED_SIZE_MIN = 1.5
PED_SIZE_MAX = 2.5
PED_SPEED_MIN = 4.0
PED_SPEED_MAX = 6.0
PED_GROUP_PROB = 0.3
PED_GROUP_SIZE = 2, 5
PED_REPULSION = 5.0
PED_ATTRACTION = 0.5
INTERVAL_MIN = 1
INTERVAL_MAX = 10
PED_INTERVAL_MIN = 3
PED_INTERVAL_MAX = 10
SAFE_DIST = 10
SAFE_LANE_CHANGE_DIST = 20
VISIBILITY = 100
CAR_VISIBILITY_RANGE = 150
LIGHT_GREEN = 30
LIGHT_YELLOW = 3
LIGHT_RED = 30
MAX_CARS = 200
SPEED_MIN = 8.33
SPEED_MAX = 33.33
TURN_RADIUS = LANE_WIDTH * 1.5
SIDEWALK_WIDTH = 10
import math

RED = 255, 0, 0
GREEN = 0, 255, 0
BLUE = 0, 0, 255
YELLOW = 255, 255, 0
GRAY = 100, 100, 100
WHITE = 255, 255, 255
BLACK = 0, 0, 0
LIGHT_GRAY = 200, 200, 200
DARK_GRAY = 50, 50, 50
UI_BG = 70, 70, 70
UI_HOVER = 150, 150, 150
UI_ACTIVE = 100, 100, 100
UI_TEXT = 255, 255, 255
UI_BORDER = 30, 30, 30
FPS = 60
SAFE_DISTANCE = 15
COMFORTABLE_DISTANCE = 30
WAYPOINT_REACH_DISTANCE = 15
LANE_CHANGE_DISTANCE = 50
ALL_RED_TIME_IN_DYNAMIC_MODE = 8
SWITCH_DELTA_IN_DYNAMIC_MODE = 220
YELLOW_TIME_CONSTANT_IN_DYNAMIC_MODE=1
DIR_INS = ['from_west', 'from_east', 'from_north', 'from_south']
TURN_PROBS = [0.6, 0.2, 0.2]
TURN_HEADINGS = {'from_west': {(0): (1, 0), (1): (0, 1), (2): (0, -1)},
                 'from_east': {(0): (-1, 0), (1): (0, -1), (2): (0, 1)}, 'from_north': {
        (0): (0, 1), (1): (-1, 0), (2): (1, 0)}, 'from_south': {(0): (0, -1), (
        1): (1, 0), (2): (-1, 0)}}
TURN_CENTERS = {'from_west': {(1): (0, TURN_RADIUS), (2): (0, -TURN_RADIUS)
                              }, 'from_east': {(1): (0, -TURN_RADIUS), (2): (0, TURN_RADIUS)},
                'from_north': {(1): (-TURN_RADIUS, 0), (2): (TURN_RADIUS, 0)},
                'from_south': {(1): (TURN_RADIUS, 0), (2): (-TURN_RADIUS, 0)}}
TURN_ANGLES = {'from_west': {(0): None, (1): (math.pi, math.pi / 2), (2): (
    math.pi, 3 * math.pi / 2)}, 'from_east': {(0): None, (1): (0, 3 * math.
                                                               pi / 2), (2): (0, math.pi / 2)},
               'from_north': {(0): None, (1): (math.
                                               pi / 2, math.pi), (2): (math.pi / 2, 0)}, 'from_south': {(0): None, (1):
        (3 * math.pi / 2, 0), (2): (3 * math.pi / 2, math.pi)}}
