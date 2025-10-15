import pygame
import random
import math

from constants import *
from traffic_controller import TrafficController


# =============================
#  СИСТЕМА ПУТЕЙ (WAYPOINTS)
# =============================
class PathGenerator:
    """
    Генерирует траектории движения автомобилей на перекрёстке.

    ═══════════════════════════════════════════════════════════════════════
    ГЕОМЕТРИЯ ПЕРЕКРЁСТКА (NUM_LANES=4, LANE_WIDTH=20)
    ═══════════════════════════════════════════════════════════════════════

    Система координат:
    - Центр перекрёстка: (0, 0)
    - X: отрицательные значения слева, положительные справа
    - Y: отрицательные значения сверху, положительные снизу

    ВСЕГО 8 ПОЛОС ДВИЖЕНИЯ (по 2 полосы в каждом направлении):

    ┌─────────────────────────────────────────────────────────────────┐
    │ ГОРИЗОНТАЛЬНАЯ ДОРОГА (параллельна оси X)                      │
    ├─────────────────────────────────────────────────────────────────┤
    │ 1. ЗАПАД → ВОСТОК (движение слева направо →)                   │
    │    Входящие полосы (к центру):                                 │
    │    • lane 0: Y = -30 (ближе к центру, может поворачивать)     │
    │    • lane 1: Y = -10 (дальше от центра)                        │
    │                                                                 │
    │ 2. ВОСТОК → ЗАПАД (движение справа налево ←)                   │
    │    Входящие полосы (к центру):                                 │
    │    • lane 0: Y = +30 (ближе к центру, может поворачивать)     │
    │    • lane 1: Y = +10 (дальше от центра)                        │
    └─────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────────┐
    │ ВЕРТИКАЛЬНАЯ ДОРОГА (параллельна оси Y)                        │
    ├─────────────────────────────────────────────────────────────────┤
    │ 3. СЕВЕР → ЮГ (движение сверху вниз ↓)                         │
    │    Входящие полосы (к центру):                                 │
    │    • lane 0: X = +30 (ближе к центру, может поворачивать)     │
    │    • lane 1: X = +10 (дальше от центра)                        │
    │                                                                 │
    │ 4. ЮГ → СЕВЕР (движение снизу вверх ↑)                         │
    │    Входящие полосы (к центру):                                 │
    │    • lane 0: X = -30 (ближе к центру, может поворачивать)     │
    │    • lane 1: X = -10 (дальше от центра)                        │
    └─────────────────────────────────────────────────────────────────┘

    ПРАВИЛА ПОВОРОТОВ:
    ══════════════════
    ✓ При движении ПРЯМО: машина остаётся на своей полосе
    ✓ При ПОВОРОТЕ: машина выезжает на ИСХОДЯЩИЕ полосы целевой дороги
    ✓ Исходящие полосы симметричны входящим относительно центра
    ✓ НИКОГДА не попадаем на встречные полосы!

    ПРИМЕРЫ:
    ────────
    • ЗАПАД→ВОСТОК, прямо: lane 0 (Y=-30) → остаётся Y=-30
    • ЗАПАД→ВОСТОК, налево→СЕВЕР: lane 0 (Y=-30) → lane 0 севера (X=-30)
    • ЗАПАД→ВОСТОК, направо→ЮГ: lane 0 (Y=-30) → lane 0 юга (X=+30)
    """

    @staticmethod
    def generate_waypoints(from_direction, lane, turn_direction):
        """
        Создаёт траекторию движения (список waypoints) для автомобиля.

        Args:
            from_direction: Направление въезда на перекрёсток
                'from_west'  - с запада (слева)
                'from_east'  - с востока (справа)
                'from_north' - с севера (сверху)
                'from_south' - с юга (снизу)

            lane: Номер полосы движения (0 или 1)
                0 - ближе к центру перекрёстка (может поворачивать)
                1 - дальше от центра (обычно для прямого движения)

            turn_direction: Направление поворота
                'straight' - прямо через перекрёсток
                'left'     - поворот налево
                'right'    - поворот направо

        Returns:
            List[(float, float)]: Список координат waypoints
        """
        road_half = (NUM_LANES * LANE_WIDTH) / 2  # = 40 (половина ширины всех полос)
        entry_dist = 500  # Расстояние появления машины за экраном

        waypoints = []

        # ════════════════════════════════════════════════════════
        # ЗАПАД → ВОСТОК (слева направо, движение →)
        # ════════════════════════════════════════════════════════
        if from_direction == 'from_west':
            # Входящие полосы запада: Y = -30 (lane 0) или Y = -10 (lane 1)
            entry_y = -road_half + (lane + 0.5) * LANE_WIDTH

            waypoints.append((-entry_dist, entry_y))
            waypoints.append((-road_half - 20, entry_y))

            if turn_direction == 'straight':
                # ПРЯМО → восток (остаёмся на той же полосе)
                waypoints.append((road_half + 20, entry_y))
                waypoints.append((entry_dist, entry_y))

            elif turn_direction == 'left':
                # НАЛЕВО → СЕВЕР (поворот вверх ↑)
                # Север движется ВВЕРХ (от center вниз), исходящие полосы: X = -30, -10
                # Используем ту же полосу (lane 0 -> -30, lane 1 -> -10)
                exit_x = -road_half + (lane + 0.5) * LANE_WIDTH

                waypoints.append((-15, entry_y))
                waypoints.append((-5, -5))
                waypoints.append((exit_x, -15))
                waypoints.append((exit_x, -road_half - 20))
                waypoints.append((exit_x, -entry_dist))

            elif turn_direction == 'right':
                # НАПРАВО → ЮГ (поворот вниз ↓)
                # Юг движется ВНИЗ (от center вверх), исходящие полосы: X = +30, +10
                # Зеркалим: lane 0 -> +30, lane 1 -> +10
                exit_x = road_half - (lane + 0.5) * LANE_WIDTH

                waypoints.append((-15, entry_y))
                waypoints.append((-5, 5))
                waypoints.append((exit_x, 15))
                waypoints.append((exit_x, road_half + 20))
                waypoints.append((exit_x, entry_dist))

        # ════════════════════════════════════════════════════════
        # ВОСТОК → ЗАПАД (справа налево, движение ←)
        # ════════════════════════════════════════════════════════
        elif from_direction == 'from_east':
            # Входящие полосы востока: Y = +30 (lane 0) или Y = +10 (lane 1)
            entry_y = road_half - (lane + 0.5) * LANE_WIDTH

            waypoints.append((entry_dist, entry_y))
            waypoints.append((road_half + 20, entry_y))

            if turn_direction == 'straight':
                # ПРЯМО → запад
                waypoints.append((-road_half - 20, entry_y))
                waypoints.append((-entry_dist, entry_y))

            elif turn_direction == 'left':
                # НАЛЕВО → ЮГ (поворот вниз ↓)
                # Юг движется ВНИЗ, исходящие полосы: X = +30, +10
                # Используем ту же полосу (lane 0 -> +30, lane 1 -> +10)
                exit_x = road_half - (lane + 0.5) * LANE_WIDTH

                waypoints.append((15, entry_y))
                waypoints.append((5, 5))
                waypoints.append((exit_x, 15))
                waypoints.append((exit_x, road_half + 20))
                waypoints.append((exit_x, entry_dist))

            elif turn_direction == 'right':
                # НАПРАВО → СЕВЕР (поворот вверх ↑)
                # Север движется ВВЕРХ, исходящие полосы: X = -30, -10
                # Зеркалим: lane 0 -> -30, lane 1 -> -10
                exit_x = -road_half + (lane + 0.5) * LANE_WIDTH

                waypoints.append((15, entry_y))
                waypoints.append((5, -5))
                waypoints.append((exit_x, -15))
                waypoints.append((exit_x, -road_half - 20))
                waypoints.append((exit_x, -entry_dist))

        # ════════════════════════════════════════════════════════
        # СЕВЕР → ЮГ (сверху вниз, движение ↓)
        # ════════════════════════════════════════════════════════
        elif from_direction == 'from_north':
            # Входящие полосы севера: X = +30 (lane 0) или X = +10 (lane 1)
            entry_x = road_half - (lane + 0.5) * LANE_WIDTH

            waypoints.append((entry_x, -entry_dist))
            waypoints.append((entry_x, -road_half - 20))

            if turn_direction == 'straight':
                # ПРЯМО → юг
                waypoints.append((entry_x, road_half + 20))
                waypoints.append((entry_x, entry_dist))

            elif turn_direction == 'left':
                # НАЛЕВО → ВОСТОК (поворот направо →)
                # Восток движется ВЛЕВО, исходящие полосы: Y = +30, +10
                # Используем ту же полосу (lane 0 -> +30, lane 1 -> +10)
                exit_y = road_half - (lane + 0.5) * LANE_WIDTH

                waypoints.append((entry_x, -15))
                waypoints.append((5, -5))
                waypoints.append((15, exit_y))
                waypoints.append((road_half + 20, exit_y))
                waypoints.append((entry_dist, exit_y))

            elif turn_direction == 'right':
                # НАПРАВО → ЗАПАД (поворот налево ←)
                # Запад движется ВПРАВО, исходящие полосы: Y = -30, -10
                # Зеркалим: lane 0 -> -30, lane 1 -> -10
                exit_y = -road_half + (lane + 0.5) * LANE_WIDTH

                waypoints.append((entry_x, -15))
                waypoints.append((-5, -5))
                waypoints.append((-15, exit_y))
                waypoints.append((-road_half - 20, exit_y))
                waypoints.append((-entry_dist, exit_y))

        # ════════════════════════════════════════════════════════
        # ЮГ → СЕВЕР (снизу вверх, движение ↑)
        # ════════════════════════════════════════════════════════
        elif from_direction == 'from_south':
            # Входящие полосы юга: X = -30 (lane 0) или X = -10 (lane 1)
            entry_x = -road_half + (lane + 0.5) * LANE_WIDTH

            waypoints.append((entry_x, entry_dist))
            waypoints.append((entry_x, road_half + 20))

            if turn_direction == 'straight':
                # ПРЯМО → север
                waypoints.append((entry_x, -road_half - 20))
                waypoints.append((entry_x, -entry_dist))

            elif turn_direction == 'left':
                # НАЛЕВО → ЗАПАД (поворот налево ←)
                # Запад движется ВПРАВО, исходящие полосы: Y = -30, -10
                # Используем ту же полосу (lane 0 -> -30, lane 1 -> -10)
                exit_y = -road_half + (lane + 0.5) * LANE_WIDTH

                waypoints.append((entry_x, 15))
                waypoints.append((-5, 5))
                waypoints.append((-15, exit_y))
                waypoints.append((-road_half - 20, exit_y))
                waypoints.append((-entry_dist, exit_y))

            elif turn_direction == 'right':
                # НАПРАВО → ВОСТОК (поворот направо →)
                # Восток движется ВЛЕВО, исходящие полосы: Y = +30, +10
                # Зеркалим: lane 0 -> +30, lane 1 -> +10
                exit_y = road_half - (lane + 0.5) * LANE_WIDTH

                waypoints.append((entry_x, 15))
                waypoints.append((5, 5))
                waypoints.append((15, exit_y))
                waypoints.append((road_half + 20, exit_y))
                waypoints.append((entry_dist, exit_y))

        return waypoints


