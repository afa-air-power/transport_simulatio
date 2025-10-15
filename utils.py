# utils.py
import pygame
from constants import *
from entities import Vehicle, Pedestrian

def draw_roads(screen, center_x: int, center_y: int, num_lanes: int):
    """Рисование простого перекрёстка — сохраняем прежнюю визуальную структуру."""
    road_half = (num_lanes * LANE_WIDTH) / 2
    # фон дороги
    road_w = int(screen.get_width() - UI_PANEL_WIDTH)
    road_h = screen.get_height()
    # центральный фон (чисто декоративно)
    # рисуем горизонтальную полосу
    horiz_rect = pygame.Rect(0, center_y - road_half, center_x * 2, int(road_half * 2))
    vert_rect = pygame.Rect(center_x - road_half, 0, int(road_half * 2), center_y * 2)
    pygame.draw.rect(screen, DARK_GRAY, horiz_rect)
    pygame.draw.rect(screen, DARK_GRAY, vert_rect)

    # полосы
    for i in range(1, num_lanes):
        offset = int(-road_half + i * LANE_WIDTH)
        pygame.draw.line(screen, LIGHT_GRAY, (0, center_y + offset), (screen.get_width() - UI_PANEL_WIDTH, center_y + offset), 1)
        pygame.draw.line(screen, LIGHT_GRAY, (center_x + offset, 0), (center_x + offset, screen.get_height()), 1)

def draw_entities(screen, sim, center_x: int, center_y: int):
    """Отрисовка всех машин и пешеходов."""
    # Машины
    for car in sim.cars:
        rect = car.to_draw_rect(center_x, center_y, scale=1.0)
        pygame.draw.rect(screen, car.color, rect)
        # небольшая граница
        pygame.draw.rect(screen, BLACK, rect, 1)

    # Пешеходы
    for ped in sim.peds:
        x, y, r = ped.to_draw_circle(center_x, center_y, scale=1.0)
        pygame.draw.circle(screen, ped.color, (x, y), r)
        pygame.draw.circle(screen, BLACK, (x, y), r, 1)
