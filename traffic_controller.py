# traffic_controller.py
import time
import math
import pygame
from typing import Dict
from constants import *
from entities import Vec2  # просто для типов (pygame.Vector2)

class LightLens:
    def __init__(self, lens_color, offset):
        self.lens_color = lens_color
        self.offset = offset
        self.active = False

    def draw(self, screen, base_pos, current_time):
        pos = (int(base_pos[0] + self.offset[0]), int(base_pos[1] + self.offset[1]))
        fill_color = self.lens_color if self.active else GRAY
        pygame.draw.circle(screen, fill_color, pos, 8)
        pygame.draw.circle(screen, BLACK, pos, 8, 1)
        if self.active:
            glow = pygame.Surface((30, 30), pygame.SRCALPHA)
            if self.lens_color == YELLOW:
                glow_alpha = 80 + 40 * math.sin(current_time * 5)
            elif self.lens_color == RED:
                glow_alpha = 80 + 40 * math.sin(current_time * 2)
            else:
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
                LightLens(RED, (0, -20)),
                LightLens(YELLOW, (0, 0)),
                LightLens(GREEN, (0, 20))
            ]
        else:
            self.lenses = [
                LightLens(RED, (-20, 0)),
                LightLens(YELLOW, (0, 0)),
                LightLens(GREEN, (20, 0))
            ]

    def set_color(self, color: str):
        if self.current_color == color:
            return
        self.current_color = color
        col_map = {'red': RED, 'yellow': YELLOW, 'green': GREEN}
        target = col_map[color]
        for lens in self.lenses:
            lens.active = (lens.lens_color == target)

    def draw(self, screen, center_x: int, center_y: int):
        base_pos = (center_x + int(self.position[0]), center_y + int(self.position[1]))
        if self.orientation == 'vertical':
            housing_rect = pygame.Rect(base_pos[0] - 10, base_pos[1] - 30, 20, 60)
        else:
            housing_rect = pygame.Rect(base_pos[0] - 30, base_pos[1] - 10, 60, 20)
        pygame.draw.rect(screen, BLACK, housing_rect, border_radius=5)
        current_time = time.time()
        for lens in self.lenses:
            lens.draw(screen, base_pos, current_time)

class TrafficController:
    """Контроллер фаз светофоров — оптимизированный, с динамическим режимом."""
    def __init__(self):
        self.lights: Dict[str, TrafficLight] = {}
        self.reset_to_defaults()
        self.update_light_positions()
        self.update_lights()

    def reset_to_defaults(self):
        self.phases = [
            {'duration': 30.0, 'horiz': 'green', 'vert': 'red'},
            {'duration': 3.0, 'horiz': 'yellow', 'vert': 'red'},
            {'duration': 2.0, 'horiz': 'red', 'vert': 'red'},
            {'duration': 30.0, 'vert': 'green', 'horiz': 'red'},
            {'duration': 3.0, 'vert': 'yellow', 'horiz': 'red'},
            {'duration': 2.0, 'vert': 'red', 'horiz': 'red'}
        ]
        self.current_phase = 0
        self.timer = 0.0
        self.mode = 'static'  # or 'dynamic'

        # параметры dynamic
        self.min_phase_time = 5.0
        self.max_phase_time = 60.0
        self.dynamic_logic_factor = 0.99
        self.weighted_h_penalty = 0.0
        self.weighted_v_penalty = 0.0
        self.traffic_density = {d: 5.0 for d in DIR_INS}

        # для UI/совместимости
        self.h_penalty = 0.0
        self.v_penalty = 0.0

    def update_light_positions(self):
        from constants import screen_config
        road_half = (NUM_LANES * LANE_WIDTH) / 2
        light_dist = int(screen_config.sim_width * 0.15)
        self.lights = {
            'h_left': TrafficLight((-light_dist, -road_half - 10), 'horizontal'),
            'h_right': TrafficLight((light_dist, road_half + 10), 'horizontal'),
            'v_top': TrafficLight((road_half + 10, -light_dist), 'vertical'),
            'v_bottom': TrafficLight((-road_half - 10, light_dist), 'vertical')
        }

    def update_lights(self):
        phase = self.phases[self.current_phase]
        self.lights['h_left'].set_color(phase['horiz'])
        self.lights['h_right'].set_color(phase['horiz'])
        self.lights['v_top'].set_color(phase['vert'])
        self.lights['v_bottom'].set_color(phase['vert'])

    def get_color(self, road: str) -> str:
        phase = self.phases[self.current_phase]
        return phase['horiz'] if road == 'horizontal' else phase['vert']

    def is_all_red(self) -> bool:
        phase = self.phases[self.current_phase]
        return (phase['horiz'] == 'red') and (phase['vert'] == 'red')

    def update(self, dt: float, waiting_h: int, waiting_v: int, h_penalty: float, v_penalty: float):
        """Обновление таймера и возможный переход фазы."""
        self.timer += dt
        self.h_penalty = h_penalty
        self.v_penalty = v_penalty

        # обновление экспоненциально-взвешенных штрафов
        self.weighted_h_penalty = self.weighted_h_penalty * self.dynamic_logic_factor + self.h_penalty
        self.weighted_v_penalty = self.weighted_v_penalty * self.dynamic_logic_factor + self.v_penalty

        should_switch = False
        phase_info = self.phases[self.current_phase]

        if self.mode == 'dynamic':
            if self._evaluate_dynamic_switch(phase_info):
                should_switch = True
        else:
            if self.timer >= phase_info['duration']:
                should_switch = True

        if should_switch:
            self.timer = 0.0
            self.current_phase = (self.current_phase + 1) % len(self.phases)
            new_phase_info = self.phases[self.current_phase]
            if new_phase_info['horiz'] == 'green':
                self.weighted_h_penalty = 0.0
            if new_phase_info['vert'] == 'green':
                self.weighted_v_penalty = 0.0

        self.update_lights()

    def _evaluate_dynamic_switch(self, current_phase_info) -> bool:
        is_h_green = current_phase_info['horiz'] == 'green'
        is_v_green = current_phase_info['vert'] == 'green'
        if not (is_h_green or is_v_green):
            return self.timer >= current_phase_info['duration']
        if self.timer < self.min_phase_time:
            return False
        if self.timer > self.max_phase_time:
            return True
        if is_h_green:
            return self.weighted_v_penalty > self.weighted_h_penalty
        if is_v_green:
            return self.weighted_h_penalty > self.weighted_v_penalty
        return False

    # ---- утилиты для UI / конфигурации ----
    def export_config_dict(self):
        return {
            'mode': self.mode,
            'phases': self.phases,
            'min_phase_time': self.min_phase_time,
            'max_phase_time': self.max_phase_time,
            'dynamic_logic_factor': self.dynamic_logic_factor,
            'traffic_density': self.traffic_density,
        }

    def import_config_dict(self, data: dict):
        mode = data.get('mode', self.mode)
        if mode in ('static', 'dynamic'):
            self.mode = mode

        phases = data.get('phases')
        if isinstance(phases, list) and len(phases) > 0:
            cleaned = []
            for ph in phases:
                try:
                    d = int(max(1, ph.get('duration', 10)))
                    h = ph.get('horiz', 'red')
                    v = ph.get('vert', 'red')
                    if h == 'green' and v == 'green':
                        v = 'red'
                    cleaned.append({'duration': d, 'horiz': h, 'vert': v})
                except Exception:
                    continue
            if cleaned:
                self.phases = cleaned
                self.current_phase = min(self.current_phase, len(self.phases) - 1)
                self.timer = 0.0

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

        self.update_lights()
