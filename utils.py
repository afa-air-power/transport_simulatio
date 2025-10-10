# utils.py
import pygame
from constants import *

class Crosswalk:
    def __init__(self, orientation):
        self.orientation = orientation  # 'horizontal' or 'vertical'

    def draw(self, screen, center_x, center_y, road_width):
        for i in range(10):  # More lines for detail
            offset = -road_width / 2 - 10 + i * 3
            if self.orientation == 'horizontal':
                pygame.draw.line(screen, WHITE, (center_x - 30, center_y + offset), (center_x + 30, center_y + offset), 3)
                pygame.draw.line(screen, WHITE, (center_x - 30, center_y - offset), (center_x + 30, center_y - offset), 3)
            else:
                pygame.draw.line(screen, WHITE, (center_x + offset, center_y - 30), (center_x + offset, center_y + 30), 3)
                pygame.draw.line(screen, WHITE, (center_x - offset, center_y - 30), (center_x - offset, center_y + 30), 3)

def draw_roads(screen, center_x, center_y, num_lanes):
    road_width = num_lanes * LANE_WIDTH
    total_road_width = road_width + 2 * SIDEWALK_WIDTH
    # Horizontal road with sidewalks
    pygame.draw.rect(screen, LIGHT_GRAY, (center_x - ROAD_SIZE, center_y - total_road_width / 2, ROAD_SIZE * 2, SIDEWALK_WIDTH))  # Bottom sidewalk
    pygame.draw.rect(screen, GRAY, (center_x - ROAD_SIZE, center_y - road_width / 2, ROAD_SIZE * 2, road_width))  # Road
    pygame.draw.rect(screen, LIGHT_GRAY, (center_x - ROAD_SIZE, center_y + road_width / 2, ROAD_SIZE * 2, SIDEWALK_WIDTH))  # Top sidewalk
    # Vertical road with sidewalks
    pygame.draw.rect(screen, LIGHT_GRAY, (center_x - total_road_width / 2, center_y - ROAD_SIZE, SIDEWALK_WIDTH, ROAD_SIZE * 2))  # Left sidewalk
    pygame.draw.rect(screen, GRAY, (center_x - road_width / 2, center_y - ROAD_SIZE, road_width, ROAD_SIZE * 2))  # Road
    pygame.draw.rect(screen, LIGHT_GRAY, (center_x + road_width / 2, center_y - ROAD_SIZE, SIDEWALK_WIDTH, ROAD_SIZE * 2))  # Right sidewalk

    # Lane lines
    for i in range(1, num_lanes):
        # Horizontal
        y = center_y - road_width / 2 + i * LANE_WIDTH
        pygame.draw.line(screen, WHITE, (center_x - ROAD_SIZE, y), (center_x + ROAD_SIZE, y), 2)
        # Vertical
        x = center_x - road_width / 2 + i * LANE_WIDTH
        pygame.draw.line(screen, WHITE, (x, center_y - ROAD_SIZE), (x, center_y + ROAD_SIZE), 2)

    # Crosswalks
    horizontal_crosswalk = Crosswalk('horizontal')
    vertical_crosswalk = Crosswalk('vertical')
    horizontal_crosswalk.draw(screen, center_x, center_y, road_width)
    vertical_crosswalk.draw(screen, center_x, center_y, road_width)

def draw_entities(screen, sim, center_x, center_y, zoom=1.0):
    for c in sim.cars:
        x = center_x + c.pos[0] * zoom
        y = center_y + c.pos[1] * zoom
        length = c.length * zoom
        width = c.width * zoom
        if abs(c.heading[0]) > abs(c.heading[1]):
            # Body
            pygame.draw.rect(screen, c.color, (x - length / 2, y - width / 2, length, width), border_radius=int(2 * zoom))
            # Windows
            pygame.draw.rect(screen, BLACK, (x - length / 3, y - width / 3, length / 6, width / 1.5), border_radius=int(1 * zoom))
            pygame.draw.rect(screen, BLACK, (x + length / 6, y - width / 3, length / 6, width / 1.5), border_radius=int(1 * zoom))
            # Wheels
            wheel_radius = 2 * zoom
            pygame.draw.circle(screen, BLACK, (int(x - length / 3), int(y + width / 2)), wheel_radius)
            pygame.draw.circle(screen, BLACK, (int(x + length / 3), int(y + width / 2)), wheel_radius)
            pygame.draw.circle(screen, BLACK, (int(x - length / 3), int(y - width / 2)), wheel_radius)
            pygame.draw.circle(screen, BLACK, (int(x + length / 3), int(y - width / 2)), wheel_radius)
        else:
            # Body
            pygame.draw.rect(screen, c.color, (x - width / 2, y - length / 2, width, length), border_radius=int(2 * zoom))
            # Windows
            pygame.draw.rect(screen, BLACK, (x - width / 3, y - length / 3, width / 1.5, length / 6), border_radius=int(1 * zoom))
            pygame.draw.rect(screen, BLACK, (x - width / 3, y + length / 6, width / 1.5, length / 6), border_radius=int(1 * zoom))
            # Wheels
            wheel_radius = 2 * zoom
            pygame.draw.circle(screen, BLACK, (int(x + width / 2), int(y - length / 3)), wheel_radius)
            pygame.draw.circle(screen, BLACK, (int(x + width / 2), int(y + length / 3)), wheel_radius)
            pygame.draw.circle(screen, BLACK, (int(x - width / 2), int(y - length / 3)), wheel_radius)
            pygame.draw.circle(screen, BLACK, (int(x - width / 2), int(y + length / 3)), wheel_radius)

    for p in sim.peds:
        x = center_x + p.pos[0] * zoom
        y = center_y + p.pos[1] * zoom
        pygame.draw.circle(screen, p.color, (int(x), int(y)), int(p.size * zoom))

    for light in sim.controller.lights.values():
        light.draw(screen, center_x, center_y)