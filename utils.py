# utils.py
import pygame
import random
import math
from constants import *

class Crosswalk:
    def __init__(self, orientation):
        self.orientation = orientation

    def draw(self, screen, center_x, center_y, road_width):
        # Неоновые пешеходные переходы
        stripe_width = 5
        stripe_spacing = 2
        num_stripes = 8

        for i in range(num_stripes):
            offset = -road_width / 2 - 12 + i * (stripe_width + stripe_spacing)

            # Неоновое свечение полосок
            glow_color = (0, 200, 255, 120)
            stripe_color = (0, 255, 255)

            if self.orientation == 'horizontal':
                # Свечение
                for j in range(3, 0, -1):
                    alpha = int(100 * (1 - j / 3))
                    glow_surf = pygame.Surface((68, stripe_width + j * 2), pygame.SRCALPHA)
                    glow_surf.fill((*glow_color[:3], alpha))
                    screen.blit(glow_surf, (center_x - 34, center_y + offset - j))
                    screen.blit(glow_surf, (center_x - 34, center_y - offset - j))

                # Основные полоски
                pygame.draw.rect(screen, stripe_color, 
                               (center_x - 34, center_y + offset, 68, stripe_width))
                pygame.draw.rect(screen, stripe_color, 
                               (center_x - 34, center_y - offset, 68, stripe_width))
            else:
                # Свечение
                for j in range(3, 0, -1):
                    alpha = int(100 * (1 - j / 3))
                    glow_surf = pygame.Surface((stripe_width + j * 2, 68), pygame.SRCALPHA)
                    glow_surf.fill((*glow_color[:3], alpha))
                    screen.blit(glow_surf, (center_x + offset - j, center_y - 34))
                    screen.blit(glow_surf, (center_x - offset - j, center_y - 34))

                # Основные полоски
                pygame.draw.rect(screen, stripe_color, 
                               (center_x + offset, center_y - 34, stripe_width, 68))
                pygame.draw.rect(screen, stripe_color, 
                               (center_x - offset, center_y - 34, stripe_width, 68))