# =============================
#  КЛАСС МАШИНЫ
# =============================
class Car:
    """Представляет одно транспортное средство, следующее по waypoints."""
    SAFE_DISTANCE = 40  # Безопасное расстояние до впереди идущей машины
    WAYPOINT_REACH_DISTANCE = 15  # Расстояние для достижения waypoint
    LANE_CHANGE_DISTANCE = 50  # Минимальное расстояние для безопасного перестроения

    def __init__(self, waypoints, speed, color, from_direction, turn_direction):
        """
        Args:
            waypoints: Список контрольных точек [(x, y), ...]
            speed: Скорость движения
            color: Цвет машины
            from_direction: Направление въезда
            turn_direction: Направление поворота
        """
        self.waypoints = waypoints
        self.current_waypoint_index = 0
        self.pos = list(waypoints[0])
        self.speed = speed
        self.current_speed = speed
        self.color = color
        self.neon_color = self.generate_neon_color(color)
        self.from_direction = from_direction
        self.turn_direction = turn_direction

        # Размеры машины
        car_type = random.choice(['small', 'medium', 'large'])
        if car_type == 'small':
            self.length = 8
            self.width = 4
        elif car_type == 'medium':
            self.length = 12
            self.width = 6
        else:
            self.length = 16
            self.width = 7

        # Состояние
        self.waiting_time = 0.0
        self.is_waiting = False
        self.glow_pulse = random.uniform(0, math.pi * 2)

        # Вычисляем начальное направление
        self.heading = self._calculate_heading()

    def _calculate_heading(self):
        """Вычисляет направление движения к следующему waypoint."""
        if self.current_waypoint_index >= len(self.waypoints) - 1:
            return [1, 0]  # Default

        current = self.waypoints[self.current_waypoint_index]
        next_wp = self.waypoints[self.current_waypoint_index + 1]

        dx = next_wp[0] - current[0]
        dy = next_wp[1] - current[1]
        dist = math.hypot(dx, dy)

        if dist > 0:
            return [dx / dist, dy / dist]
        return [1, 0]

    def _move_towards_waypoint(self, dt, speed):
        """Двигается к текущему waypoint."""
        if self.current_waypoint_index >= len(self.waypoints):
            return False  # Достигли конца пути

        target = self.waypoints[self.current_waypoint_index]
        dx = target[0] - self.pos[0]
        dy = target[1] - self.pos[1]
        dist = math.hypot(dx, dy)

        # Достигли текущего waypoint?
        if dist < self.WAYPOINT_REACH_DISTANCE:
            self.current_waypoint_index += 1
            if self.current_waypoint_index < len(self.waypoints):
                self.heading = self._calculate_heading()
            return True

        # Двигаемся к waypoint
        if dist > 0:
            self.heading = [dx / dist, dy / dist]
            move_dist = min(speed * dt, dist)
            self.pos[0] += self.heading[0] * move_dist
            self.pos[1] += self.heading[1] * move_dist

        return True

    def _check_traffic_light(self, controller):
        """Проверяет, нужно ли остановиться на светофоре."""
        road_half = (NUM_LANES * LANE_WIDTH) / 2
        stop_distance = 20

        # Проверяем только перед перекрестком
        if self.current_waypoint_index >= len(self.waypoints) - 2:
            return False  # Уже проехали перекресток

        # Определяем направление движения
        if abs(self.heading[0]) > abs(self.heading[1]):  # Горизонтальное
            light_color = controller.get_color('horizontal')
            in_stop_zone = (-road_half - stop_distance < self.pos[0] < -road_half + 10 and self.heading[0] > 0) or \
                          (road_half - 10 < self.pos[0] < road_half + stop_distance and self.heading[0] < 0)
        else:  # Вертикальное
            light_color = controller.get_color('vertical')
            in_stop_zone = (-road_half - stop_distance < self.pos[1] < -road_half + 10 and self.heading[1] > 0) or \
                          (road_half - 10 < self.pos[1] < road_half + stop_distance and self.heading[1] < 0)

        return in_stop_zone and light_color in ['red', 'yellow']

    def _find_car_ahead(self, all_cars):
        """Находит ближайшую машину впереди на том же пути."""
        min_dist = float('inf')
        car_ahead = None

        for other in all_cars:
            if other is self:
                continue

            # Проверяем, едет ли в том же направлении
            dot_product = self.heading[0] * other.heading[0] + self.heading[1] * other.heading[1]
            if dot_product < 0.7:  # Не в том же направлении
                continue

            # Вычисляем расстояние
            dx = other.pos[0] - self.pos[0]
            dy = other.pos[1] - self.pos[1]
            dist = math.hypot(dx, dy)

            # Машина должна быть впереди
            forward_dot = dx * self.heading[0] + dy * self.heading[1]
            if forward_dot > 0 and dist < min_dist:
                min_dist = dist
                car_ahead = other

        return car_ahead, min_dist

    @staticmethod
    def generate_neon_color(base_color):
        """Генерирует яркий неоновый цвет на основе базового."""
        return tuple(min(255, c + 100) for c in base_color)

    def update(self, dt, controller, all_cars):
        """Обновляет позицию автомобиля, следуя по waypoints."""
        self.glow_pulse += dt * 3

        effective_speed = self.speed
        was_waiting = self.is_waiting
        self.is_waiting = False

        # Проверяем светофор
        if self._check_traffic_light(controller):
            effective_speed = 0
            self.is_waiting = True

        # Проверяем машину впереди
        if not self.is_waiting:
            car_ahead, dist_ahead = self._find_car_ahead(all_cars)

            if car_ahead and dist_ahead < self.SAFE_DISTANCE:
                effective_speed = 0
                self.is_waiting = True
            elif car_ahead and dist_ahead < self.SAFE_DISTANCE * 2:
                # Плавное торможение
                slow_factor = (dist_ahead - self.SAFE_DISTANCE) / self.SAFE_DISTANCE
                effective_speed *= max(0.3, slow_factor)

        # Обновляем время ожидания
        if self.is_waiting:
            self.waiting_time += dt
        else:
            self.waiting_time = 0.0

        # Двигаемся к следующему waypoint
        self._move_towards_waypoint(dt, effective_speed)

    # Удаляем старые методы перестроения и поворотов
    # def try_lane_change(self, all_cars):
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

        # Проверяем каждую возможную полосу на безопасность
        for target_lane in possible_lanes:
            if self.is_lane_safe(target_lane, all_cars):
                self.start_lane_change(target_lane)
                return

    def is_lane_safe(self, target_lane, all_cars):
        """Проверяет, безопасно ли перестроиться на целевую полосу."""
        road_half = (NUM_LANES * LANE_WIDTH) / 2
        target_offset = -road_half + target_lane * LANE_WIDTH + LANE_WIDTH / 2

        for other in all_cars:
            if other is self:
                continue

            # Проверяем только машины на той же дороге
            if (abs(self.heading[0] - other.heading[0]) < 0.1 and
                abs(self.heading[1] - other.heading[1]) < 0.1):

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

    def update(self, dt, controller):
        self.glow_pulse += dt * 4

        can_cross = controller.is_all_red()
        road_half = (NUM_LANES * LANE_WIDTH) / 2
        on_intersection = (-road_half < self.pos[0] < road_half and -road_half < self.pos[1] < road_half)

        if on_intersection or can_cross:
            dx = self.goal[0] - self.pos[0]
            dy = self.goal[1] - self.pos[1]
            dist = math.hypot(dx, dy)
            if dist > 1:
                move_dist = self.speed * dt
                self.pos[0] += move_dist * (dx / dist)
                self.pos[1] += move_dist * (dy / dist)

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
        """Создает машину с waypoint-based маршрутом."""
        # Выбираем случайную полосу (0 или 1 для каждого направления)
        lane = random.randint(0, 1)

        # Выбираем направление поворота с вероятностями
        turn_direction = random.choices(
            ['straight', 'left', 'right'],
            weights=[0.6, 0.2, 0.2]
        )[0]

        # Генерируем путь
        waypoints = PathGenerator.generate_waypoints(direction, lane, turn_direction)

        # Создаем машину
        speed = random.uniform(SPEED_MIN, SPEED_MAX)
        color = random.choice([RED, GREEN, BLUE, YELLOW, WHITE])

        car = Car(waypoints, speed, color, direction, turn_direction)
        self.cars.append(car)

        print(f"Spawned car: {direction}, lane {lane}, turn {turn_direction}")

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

        # генерация машин
        for direction, density in self.controller.traffic_density.items():
            if density > 0:
                interval = 10.0 / density
                self.last_car_spawns[direction] += dt
                if self.last_car_spawns[direction] > interval and len(self.cars) < MAX_CARS:
                    self.spawn_car(direction)
                    self.last_car_spawns[direction] = 0

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
        self.peds[:] = [p for p in self.peds if math.hypot(p.pos[0] - p.goal[0], p.pos[1] - p.goal[1]) > 5]

    def draw(self, screen):
        """Рисует все объекты симуляции."""
        for car in self.cars:
            car.draw(screen)
        for ped in self.peds:
            ped.draw(screen)
