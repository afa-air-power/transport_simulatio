import pygame
import random
import math
from collections import defaultdict

from constants import *
from constants import LANES_PER_DIRECTION, INTERSECTION_SIZE
from traffic_controller import TrafficController


# =============================
#  КЛАСС МАШИНЫ (IDM + Правила ДД)
# =============================
class Car:
    """
    Автомобиль с реалистичной моделью движения IDM (Intelligent Driver Model).
    Поддерживает двунаправленное движение, перестроение и повороты.
    """
    _id_counter = 0  # Для уникальных ID машин
    """Представляет одно транспортное средство в симуляции."""
    SAFE_DISTANCE = 60  # Увеличенное расстояние между машинами
    LANE_CHANGE_DISTANCE = 80  # Дистанция для безопасного перестроения
    BRAKING_DISTANCE = 100  # Дистанция для начала торможения
    SLOW_DOWN_DISTANCE = 120  # Дистанция для снижения скорости
    ACCELERATION_DISTANCE = 200  # Дистанция для начала ускорения на пустом участке
    MAX_ACCELERATION_RATE = 0.8  # Коэффициент ускорения на пустой дороге

    def __init__(self, pos, heading, speed, color, direction=None, lane=0):
        # Уникальный ID для машины
        self.id = Car._id_counter
        Car._id_counter += 1

        self.pos = list(pos)
        self.heading = list(heading)
        self.speed = speed
        self.current_speed = speed  # Текущая скорость (может отличаться от базовой)
        self.color = color
        self.neon_color = self.generate_neon_color(color)

        # Направление движения машины
        self.current_direction = direction if direction else self._infer_direction_from_heading(heading)
        self.lane = lane

        # Разнообразие размеров машин
        car_type = random.choice(['small', 'medium', 'large'])
        if car_type == 'small':
            self.length = 8
            self.width = 4
        elif car_type == 'medium':
            self.length = 12
            self.width = 6
        else:  # large
            self.length = 16
            self.width = 7

        self.waiting_time = 0.0
        self.is_waiting = False

        # Логика поворотов - улучшенная система
        self.turn_direction = random.choice(['straight', 'left', 'right'])
        self.is_turning = False
        self.turn_started = False
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
        self.current_lane = lane
        self.target_lane = lane
        self.is_changing_lane = False
        self.lane_change_progress = 0.0
        self.lane_change_start_pos = [0, 0]
        self.lane_change_target_offset = 0
        self.last_lane_change_time = 0
        self.lane_change_cooldown = 3.0  # Секунды между перестроениями

        # IDM параметры (Intelligent Driver Model)
        self.desired_speed = speed  # Желаемая скорость
        self.min_gap = 10  # Минимальное расстояние до лидера (м)
        self.desired_time_headway = 1.5  # Желаемый временной интервал (с)
        self.max_acceleration = 2.0  # Максимальное ускорение (м/с²)
        self.comfortable_deceleration = 3.0  # Комфортное торможение (м/с²)
        self.acceleration = 0.0  # Текущее ускорение

    def get_initial_position(self):
        """Возвращает начальную позицию машины на краю карты."""
        road_half = (NUM_LANES * LANE_WIDTH) / 2
        spawn_distance = ROAD_SIZE + 50  # За пределами видимой области

        # Определяем смещение полосы
        # Полосы нумеруются от центра: 0-1 для одного направления, 2-3 для другого
        if self.start_direction == 'from_west':
            # Движемся на восток (вправо)
            # Полосы снизу от центральной линии
            lane_offset = road_half - (self.lane + 0.5) * LANE_WIDTH
            return [-spawn_distance, lane_offset]
        elif self.start_direction == 'from_east':
            # Движемся на запад (влево)
            # Полосы сверху от центральной линии
            lane_offset = -road_half + (self.lane + 0.5) * LANE_WIDTH
            return [spawn_distance, lane_offset]
        elif self.start_direction == 'from_north':
            # Движемся на юг (вниз)
            # Полосы справа от центральной линии
            lane_offset = road_half - (self.lane + 0.5) * LANE_WIDTH
            return [lane_offset, -spawn_distance]
        else:  # from_south
            # Движемся на север (вверх)
            # Полосы слева от центральной линии
            lane_offset = -road_half + (self.lane + 0.5) * LANE_WIDTH
            return [lane_offset, spawn_distance]

    def get_heading_vector(self):
        """Возвращает вектор направления движения."""
        if self.current_direction in ['from_west', 'to_east']:
            return [1, 0]  # Вправо
        elif self.current_direction in ['from_east', 'to_west']:
            return [-1, 0]  # Влево
        elif self.current_direction in ['from_north', 'to_south']:
            return [0, 1]  # Вниз
        else:  # from_south, to_north
            return [0, -1]  # Вверх

    def get_lane_center_offset(self):
        """Возвращает смещение центра текущей полосы от оси дороги."""
        road_half = (NUM_LANES * LANE_WIDTH) / 2

        # В зависимости от направления, полосы располагаются по-разному
        if self.current_direction in ['from_west', 'to_east']:
            # Горизонтальное движение вправо - полосы снизу
            return road_half - (self.lane + 0.5) * LANE_WIDTH
        elif self.current_direction in ['from_east', 'to_west']:
            # Горизонтальное движение влево - полосы сверху
            return -road_half + (self.lane + 0.5) * LANE_WIDTH
        elif self.current_direction in ['from_north', 'to_south']:
            # Вертикальное движение вниз - полосы справа
            return road_half - (self.lane + 0.5) * LANE_WIDTH
        else:  # from_south, to_north
            # Вертикальное движение вверх - полосы слева
            return -road_half + (self.lane + 0.5) * LANE_WIDTH

    @staticmethod
    def generate_neon_color(base_color):
        """Генерирует яркий неоновый цвет на основе базового."""
        return tuple(min(255, c + 100) for c in base_color)

    def _infer_direction_from_heading(self, heading):
        """Определяет направление движения по вектору heading."""
        if abs(heading[0]) > abs(heading[1]):
            # Горизонтальное движение
            if heading[0] > 0:
                return 'from_west'  # Движемся на восток
            else:
                return 'from_east'  # Движемся на запад
        else:
            # Вертикальное движение
            if heading[1] > 0:
                return 'from_north'  # Движемся на юг
            else:
                return 'from_south'  # Движемся на север

    def calculate_idm_acceleration(self, leader_distance, leader_speed):
        """
        Вычисляет ускорение по модели IDM (Intelligent Driver Model).

        Формула IDM:
        a = a_max * [1 - (v/v0)^δ - (s*/s)^2]
        где s* = s0 + vT + (v·Δv)/(2√(ab))

        Args:
            leader_distance: Чистое расстояние до лидера (за вычетом длин машин)
            leader_speed: Скорость лидера

        Returns:
            Ускорение в пикселях/сек²
        """
        v = self.current_speed
        v0 = self.desired_speed

        # Свободное ускорение (когда нет препятствий)
        if v0 > 0:
            free_term = 1.0 - (v / v0) ** IDM_ACCELERATION_EXPONENT
        else:
            free_term = 0.0

        # Если есть лидер впереди
        if leader_distance is not None and leader_distance < VISIBILITY_RANGE:
            delta_v = v - leader_speed

            # Желаемая динамическая дистанция s*
            interaction_term = v * self.desired_time_headway

            # Умный тормозной компонент
            if self.comfortable_deceleration > 0 and self.max_acceleration > 0:
                braking_term = (v * delta_v) / (2 * math.sqrt(
                    self.max_acceleration * self.comfortable_deceleration
                ))
            else:
                braking_term = 0

            desired_gap = self.min_gap + interaction_term + braking_term

            # Взаимодействие с лидером
            if leader_distance > 0.1:
                interaction_factor = (desired_gap / leader_distance) ** 2
            else:
                # Аварийное торможение!
                return -IDM_SAFE_DECELERATION

            # Итоговое ускорение
            accel = self.max_acceleration * (free_term - interaction_factor)
        else:
            # Нет лидера - свободное ускорение
            accel = self.max_acceleration * free_term

        # Ограничения на ускорение
        accel = max(-IDM_SAFE_DECELERATION, min(self.max_acceleration, accel))

        return accel

    def find_leader(self, all_cars):
        """
        Находит ближайший автомобиль впереди в той же полосе.

        Returns:
            (distance, speed) или (None, None)
        """
        min_distance = float('inf')
        leader = None

        for other in all_cars:
            if other.id == self.id:
                continue

            # Проверяем, движется ли в том же направлении
            if other.current_direction != self.current_direction:
                continue

            # Проверяем, в той же ли полосе
            if other.lane != self.lane:
                continue

            # Вычисляем расстояние по направлению движения
            dx = other.pos[0] - self.pos[0]
            dy = other.pos[1] - self.pos[1]

            forward_dist = dx * self.heading[0] + dy * self.heading[1]

            # Машина должна быть впереди
            if forward_dist > 0:
                total_dist = math.hypot(dx, dy)
                if total_dist < min_distance:
                    min_distance = total_dist
                    leader = other

        if leader:
            # Вычитаем длины машин для получения чистого зазора
            net_gap = min_distance - (self.length + leader.length) / 2
            return max(0, net_gap), leader.current_speed

        return None, None

    def check_traffic_light(self, controller):
        """
        Проверяет расстояние до светофора и необходимость остановки.

        Returns:
            (distance_to_stop_line, must_stop) или (None, False)
        """
        intersection_half = INTERSECTION_SIZE / 2
        stop_line = intersection_half + TRAFFIC_LIGHT_STOP_DISTANCE

        # Определяем расстояние до стоп-линии
        if self.current_direction == 'from_west':
            distance = -intersection_half - self.pos[0]
            light_color = controller.get_color('horizontal')
        elif self.current_direction == 'from_east':
            distance = self.pos[0] - intersection_half
            light_color = controller.get_color('horizontal')
        elif self.current_direction == 'from_north':
            distance = -intersection_half - self.pos[1]
            light_color = controller.get_color('vertical')
        else:  # from_south
            distance = self.pos[1] - intersection_half
            light_color = controller.get_color('vertical')

        # Если перед светофором и он красный/желтый
        if 0 < distance < VISIBILITY_RANGE:
            must_stop = light_color in ['red', 'yellow']
            return distance, must_stop

        return None, False

    def should_prepare_for_turn(self):
        """Проверяет, нужно ли перестраиваться для будущего поворота."""
        if self.turn_direction == 'straight' or self.is_turning:
            return False

        # Расстояние до перекрестка
        intersection_half = INTERSECTION_SIZE / 2
        distance_to_intersection = 0

        if abs(self.heading[0]) > abs(self.heading[1]):  # Горизонтальное
            if self.heading[0] > 0:  # На восток
                distance_to_intersection = -intersection_half - self.pos[0]
            else:  # На запад
                distance_to_intersection = self.pos[0] - intersection_half
        else:  # Вертикальное
            if self.heading[1] > 0:  # На юг
                distance_to_intersection = -intersection_half - self.pos[1]
            else:  # На север
                distance_to_intersection = self.pos[1] - intersection_half

        # Начинаем перестроение за 100 метров до перекрестка
        return 0 < distance_to_intersection < 100

    def get_target_lane_for_turn(self):
        """Возвращает целевую полосу для планируемого поворота."""
        from constants import LANES_PER_DIRECTION

        current_lane = self.get_current_lane()
        direction = current_lane // LANES_PER_DIRECTION
        direction_start = direction * LANES_PER_DIRECTION
        direction_end = direction_start + LANES_PER_DIRECTION - 1

        if self.turn_direction == 'left':
            # Левый поворот - крайняя левая полоса направления
            return direction_start
        elif self.turn_direction == 'right':
            # Правый поворот - крайняя правая полоса направления
            return direction_end
        else:
            # Прямо - любая средняя полоса
            return current_lane

    def check_start_turn(self):
        """Проверяет, нужно ли начинать поворот на перекрестке."""
        intersection_half = INTERSECTION_SIZE / 2

        # Проверяем, достигли ли перекрестка
        in_intersection = False

        if abs(self.heading[0]) > abs(self.heading[1]):  # Горизонтальное движение
            if -intersection_half < self.pos[0] < intersection_half:
                in_intersection = True
        else:  # Вертикальное движение
            if -intersection_half < self.pos[1] < intersection_half:
                in_intersection = True

        # Если в зоне перекрестка и еще не начали поворот
        if in_intersection and self.turn_direction != 'straight' and not self.is_turning:
            self.start_turn()

    def start_turn(self):
        """Начинает поворот на перекрестке."""
        self.is_turning = True
        self.turn_progress = 0.0

        # Определяем радиус и направление поворота
        if self.turn_direction == 'left':
            turn_radius = INTERSECTION_SIZE * 0.4
            sign = 1
        elif self.turn_direction == 'right':
            turn_radius = INTERSECTION_SIZE * 0.25
            sign = -1
        else:
            return  # Прямо - не поворачиваем

        # Вычисляем центр окружности поворота в зависимости от направления движения
        if abs(self.heading[0]) > abs(self.heading[1]):  # Горизонтальное движение
            if self.heading[0] > 0:  # Движемся на восток
                self.turn_center = [self.pos[0], self.pos[1] - turn_radius * sign]
            else:  # Движемся на запад
                self.turn_center = [self.pos[0], self.pos[1] + turn_radius * sign]
        else:  # Вертикальное движение
            if self.heading[1] > 0:  # Движемся на юг
                self.turn_center = [self.pos[0] + turn_radius * sign, self.pos[1]]
            else:  # Движемся на север
                self.turn_center = [self.pos[0] - turn_radius * sign, self.pos[1]]

        # Вычисляем начальный угол
        self.turn_start_angle = math.atan2(
            self.pos[1] - self.turn_center[1],
            self.pos[0] - self.turn_center[0]
        )

        # Конечный угол (поворот на 90 градусов)
        if self.turn_direction == 'left':
            self.turn_end_angle = self.turn_start_angle + math.pi / 2
        else:  # right
            self.turn_end_angle = self.turn_start_angle - math.pi / 2

    def update(self, dt, controller, all_cars):
        """Главный метод обновления состояния автомобиля."""
        self.glow_pulse += dt * 3
        self.last_lane_change_time += dt

        road_half = (NUM_LANES * LANE_WIDTH) / 2
        stop_buffer = 15
        stop_pos = road_half + stop_buffer

        effective_speed = self.speed
        was_waiting = self.is_waiting
        self.is_waiting = False

        # Проверяем светофор (если не поворачиваем)
        if not self.is_turning:
            if abs(self.heading[0]) > abs(self.heading[1]):
                light = controller.get_color('horizontal')
                if light in ['red', 'yellow']:
                    if self.heading[0] > 0 and -stop_pos < self.pos[0] < -road_half:
                        effective_speed = 0
                        self.is_waiting = True
                    elif self.heading[0] < 0 and road_half < self.pos[0] < stop_pos:
                        effective_speed = 0
                        self.is_waiting = True
            else:
                light = controller.get_color('vertical')
                if light in ['red', 'yellow']:
                    if self.heading[1] > 0 and -stop_pos < self.pos[1] < -road_half:
                        effective_speed = 0
                        self.is_waiting = True
                    elif self.heading[1] < 0 and road_half < self.pos[1] < stop_pos:
                        effective_speed = 0
                        self.is_waiting = True

        # Проверяем дистанцию до впереди идущих машин и возможность перестроения
        if not self.is_turning and not self.is_changing_lane:
            car_ahead = None
            min_distance = float('inf')
            current_lane = self.get_current_lane()

            for other in all_cars:
                if other is self:
                    continue

                # Проверяем машины в той же полосе и направлении
                if (abs(self.heading[0] - other.heading[0]) < 0.1 and
                    abs(self.heading[1] - other.heading[1]) < 0.1):

                    other_lane = other.get_current_lane()
                    
                    # Проверяем только машины в той же полосе
                    if other_lane == current_lane:
                        dx = other.pos[0] - self.pos[0]
                        dy = other.pos[1] - self.pos[1]
                        dist = math.hypot(dx, dy)

                        # Проверяем, впереди ли машина
                        forward = (dx * self.heading[0] + dy * self.heading[1]) > 0
                        if forward and dist < min_distance:
                            min_distance = dist
                            car_ahead = other

            # Условия изменения скорости в зависимости от препятствия спереди
            if car_ahead:
                if min_distance < self.SAFE_DISTANCE:
                    # Полная остановка при критическом расстоянии
                    effective_speed = 0
                    self.is_waiting = True
                    
                    # Пытаемся перестроиться, если возможно
                    if self.last_lane_change_time > self.lane_change_cooldown:
                        self.try_lane_change(all_cars)
                        
                elif min_distance < self.BRAKING_DISTANCE:
                    # Сильное торможение при близкой дистанции
                    speed_reduction = 1.0 - (min_distance - self.SAFE_DISTANCE) / (self.BRAKING_DISTANCE - self.SAFE_DISTANCE)
                    effective_speed *= max(0.1, 1.0 - speed_reduction * 0.8)
                    
                    # Пытаемся перестроиться при торможении
                    if self.last_lane_change_time > self.lane_change_cooldown * 0.7:
                        self.try_lane_change(all_cars)
                        
                elif min_distance < self.SLOW_DOWN_DISTANCE:
                    # Плавное замедление при средней дистанции
                    speed_reduction = (self.SLOW_DOWN_DISTANCE - min_distance) / (self.SLOW_DOWN_DISTANCE - self.BRAKING_DISTANCE)
                    effective_speed *= max(0.4, 1.0 - speed_reduction * 0.5)
                    
            else:
                # Нет препятствий впереди - можем ускориться на пустом участке
                if min_distance > self.ACCELERATION_DISTANCE or min_distance == float('inf'):
                    # Ускорение на пустой дороге - увеличиваем до максимальной скорости
                    acceleration_factor = 1.0 + self.MAX_ACCELERATION_RATE
                    effective_speed = min(effective_speed * acceleration_factor, self.speed * 1.5)  # Максимум 150% от базовой скорости
                    
        # Дополнительная проверка машин в соседних полосах для предупреждения
        effective_speed = self.check_side_obstacles(all_cars, effective_speed)
        
        # Обновляем текущую скорость для отслеживания
        self.current_speed = effective_speed

        # Обновляем время ожидания
        if self.is_waiting:
            self.waiting_time += dt
        elif was_waiting and not self.is_waiting:
            self.waiting_time = 0.0

        # Проверяем, нужно ли перестроиться для поворота
        if not self.is_turning and not self.is_changing_lane and not self.is_waiting:
            if self.should_prepare_for_turn():
                target_lane = self.get_target_lane_for_turn()
                if target_lane != self.get_current_lane():
                    if self.is_lane_safe(target_lane, all_cars):
                        self.start_lane_change(target_lane)

        # Проверяем начало поворота
        if not self.is_turning and not self.is_waiting and not self.is_changing_lane:
            self.check_start_turn()

        # Обновляем позицию
        if self.is_changing_lane:
            self.update_lane_change(dt, all_cars)
        elif self.is_turning:
            self.update_turn(dt, effective_speed)
        else:
            # Плавная интерполяция направления для более естественного движения
            self.heading[0] += (self.target_heading[0] - self.heading[0]) * self.heading_interpolation
            self.heading[1] += (self.target_heading[1] - self.heading[1]) * self.heading_interpolation

            self.pos[0] += self.heading[0] * effective_speed * dt
            self.pos[1] += self.heading[1] * effective_speed * dt

            # Ограничиваем позицию границами дороги
            self.clamp_to_lane_boundaries()

    def check_side_obstacles(self, all_cars, current_speed):
        """Проверяет препятствия в соседних полосах и корректирует скорость."""
        from constants import LANES_PER_DIRECTION
        if NUM_LANES < 2:
            return current_speed
            
        road_half = (NUM_LANES * LANE_WIDTH) / 2
        current_lane = self.get_current_lane()
        
        # Проверяем соседние полосы на наличие медленных машин
        for other in all_cars:
            if other is self:
                continue
                
            # Проверяем только машины в том же направлении движения
            if (abs(self.heading[0] - other.heading[0]) < 0.1 and
                abs(self.heading[1] - other.heading[1]) < 0.1):
                
                other_lane = other.get_current_lane()
                
                # Если машина в соседней полосе того же направления
                if (abs(other_lane - current_lane) == 1 and 
                    self.is_same_direction_lane(current_lane, other_lane)):
                    dx = other.pos[0] - self.pos[0]
                    dy = other.pos[1] - self.pos[1]
                    dist = math.hypot(dx, dy)
                    
                    # Проверяем, рядом ли машина (не сильно впереди или сзади)
                    longitudinal_dist = abs(dx * self.heading[0] + dy * self.heading[1])
                    if dist < 80 and longitudinal_dist < 40:
                        if other.is_waiting or other.current_speed < self.speed * 0.3:
                            # Слегка снижаем скорость из-за препятствия в соседней полосе
                            return current_speed * 0.85
                            
        return current_speed

    def get_current_lane(self):
        """Определяет текущую полосу автомобиля."""
        road_half = (NUM_LANES * LANE_WIDTH) / 2
        
        # Для горизонтального движения полоса определяется по Y
        # Для вертикального движения полоса определяется по X
        if abs(self.heading[0]) > abs(self.heading[1]):  # Горизонтальное движение
            relative_pos = self.pos[1]
        else:  # Вертикальное движение
            relative_pos = self.pos[0]

        # Преобразуем координату в номер полосы (0-3)
        # relative_pos изменяется от -road_half до +road_half
        current_lane = int((relative_pos + road_half) / LANE_WIDTH)

        # Ограничиваем диапазон
        current_lane = max(0, min(NUM_LANES - 1, current_lane))

        return current_lane

    def clamp_to_lane_boundaries(self):
        """Ограничивает позицию машины границами дороги и полосы."""
        if self.is_turning:
            return  # Во время поворота не ограничиваем

        road_half = (NUM_LANES * LANE_WIDTH) / 2
        margin = 1.0  # Небольшой отступ от края полосы

        if abs(self.heading[0]) > abs(self.heading[1]):  # Горизонтальное движение
            # Ограничиваем Y координату границами дороги
            min_y = -road_half + margin
            max_y = road_half - margin
            self.pos[1] = max(min_y, min(max_y, self.pos[1]))

        else:  # Вертикальное движение
            # Ограничиваем X координату границами дороги
            min_x = -road_half + margin
            max_x = road_half - margin
            self.pos[0] = max(min_x, min(max_x, self.pos[0]))

    def is_same_direction_lane(self, lane1, lane2):
        """Проверяет, находятся ли полосы в одном направлении движения."""
        from constants import LANES_PER_DIRECTION
        
        # Определяем направления полос (0-1 = первое направление, 2-3 = второе направление)
        direction1 = lane1 // LANES_PER_DIRECTION
        direction2 = lane2 // LANES_PER_DIRECTION
        
        return direction1 == direction2

    def try_lane_change(self, all_cars):
        """Пытается выполнить перестроение на соседнюю полосу в том же направлении."""
        from constants import LANES_PER_DIRECTION
        if NUM_LANES < 2:
            return

        self.current_lane = self.get_current_lane()
        
        # Определяем направление движения (какие 2 полосы доступны)
        direction = self.current_lane // LANES_PER_DIRECTION
        direction_start = direction * LANES_PER_DIRECTION
        direction_end = direction_start + LANES_PER_DIRECTION - 1

        # Выбираем целевую полосу (только в пределах того же направления)
        possible_lanes = []
        if self.current_lane > direction_start:
            possible_lanes.append(self.current_lane - 1)
        if self.current_lane < direction_end:
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
        for other in all_cars:
            if other is self:
                continue

            # Проверяем только машины в том же направлении движения
            if (abs(self.heading[0] - other.heading[0]) < 0.1 and
                abs(self.heading[1] - other.heading[1]) < 0.1):

                other_lane = other.get_current_lane()

                # Если машина на целевой полосе
                if other_lane == target_lane:
                    dx = other.pos[0] - self.pos[0]
                    dy = other.pos[1] - self.pos[1]
                    dist = math.hypot(dx, dy)

                    # Увеличенная проверка безопасности для перестроения
                    if dist < self.LANE_CHANGE_DISTANCE:
                        return False
                    
                    # Дополнительная проверка для машин, движущихся быстрее сзади
                    relative_speed = other.current_speed - self.current_speed
                    if relative_speed > 0:  # Другая машина быстрее
                        # Увеличиваем безопасную дистанцию в зависимости от разности скоростей
                        safe_distance = self.LANE_CHANGE_DISTANCE + relative_speed * 2
                        if dist < safe_distance:
                            return False

        return True

    def start_lane_change(self, target_lane):
        """Начинает процесс перестроения."""
        self.is_changing_lane = True
        self.lane_change_progress = 0.0
        self.lane_change_start_pos = list(self.pos)

        # Вычисляем целевую позицию в новой полосе
        self.lane_change_target_pos = list(self.pos)

        # Определяем смещение в зависимости от направления
        road_half = (NUM_LANES * LANE_WIDTH) / 2

        # Центр целевой полосы
        target_lane_center = -road_half + (target_lane + 0.5) * LANE_WIDTH

        # Для горизонтального движения меняем Y координату
        if abs(self.heading[0]) > abs(self.heading[1]):
            self.lane_change_target_pos[1] = target_lane_center
        # Для вертикального движения меняем X координату
        else:
            self.lane_change_target_pos[0] = target_lane_center

        # Обновляем целевую полосу
        old_lane = self.lane
        self.lane = target_lane
        self.last_lane_change_time = 0

        print(f"Car {self.id}: Lane change {old_lane} -> {target_lane}, pos: ({self.pos[0]:.1f}, {self.pos[1]:.1f}) -> ({self.lane_change_target_pos[0]:.1f}, {self.lane_change_target_pos[1]:.1f})")

    def update_lane_change(self, dt, all_cars):
        """Обновляет позицию машины во время перестроения с продолжением IDM."""
        lane_change_duration = 3.0  # Длительность перестроения в секундах
        self.lane_change_progress += dt / lane_change_duration

        if self.lane_change_progress >= 1.0:
            # Перестроение завершено
            self.is_changing_lane = False
            self.lane_change_progress = 0.0
            self.lane_change_start_pos = None
            self.lane_change_target_pos = None
        else:
            # Продолжаем IDM в продольном направлении
            leader_gap, leader_speed = self.find_leader(all_cars)
            self.acceleration = self.calculate_idm_acceleration(leader_gap, leader_speed)
            new_speed = self.current_speed + self.acceleration * dt
            self.current_speed = max(0, min(new_speed, self.desired_speed * 1.2))

            # Плавная интерполяция бокового смещения
            t = self.ease_in_out_cubic(self.lane_change_progress)

            # Движение вперед
            self.pos[0] += self.heading[0] * self.current_speed * dt
            self.pos[1] += self.heading[1] * self.current_speed * dt

            # Боковое смещение (интерполяция между start и target)
            # Определяем по heading, а не по current_direction
            if abs(self.heading[0]) > abs(self.heading[1]):
                # Горизонтальное движение - смещение по Y
                start_y = self.lane_change_start_pos[1]
                target_y = self.lane_change_target_pos[1]
                self.pos[1] = start_y + (target_y - start_y) * t
            else:
                # Вертикальное движение - смещение по X
                start_x = self.lane_change_start_pos[0]
                target_x = self.lane_change_target_pos[0]
                self.pos[0] = start_x + (target_x - start_x) * t

    def update_turn(self, dt, effective_speed):
        """Обновляет позицию машины во время поворота."""
        if self.turn_direction == 'left':
            turn_radius = INTERSECTION_SIZE * 0.4
        else:
            turn_radius = INTERSECTION_SIZE * 0.25

        # Длительность поворота зависит от скорости
        arc_length = turn_radius * math.pi / 2
        turn_duration = arc_length / max(effective_speed, 1.0)

        self.turn_progress += dt / turn_duration

        if self.turn_progress >= 1.0:
            # Поворот завершен
            self.is_turning = False
            self.turn_progress = 0.0
            self.turn_started = False

            # Обновляем направление после поворота
            if self.turn_direction == 'left':
                # Поворот налево: меняем направление на 90 градусов против часовой
                new_heading = [-self.original_heading[1], self.original_heading[0]]
            elif self.turn_direction == 'right':
                # Поворот направо: меняем направление на 90 градусов по часовой
                new_heading = [self.original_heading[1], -self.original_heading[0]]
            else:
                new_heading = self.original_heading

            self.heading = new_heading
            self.target_heading = new_heading
            self.original_heading = new_heading

            # Обновляем current_direction после поворота
            self.current_direction = self._infer_direction_from_heading(new_heading)

            # Сбрасываем направление поворота для следующего перекрестка
            self.turn_direction = random.choice(['straight', 'left', 'right'])
        else:
            # Продолжаем поворот
            current_angle = self.turn_start_angle + (self.turn_end_angle - self.turn_start_angle) * self.turn_progress
            self.pos[0] = self.turn_center[0] + turn_radius * math.cos(current_angle)
            self.pos[1] = self.turn_center[1] + turn_radius * math.sin(current_angle)

            # Обновляем направление для плавности
            if self.turn_direction == 'left':
                # Поворот налево
                self.heading[0] = -math.sin(current_angle)
                self.heading[1] = math.cos(current_angle)
            else:
                # Поворот направо
                self.heading[0] = math.cos(current_angle - math.pi/2)
                self.heading[1] = math.sin(current_angle - math.pi/2)

    @staticmethod
    def ease_in_out_cubic(t):
        """Функция плавности для естественных переходов."""
        if t < 0.5:
            return 4 * t * t * t
        else:
            return 1 - pow(-2 * t + 2, 3) / 2

    def draw_direction_arrow(self, screen, center_x, center_y):
        """Рисует стрелку направления поворота над машиной."""
        if self.is_turning or self.turn_started:
            return  # Уже поворачиваем

        arrow_colors = {
            'straight': (0, 255, 0),  # Зеленый
            'right': (255, 255, 0),  # Желтый
            'left': (0, 150, 255)  # Голубой
        }

        if self.turn_direction not in arrow_colors:
            return

        x = center_x + self.pos[0]
        y = center_y + self.pos[1]
        color = arrow_colors[self.turn_direction]

        # Рисуем простую стрелку над машиной
        arrow_size = 12
        pygame.draw.circle(screen, color, (int(x), int(y - 20)), 8, 2)

        if self.turn_direction == 'left':
            pygame.draw.line(screen, color, (int(x - 5), int(y - 20)), (int(x), int(y - 25)), 2)
            pygame.draw.line(screen, color, (int(x - 5), int(y - 20)), (int(x), int(y - 15)), 2)
        elif self.turn_direction == 'right':
            pygame.draw.line(screen, color, (int(x + 5), int(y - 20)), (int(x), int(y - 25)), 2)
            pygame.draw.line(screen, color, (int(x + 5), int(y - 20)), (int(x), int(y - 15)), 2)
        else:  # straight
            pygame.draw.line(screen, color, (int(x), int(y - 28)), (int(x), int(y - 12)), 2)
            pygame.draw.line(screen, color, (int(x), int(y - 28)), (int(x - 3), int(y - 24)), 2)
            pygame.draw.line(screen, color, (int(x), int(y - 28)), (int(x + 3), int(y - 24)), 2)

    def draw(self, screen, center_x, center_y):
        """Рисует машину с неоновым стилем и индикаторами направления."""
        x = center_x + self.pos[0]
        y = center_y + self.pos[1]
        angle = math.degrees(math.atan2(self.heading[1], self.heading[0]))

        car_length = self.length
        car_width = self.width

        # Рисуем стрелку направления
        self.draw_direction_arrow(screen, center_x, center_y)

        # Неоновое свечение
        glow_size = int(6 + 3 * math.sin(self.glow_pulse))
        glow_surf = pygame.Surface((int(car_length) + glow_size * 2, int(car_width) + glow_size * 2), pygame.SRCALPHA)

        for i in range(glow_size, 0, -1):
            alpha = int(60 * (1 - i / glow_size))
            glow_color = (*self.neon_color, alpha)
            pygame.draw.rect(glow_surf, glow_color, 
                           (glow_size - i, glow_size - i, 
                            int(car_length) + i * 2, int(car_width) + i * 2), 
                           border_radius=4)

        rotated_glow = pygame.transform.rotate(glow_surf, -angle)
        glow_rect = rotated_glow.get_rect(center=(int(x), int(y)))
        screen.blit(rotated_glow, glow_rect)

        # Основная поверхность
        rect_surf = pygame.Surface((int(car_length), int(car_width)), pygame.SRCALPHA)

        # Темный корпус
        dark_color = tuple(min(80, c // 3) for c in self.color)
        pygame.draw.rect(rect_surf, dark_color, (0, 0, int(car_length), int(car_width)), border_radius=4)

        # Неоновая окантовка
        pygame.draw.rect(rect_surf, self.neon_color, 
                       (0, 0, int(car_length), int(car_width)), 2, border_radius=4)

        # Окна
        window_color = (20, 40, 60, 200)
        window_len = int(car_length * 0.25)
        pygame.draw.rect(rect_surf, window_color, 
                        (int(car_length * 0.7), int(car_width * 0.2), 
                         window_len, int(car_width * 0.6)), border_radius=2)

        # Фары
        if self.current_speed < 0.5:
            # Стоп-сигналы
            pygame.draw.circle(rect_surf, (255, 50, 50), (5, int(car_width * 0.3)), 2)
            pygame.draw.circle(rect_surf, (255, 50, 50), (5, int(car_width * 0.7)), 2)
        else:
            # Передние фары
            pygame.draw.circle(rect_surf, (200, 240, 255), (int(car_length) - 3, int(car_width * 0.3)), 2)
            pygame.draw.circle(rect_surf, (200, 240, 255), (int(car_length) - 3, int(car_width * 0.7)), 2)

        rotated = pygame.transform.rotate(rect_surf, -angle)
        rect = rotated.get_rect(center=(int(x), int(y)))
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
        intersection_half = INTERSECTION_SIZE / 2
        on_intersection = (-intersection_half < self.pos[0] < intersection_half and 
                          -intersection_half < self.pos[1] < intersection_half)

        if on_intersection or can_cross:
            dx = self.goal[0] - self.pos[0]
            dy = self.goal[1] - self.pos[1]
            dist = math.hypot(dx, dy)
            if dist > 1:
                move_dist = self.speed * dt
                self.pos[0] += move_dist * (dx / dist)
                self.pos[1] += move_dist * (dy / dist)

    def draw(self, screen, center_x, center_y):
        x = center_x + self.pos[0]
        y = center_y + self.pos[1]

        # Неоновое свечение
        glow_intensity = int(100 + 60 * math.sin(self.glow_pulse))
        glow_surf = pygame.Surface((self.size * 6, self.size * 6), pygame.SRCALPHA)
        for i in range(self.size * 2, 0, -1):
            alpha = int(glow_intensity * (1 - i / (self.size * 2)))
            pygame.draw.circle(glow_surf, (*self.neon_color, alpha), 
                             (self.size * 3, self.size * 3), i)
        screen.blit(glow_surf, (int(x) - self.size * 3, int(y) - self.size * 3))

        # Темное ядро
        dark_color = tuple(c // 3 for c in self.color)
        pygame.draw.circle(screen, dark_color, (int(x), int(y)), self.size)
        pygame.draw.circle(screen, self.neon_color, (int(x), int(y)), self.size, 2)
        pygame.draw.circle(screen, self.neon_color, (int(x), int(y)), self.size // 2)


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

        # Initialize stats dictionary
        self.stats = {
            'avg_wait_time': 0.0,
            'total_cars_passed': 0,
            'max_wait_time': 0.0
        }

    def update_screen_size(self):
        self.controller.update_light_positions()

    def toggle_pause(self):
        self.paused = not self.paused

    def spawn_car(self, direction):
        from constants import screen_config, DIRECTION_MAPPINGS, LANES_PER_DIRECTION

        # Половина ширины дороги (все 4 полосы)
        road_half = (NUM_LANES * LANE_WIDTH) / 2
        entry_dist = (screen_config.sim_width / 2) + 50

        # Получаем информацию о направлении
        dir_info = DIRECTION_MAPPINGS[direction]
        heading = dir_info['heading']

        # Логика создания машин для каждого направления
        # Горизонтальная дорога: Y координата определяет полосу
        # Вертикальная дорога: X координата определяет полосу

        if direction == 'from_west':
            # Едем на ВОСТОК (слева направо), верхние полосы (отрицательный Y)
            # Полосы 0-1 (верхние две полосы горизонтальной дороги)
            lane = random.randint(0, LANES_PER_DIRECTION - 1)
            # Y от -road_half до -road_half + 2*LANE_WIDTH
            lane_y = -road_half + lane * LANE_WIDTH + LANE_WIDTH / 2
            pos = (-entry_dist, lane_y)

        elif direction == 'from_east':
            # Едем на ЗАПАД (справа налево), нижние полосы (положительный Y)
            # Полосы 2-3 (нижние две полосы горизонтальной дороги)
            lane = random.randint(LANES_PER_DIRECTION, NUM_LANES - 1)
            # Y от -road_half + 2*LANE_WIDTH до road_half
            lane_y = -road_half + lane * LANE_WIDTH + LANE_WIDTH / 2
            pos = (entry_dist, lane_y)

        elif direction == 'from_north':
            # Едем на ЮГ (сверху вниз), левые полосы (отрицательный X)
            # Полосы 0-1 (левые две полосы вертикальной дороги)
            lane = random.randint(0, LANES_PER_DIRECTION - 1)
            # X от -road_half до -road_half + 2*LANE_WIDTH
            lane_x = -road_half + lane * LANE_WIDTH + LANE_WIDTH / 2
            pos = (lane_x, -entry_dist)

        elif direction == 'from_south':
            # Едем на СЕВЕР (снизу вверх), правые полосы (положительный X)
            # Полосы 2-3 (правые две полосы вертикальной дороги)
            lane = random.randint(LANES_PER_DIRECTION, NUM_LANES - 1)
            # X от -road_half + 2*LANE_WIDTH до road_half
            lane_x = -road_half + lane * LANE_WIDTH + LANE_WIDTH / 2
            pos = (lane_x, entry_dist)

        else:
            # Для обратных направлений (to_west, to_east, etc.) - не используем в основном потоке
            # Они нужны только для внутренней логики после поворотов
            lane = random.randint(0, NUM_LANES - 1)
            lane_offset = -road_half + lane * LANE_WIDTH + LANE_WIDTH / 2
            if 'west' in direction or 'east' in direction:
                pos = (-entry_dist if heading[0] > 0 else entry_dist, lane_offset)
            else:
                pos = (lane_offset, -entry_dist if heading[1] > 0 else entry_dist)

        speed = random.uniform(SPEED_MIN, SPEED_MAX)
        color = random.choice([RED, GREEN, BLUE, YELLOW, WHITE])

        # Создаем машину
        car = Car(pos, heading, speed, color, direction=direction, lane=lane)
        self.cars.append(car)

        # Отладочный вывод
        print(f"Spawned car: dir={direction}, lane={lane}, pos=({pos[0]:.1f}, {pos[1]:.1f}), heading={heading}")

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

        # Calculate statistics
        total_waiting_time = 0.0
        waiting_count = 0
        max_wait = 0.0

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

            # Подсчет ожидающих машин и статистики
            if car.is_waiting:
                waiting_count += 1
                total_waiting_time += car.waiting_time
                max_wait = max(max_wait, car.waiting_time)

                if abs(car.heading[0]) > abs(car.heading[1]):
                    self.waiting_cars_h += 1
                    self.h_wait_time_sq_sum += car.waiting_time ** 2
                else:
                    self.waiting_cars_v += 1
                    self.v_wait_time_sq_sum += car.waiting_time ** 2

        # Update stats dictionary
        if waiting_count > 0:
            self.stats['avg_wait_time'] = total_waiting_time / waiting_count
        else:
            self.stats['avg_wait_time'] = 0.0
        self.stats['max_wait_time'] = max_wait

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

    def draw(self, screen, center_x, center_y):
        """Рисует все объекты симуляции."""
        for car in self.cars:
            car.draw(screen, center_x, center_y)
        for ped in self.peds:
            ped.draw(screen, center_x, center_y)