def draw_roads(screen, center_x, center_y, num_lanes, zoom=1.0):
    from constants import screen_config
    road_width = num_lanes * LANE_WIDTH

    # Темный фон (почти черный с фиолетовым оттенком)
    bg_color = (10, 5, 20)
    screen.fill(bg_color, (0, 0, screen_config.sim_width, screen_config.sim_height))

    # Добавляем звездное небо / частицы
    for _ in range(300):
        x = random.randint(0, screen_config.sim_width)
        y = random.randint(0, screen_config.sim_height)
        brightness = random.randint(100, 255)
        size = random.randint(1, 2)
        star_color = random.choice([
            (brightness, brightness, brightness),
            (brightness, brightness // 2, brightness),
            (brightness // 2, brightness, brightness)
        ])
        pygame.draw.circle(screen, star_color, (x, y), size)

    # Тротуары в углах (темные с неоновой окантовкой)
    sidewalk_color = (20, 20, 30)
    sidewalk_glow = (100, 0, 255)
    corner_sidewalks = [
        pygame.Rect(0, 0, center_x - road_width / 2, center_y - road_width / 2),
        pygame.Rect(center_x + road_width / 2, 0, screen_config.sim_width, center_y - road_width / 2),
        pygame.Rect(0, center_y + road_width / 2, center_x - road_width / 2, screen_config.sim_height),
        pygame.Rect(center_x + road_width / 2, center_y + road_width / 2, screen_config.sim_width, screen_config.sim_height)
    ]

    for rect in corner_sidewalks:
        pygame.draw.rect(screen, sidewalk_color, rect)
        # Неоновая окантовка тротуаров
        pygame.draw.rect(screen, sidewalk_glow, rect, 3)
        # Дополнительное свечение
        pygame.draw.rect(screen, (*sidewalk_glow, 100), rect, 6)

    # Дороги - темно-серые с синеватым оттенком
    road_color = (25, 28, 35)

    # Горизонтальная дорога
    pygame.draw.rect(screen, road_color, 
                    (0, center_y - road_width / 2, screen_config.sim_width, road_width))
    # Неоновая окантовка
    pygame.draw.line(screen, (0, 150, 255), (0, center_y - road_width / 2), 
                    (screen_config.sim_width, center_y - road_width / 2), 2)
    pygame.draw.line(screen, (0, 150, 255), (0, center_y + road_width / 2), 
                    (screen_config.sim_width, center_y + road_width / 2), 2)

    # Вертикальная дорога
    pygame.draw.rect(screen, road_color, 
                    (center_x - road_width / 2, 0, road_width, screen_config.sim_height))
    # Неоновая окантовка
    pygame.draw.line(screen, (0, 150, 255), (center_x - road_width / 2, 0), 
                    (center_x - road_width / 2, screen_config.sim_height), 2)
    pygame.draw.line(screen, (0, 150, 255), (center_x + road_width / 2, 0), 
                    (center_x + road_width / 2, screen_config.sim_height), 2)

    # Неоновая разметка полос (пунктирная)
    line_color = (0, 255, 200)
    line_glow = (0, 200, 150, 100)

    for i in range(1, num_lanes):
        y = center_y - road_width / 2 + i * LANE_WIDTH
        for x_start in range(0, screen_config.sim_width, 40):
            if not (center_x - road_width / 2 - 20 < x_start < center_x + road_width / 2):
                # Свечение линии
                for thickness in range(5, 0, -1):
                    alpha = int(50 * (1 - thickness / 5))
                    pygame.draw.line(screen, (*line_glow[:3], alpha), 
                                   (x_start, y), (x_start + 20, y), thickness)
                # Основная линия
                pygame.draw.line(screen, line_color, (x_start, y), (x_start + 20, y), 2)

        x = center_x - road_width / 2 + i * LANE_WIDTH
        for y_start in range(0, screen_config.sim_height, 40):
            if not (center_y - road_width / 2 - 20 < y_start < center_y + road_width / 2):
                # Свечение линии
                for thickness in range(5, 0, -1):
                    alpha = int(50 * (1 - thickness / 5))
                    pygame.draw.line(screen, (*line_glow[:3], alpha), 
                                   (x, y_start), (x, y_start + 20), thickness)
                # Основная линия
                pygame.draw.line(screen, line_color, (x, y_start), (x, y_start + 20), 2)

    # Неоновая сетка на перекрестке
    grid_color = (50, 0, 100, 80)
    grid_spacing = 10
    for i in range(-int(road_width / 2), int(road_width / 2), grid_spacing):
        pygame.draw.line(screen, grid_color, 
                        (center_x + i, center_y - road_width / 2),
                        (center_x + i, center_y + road_width / 2), 1)
        pygame.draw.line(screen, grid_color, 
                        (center_x - road_width / 2, center_y + i),
                        (center_x + road_width / 2, center_y + i), 1)

    # Пешеходные переходы
    horizontal_crosswalk = Crosswalk('horizontal')
    vertical_crosswalk = Crosswalk('vertical')
    horizontal_crosswalk.draw(screen, center_x, center_y, road_width)
    vertical_crosswalk.draw(screen, center_x, center_y, road_width)

def draw_entities(screen, sim, center_x, center_y, zoom=1.0):
    for c in sim.cars:
        x = center_x + c.pos[0] * zoom
        y = center_y + c.pos[1] * zoom
        c.pos_temp = c.pos
        c.pos = [x, y]
        c.draw(screen)
        c.pos = c.pos_temp

    for p in sim.peds:
        x = center_x + p.pos[0] * zoom
        y = center_y + p.pos[1] * zoom
        p.pos_temp = p.pos
        p.pos = [x, y]
        p.draw(screen)
        p.pos = p.pos_temp

    for light in sim.controller.lights.values():
        light.draw(screen, center_x, center_y)