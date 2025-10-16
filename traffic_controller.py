# traffic_controller.py
import time
import math
from pygame.locals import SRCALPHA
from constants import *

class LightLens:
    def __init__(self, lens_color, offset):
        self.lens_color = lens_color
        self.offset = offset
        self.active = False

    def draw(self, screen, base_pos, current_time):
        pos = (base_pos[0] + self.offset[0], base_pos[1] + self.offset[1])
        fill_color = self.lens_color if self.active else GRAY
        pygame.draw.circle(screen, fill_color, pos, 8)
        pygame.draw.circle(screen, BLACK, pos, 8, 1)  # Border
        if self.active:
            glow = pygame.Surface((30, 30), SRCALPHA)
            if self.lens_color == YELLOW:
                glow_alpha = 80 + 40 * math.sin(current_time * 5)
            elif self.lens_color == RED:
                glow_alpha = 80 + 40 * math.sin(current_time * 2)
            else:  # GREEN
                glow_alpha = 80 + 40 * math.sin(current_time * 3)
            pygame.draw.circle(glow, (*self.lens_color, int(glow_alpha)), (15, 15), 15)
            screen.blit(glow, (pos[0] - 15, pos[1] - 15))

class TrafficLight:
    def __init__(self, position, orientation):
        self.position = position
        self.orientation = orientation
        self.current_color = 'red'
        if orientation == 'vertical':
            self.lenses = [
                LightLens(RED, (0, -20)),     # Top: red
                LightLens(YELLOW, (0, 0)),    # Middle: yellow
                LightLens(GREEN, (0, 20))     # Bottom: green
            ]
        else:  # horizontal
            self.lenses = [
                LightLens(RED, (-20, 0)),    # Left: red
                LightLens(YELLOW, (0, 0)),   # Middle: yellow
                LightLens(GREEN, (20, 0))    # Right: green
            ]

    def set_color(self, color):
        if self.current_color != color:
            self.current_color = color
            for lens in self.lenses:
                lens.active = lens.lens_color == {'red': RED, 'yellow': YELLOW, 'green': GREEN}[color]

    def draw(self, screen, center_x, center_y):
        base_pos = (center_x + self.position[0], center_y + self.position[1])
        # Draw housing
        if self.orientation == 'vertical':
            housing_rect = pygame.Rect(base_pos[0] - 10, base_pos[1] - 30, 20, 60)
        else:
            housing_rect = pygame.Rect(base_pos[0] - 30, base_pos[1] - 10, 60, 20)
        pygame.draw.rect(screen, BLACK, housing_rect, border_radius=5)
        current_time = time.time()
        for lens in self.lenses:
            lens.draw(screen, base_pos, current_time)

