# entities.py
import random
import math
import pygame
from typing import Tuple, Optional
from constants import *

# Используем pygame.Vector2 для удобных векторных операций
Vec2 = pygame.math.Vector2

class Vehicle:
    """Унифицированный класс машины — заменяет старые Car/Vehicle дубли."""
    def __init__(self, dir_in: str, num_lanes: int = NUM_LANES):
        self.dir_in = dir_in
        # turn: 0 = straight, 1 = right, 2 = left
        self.turn = random.choices([0, 1, 2], TURN_PROBS)[0]
        self.lane = random.randint(0, num_lanes - 1)
        self.target_lane = self._choose_target_lane(num_lanes)

        # Физика
        self.target_speed = random.uniform(SPEED_MIN, SPEED_MAX)
        self.current_speed = 0.0
        self.pos = Vec2(self._initial_pos(num_lanes))
        self.heading = Vec2(self._initial_heading())
        self.has_turned = False
        self.turning = False
        self.turn_center = Vec2(0, 0)
        self.turn_angle = 0.0
        self.turn_start_angle = 0.0
        self.turn_end_angle = 0.0

        # визуальные размеры и масса
        self.mass = random.uniform(800.0, 1500.0)
        self.length = random.uniform(4.0, 6.0)
        self.width = random.uniform(2.0, 3.5)
        self.accel_rate = random.uniform(1.5, 3.0)
        self.brake_rate = random.uniform(4.0, 6.0)

        # цвет по направлению (сохранение визуала)
        if self.turn == 0:
            self.color = (random.randint(0, 100), random.randint(150, 255), random.randint(0, 100))
        elif self.turn == 1:
            self.color = (random.randint(150, 255), random.randint(0, 100), random.randint(0, 100))
        else:
            self.color = (random.randint(0, 100), random.randint(0, 100), random.randint(150, 255))

        self.wait_time = 0.0
        self.stopped = False

    def _choose_target_lane(self, num_lanes: int) -> int:
        if num_lanes < 2:
            return 0
        if self.turn == 2:  # left
            return 0
        if self.turn == 1:  # right
            return num_lanes - 1
        # straight
        if self.lane == 0:
            return 1
        if self.lane == num_lanes - 1:
            return num_lanes - 2
        return self.lane

    def _initial_pos(self, num_lanes: int) -> Tuple[float, float]:
        offset = - (num_lanes * LANE_WIDTH) / 2 + self.lane * LANE_WIDTH + LANE_WIDTH / 2
        if self.dir_in == 'from_west':
            return (-ROAD_SIZE, offset)
        if self.dir_in == 'from_east':
            return (ROAD_SIZE, -offset)
        if self.dir_in == 'from_north':
            return (offset, -ROAD_SIZE)
        # from_south
        return (-offset, ROAD_SIZE)

    def _initial_heading(self) -> Tuple[int, int]:
        return {
            'from_west': (1, 0),
            'from_east': (-1, 0),
            'from_north': (0, 1),
            'from_south': (0, -1)
        }[self.dir_in]

    def update(self, dt: float):
        """Обновление скорости и позиции. Внешняя логика должна устанавливать self.turning / остановки."""
        # простая модель ускорения/торможения к target_speed
        if self.current_speed < self.target_speed:
            self.current_speed = min(self.current_speed + self.accel_rate * dt, self.target_speed)
        else:
            self.current_speed = max(self.current_speed - self.brake_rate * dt, self.target_speed)

        if self.turning:
            # вращение по дуге вокруг turn_center
            angular_speed = (self.current_speed / max(TURN_RADIUS, 0.1))
            # определим направление вращения по знаку разницы углов
            # используем модульную арифметику
            # двигаем угол в сторону turn_end_angle
            diff = (self.turn_end_angle - self.turn_angle + math.pi*2) % (math.pi*2)
            if diff > math.pi:
                # короткий путь в отрицательную сторону
                self.turn_angle -= angular_speed * dt
            else:
                self.turn_angle += angular_speed * dt

            # позиция на дуге
            self.pos = self.turn_center + Vec2(math.cos(self.turn_angle), math.sin(self.turn_angle)) * TURN_RADIUS
            self.heading = Vec2(math.cos(self.turn_angle), math.sin(self.turn_angle))
            # завершение поворота (по близости)
            if abs((self.turn_angle - self.turn_end_angle + math.pi*2) % (math.pi*2)) < 0.02:
                self.turning = False
                self.has_turned = True
        else:
            self.pos += self.heading * self.current_speed * dt

    def try_start_turn(self):
        """Инициализация параметров поворота. Возвращает True, если поворот запущен."""
        if self.turn == 0 or self.turning or self.has_turned:
            return False
        centers = TURN_CENTERS.get(self.dir_in, {})
        angles = TURN_ANGLES.get(self.dir_in, {})
        if self.turn not in centers or self.turn not in angles:
            return False
        # вычисляем центр и углы
        base_center = centers[self.turn]
        self.turn_center = Vec2(base_center)
        self.turn_start_angle, self.turn_end_angle = angles[self.turn]
        self.turn_angle = self.turn_start_angle
        self.turning = True
        return True

    def to_draw_rect(self, center_x: int, center_y: int, scale: float = 1.0):
        """Возвращает pygame.Rect для отрисовки машины (простейшее представление)."""
        # шкалирование логики в пиксели — в твоей системе координаты симуляции сопоставляются экрану
        w = max(4, int(self.width * 2 * scale))
        h = max(8, int(self.length * 2 * scale))
        # позиция относительно центра
        x = int(center_x + self.pos.x) - w // 2
        y = int(center_y + self.pos.y) - h // 2
        return pygame.Rect(x, y, w, h)

