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
    from constants import screen_config
    road_width = num_lanes * LANE_WIDTH

    # Фон симуляции (трава)
    screen.fill((34, 139, 34), (0, 0, screen_config.sim_width, screen_config.sim_height))

    # Тротуары в углах (более темный серый цвет для контраста)
    sidewalk_color = (160, 160, 160)
    corner_sidewalks = [
        pygame.Rect(0, 0, center_x - road_width / 2, center_y - road_width / 2),
        pygame.Rect(center_x + road_width / 2, 0, screen_config.sim_width, center_y - road_width / 2),
        pygame.Rect(0, center_y + road_width / 2, center_x - road_width / 2, screen_config.sim_height),
        pygame.Rect(center_x + road_width / 2, center_y + road_width / 2, screen_config.sim_width, screen_config.sim_height)
    ]

    for rect in corner_sidewalks:
        pygame.draw.rect(screen, sidewalk_color, rect)
        # Добавляем текстуру тротуара (точечный узор)
        for x in range(int(rect.x), int(rect.x + rect.width), 20):
            for y in range(int(rect.y), int(rect.y + rect.height), 20):
                if (x + y) % 40 == 0:
                    pygame.draw.circle(screen, (140, 140, 140), (x, y), 2)

    # Горизонтальная дорога
    pygame.draw.rect(screen, GRAY, (0, center_y - road_width / 2, screen_config.sim_width, road_width))
    # Вертикальная дорога
    pygame.draw.rect(screen, GRAY, (center_x - road_width / 2, 0, road_width, screen_config.sim_height))

    # Разметка полос
    for i in range(1, num_lanes):
        y = center_y - road_width / 2 + i * LANE_WIDTH
        for x_start in range(0, screen_config.sim_width, 40):
            if not (center_x - road_width / 2 - 20 < x_start < center_x + road_width / 2):
                pygame.draw.line(screen, WHITE, (x_start, y), (x_start + 20, y), 2)

        x = center_x - road_width / 2 + i * LANE_WIDTH
        for y_start in range(0, screen_config.sim_height, 40):
            if not (center_y - road_width / 2 - 20 < y_start < center_y + road_width / 2):
                pygame.draw.line(screen, WHITE, (x, y_start), (x, y_start + 20), 2)

    # Пешеходные переходы
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