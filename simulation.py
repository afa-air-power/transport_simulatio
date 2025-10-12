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
        self.waiting_time = 0.0  # Время ожидания на светофоре
        self.is_waiting = False  # Флаг ожидания

        # Логика поворотов
        self.turn_direction = random.choice(['straight', 'left', 'right'])  # Направление поворота
        self.is_turning = False  # Флаг поворота
        self.turn_progress = 0.0  # Прогресс поворота (0-1)
        self.turn_center = None  # Центр поворота
        self.turn_start_angle = 0.0  # Начальный угол поворота
        self.original_heading = list(heading)  # Исходное направление

    def update(self, dt, controller):
        """Обновляет позицию автомобиля, учитывая светофоры и повороты."""
        road_half = (NUM_LANES * LANE_WIDTH) / 2
        stop_buffer = 15  # Расстояние от перекрестка для остановки
        stop_pos = road_half + stop_buffer

        effective_speed = self.speed
        was_waiting = self.is_waiting
        self.is_waiting = False

        # Проверяем светофоры только если не поворачиваем
        if not self.is_turning:
            # Горизонтальное движение
            if abs(self.heading[0]) > abs(self.heading[1]):
                light = controller.get_color('horizontal')
                if light in ['red', 'yellow']:
                    # Движение на восток (слева направо)
                    if self.heading[0] > 0 and -stop_pos < self.pos[0] < -road_half:
                        effective_speed = 0
                        self.is_waiting = True
                    # Движение на запад (справа налево)
                    elif self.heading[0] < 0 and road_half < self.pos[0] < stop_pos:
                        effective_speed = 0
                        self.is_waiting = True
            # Вертикальное движение
            else:
                light = controller.get_color('vertical')
                if light in ['red', 'yellow']:
                    # Движение на юг (сверху вниз)
                    if self.heading[1] > 0 and -stop_pos < self.pos[1] < -road_half:
                        effective_speed = 0
                        self.is_waiting = True
                    # Движение на север (снизу вверх)
                    elif self.heading[1] < 0 and road_half < self.pos[1] < stop_pos:
                        effective_speed = 0
                        self.is_waiting = True

        # Обновляем время ожидания
        if self.is_waiting:
            self.waiting_time += dt
        elif was_waiting and not self.is_waiting:
            self.waiting_time = 0.0  # Сброс при начале движения

        # Проверяем необходимость начать поворот
        if not self.is_turning and not self.is_waiting:
            self.check_start_turn()

        # Обновляем позицию
        if self.is_turning:
            self.update_turn(dt, effective_speed)
        else:
            self.pos[0] += self.heading[0] * effective_speed * dt
            self.pos[1] += self.heading[1] * effective_speed * dt

    def check_start_turn(self):
        """Проверяет, нужно ли начинать поворот на перекрестке."""
        road_half = (NUM_LANES * LANE_WIDTH) / 2

        # Проверяем, находимся ли мы на перекрестке
        at_intersection = (-road_half < self.pos[0] < road_half and 
                          -road_half < self.pos[1] < road_half)

        if at_intersection and self.turn_direction != 'straight':
            self.start_turn()

    def start_turn(self):
        """Начинает поворот на перекрестке."""
        self.is_turning = True
        self.turn_progress = 0.0

        # Определяем центр поворота
        turn_radius = 20  # Радиус поворота

        if self.turn_direction == 'left':
            # Поворот налево
            if abs(self.heading[0]) > abs(self.heading[1]):  # Горизонтальное движение
                self.turn_center = [self.pos[0], self.pos[1] + turn_radius * (1 if self.heading[0] > 0 else -1)]
                self.turn_start_angle = math.atan2(self.pos[1] - self.turn_center[1], self.pos[0] - self.turn_center[0])
            else:  # Вертикальное движение
                self.turn_center = [self.pos[0] - turn_radius * (1 if self.heading[1] > 0 else -1), self.pos[1]]
                self.turn_start_angle = math.atan2(self.pos[1] - self.turn_center[1], self.pos[0] - self.turn_center[0])
        else:  # right
            # Поворот направо
            if abs(self.heading[0]) > abs(self.heading[1]):  # Горизонтальное движение
                self.turn_center = [self.pos[0], self.pos[1] - turn_radius * (1 if self.heading[0] > 0 else -1)]
                self.turn_start_angle = math.atan2(self.pos[1] - self.turn_center[1], self.pos[0] - self.turn_center[0])
            else:  # Вертикальное движение
                self.turn_center = [self.pos[0] + turn_radius * (1 if self.heading[1] > 0 else -1), self.pos[1]]
                self.turn_start_angle = math.atan2(self.pos[1] - self.turn_center[1], self.pos[0] - self.turn_center[0])

    def update_turn(self, dt, speed):
        """Обновляет позицию машины во время поворота."""
        turn_radius = 20
        turn_speed = 1.5  # Скорость поворота

        self.turn_progress += turn_speed * dt

        if self.turn_progress >= 1.0:
            # Завершаем поворот
            self.is_turning = False
            self.turn_progress = 0.0

            # Обновляем направление движения
            if self.turn_direction == 'left':
                if abs(self.original_heading[0]) > abs(self.original_heading[1]):
                    self.heading = [0, self.original_heading[0]]  # Поворот на 90° влево
                else:
                    self.heading = [-self.original_heading[1], 0]
            elif self.turn_direction == 'right':
                if abs(self.original_heading[0]) > abs(self.original_heading[1]):
                    self.heading = [0, -self.original_heading[0]]  # Поворот на 90° вправо
                else:
                    self.heading = [self.original_heading[1], 0]
        else:
            # Вычисляем позицию на дуге поворота
            total_angle = math.pi / 2  # 90 градусов
            current_angle = self.turn_start_angle + total_angle * self.turn_progress * (1 if self.turn_direction == 'left' else -1)

            self.pos[0] = self.turn_center[0] + turn_radius * math.cos(current_angle)
            self.pos[1] = self.turn_center[1] + turn_radius * math.sin(current_angle)

            # Обновляем направление для плавного поворота
            self.heading[0] = -math.sin(current_angle) * (1 if self.turn_direction == 'left' else -1)
            self.heading[1] = math.cos(current_angle) * (1 if self.turn_direction == 'left' else -1)