class Pedestrian:
    """Пешеход с простыми силами притяжения/отталкивания."""
    def __init__(self, cross: str, group_pos: Optional[Tuple[float, float]] = None, num_lanes: int = NUM_LANES):
        self.cross = cross  # 'horizontal' или 'vertical'
        self.size = random.uniform(PED_SIZE_MIN, PED_SIZE_MAX)
        self.speed = random.uniform(PED_SPEED_MIN, PED_SPEED_MAX)
        self.color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
        self.pos = Vec2(group_pos) if group_pos else Vec2(self._initial_pos(num_lanes))
        self.heading = Vec2(self._initial_heading())
        self.current_speed = 0.0
        self.stopped = True
        self.wait_time = 0.0
        self.goal = Vec2(self._get_goal(num_lanes))

    def _initial_pos(self, num_lanes: int):
        side = random.choice([-1, 1])
        offset = random.uniform(-10, 10)
        sidewalk_offset = num_lanes * LANE_WIDTH / 2 + SIDEWALK_WIDTH / 2 + 10
        if self.cross == 'horizontal':
            return (offset, side * sidewalk_offset)
        else:
            return (side * sidewalk_offset, offset)

    def _initial_heading(self):
        if self.cross == 'horizontal':
            return (0, -1 if self.pos.y > 0 else 1)
        else:
            return (-1 if self.pos.x > 0 else 1, 0)

    def _get_goal(self, num_lanes: int):
        if self.cross == 'horizontal':
            return (self.pos.x, -self.pos.y)
        else:
            return (-self.pos.x, self.pos.y)

    def calculate_forces(self, others: list, cars: list):
        # Attraction to goal
        to_goal = self.goal - self.pos
        dist_goal = to_goal.length()
        attraction = Vec2(0, 0)
        if dist_goal > 0:
            attraction = to_goal.normalize() * PED_ATTRACTION

        # Repulsion from other peds
        repulsion = Vec2(0, 0)
        for o in others:
            if o is self:
                continue
            diff = o.pos - self.pos
            d = diff.length()
            if 0 < d < 5:
                repulsion -= diff.normalize() * (PED_REPULSION / (d * d + 1e-6))

        # Repulsion from cars (stronger)
        rep_cars = Vec2(0, 0)
        for c in cars:
            diff = c.pos - self.pos
            d = diff.length()
            if 0 < d < 10:
                rep_cars -= diff.normalize() * (PED_REPULSION * 2 / (d * d + 1e-6))

        total = attraction + repulsion + rep_cars
        if total.length_squared() > 0:
            self.heading = total.normalize()

    def move(self, dt: float, can_go: bool, others: list, cars: list):
        if can_go:
            self.calculate_forces(others, cars)
            self.current_speed = self.speed
            self.stopped = False
        else:
            self.current_speed = 0.0
            self.stopped = True
            self.wait_time += dt
        self.pos += self.heading * self.current_speed * dt

    def to_draw_circle(self, center_x: int, center_y: int, scale: float = 1.0):
        r = max(2, int(self.size * scale))
        x = int(center_x + self.pos.x)
        y = int(center_y + self.pos.y)
        return (x, y, r)
