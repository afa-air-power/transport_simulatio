import pygame
import random
import math

from constants import *
from traffic_controller import TrafficController


# Эти классы в идеале должны находиться в отдельном файле entities.py
class Car:
    """Представляет одно транспортное средство в симуляции."""
    def __init__(self, pos, heading, speed, color):
        self.pos = list(pos)
        self.heading = heading
        self.speed = speed
        self.color = color
        self.length = 10  # Визуальный размер
        self.width = 5   # Визуальный размер

    def update(self, dt, controller):
        """Обновляет позицию автомобиля, учитывая светофоры."""
        road_half = (NUM_LANES * LANE_WIDTH) / 2
        stop_buffer = 15  # Расстояние от перекрестка для остановки
        stop_pos = road_half + stop_buffer

        effective_speed = self.speed

        # Горизонтальное движение
        if self.heading[0] != 0:
            light = controller.get_color('horizontal')
            if light in ['red', 'yellow']:
                # Движение на восток (слева направо)
                if self.heading[0] > 0 and -stop_pos < self.pos[0] < -road_half:
                    effective_speed = 0
                # Движение на запад (справа налево)
                elif self.heading[0] < 0 and road_half < self.pos[0] < stop_pos:
                    effective_speed = 0
        # Вертикальное движение
        elif self.heading[1] != 0:
            light = controller.get_color('vertical')
            if light in ['red', 'yellow']:
                # Движение на юг (сверху вниз)
                if self.heading[1] > 0 and -stop_pos < self.pos[1] < -road_half:
                    effective_speed = 0
                # Движение на север (снизу вверх)
                elif self.heading[1] < 0 and road_half < self.pos[1] < stop_pos:
                    effective_speed = 0

        self.pos[0] += self.heading[0] * effective_speed * dt
        self.pos[1] += self.heading[1] * effective_speed * dt

class Pedestrian:
    """Представляет одного пешехода в симуляции."""
    def __init__(self, pos, goal, speed, color, size):
        self.pos = list(pos)
        self.goal = goal
        self.speed = speed
        self.color = color
        self.size = size

    def update(self, dt):
        """Обновляет позицию пешехода в направлении его цели."""
        dx = self.goal[0] - self.pos[0]
        dy = self.goal[1] - self.pos[1]
        dist = math.hypot(dx, dy)
        if dist > 1:
            move_dist = self.speed * dt
            self.pos[0] += (dx / dist) * move_dist
            self.pos[1] += (dy / dist) * move_dist

class TrafficSimulation:
    def __init__(self):
        self.controller = TrafficController()
        self.cars = []
        self.peds = []
        self.pedestrians = self.peds  # Псевдоним для совместимости с UI
        self.paused = False
        # Таймеры для генерации сущностей
        self.last_car_spawn = 0
        self.car_spawn_interval = 2.0  # секунды
        self.last_ped_spawn = 0
        self.ped_spawn_interval = 3.0 # секунды

        # Свойства для совместимости с UI
        self.current_phase = 0
        self.phase_time = 0.0

    def set_phase_duration(self, duration):
        if self.controller and 0 <= self.controller.current_phase < len(self.controller.phases):
            self.controller.phases[self.controller.current_phase]['duration'] = max(1.0, duration)

    def set_traffic_color(self, color):
        # Упрощенное ручное управление для горизонтальных светофоров по запросу UI
        if self.controller:
            h_color = color.lower()
            if h_color in ['red', 'yellow', 'green']:
                self.controller.lights['h_left'].set_color(h_color)
                self.controller.lights['h_right'].set_color(h_color)

    def toggle_pause(self):
        self.paused = not self.paused

    def spawn_car(self):
        """Создает новый автомобиль на одном из въездов."""
        road_half = (NUM_LANES * LANE_WIDTH) / 2
        entry_dist = (SIM_WIDTH / 2) + 50

        direction = random.choice(['from_west', 'from_east', 'from_north', 'from_south'])
        lane_pos = road_half / 2 # упрощенная позиция полосы

        if direction == 'from_west':
            pos = (-entry_dist, -lane_pos)
            heading = (1, 0)
        elif direction == 'from_east':
            pos = (entry_dist, lane_pos)
            heading = (-1, 0)
        elif direction == 'from_north':
            pos = (lane_pos, -entry_dist)
            heading = (0, 1)
        else:  # from_south
            pos = (-lane_pos, entry_dist)
            heading = (0, -1)

        speed = random.uniform(SPEED_MIN, SPEED_MAX)
        color = random.choice([c for c in [RED, GREEN, BLUE, YELLOW, WHITE] if c != BLACK and c != GRAY])

        self.cars.append(Car(pos, heading, speed / 5, color)) # коэффициент /5 для замедления визуализации

    def spawn_pedestrian(self):
        """Создает нового пешехода на тротуаре."""
        road_half = (NUM_LANES * LANE_WIDTH) / 2
        sidewalk_dist = road_half + SIDEWALK_WIDTH / 2

        start_pos = random.choice([
            (-sidewalk_dist, -sidewalk_dist), (sidewalk_dist, -sidewalk_dist),
            (-sidewalk_dist, sidewalk_dist), (sidewalk_dist, sidewalk_dist)
        ])
        goal_pos = (-start_pos[0], -start_pos[1])

        speed = random.uniform(PED_SPEED_MIN, PED_SPEED_MAX)
        self.peds.append(Pedestrian(start_pos, goal_pos, speed, (200, 200, 255), 2))

    def update(self, dt):
        if self.paused:
            return

        self.controller.update(dt, 0, 0)

        self.current_phase = self.controller.current_phase
        self.phase_time = self.controller.timer

        # Генерация машин
        self.last_car_spawn += dt
        if self.last_car_spawn > self.car_spawn_interval and len(self.cars) < MAX_CARS:
            self.spawn_car()
            self.last_car_spawn = 0

        # Генерация пешеходов
        self.last_ped_spawn += dt
        if self.last_ped_spawn > self.ped_spawn_interval and len(self.peds) < 50:
            self.spawn_pedestrian()
            self.last_ped_spawn = 0

        for car in self.cars:
            car.update(dt, self.controller)
        for ped in self.peds:
            ped.update(dt)

        # Удаление сущностей за пределами экрана
        limit_x = (SIM_WIDTH / 2) + 100
        limit_y = (SIM_HEIGHT / 2) + 100
        self.cars = [c for c in self.cars if -limit_x < c.pos[0] < limit_x and -limit_y < c.pos[1] < limit_y]
        self.peds[:] = [p for p in self.peds if math.hypot(p.pos[0] - p.goal[0], p.pos[1] - p.goal[1]) > 5]