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

def draw_roads(screen, center_x, center_y):
    """
    Рисует дороги с двунаправленным движением (4 полосы на каждой дороге).
    """
    from constants import screen_config
    road_width = NUM_LANES * LANE_WIDTH

    # Темный фон
    bg_color = (10, 5, 20)
    screen.fill(bg_color, (0, 0, screen_config.sim_width, screen_config.sim_height))

    # Звездное небо
    for _ in range(250):
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

    # Тротуары в углах
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
        pygame.draw.rect(screen, sidewalk_glow, rect, 2)

    # Дороги
    road_color = (25, 28, 35)

    # Горизонтальная дорога
    pygame.draw.rect(screen, road_color, 
                    (0, center_y - road_width / 2, screen_config.sim_width, road_width))
    # Края дороги
    pygame.draw.line(screen, (0, 150, 255), (0, center_y - road_width / 2), 
                    (screen_config.sim_width, center_y - road_width / 2), 2)
    pygame.draw.line(screen, (0, 150, 255), (0, center_y + road_width / 2), 
                    (screen_config.sim_width, center_y + road_width / 2), 2)

    # Вертикальная дорога
    pygame.draw.rect(screen, road_color, 
                    (center_x - road_width / 2, 0, road_width, screen_config.sim_height))
    # Края дороги
    pygame.draw.line(screen, (0, 150, 255), (center_x - road_width / 2, 0), 
                    (center_x - road_width / 2, screen_config.sim_height), 2)
    pygame.draw.line(screen, (0, 150, 255), (center_x + road_width / 2, 0), 
                    (center_x + road_width / 2, screen_config.sim_height), 2)

    # Центральная сплошная линия (разделяет встречные потоки)
    center_line_color = (255, 200, 0)  # Желтая

    # Горизонтальная центральная линия
    pygame.draw.line(screen, center_line_color, 
                    (0, center_y), 
                    (center_x - road_width / 2, center_y), 3)
    pygame.draw.line(screen, center_line_color, 
                    (center_x + road_width / 2, center_y), 
                    (screen_config.sim_width, center_y), 3)

    # Вертикальная центральная линия
    pygame.draw.line(screen, center_line_color, 
                    (center_x, 0), 
                    (center_x, center_y - road_width / 2), 3)
    pygame.draw.line(screen, center_line_color, 
                    (center_x, center_y + road_width / 2), 
                    (center_x, screen_config.sim_height), 3)

    # Разметка полос (пунктирная)
    line_color = (0, 255, 200)
    dash_length = 20
    gap_length = 20

    # Полосы на горизонтальной дороге (кроме центральной)
    for i in [1, 3]:  # Линии между полосами в одном направлении
        y = center_y - road_width / 2 + i * LANE_WIDTH
        x = 0
        while x < screen_config.sim_width:
            # Пропускаем зону перекрестка
            if not (center_x - road_width / 2 - gap_length < x < center_x + road_width / 2 + gap_length):
                pygame.draw.line(screen, line_color, 
                               (x, y), (x + dash_length, y), 2)
            x += dash_length + gap_length

    # Полосы на вертикальной дороге (кроме центральной)
    for i in [1, 3]:
        x = center_x - road_width / 2 + i * LANE_WIDTH
        y = 0
        while y < screen_config.sim_height:
            # Пропускаем зону перекрестка
            if not (center_y - road_width / 2 - gap_length < y < center_y + road_width / 2 + gap_length):
                pygame.draw.line(screen, line_color, 
                               (x, y), (x, y + dash_length), 2)
            y += dash_length + gap_length

    # Сетка на перекрестке
    grid_color = (50, 0, 100)
    grid_spacing = 15
    for i in range(int(-road_width / 2), int(road_width / 2), grid_spacing):
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

def draw_entities(screen, sim, center_x, center_y):
    """
    Рисует все сущности симуляции (машины, пешеходы, светофоры).

    Args:
        screen: Pygame surface
        sim: Экземпляр TrafficSimulation
        center_x, center_y: Координаты центра перекрестка
    """
    # Рисуем через метод draw симуляции
    sim.draw(screen, center_x, center_y)