class Pedestrian:
    """Представляет одного пешехода в симуляции."""
    def __init__(self, pos, goal, speed, color, size):
        self.pos = list(pos)
        self.goal = goal
        self.speed = speed
        self.color = color
        self.size = size

    def update(self, dt, controller):
        """Обновляет позицию пешехода в направлении его цели, учитывая светофоры."""
        # Проверяем, можно ли переходить дорогу (все светофоры красные)
        can_cross = controller.is_all_red()

        road_half = (NUM_LANES * LANE_WIDTH) / 2

        # Определяем, находится ли пешеход на перекрестке
        on_intersection = (-road_half < self.pos[0] < road_half and 
                          -road_half < self.pos[1] < road_half)

        # Если пешеход уже на перекрестке, позволяем ему закончить переход
        if on_intersection or can_cross:
            dx = self.goal[0] - self.pos[0]
            dy = self.goal[1] - self.pos[1]

            # Движение строго по осям (без диагонали)
            if abs(dx) > abs(dy):
                # Движемся горизонтально
                if abs(dx) > 1:
                    move_dist = self.speed * dt
                    self.pos[0] += move_dist if dx > 0 else -move_dist
            else:
                # Движемся вертикально
                if abs(dy) > 1:
                    move_dist = self.speed * dt
                    self.pos[1] += move_dist if dy > 0 else -move_dist
        # Иначе пешеход ждет на тротуаре

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

    def update_screen_size(self):
        """Обновляет позиции светофоров при изменении размера экрана"""
        self.controller.update_light_positions()

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
        from constants import screen_config
        road_half = (NUM_LANES * LANE_WIDTH) / 2
        entry_dist = (screen_config.sim_width / 2) + 50

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

        # Подсчитываем ожидающие машины
        waiting_h = sum(1 for car in self.cars if car.is_waiting and abs(car.heading[0]) > abs(car.heading[1]))
        waiting_v = sum(1 for car in self.cars if car.is_waiting and abs(car.heading[1]) > abs(car.heading[0]))

        self.controller.update(dt, waiting_h, waiting_v)

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
            ped.update(dt, self.controller)

        # Удаление сущностей за пределами экрана
        from constants import screen_config
        limit_x = (screen_config.sim_width / 2) + 100
        limit_y = (screen_config.sim_height / 2) + 100
        self.cars = [c for c in self.cars if -limit_x < c.pos[0] < limit_x and -limit_y < c.pos[1] < limit_y]
        self.peds[:] = [p for p in self.peds if math.hypot(p.pos[0] - p.goal[0], p.pos[1] - p.goal[1]) > 5]