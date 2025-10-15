# simulation.py
import random
import math
import pygame
from typing import Dict
from constants import *
from entities import Vehicle, Pedestrian
from traffic_controller import TrafficController

class TrafficSimulation:
    """Основная логика симуляции — генерация сущностей, обновление, удаление."""
    def __init__(self):
        self.controller = TrafficController()
        self.cars: list[Vehicle] = []
        self.peds: list[Pedestrian] = []
        self.pedestrians = self.peds  # для совместимости с UI
        self.paused = False

        # Таймеры для генерации
        self.last_car_spawns: Dict[str, float] = {d: 0.0 for d in DIR_INS}
        self.last_ped_spawn = 0.0
        self.ped_spawn_interval = 3.0

        # UI-совместимые поля
        self.current_phase = 0
        self.phase_time = 0.0
        self.waiting_cars_h = 0
        self.waiting_cars_v = 0
        self.h_wait_time_sq_sum = 0.0
        self.v_wait_time_sq_sum = 0.0

    def update_screen_size(self):
        self.controller.update_light_positions()

    def set_phase_duration(self, duration: float):
        if 0 <= self.controller.current_phase < len(self.controller.phases):
            self.controller.phases[self.controller.current_phase]['duration'] = max(1.0, duration)

    def toggle_pause(self):
        self.paused = not self.paused

    def spawn_car(self, direction: str):
        """Создает машину с более реалистичной стартовой позицией и скоростью."""
        from constants import screen_config
        # entry_dist — расстояние от центра, где спавнится машина
        entry_dist = (screen_config.sim_width / 2) + 50
        num_lanes = NUM_LANES
        # выбираем полосу
        lane = random.randint(0, num_lanes - 1)
        offset = - (num_lanes * LANE_WIDTH) / 2 + lane * LANE_WIDTH + LANE_WIDTH / 2

        if direction == 'from_west':
            pos = (-entry_dist, offset)
            heading = (1, 0)
        elif direction == 'from_east':
            pos = (entry_dist, -offset)
            heading = (-1, 0)
        elif direction == 'from_north':
            pos = (offset, -entry_dist)
            heading = (0, 1)
        else:
            pos = (-offset, entry_dist)
            heading = (0, -1)

        v = Vehicle(direction, num_lanes)
        # переопределим позу/heading, чтобы соответствовало спавну
        v.pos = pygame.math.Vector2(pos)
        v.heading = pygame.math.Vector2(heading)
        v.lane = lane
        v.target_lane = v._choose_target_lane(num_lanes)
        # немного сниженная визуальная скорость
        v.target_speed = random.uniform(SPEED_MIN, SPEED_MAX) * 0.6
        self.cars.append(v)

    def spawn_pedestrian(self):
        num_lanes = NUM_LANES
        # случайно выбираем сторону перехода
        cross = 'horizontal' if random.choice([True, False]) else 'vertical'
        road_half = (num_lanes * LANE_WIDTH) / 2
        sidewalk_dist = road_half + SIDEWALK_WIDTH / 2
        sx = random.choice([-1, 1]) * sidewalk_dist
        sy = random.choice([-1, 1]) * sidewalk_dist
        start_pos = (sx, sy)
        # цель — противоположная сторона
        if cross == 'horizontal':
            goal = (sx, -sy)
        else:
            goal = (-sx, sy)
        p = Pedestrian(cross, group_pos=start_pos, num_lanes=num_lanes)
        p.pos = pygame.math.Vector2(start_pos)
        p.goal = pygame.math.Vector2(goal)
        p.speed = random.uniform(PED_SPEED_MIN, PED_SPEED_MAX)
        self.peds.append(p)

    def update(self, dt: float):
        if self.paused:
            return

        # --- подсчёт ожидающих машин и штрафов ---
        self.waiting_cars_h = 0
        self.waiting_cars_v = 0
        self.h_wait_time_sq_sum = 0.0
        self.v_wait_time_sq_sum = 0.0

        for car in self.cars:
            if getattr(car, "stopped", False) or getattr(car, "is_waiting", False):
                # определение направления по вектору heading
                if abs(car.heading.x) > abs(car.heading.y):
                    self.waiting_cars_h += 1
                    self.h_wait_time_sq_sum += car.wait_time ** 2
                else:
                    self.waiting_cars_v += 1
                    self.v_wait_time_sq_sum += car.wait_time ** 2

        # Обновление контроллера
        self.controller.update(dt, self.waiting_cars_h, self.waiting_cars_v,
                               self.h_wait_time_sq_sum, self.v_wait_time_sq_sum)

        self.current_phase = self.controller.current_phase
        self.phase_time = self.controller.timer

        # --- генерация машин согласно плотности ---
        for direction, density in self.controller.traffic_density.items():
            if density <= 0:
                continue
            interval = 10.0 / density  # среднее время между машинами для данного направления
            self.last_car_spawns[direction] += dt
            if self.last_car_spawns[direction] >= max(0.1, interval) and len(self.cars) < MAX_CARS:
                self.spawn_car(direction)
                self.last_car_spawns[direction] = 0.0

        # --- генерация пешеходов ---
        self.last_ped_spawn += dt
        if self.last_ped_spawn >= self.ped_spawn_interval and len(self.peds) < 50:
            self.spawn_pedestrian()
            self.last_ped_spawn = 0.0

        # --- обновление сущностей ---
        # машины: сначала проверка на светофоры/начало поворота, затем физика
        h_light = self.controller.get_color('horizontal')
        v_light = self.controller.get_color('vertical')
        # проходим по машинам
        for car in self.cars:
            # простая логика ожидания у светофора (если цвет запрещающий и близко к пересечению)
            road_half = (NUM_LANES * LANE_WIDTH) / 2
            stop_buffer = 15
            stop_pos = road_half + stop_buffer
            car_is_waiting = False

            # горизонтальное движение
            if abs(car.heading.x) > abs(car.heading.y):
                light = h_light
                if light in ('red', 'yellow'):
                    if car.heading.x > 0 and -stop_pos < car.pos.x < -road_half:
                        car_is_waiting = True
                    if car.heading.x < 0 and road_half < car.pos.x < stop_pos:
                        car_is_waiting = True
            else:
                light = v_light
                if light in ('red', 'yellow'):
                    if car.heading.y > 0 and -stop_pos < car.pos.y < -road_half:
                        car_is_waiting = True
                    if car.heading.y < 0 and road_half < car.pos.y < stop_pos:
                        car_is_waiting = True

            if car_is_waiting:
                car.wait_time += dt
                car.stopped = True
                car.current_speed = 0.0
            else:
                car.stopped = False
                if car.wait_time > 0 and not car_is_waiting:
                    car.wait_time = 0.0

            # если в пределах перекрестка и нужно поворачивать — попробовать начать поворот
            at_intersection = (-road_half < car.pos.x < road_half and -road_half < car.pos.y < road_half)
            if at_intersection and not car.has_turned and not car.turning:
                car.try_start_turn()

            car.update(dt)

        # пешеходы: если все светофоры красные — можно переходить
        can_cross = self.controller.is_all_red()
        for ped in self.peds:
            ped.move(dt, can_cross, self.peds, self.cars)

        # --- очистка: удаление ушедших за пределы области ---
        from constants import screen_config
        limit_x = (screen_config.sim_width / 2) + 100
        limit_y = (screen_config.sim_height / 2) + 100

        self.cars = [c for c in self.cars if -limit_x < c.pos.x < limit_x and -limit_y < c.pos.y < limit_y]

        # оставляем пешеходов, если они не достигли цели (малый порог)
        self.peds = [p for p in self.peds if (p.pos - p.goal).length() > 5.0]
