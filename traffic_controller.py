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
            {'duration': 30, 'horiz': 'green', 'vert': 'red'},
            {'duration': 3, 'horiz': 'yellow', 'vert': 'red'},
            {'duration': 2, 'horiz': 'red', 'vert': 'red'},
            {'duration': 30, 'vert': 'green', 'horiz': 'red'},
            {'duration': 3, 'vert': 'yellow', 'horiz': 'red'},
            {'duration': 2, 'vert': 'red', 'horiz': 'red'}
        ]
        self.current_phase = 0
        self.timer = 0
        self.mode = 'static'

        # Параметры динамического режима
        self.min_phase_time = 5.0
        self.max_phase_time = 60.0
        self.waiting_cars_h = 0
        self.waiting_cars_v = 0
        self.h_penalty = 0.0
        self.v_penalty = 0.0
        # Интегральные (накопленные) штрафы
        self.integrated_h_penalty = 0.0
        self.integrated_v_penalty = 0.0


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
        h_color = phase['horiz']
        v_color = phase['vert']
        self.lights['h_left'].set_color(h_color)
        self.lights['h_right'].set_color(h_color)
        self.lights['v_top'].set_color(v_color)
        self.lights['v_bottom'].set_color(v_color)

    def get_color(self, road):
        phase = self.phases[self.current_phase]
        return phase['horiz'] if road == 'horizontal' else phase['vert']

    def is_all_red(self):
        phase = self.phases[self.current_phase]
        return phase['horiz'] == 'red' and phase['vert'] == 'red'

    def get_ped_color(self, cross_road):
        return 'green' if self.is_all_red() else 'red'

    def update(self, dt, waiting_h, waiting_v, h_penalty, v_penalty):
        self.timer += dt
        self.waiting_cars_h = waiting_h
        self.waiting_cars_v = waiting_v
        self.h_penalty = h_penalty
        self.v_penalty = v_penalty

        # Накапливаем "недовольство" (интегрированный штраф) для каждого направления
        self.integrated_h_penalty += self.h_penalty * dt
        self.integrated_v_penalty += self.v_penalty * dt

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

            # "Списываем" накопленный штраф для направления, получившего зеленый свет
            new_phase_info = self.phases[self.current_phase]
            if new_phase_info['horiz'] == 'green' and new_phase_info['vert'] == 'red':
                self.integrated_h_penalty = 0.0
            elif new_phase_info['vert'] == 'green' and new_phase_info['horiz'] == 'red':
                self.integrated_v_penalty = 0.0

        self.update_lights()

    def evaluate_dynamic_switch(self):
        """
        Оценивает необходимость переключения фазы в динамическом режиме.
        Цель - сбалансировать "интегральный штраф" (накопленное недовольство) ожидающих направлений.
        """
        current_phase_info = self.phases[self.current_phase]

        is_h_green = current_phase_info['horiz'] == 'green' and current_phase_info['vert'] == 'red'
        is_v_green = current_phase_info['vert'] == 'green' and current_phase_info['horiz'] == 'red'

        if is_h_green or is_v_green:
            # Принудительное соблюдение минимального и максимального времени зеленой фазы
            if self.timer < self.min_phase_time:
                return False
            if self.timer > self.max_phase_time:
                return True

            # Основная логика: переключаемся, если накопленный штраф другого направления стал больше
            if is_h_green:
                return self.integrated_v_penalty > self.integrated_h_penalty
            if is_v_green:
                return self.integrated_h_penalty > self.integrated_v_penalty
        else:
            # Для желтой и красной фаз используем их фиксированную длительность
            return self.timer >= current_phase_info['duration']

        return False

    def set_mode(self, mode):
        """Устанавливает режим работы светофора"""
        if mode in ['static', 'dynamic']:
            self.mode = mode

    def reorder_phases(self, new_order):
        self.phases = [self.phases[i] for i in new_order]

    def add_phase(self, duration=10, horiz='red', vert='red'):
        if horiz == 'green' and vert == 'green':
            return False  # Invalid
        self.phases.append({'duration': duration, 'horiz': horiz, 'vert': vert})
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
        other_direction = 'vert' if direction == 'horiz' else 'horiz'
        if color == 'green' and self.phases[index][other_direction] == 'green':
            self.phases[index][other_direction] = 'red'
        self.phases[index][direction] = color

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
            'switch_threshold': self.switch_threshold
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
        thr = data.get('switch_threshold')
        if isinstance(thr, (int, float)) and thr >= 0:
            self.switch_threshold = float(thr)

        self.update_lights()