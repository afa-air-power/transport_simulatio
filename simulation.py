import pygame
import random
import math

from constants import *
from traffic_controller import TrafficController


# =============================
#  КЛАСС МАШИНЫ
# =============================
class Car:
    """Представляет одно транспортное средство в симуляции."""
    SAFE_DISTANCE = 35  # Увеличенное расстояние между машинами
    LANE_CHANGE_DISTANCE = 50  # Дистанция для безопасного перестроения

    def __init__(self, pos, heading, speed, color, direction='from_west'):
        self.pos = list(pos)
        self.heading = list(heading)
        self.max_speed = speed  # Максимальная скорость машины
        self.current_speed = 0.0  # Текущая скорость (начинаем с 0)
        self.color = color
        self.neon_color = self.generate_neon_color(color)
        self.direction = direction  # Направление движения (from_west, from_east, etc.)

        # Разнообразие размеров машин
        car_type = random.choice(['small', 'medium', 'large'])
        if car_type == 'small':
            self.length = 8
            self.width = 4
            self.acceleration = random.uniform(15.0, 20.0)  # м/с² - быстрое ускорение
            self.braking = random.uniform(25.0, 30.0)  # м/с² - сильное торможение
        elif car_type == 'medium':
            self.length = 12
            self.width = 6
            self.acceleration = random.uniform(10.0, 15.0)  # м/с²
            self.braking = random.uniform(20.0, 25.0)  # м/с²
        else:  # large
            self.length = 16
            self.width = 7
            self.acceleration = random.uniform(7.0, 12.0)  # м/с² - медленное ускорение
            self.braking = random.uniform(18.0, 23.0)  # м/с²

        self.waiting_time = 0.0
        self.is_waiting = False

        # Логика поворотов - улучшенная система
        self.turn_direction = random.choice(['straight', 'left', 'right'])
        self.is_turning = False
        self.turn_progress = 0.0
        self.turn_center = None
        self.turn_start_angle = 0.0
        self.original_heading = list(heading)

        # Плавность поворота (очень плавная)
        self.target_heading = list(heading)
        self.heading_interpolation = 0.08  # Уменьшено для большей плавности

        # Анимация неонового свечения
        self.glow_pulse = random.uniform(0, math.pi * 2)

        # Система перестроения
        self.current_lane = 0
        self.target_lane = 0
        self.is_changing_lane = False
        self.lane_change_progress = 0.0
        self.lane_change_start_pos = [0, 0]
        self.lane_change_target_offset = 0
        self.last_lane_change_time = 0
        self.lane_change_cooldown = 3.0  # Секунды между перестроениями

        # Определение направления полосы (попутное/встречное)
        self.lane_direction = self.get_lane_direction()

    def get_lane_direction(self):
        """Определяет направление движения по полосе (1 = попутное, -1 = встречное)"""
        # В зависимости от направления въезда определяем, по какой стороне дороги едем
        if self.direction in ['from_west', 'from_north']:
            return 1  # Попутное направление (правая сторона дороги)
        else:
            return -1  # Встречное направление (левая сторона дороги)

    def is_lane_correct_for_direction(self, lane_index):
        """Проверяет, подходит ли полоса для данного направления движения"""
        # Полосы нумеруются от 0 (левая) до NUM_LANES-1 (правая)
        # Для from_west и from_north: должны использовать правые полосы (бОльшие индексы)
        # Для from_east и from_south: должны использовать левые полосы (меньшие индексы)

        mid_lane = NUM_LANES / 2

        if self.direction in ['from_west', 'from_north']:
            # Правостороннее движение - используем полосы с индексом >= mid_lane
            return lane_index >= mid_lane
        else:
            # Левостороннее движение - используем полосы с индексом < mid_lane
            return lane_index < mid_lane

    def get_correct_lane_for_direction(self):
        """Возвращает случайную корректную полосу для данного направления"""
        if self.direction in ['from_west', 'from_north']:
            # Правые полосы
            if NUM_LANES == 1:
                return 0
            start_lane = NUM_LANES // 2
            return random.randint(start_lane, NUM_LANES - 1)
        else:
            # Левые полосы
            if NUM_LANES == 1:
                return 0
            end_lane = (NUM_LANES // 2) - 1
            return random.randint(0, max(0, end_lane))

    @staticmethod
    def generate_neon_color(base_color):
        """Генерирует яркий неоновый цвет на основе базового."""
        return tuple(min(255, c + 100) for c in base_color)

    def update(self, dt, controller, all_cars):
        """Обновляет позицию автомобиля, учитывая светофоры и дистанцию."""
        self.glow_pulse += dt * 3
        self.last_lane_change_time += dt

        road_half = (NUM_LANES * LANE_WIDTH) / 2
        stop_buffer = 15
        stop_pos = road_half + stop_buffer

        # Целевая скорость (по умолчанию максимальная)
        target_speed = self.max_speed
        was_waiting = self.is_waiting
        self.is_waiting = False

        # Проверяем светофор (если не поворачиваем)
        if not self.is_turning:
            if abs(self.heading[0]) > abs(self.heading[1]):
                light = controller.get_color('horizontal')
                if light in ['red', 'yellow']:
                    if self.heading[0] > 0 and -stop_pos < self.pos[0] < -road_half:
                        target_speed = 0
                        self.is_waiting = True  # Только здесь устанавливаем is_waiting (светофор)
                    elif self.heading[0] < 0 and road_half < self.pos[0] < stop_pos:
                        target_speed = 0
                        self.is_waiting = True  # Только здесь устанавливаем is_waiting (светофор)
            else:
                light = controller.get_color('vertical')
                if light in ['red', 'yellow']:
                    if self.heading[1] > 0 and -stop_pos < self.pos[1] < -road_half:
                        target_speed = 0
                        self.is_waiting = True  # Только здесь устанавливаем is_waiting (светофор)
                    elif self.heading[1] < 0 and road_half < self.pos[1] < stop_pos:
                        target_speed = 0
                        self.is_waiting = True  # Только здесь устанавливаем is_waiting (светофор)

        # Проверяем дистанцию до впереди идущих машин и возможность перестроения
        if not self.is_turning and not self.is_changing_lane:
            car_ahead = None
            min_distance = float('inf')

            for other in all_cars:
                if other is self:
                    continue

                # Проверяем только машины с тем же направлением движения и направлением полосы
                same_direction = (abs(self.heading[0] - other.heading[0]) < 0.1 and
                                 abs(self.heading[1] - other.heading[1]) < 0.1)
                same_lane_direction = (self.lane_direction == other.lane_direction)

                if same_direction and same_lane_direction:
                    dx = other.pos[0] - self.pos[0]
                    dy = other.pos[1] - self.pos[1]
                    dist = math.hypot(dx, dy)

                    # проверяем, впереди ли машина
                    forward = (dx * self.heading[0] + dy * self.heading[1]) > 0
                    if forward and dist < min_distance:
                        min_distance = dist
                        car_ahead = other

            # Адаптивное управление скоростью в зависимости от расстояния до препятствия
            if car_ahead:
                if min_distance < self.SAFE_DISTANCE:
                    # Очень близко - едем со скоростью впереди идущей машины (или стоим)
                    target_speed = car_ahead.current_speed
                    # Устанавливаем is_waiting только если полностью останавливаемся
                    if car_ahead.current_speed < 0.1:
                        self.is_waiting = True

                    # Пытаемся перестроиться, если возможно
                    if self.last_lane_change_time > self.lane_change_cooldown:
                        self.try_lane_change(all_cars)

                elif min_distance < self.SAFE_DISTANCE * 2:
                    # Средняя дистанция - плавно снижаем скорость
                    # Чем ближе препятствие, тем больше снижаем скорость
                    distance_ratio = (min_distance - self.SAFE_DISTANCE) / self.SAFE_DISTANCE
                    target_speed = min(target_speed, 
                                      car_ahead.current_speed + (self.max_speed - car_ahead.current_speed) * distance_ratio)
                elif min_distance < self.SAFE_DISTANCE * 3:
                    # Дальняя дистанция - небольшая корректировка
                    target_speed = min(target_speed, self.max_speed * 0.9)

        # Обновляем время ожидания
        if self.is_waiting:
            self.waiting_time += dt
        elif was_waiting and not self.is_waiting:
            self.waiting_time = 0.0

        # Физика разгона/торможения - ИСПРАВЛЕНО
        # Теперь машины ВСЕГДА стремятся к целевой скорости, а не останавливаются
        if target_speed > self.current_speed:
            # Разгон - используем ускорение
            acceleration_value = self.acceleration * dt
            self.current_speed = min(self.current_speed + acceleration_value, target_speed)
        elif target_speed < self.current_speed:
            # Торможение - используем торможение
            braking_value = self.braking * dt
            self.current_speed = max(self.current_speed - braking_value, max(0, target_speed))

        # Гарантируем, что скорость не отрицательна
        self.current_speed = max(0, self.current_speed)

        # Проверяем начало поворота
        if not self.is_turning and not self.is_waiting and not self.is_changing_lane:
            self.check_start_turn()

        # Обновляем позицию
        if self.is_changing_lane:
            self.update_lane_change(dt, self.current_speed)
        elif self.is_turning:
            self.update_turn(dt, self.current_speed)
        else:
            # Плавная интерполяция направления для более естественного движения
            self.heading[0] += (self.target_heading[0] - self.heading[0]) * self.heading_interpolation
            self.heading[1] += (self.target_heading[1] - self.heading[1]) * self.heading_interpolation

            self.pos[0] += self.heading[0] * self.current_speed * dt
            self.pos[1] += self.heading[1] * self.current_speed * dt

    def try_lane_change(self, all_cars):
        """Пытается выполнить перестроение на соседнюю полосу."""
        if NUM_LANES < 2:
            return

        # Определяем текущую полосу
        road_half = (NUM_LANES * LANE_WIDTH) / 2

        if abs(self.heading[0]) > abs(self.heading[1]):  # Горизонтальное движение
            relative_pos = self.pos[1] if self.heading[0] > 0 else -self.pos[1]
            self.current_lane = int((relative_pos + road_half) / LANE_WIDTH)
        else:  # Вертикальное движение
            relative_pos = self.pos[0] if self.heading[1] > 0 else -self.pos[0]
            self.current_lane = int((relative_pos + road_half) / LANE_WIDTH)

        self.current_lane = max(0, min(NUM_LANES - 1, self.current_lane))

        # Выбираем целевую полосу (соседнюю)
        possible_lanes = []
        if self.current_lane > 0:
            possible_lanes.append(self.current_lane - 1)
        if self.current_lane < NUM_LANES - 1:
            possible_lanes.append(self.current_lane + 1)

        if not possible_lanes:
            return

        # Проверяем каждую возможную полосу на безопасность И правильность направления
        for target_lane in possible_lanes:
            # ВАЖНО: проверяем, что целевая полоса предназначена для нашего направления движения
            if self.is_lane_correct_for_direction(target_lane) and self.is_lane_safe(target_lane, all_cars):
                self.start_lane_change(target_lane)
                return

    def is_lane_safe(self, target_lane, all_cars):
        """Проверяет, безопасно ли перестроиться на целевую полосу."""
        road_half = (NUM_LANES * LANE_WIDTH) / 2
        target_offset = -road_half + target_lane * LANE_WIDTH + LANE_WIDTH / 2

        for other in all_cars:
            if other is self:
                continue

            # Проверяем только машины на той же дороге и с тем же направлением полосы
            same_direction = (abs(self.heading[0] - other.heading[0]) < 0.1 and
                             abs(self.heading[1] - other.heading[1]) < 0.1)
            same_lane_direction = (self.lane_direction == other.lane_direction)

            if same_direction and same_lane_direction:

                # Определяем полосу другой машины
                if abs(self.heading[0]) > abs(self.heading[1]):
                    other_offset = other.pos[1] if self.heading[0] > 0 else -other.pos[1]
                else:
                    other_offset = other.pos[0] if self.heading[1] > 0 else -other.pos[0]

                # Если машина на целевой полосе
                if abs(other_offset - target_offset) < LANE_WIDTH / 2:
                    dx = other.pos[0] - self.pos[0]
                    dy = other.pos[1] - self.pos[1]
                    dist = math.hypot(dx, dy)

                    if dist < self.LANE_CHANGE_DISTANCE:
                        return False

        return True

    def start_lane_change(self, target_lane):
        """Начинает процесс перестроения."""
        self.is_changing_lane = True
        self.target_lane = target_lane
        self.lane_change_progress = 0.0
        self.lane_change_start_pos = list(self.pos)

        road_half = (NUM_LANES * LANE_WIDTH) / 2
        self.lane_change_target_offset = -road_half + target_lane * LANE_WIDTH + LANE_WIDTH / 2
        self.last_lane_change_time = 0

    def update_lane_change(self, dt, speed):
        """Обновляет позицию машины во время перестроения."""
        lane_change_speed = 0.8  # Скорость перестроения
        self.lane_change_progress += lane_change_speed * dt

        if self.lane_change_progress >= 1.0:
            self.is_changing_lane = False
            self.lane_change_progress = 0.0
            self.current_lane = self.target_lane
        else:
            # Плавная интерполяция с ease-in-out
            t = self.ease_in_out_cubic(self.lane_change_progress)

            # Движение вперед
            self.pos[0] += self.heading[0] * speed * dt
            self.pos[1] += self.heading[1] * speed * dt

            # Боковое смещение для перестроения
            if abs(self.heading[0]) > abs(self.heading[1]):  # Горизонтальное движение
                start_offset = self.lane_change_start_pos[1] if self.heading[0] > 0 else -self.lane_change_start_pos[1]
                current_offset = start_offset + (self.lane_change_target_offset - start_offset) * t
                self.pos[1] = current_offset if self.heading[0] > 0 else -current_offset
            else:  # Вертикальное движение
                start_offset = self.lane_change_start_pos[0] if self.heading[1] > 0 else -self.lane_change_start_pos[0]
                current_offset = start_offset + (self.lane_change_target_offset - start_offset) * t
                self.pos[0] = current_offset if self.heading[1] > 0 else -current_offset

    def check_start_turn(self):
        """Проверяет, нужно ли начинать поворот на перекрестке."""
        road_half = (NUM_LANES * LANE_WIDTH) / 2
        at_intersection = (-road_half < self.pos[0] < road_half and
                           -road_half < self.pos[1] < road_half)

        if at_intersection and self.turn_direction != 'straight':
            self.start_turn()

    def start_turn(self):
        """Начинает очень плавный поворот на перекрестке."""
        self.is_turning = True
        self.turn_progress = 0.0

        turn_radius = 35  # Увеличен радиус для более плавного поворота
        if self.turn_direction == 'left':
            if abs(self.heading[0]) > abs(self.heading[1]):
                self.turn_center = [self.pos[0], self.pos[1] + turn_radius * (1 if self.heading[0] > 0 else -1)]
                self.turn_start_angle = math.atan2(self.pos[1] - self.turn_center[1], self.pos[0] - self.turn_center[0])
            else:
                self.turn_center = [self.pos[0] - turn_radius * (1 if self.heading[1] > 0 else -1), self.pos[1]]
                self.turn_start_angle = math.atan2(self.pos[1] - self.turn_center[1], self.pos[0] - self.turn_center[0])
        else:
            if abs(self.heading[0]) > abs(self.heading[1]):
                self.turn_center = [self.pos[0], self.pos[1] - turn_radius * (1 if self.heading[0] > 0 else -1)]
                self.turn_start_angle = math.atan2(self.pos[1] - self.turn_center[1], self.pos[0] - self.turn_center[0])
            else:
                self.turn_center = [self.pos[0] + turn_radius * (1 if self.heading[1] > 0 else -1), self.pos[1]]
                self.turn_start_angle = math.atan2(self.pos[1] - self.turn_center[1], self.pos[0] - self.turn_center[0])

    def update_turn(self, dt, speed):
        """Обновляет позицию машины во время очень плавного поворота."""
        turn_radius = 35
        turn_speed = 0.7  # Снижена скорость для еще более плавного поворота
        self.turn_progress += turn_speed * dt

        if self.turn_progress >= 1.0:
            self.is_turning = False
            self.turn_progress = 0.0
            if self.turn_direction == 'left':
                if abs(self.original_heading[0]) > abs(self.original_heading[1]):
                    self.heading = [0, self.original_heading[0]]
                    self.target_heading = [0, self.original_heading[0]]
                else:
                    self.heading = [-self.original_heading[1], 0]
                    self.target_heading = [-self.original_heading[1], 0]
            elif self.turn_direction == 'right':
                if abs(self.original_heading[0]) > abs(self.original_heading[1]):
                    self.heading = [0, -self.original_heading[0]]
                    self.target_heading = [0, -self.original_heading[0]]
                else:
                    self.heading = [self.original_heading[1], 0]
                    self.target_heading = [self.original_heading[1], 0]
        else:
            # Использование двойного ease-in-out для максимальной плавности
            eased_progress = self.ease_in_out_quintic(self.turn_progress)
            total_angle = math.pi / 2
            current_angle = self.turn_start_angle + total_angle * eased_progress * (1 if self.turn_direction == 'left' else -1)
            self.pos[0] = self.turn_center[0] + turn_radius * math.cos(current_angle)
            self.pos[1] = self.turn_center[1] + turn_radius * math.sin(current_angle)

            # Плавное обновление направления
            self.heading[0] = -math.sin(current_angle) * (1 if self.turn_direction == 'left' else -1)
            self.heading[1] = math.cos(current_angle) * (1 if self.turn_direction == 'left' else -1)

    @staticmethod
    def ease_in_out_cubic(t):
        """Функция плавности для естественных переходов."""
        if t < 0.5:
            return 4 * t * t * t
        else:
            return 1 - pow(-2 * t + 2, 3) / 2

    @staticmethod
    def ease_in_out_quintic(t):
        """Функция плавности для очень плавных поворотов."""
        if t < 0.5:
            return 16 * t * t * t * t * t
        else:
            return 1 - pow(-2 * t + 2, 5) / 2

    def draw(self, screen):
        """Рисует машину в киберпанк/неоновом стиле."""
        x, y = self.pos
        angle = math.degrees(math.atan2(self.heading[1], self.heading[0]))

        car_length = self.length * 2.5
        car_width = self.width * 2.5

        # Неоновое свечение (пульсирующее)
        glow_size = int(8 + 4 * math.sin(self.glow_pulse))
        glow_surf = pygame.Surface((car_length + glow_size * 2, car_width + glow_size * 2), pygame.SRCALPHA)

        for i in range(glow_size, 0, -1):
            alpha = int(80 * (1 - i / glow_size))
            glow_color = (*self.neon_color, alpha)
            pygame.draw.rect(glow_surf, glow_color, 
                           (glow_size - i, glow_size - i, 
                            car_length + i * 2, car_width + i * 2), 
                           border_radius=6)

        rotated_glow = pygame.transform.rotate(glow_surf, -angle)
        glow_rect = rotated_glow.get_rect(center=(x, y))
        screen.blit(rotated_glow, glow_rect)

        # Основная поверхность машины
        rect_surf = pygame.Surface((car_length, car_width), pygame.SRCALPHA)

        # Темный корпус с неоновой окантовкой
        dark_color = tuple(min(80, c // 3) for c in self.color)
        pygame.draw.rect(rect_surf, dark_color, (0, 0, car_length, car_width), border_radius=6)

        # Неоновая окантовка
        for i in range(3):
            pygame.draw.rect(rect_surf, (*self.neon_color, 150 - i * 50), 
                           (i, i, car_length - i * 2, car_width - i * 2), 
                           2, border_radius=6)

        # Окна (темные с голубым оттенком)
        window_color = (20, 40, 60, 200)
        window_width = car_length * 0.3
        window_spacing = car_length * 0.15

        # Переднее окно
        pygame.draw.rect(rect_surf, window_color, 
                        (car_length - window_spacing - window_width, car_width * 0.15, 
                         window_width, car_width * 0.7), border_radius=3)
        # Заднее окно
        pygame.draw.rect(rect_surf, window_color, 
                        (window_spacing, car_width * 0.15, 
                         window_width, car_width * 0.7), border_radius=3)

        # Неоновые подсветки на окнах
        pygame.draw.rect(rect_surf, (*self.neon_color, 100), 
                        (car_length - window_spacing - window_width, car_width * 0.15, 
                         window_width, car_width * 0.7), 1, border_radius=3)

        # Фары
        if self.is_waiting:
            # Стоп-сигналы (неоновые красные)
            light_x = 8
            for offset in [0.25, 0.75]:
                # Свечение
                glow_surf_light = pygame.Surface((16, 16), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf_light, (255, 0, 0, 150), (8, 8), 8)
                pygame.draw.circle(glow_surf_light, (255, 0, 0, 80), (8, 8), 10)
                rect_surf.blit(glow_surf_light, (light_x - 8, car_width * offset - 8))
                # Яркое ядро
                pygame.draw.circle(rect_surf, (255, 50, 50), (int(light_x), int(car_width * offset)), 4)
                pygame.draw.circle(rect_surf, (255, 150, 150), (int(light_x), int(car_width * offset)), 2)
        else:
            # Передние фары (неоновые голубые/белые)
            light_x = car_length - 8
            for offset in [0.25, 0.75]:
                # Свечение
                glow_surf_light = pygame.Surface((20, 20), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf_light, (100, 200, 255, 120), (10, 10), 10)
                pygame.draw.circle(glow_surf_light, (150, 220, 255, 60), (10, 10), 12)
                rect_surf.blit(glow_surf_light, (light_x - 10, car_width * offset - 10))
                # Яркое ядро
                pygame.draw.circle(rect_surf, (200, 240, 255), (int(light_x), int(car_width * offset)), 4)
                pygame.draw.circle(rect_surf, (255, 255, 255), (int(light_x), int(car_width * offset)), 2)

        # Декоративные неоновые полоски по бокам
        stripe_y_top = car_width * 0.2
        stripe_y_bottom = car_width * 0.8
        pygame.draw.line(rect_surf, (*self.neon_color, 180), 
                        (car_length * 0.2, stripe_y_top), 
                        (car_length * 0.8, stripe_y_top), 2)
        pygame.draw.line(rect_surf, (*self.neon_color, 180), 
                        (car_length * 0.2, stripe_y_bottom), 
                        (car_length * 0.8, stripe_y_bottom), 2)

        rotated = pygame.transform.rotate(rect_surf, -angle)
        rect = rotated.get_rect(center=(x, y))
        screen.blit(rotated, rect)


# =============================
#  КЛАСС ПЕШЕХОДА
# =============================
class Pedestrian:
    """Представляет одного пешехода в симуляции."""
    def __init__(self, pos, goal, speed, color, size):
        self.pos = list(pos)
        self.goal = goal
        self.speed = speed
        self.color = color
        self.neon_color = tuple(min(255, c + 120) for c in color)
        self.size = size
        self.glow_pulse = random.uniform(0, math.pi * 2)
        self.is_crossing = False  # Начал ли пешеход переход
        self.reached_goal = False  # Достиг ли цели
        self.should_disappear = False  # Нужно ли удалить

    def update(self, dt, controller):
        self.glow_pulse += dt * 4

        can_cross = controller.is_all_red()
        road_half = (NUM_LANES * LANE_WIDTH) / 2
        on_intersection = (-road_half < self.pos[0] < road_half and -road_half < self.pos[1] < road_half)

        # Если пешеход начал переход, он должен закончить его на тротуаре
        if self.is_crossing or (can_cross and not self.reached_goal):
            if not self.is_crossing and can_cross:
                self.is_crossing = True  # Начинаем переход

            dx = self.goal[0] - self.pos[0]
            dy = self.goal[1] - self.pos[1]
            dist = math.hypot(dx, dy)

            if dist > 1:
                move_dist = self.speed * dt
                self.pos[0] += move_dist * (dx / dist)
                self.pos[1] += move_dist * (dy / dist)
            else:
                # Пешеход достиг цели (тротуара)
                self.reached_goal = True
                self.is_crossing = False

                # С вероятностью 80% пешеход исчезает
                if random.random() < 0.8:
                    self.should_disappear = True

    def draw(self, screen):
        # Неоновое свечение
        glow_intensity = int(100 + 60 * math.sin(self.glow_pulse))
        glow_surf = pygame.Surface((self.size * 6, self.size * 6), pygame.SRCALPHA)
        for i in range(self.size * 2, 0, -1):
            alpha = int(glow_intensity * (1 - i / (self.size * 2)))
            pygame.draw.circle(glow_surf, (*self.neon_color, alpha), 
                             (self.size * 3, self.size * 3), i)
        screen.blit(glow_surf, (int(self.pos[0]) - self.size * 3, int(self.pos[1]) - self.size * 3))

        # Темное ядро
        dark_color = tuple(c // 3 for c in self.color)
        pygame.draw.circle(screen, dark_color, (int(self.pos[0]), int(self.pos[1])), self.size)
        # Неоновая окантовка
        pygame.draw.circle(screen, self.neon_color, (int(self.pos[0]), int(self.pos[1])), self.size, 2)
        # Яркое ядро
        pygame.draw.circle(screen, self.neon_color, (int(self.pos[0]), int(self.pos[1])), self.size // 2)


# =============================
#  КЛАСС СИМУЛЯЦИИ
# =============================
class TrafficSimulation:
    def __init__(self):
        self.controller = TrafficController()
        self.cars = []
        self.peds = []
        self.pedestrians = self.peds
        self.paused = False

        self.last_car_spawns = {d: 0 for d in DIR_INS}
        self.last_ped_spawn = 0
        self.ped_spawn_interval = 3.0

        self.current_phase = 0
        self.phase_time = 0.0
        self.waiting_cars_h = 0
        self.waiting_cars_v = 0
        self.h_wait_time_sq_sum = 0.0
        self.v_wait_time_sq_sum = 0.0

        self.speed_multiplier = 1.0

    def update_screen_size(self):
        self.controller.update_light_positions()

    def toggle_pause(self):
        self.paused = not self.paused

    def spawn_car(self, direction):
        from constants import screen_config
        road_half = (NUM_LANES * LANE_WIDTH) / 2
        entry_dist = (screen_config.sim_width / 2) + 50

        # Случайная полоса для спавна
        lane = random.randint(0, NUM_LANES - 1)
        lane_offset = -road_half + lane * LANE_WIDTH + LANE_WIDTH / 2

        if direction == 'from_west':
            pos = (-entry_dist, lane_offset)
            heading = (1, 0)
        elif direction == 'from_east':
            pos = (entry_dist, -lane_offset)
            heading = (-1, 0)
        elif direction == 'from_north':
            pos = (lane_offset, -entry_dist)
            heading = (0, 1)
        else:
            pos = (-lane_offset, entry_dist)
            heading = (0, -1)

        speed = random.uniform(SPEED_MIN, SPEED_MAX)
        color = random.choice([RED, GREEN, BLUE, YELLOW, WHITE])
        self.cars.append(Car(pos, heading, speed / 5, color))

    def spawn_pedestrian(self):
        road_half = (NUM_LANES * LANE_WIDTH) / 2
        sidewalk_dist = road_half + SIDEWALK_WIDTH / 2
        start_x_sign = random.choice([-1, 1])
        start_y_sign = random.choice([-1, 1])
        start_pos = (start_x_sign * sidewalk_dist, start_y_sign * sidewalk_dist)
        if random.choice([True, False]):
            goal_pos = (start_pos[0], -start_pos[1])
        else:
            goal_pos = (-start_pos[0], start_pos[1])
        speed = random.uniform(PED_SPEED_MIN, PED_SPEED_MAX)
        self.peds.append(Pedestrian(start_pos, goal_pos, speed, (200, 200, 255), 2))

    def update(self, dt):
        if self.paused:
            return

        self.waiting_cars_h = 0
        self.waiting_cars_v = 0
        self.h_wait_time_sq_sum = 0.0
        self.v_wait_time_sq_sum = 0.0

        # Подсчет видимых машин в зоне видимости для динамического режима
        visible_cars_h = 0
        visible_cars_v = 0

        road_half = (NUM_LANES * LANE_WIDTH) / 2

        for car in self.cars:
            # Расстояние до перекрестка
            dist_to_intersection = 0
            if abs(car.heading[0]) > abs(car.heading[1]):  # Горизонтальное движение
                if car.heading[0] > 0:  # Движется на восток
                    dist_to_intersection = -road_half - car.pos[0]
                else:  # Движется на запад
                    dist_to_intersection = car.pos[0] - road_half
            else:  # Вертикальное движение
                if car.heading[1] > 0:  # Движется на юг
                    dist_to_intersection = -road_half - car.pos[1]
                else:  # Движется на север
                    dist_to_intersection = car.pos[1] - road_half

            # Учитываем только машины в зоне видимости перед перекрестком
            if 0 < dist_to_intersection < CAR_VISIBILITY_RANGE:
                if abs(car.heading[0]) > abs(car.heading[1]):
                    visible_cars_h += 1
                else:
                    visible_cars_v += 1

            # Подсчет ожидающих машин
            if car.is_waiting:
                if abs(car.heading[0]) > abs(car.heading[1]):
                    self.waiting_cars_h += 1
                    self.h_wait_time_sq_sum += car.waiting_time ** 2
                else:
                    self.waiting_cars_v += 1
                    self.v_wait_time_sq_sum += car.waiting_time ** 2

        self.controller.update(dt, self.waiting_cars_h, self.waiting_cars_v,
                               self.h_wait_time_sq_sum, self.v_wait_time_sq_sum,
                               visible_cars_h, visible_cars_v)
        self.current_phase = self.controller.current_phase
        self.phase_time = self.controller.timer

        # Генерация машин с использованием таймера спавна
        # Плотность λ (машин/10 секунд) преобразуется в интервал спавна: T = 10/λ секунд
        # Каждое направление имеет свой независимый таймер
        for direction, density in self.controller.traffic_density.items():
            if density > 0 and len(self.cars) < MAX_CARS:
                # Интервал между спавнами: 1/λ * 10 секунд
                # Например: λ=5 машин/10с → T=10/5=2 секунды между машинами
                spawn_interval = 10.0 / density

                # Обновляем таймер для этого направления
                self.last_car_spawns[direction] += dt

                # Когда таймер достигает интервала - спавним машину
                if self.last_car_spawns[direction] >= spawn_interval:
                    self.spawn_car(direction)
                    # Сбрасываем таймер (учитываем переполнение для точности)
                    self.last_car_spawns[direction] -= spawn_interval

        # пешеходы
        self.last_ped_spawn += dt
        if self.last_ped_spawn > self.ped_spawn_interval and len(self.peds) < 50:
            self.spawn_pedestrian()
            self.last_ped_spawn = 0

        for car in self.cars:
            car.update(dt, self.controller, self.cars)
        for ped in self.peds:
            ped.update(dt, self.controller)

        from constants import screen_config
        limit_x = (screen_config.sim_width / 2) + 100
        limit_y = (screen_config.sim_height / 2) + 100
        self.cars = [c for c in self.cars if -limit_x < c.pos[0] < limit_x and -limit_y < c.pos[1] < limit_y]

        # Удаляем пешеходов:
        # 1. Которые должны исчезнуть (80% после завершения перехода)
        # 2. Которые вышли за границы экрана
        # 3. Которые достигли цели и не исчезли (остальные 20%)
        self.peds[:] = [p for p in self.peds 
                       if not p.should_disappear 
                       and (-limit_x < p.pos[0] < limit_x and -limit_y < p.pos[1] < limit_y)
                       and not (p.reached_goal and math.hypot(p.pos[0] - p.goal[0], p.pos[1] - p.goal[1]) < 5)]

    def draw(self, screen):
        """Рисует все объекты симуляции."""
        for car in self.cars:
            car.draw(screen)
        for ped in self.peds:
            ped.draw(screen)
