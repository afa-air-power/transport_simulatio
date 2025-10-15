# simple_traffic_light.py
import pygame
from constants import *

class SimpleTrafficLight:
    """Простой светофор для waypoint системы"""
    def __init__(self):
        self.timer = 0.0
        # state 0: NS green, EW red; 1: NS yellow; 2: EW green; 3: EW yellow
        self.state = 0

    def update(self, dt):
        self.timer += dt
        if self.state == 0 and self.timer >= GREEN_DURATION:
            self.timer = 0
            self.state = 1
        elif self.state == 1 and self.timer >= YELLOW_DURATION:
            self.timer = 0
            self.state = 2
        elif self.state == 2 and self.timer >= GREEN_DURATION:
            self.timer = 0
            self.state = 3
        elif self.state == 3 and self.timer >= YELLOW_DURATION:
            self.timer = 0
            self.state = 0

    def is_green(self, incoming_dir):
        """Проверяет, зеленый ли свет для данного направления"""
        # incoming_dir 'N' or 'S' are NS group; 'E'/'W' are EW group
        ns = incoming_dir in ('N', 'S')
        if self.state in (0, 1):  # NS has green (0 green, 1 yellow)
            return ns
        else:
            return not ns

    def is_yellow(self, incoming_dir):
        """Проверяет, желтый ли свет для данного направления"""
        if self.state == 1:
            return incoming_dir in ('N', 'S')
        if self.state == 3:
            return incoming_dir in ('E', 'W')
        return False

    def draw(self, screen, center_x, center_y):
        """Рисует простые светофоры в углах перекрестка"""
        # NS light (for N/S incoming) top-left
        # show green if self.state 0/1, else red
        ns_green = self.state in (0, 1)
        ew_green = self.state in (2, 3)

        # NS box
        pygame.draw.rect(screen, (0, 0, 0), (center_x - 50, center_y - 120, 30, 60))
        pygame.draw.circle(screen, (0, 255, 0) if ns_green else (80, 80, 80), (center_x - 35, center_y - 105), 8)
        pygame.draw.circle(screen, (255, 255, 0) if self.state == 1 else (80, 80, 80), (center_x - 35, center_y - 90), 8)
        pygame.draw.circle(screen, (255, 0, 0) if not ns_green else (80, 80, 80), (center_x - 35, center_y - 75), 8)

        # EW box
        pygame.draw.rect(screen, (0, 0, 0), (center_x + 20, center_y + 60, 30, 60))
        pygame.draw.circle(screen, (0, 255, 0) if ew_green else (80, 80, 80), (center_x + 35, center_y + 95), 8)
        pygame.draw.circle(screen, (255, 255, 0) if self.state == 3 else (80, 80, 80), (center_x + 35, center_y + 80), 8)
        pygame.draw.circle(screen, (255, 0, 0) if not ew_green else (80, 80, 80), (center_x + 35, center_y + 65), 8)