class TrafficController:
    def __init__(self):
        self.lights = {}
        self.reset_to_defaults()
        self.update_light_positions()
        self.update_lights()

    def reset_to_defaults(self):
        """Resets all settings and state to their default values."""
        self.phases = [
            {'duration': 30, 'west': 'green', 'east': 'green', 'north': 'red', 'south': 'red'},
            {'duration': 3, 'west': 'yellow', 'east': 'yellow', 'north': 'red', 'south': 'red'},
            {'duration': 2, 'west': 'red', 'east': 'red', 'north': 'red', 'south': 'red'},
            {'duration': 30, 'west': 'red', 'east': 'red', 'north': 'green', 'south': 'green'},
            {'duration': 3, 'west': 'red', 'east': 'red', 'north': 'yellow', 'south': 'yellow'},
            {'duration': 2, 'west': 'red', 'east': 'red', 'north': 'red', 'south': 'red'}
        ]
        self.current_phase = 0
        self.timer = 0
        self.mode = 'static'

        # Параметры динамического режима
        self.min_phase_time = 5.0
        self.max_phase_time = 60.0
        self.dynamic_logic_factor = 0.99  # Фактор затухания для взвешенного штрафа
        self.weighted_h_penalty = 0.0
        self.weighted_v_penalty = 0.0
        # Плотность трафика: машин в среднем за 10 секунд
        self.traffic_density = {d: 5.0 for d in DIR_INS}

        # Параметры дифференциального уравнения для динамического режима
        self.pressure_h = 0.0  # Давление горизонтального направления
        self.pressure_v = 0.0  # Давление вертикального направления
        self.pressure_growth_rate = 0.5  # Скорость роста давления
        self.pressure_decay_rate = 0.3  # Скорость спада давления
        self.switch_threshold = 10.0  # Порог переключения

        # Старые переменные для обратной совместимости и UI
        self.h_penalty = 0.0
        self.v_penalty = 0.0
        self.visible_cars_h = 0
        self.visible_cars_v = 0

        if self.lights:
            self.update_lights()

    def update_light_positions(self):
        """Обновляет позиции светофоров при изменении размера экрана"""
        from constants import screen_config
        road_half = (NUM_LANES * LANE_WIDTH) / 2
        light_dist = screen_config.sim_width * 0.15 # 15% от ширины экрана симуляции

        self.lights = {
            'h_left': TrafficLight((-light_dist, -road_half - 10), 'horizontal'),
            'h_right': TrafficLight((light_dist, road_half + 10), 'horizontal'),
            'v_top': TrafficLight((road_half + 10, -light_dist), 'vertical'),
            'v_bottom': TrafficLight((-road_half - 10, light_dist), 'vertical')
        }

    def update_lights(self):
        phase = self.phases[self.current_phase]
        west_color = phase.get('west', phase.get('horiz', 'red'))  # Обратная совместимость
        east_color = phase.get('east', phase.get('horiz', 'red'))
        north_color = phase.get('north', phase.get('vert', 'red'))
        south_color = phase.get('south', phase.get('vert', 'red'))

        self.lights['h_left'].set_color(west_color)
        self.lights['h_right'].set_color(east_color)
        self.lights['v_top'].set_color(north_color)
        self.lights['v_bottom'].set_color(south_color)

    def get_color(self, direction):
        """
        Получает цвет светофора для конкретного направления.
        direction: 'west', 'east', 'north', 'south', 'horizontal', 'vertical'
        """
        phase = self.phases[self.current_phase]

        # Обратная совместимость со старым API
        if direction == 'horizontal':
            # Возвращаем цвет западного светофора (или первый горизонтальный)
            return phase.get('west', phase.get('horiz', 'red'))
        elif direction == 'vertical':
            return phase.get('north', phase.get('vert', 'red'))

        # Новый API - конкретное направление
        return phase.get(direction, phase.get('horiz' if direction in ['west', 'east'] else 'vert', 'red'))

    def is_all_red(self):
        phase = self.phases[self.current_phase]
        west = phase.get('west', phase.get('horiz', 'red'))
        east = phase.get('east', phase.get('horiz', 'red'))
        north = phase.get('north', phase.get('vert', 'red'))
        south = phase.get('south', phase.get('vert', 'red'))
        return west == 'red' and east == 'red' and north == 'red' and south == 'red'

    def get_ped_color(self, cross_road):
        return 'green' if self.is_all_red() else 'red'

    def update(self, dt, waiting_h, waiting_v, h_penalty, v_penalty, visible_cars_h=0, visible_cars_v=0):
        self.timer += dt
        # Эти переменные обновляются для отображения в UI
        self.h_penalty = h_penalty
        self.v_penalty = v_penalty
        self.visible_cars_h = visible_cars_h
        self.visible_cars_v = visible_cars_v

        # Обновляем взвешенные штрафы с использованием фактора затухания.
        self.weighted_h_penalty = self.weighted_h_penalty * self.dynamic_logic_factor + self.h_penalty
        self.weighted_v_penalty = self.weighted_v_penalty * self.dynamic_logic_factor + self.v_penalty

        # Решение дифференциального уравнения для динамического режима
        if self.mode == 'dynamic':
            self.solve_differential_equation(dt, waiting_h, waiting_v, visible_cars_h, visible_cars_v)


        should_switch = False
        if self.mode == 'dynamic':
            if self.evaluate_dynamic_switch():
                should_switch = True
        else:  # static mode
            if self.timer >= self.phases[self.current_phase]['duration']:
                should_switch = True

        if should_switch:
            self.timer = 0
            self.current_phase = (self.current_phase + 1) % len(self.phases)

            # При переключении на зеленый, сбрасываем "давление" этого направления
            new_phase_info = self.phases[self.current_phase]
            west = new_phase_info.get('west', new_phase_info.get('horiz', 'red'))
            east = new_phase_info.get('east', new_phase_info.get('horiz', 'red'))
            north = new_phase_info.get('north', new_phase_info.get('vert', 'red'))
            south = new_phase_info.get('south', new_phase_info.get('vert', 'red'))

            if west == 'green' or east == 'green':
                self.weighted_h_penalty = 0
                self.pressure_h = 0
            if north == 'green' or south == 'green':
                self.weighted_v_penalty = 0
                self.pressure_v = 0


        self.update_lights()

    def solve_differential_equation(self, dt, waiting_h, waiting_v, visible_h, visible_v):
        """
        Решает дифференциальное уравнение для определения давления трафика.

        Модель:
        dP_h/dt = k_growth * (waiting_h + visible_h * 0.3) - k_decay * P_h * (is_green_h ? 1 : 0)
        dP_v/dt = k_growth * (waiting_v + visible_v * 0.3) - k_decay * P_v * (is_green_v ? 1 : 0)

        где:
        - P_h, P_v - давление (pressure) для горизонтального и вертикального направлений
        - k_growth - коэффициент роста давления
        - k_decay - коэффициент спада давления при открытом светофоре
        - waiting_* - количество ожидающих машин
        - visible_* - количество видимых машин (с меньшим весом)
        """
        current_phase_info = self.phases[self.current_phase]
        is_h_green = current_phase_info['horiz'] == 'green'
        is_v_green = current_phase_info['vert'] == 'green'

        # Вклад видимых машин (с коэффициентом 0.3, так как они еще далеко)
        h_traffic_load = waiting_h + visible_h * 0.3
        v_traffic_load = waiting_v + visible_v * 0.3

        # Дифференциальное уравнение методом Эйлера
        # dP/dt = рост от трафика - спад при зеленом свете
        dP_h = self.pressure_growth_rate * h_traffic_load * dt
        dP_v = self.pressure_growth_rate * v_traffic_load * dt

        # Спад давления, когда светофор зеленый (машины проезжают)
        if is_h_green and self.pressure_h > 0:
            dP_h -= self.pressure_decay_rate * self.pressure_h * dt
        if is_v_green and self.pressure_v > 0:
            dP_v -= self.pressure_decay_rate * self.pressure_v * dt

        # Обновляем давление
        self.pressure_h = max(0, self.pressure_h + dP_h)
        self.pressure_v = max(0, self.pressure_v + dP_v)

        # Дополнительное увеличение давления от времени ожидания (квадратичная зависимость)
        self.pressure_h += self.h_penalty * 0.01 * dt
        self.pressure_v += self.v_penalty * 0.01 * dt

    def evaluate_dynamic_switch(self):
        """
        Оценивает необходимость переключения фазы в динамическом режиме.
        Использует результаты дифференциального уравнения для принятия решения.
        """
        current_phase_info = self.phases[self.current_phase]

        # Проверяем наличие зеленых светофоров (новый и старый формат)
        west = current_phase_info.get('west', current_phase_info.get('horiz', 'red'))
        east = current_phase_info.get('east', current_phase_info.get('horiz', 'red'))
        north = current_phase_info.get('north', current_phase_info.get('vert', 'red'))
        south = current_phase_info.get('south', current_phase_info.get('vert', 'red'))

        is_h_green = west == 'green' or east == 'green'
        is_v_green = north == 'green' or south == 'green'

        # Для желтых и чисто красных фаз используем их фиксированную длительность
        if not (is_h_green or is_v_green):
            return self.timer >= current_phase_info['duration']

        # Соблюдение минимального и максимального времени зеленой фазы
        if self.timer < self.min_phase_time:
            return False
        if self.timer > self.max_phase_time:
            return True

        # Комбинированная логика: используем и давление, и взвешенные штрафы
        # Давление из дифференциального уравнения (60%) + взвешенные штрафы (40%)
        if is_h_green:
            # Переключаемся, если давление вертикального направления значительно выше
            pressure_diff = self.pressure_v - self.pressure_h
            penalty_diff = self.weighted_v_penalty - self.weighted_h_penalty

            # Комбинированный критерий переключения
            combined_metric = pressure_diff * 0.6 + penalty_diff * 0.4

            return combined_metric > self.switch_threshold

        if is_v_green:
            # Переключаемся, если давление горизонтального направления значительно выше
            pressure_diff = self.pressure_h - self.pressure_v
            penalty_diff = self.weighted_h_penalty - self.weighted_v_penalty

            # Комбинированный критерий переключения
            combined_metric = pressure_diff * 0.6 + penalty_diff * 0.4

            return combined_metric > self.switch_threshold

        return False

    def set_mode(self, mode):
        """Устанавливает режим работы светофора"""
        if mode in ['static', 'dynamic']:
            self.mode = mode

    def reorder_phases(self, new_order):
        self.phases = [self.phases[i] for i in new_order]

    def add_phase(self, duration=10, west='red', east='red', north='red', south='red'):
        self.phases.append({
            'duration': duration, 
            'west': west, 
            'east': east, 
            'north': north, 
            'south': south
        })
        return True

    def remove_phase(self, index):
        if len(self.phases) > 1 and 0 <= index < len(self.phases):
            del self.phases[index]
            if self.current_phase >= len(self.phases):
                self.current_phase = 0
                self.timer = 0

    def change_phase_duration(self, index, delta):
        new_duration = self.phases[index]['duration'] + delta
        self.phases[index]['duration'] = max(1, new_duration)

    def update_phase_color(self, index, direction, color):
        """
        Обновляет цвет светофора для конкретного направления.
        direction: 'west', 'east', 'north', 'south'
        """
        # Конвертируем старый формат в новый при необходимости
        if 'horiz' in self.phases[index] or 'vert' in self.phases[index]:
            self._convert_phase_to_new_format(index)

        self.phases[index][direction] = color

    def _convert_phase_to_new_format(self, index):
        """Конвертирует старый формат фазы (horiz/vert) в новый (west/east/north/south)"""
        phase = self.phases[index]
        if 'horiz' in phase or 'vert' in phase:
            horiz_color = phase.get('horiz', 'red')
            vert_color = phase.get('vert', 'red')
            self.phases[index] = {
                'duration': phase['duration'],
                'west': horiz_color,
                'east': horiz_color,
                'north': vert_color,
                'south': vert_color
            }

    def move_phase(self, index, move_by):
        new_index = index + move_by
        if not (0 <= index < len(self.phases) and 0 <= new_index < len(self.phases)):
            return
        self.phases.insert(new_index, self.phases.pop(index))

    # ---- Импорт/Экспорт конфигурации ----
    def export_config_dict(self):
        return {
            'mode': self.mode,
            'phases': self.phases,
            'min_phase_time': self.min_phase_time,
            'max_phase_time': self.max_phase_time,
            'dynamic_logic_factor': self.dynamic_logic_factor,
            'traffic_density': self.traffic_density,
            'pressure_growth_rate': self.pressure_growth_rate,
            'pressure_decay_rate': self.pressure_decay_rate,
            'switch_threshold': self.switch_threshold,
        }

    def import_config_dict(self, data: dict):
        # Безопасные присваивания с валидацией
        mode = data.get('mode', self.mode)
        if mode in ['static', 'dynamic']:
            self.mode = mode

        phases = data.get('phases')
        if isinstance(phases, list) and len(phases) > 0:
            cleaned = []
            for ph in phases:
                try:
                    d = int(max(1, ph.get('duration', 10)))
                    h = ph.get('horiz', 'red')
                    v = ph.get('vert', 'red')
                    # недопустимо два зелёных
                    if h == 'green' and v == 'green':
                        v = 'red'
                    cleaned.append({'duration': d, 'horiz': h, 'vert': v})
                except Exception:
                    continue
            if cleaned:
                self.phases = cleaned
                self.current_phase = min(self.current_phase, len(self.phases) - 1)
                self.timer = 0

        mpt = data.get('min_phase_time')
        if isinstance(mpt, (int, float)) and mpt > 0:
            self.min_phase_time = float(mpt)

        mxpt = data.get('max_phase_time')
        if isinstance(mxpt, (int, float)) and mxpt >= self.min_phase_time:
            self.max_phase_time = float(mxpt)

        dlf = data.get('dynamic_logic_factor')
        if isinstance(dlf, (int, float)) and 0 < dlf <= 1:
            self.dynamic_logic_factor = float(dlf)

        rates = data.get('traffic_density')
        if isinstance(rates, dict):
            for d in DIR_INS:
                if d in rates and isinstance(rates[d], (int, float)) and rates[d] >= 0:
                    self.traffic_density[d] = float(rates[d])

        # Импорт параметров дифференциального уравнения
        pgr = data.get('pressure_growth_rate')
        if isinstance(pgr, (int, float)) and pgr > 0:
            self.pressure_growth_rate = float(pgr)

        pdr = data.get('pressure_decay_rate')
        if isinstance(pdr, (int, float)) and pdr > 0:
            self.pressure_decay_rate = float(pdr)

        st = data.get('switch_threshold')
        if isinstance(st, (int, float)) and st > 0:
            self.switch_threshold = float(st)

        self.update_lights()