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

    def draw(self, screen, base_pos, active_color):
        pos = (base_pos[0] + self.offset[0], base_pos[1] + self.offset[1])
        fill_color = self.lens_color if self.active else GRAY
        pygame.draw.circle(screen, fill_color, pos, 8)
        pygame.draw.circle(screen, BLACK, pos, 8, 1)  # Border

class TrafficLight:
    def __init__(self, position, orientation):
        self.position = position
        self.orientation = orientation
        self.current_color = 'red'
        self.lenses = [
            LightLens(RED, (0, -20)),     # Top: red
            LightLens(YELLOW, (0, 0)),    # Middle: yellow
            LightLens(GREEN, (0, 20))     # Bottom: green
        ]

    def set_color(self, color):
        if self.current_color != color:
            self.current_color = color
            for lens in self.lenses:
                lens.active = False
            if color == 'red':
                self.lenses[0].active = True
            elif color == 'yellow':
                self.lenses[1].active = True
            elif color == 'green':
                self.lenses[2].active = True

    def draw(self, screen, center_x, center_y):
        base_pos = (center_x + self.position[0], center_y + self.position[1])
        # Draw housing
        housing_rect = pygame.Rect(base_pos[0] - 10, base_pos[1] - 30, 20, 60)
        pygame.draw.rect(screen, BLACK, housing_rect, border_radius=5)
        # Draw lenses
        for lens in self.lenses:
            lens.draw(screen, base_pos, self.current_color)
        # Glow for yellow
        if self.current_color == 'yellow':
            glow_pos = (base_pos[0], base_pos[1])
            glow = pygame.Surface((40, 40), SRCALPHA)
            pygame.draw.circle(glow, (*YELLOW, 80 + 40 * math.sin(time.time() * 5)), (20, 20), 20)
            screen.blit(glow, (glow_pos[0] - 20, glow_pos[1] - 20))

class TrafficController:
    def __init__(self):
        self.state = 'horizontal_green'
        self.timer = 0
        self.green_time = LIGHT_GREEN
        self.yellow_time = LIGHT_YELLOW
        self.red_time = LIGHT_RED
        self.mode = 'static'
        self.lights = {
            'h_left': TrafficLight((-60, -60), 'horizontal'),  # Adjusted positions for size
            'h_right': TrafficLight((60, 60), 'horizontal'),
            'v_top': TrafficLight((-60, 60), 'vertical'),
            'v_bottom': TrafficLight((60, -60), 'vertical')
        }
        self.update_lights()

    def update_lights(self):
        h_color = self.get_color('horizontal')
        v_color = self.get_color('vertical')
        self.lights['h_left'].set_color(h_color)
        self.lights['h_right'].set_color(h_color)
        self.lights['v_top'].set_color(v_color)
        self.lights['v_bottom'].set_color(v_color)

    def get_color(self, road):
        if road == 'horizontal':
            if self.state == 'horizontal_green':
                return 'green'
            elif self.state == 'horizontal_yellow':
                return 'yellow'
            else:
                return 'red'
        else:
            if self.state == 'vertical_green':
                return 'green'
            elif self.state == 'vertical_yellow':
                return 'yellow'
            else:
                return 'red'

    def get_ped_color(self, cross_road):
        return 'green' if self.get_color(cross_road) == 'red' else 'red'

    def update(self, dt, waiting_h, waiting_v):
        self.timer += dt
        if self.mode == 'static':
            if self.state == 'horizontal_green' and self.timer > self.green_time:
                self.state = 'horizontal_yellow'
                self.timer = 0
            elif self.state == 'horizontal_yellow' and self.timer > self.yellow_time:
                self.state = 'vertical_green'
                self.timer = 0
            elif self.state == 'vertical_green' and self.timer > self.green_time:
                self.state = 'vertical_yellow'
                self.timer = 0
            elif self.state == 'vertical_yellow' and self.timer > self.yellow_time:
                self.state = 'horizontal_green'
                self.timer = 0
        else:
            if 'green' in self.state and self.timer > self.green_time:
                self.state = self.state.replace('green', 'yellow')
                self.timer = 0
            elif 'yellow' in self.state and self.timer > self.yellow_time:
                sum_sq_h = sum(w ** 2 for w in waiting_h)
                sum_sq_v = sum(w ** 2 for w in waiting_v)
                self.state = 'horizontal_green' if sum_sq_h > sum_sq_v else 'vertical_green'
                self.timer = 0
                total = sum_sq_h + sum_sq_v + 1
                self.green_time = 10 + 40 * max(sum_sq_h, sum_sq_v) / total

        self.update_lights()