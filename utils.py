# utils.py
import pygame
from constants import *

def draw_roads(screen, center_x, center_y):
    road_width = NUM_LANES * LANE_WIDTH
    # Horizontal road
    pygame.draw.rect(screen, GRAY, (center_x - ROAD_SIZE, center_y - road_width / 2, ROAD_SIZE * 2, road_width))
    # Vertical road
    pygame.draw.rect(screen, GRAY, (center_x - road_width / 2, center_y - ROAD_SIZE, road_width, ROAD_SIZE * 2))

    # Lane lines
    for i in range(1, NUM_LANES):
        # Horizontal
        y = center_y - road_width / 2 + i * LANE_WIDTH
        pygame.draw.line(screen, WHITE, (center_x - ROAD_SIZE, y), (center_x + ROAD_SIZE, y), 1)
        # Vertical
        x = center_x - road_width / 2 + i * LANE_WIDTH
        pygame.draw.line(screen, WHITE, (x, center_y - ROAD_SIZE), (x, center_y + ROAD_SIZE), 1)

    # Crosswalk lines
    for i in range(5):
        offset = -road_width / 2 - 5 + i * 3
        # Horizontal crosswalk
        pygame.draw.line(screen, WHITE, (center_x - 20, center_y + offset), (center_x + 20, center_y + offset), 2)
        pygame.draw.line(screen, WHITE, (center_x - 20, center_y - offset), (center_x + 20, center_y - offset), 2)
        # Vertical crosswalk
        pygame.draw.line(screen, WHITE, (center_x + offset, center_y - 20), (center_x + offset, center_y + 20), 2)
        pygame.draw.line(screen, WHITE, (center_x - offset, center_y - 20), (center_x - offset, center_y + 20), 2)

def draw_entities(screen, sim, center_x, center_y):
    for c in sim.cars:
        x = center_x + c.pos[0]
        y = center_y + c.pos[1]
        length = c.length
        width = c.width
        if abs(c.heading[0]) > abs(c.heading[1]):  # horizontal
            # Body
            pygame.draw.rect(screen, c.color, (x - length / 2, y - width / 2, length, width))
            # Windows
            pygame.draw.rect(screen, BLACK, (x - length / 3, y - width / 3, length / 6, width / 1.5))
            pygame.draw.rect(screen, BLACK, (x + length / 6, y - width / 3, length / 6, width / 1.5))
            # Wheels
            pygame.draw.circle(screen, BLACK, (int(x - length / 3), int(y + width / 2)), 2)
            pygame.draw.circle(screen, BLACK, (int(x + length / 3), int(y + width / 2)), 2)
            pygame.draw.circle(screen, BLACK, (int(x - length / 3), int(y - width / 2)), 2)
            pygame.draw.circle(screen, BLACK, (int(x + length / 3), int(y - width / 2)), 2)
        else:  # vertical
            # Body
            pygame.draw.rect(screen, c.color, (x - width / 2, y - length / 2, width, length))
            # Windows
            pygame.draw.rect(screen, BLACK, (x - width / 3, y - length / 3, width / 1.5, length / 6))
            pygame.draw.rect(screen, BLACK, (x - width / 3, y + length / 6, width / 1.5, length / 6))
            # Wheels
            pygame.draw.circle(screen, BLACK, (int(x + width / 2), int(y - length / 3)), 2)
            pygame.draw.circle(screen, BLACK, (int(x + width / 2), int(y + length / 3)), 2)
            pygame.draw.circle(screen, BLACK, (int(x - width / 2), int(y - length / 3)), 2)
            pygame.draw.circle(screen, BLACK, (int(x - width / 2), int(y + length / 3)), 2)

    for p in sim.peds:
        x = center_x + p.pos[0]
        y = center_y + p.pos[1]
        pygame.draw.circle(screen, p.color, (int(x), int(y)), int(p.size))

    for light in sim.controller.lights.values():
        light.draw(screen, center_x, center_y)tt