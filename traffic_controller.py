# traffic_controller.py
import time
from pygame.locals import SRCALPHA
from constants import *
import math
class TrafficLight:
    def __init__(self, position, orientation):
        self.position = position
        self.orientation = orientation
        self.color = 'red'
        self.alpha = 255

    def set_color(self, color):
        if self.color != color:
            self.color = color

    def draw(self, screen, center_x, center_y):
        pos = (center_x + self.position[0], center_y + self.position[1])
        col = {'red': RED, 'yellow': YELLOW, 'green': GREEN}[self.color]
        pygame.draw.circle(screen, col, pos, 10)
        if self.color == 'yellow':
            glow = pygame.Surface((30, 30), SRCALPHA)
            pygame.draw.circle(glow, (*col, 100 + 50 * math.sin(time.time() * 5)), (15, 15), 15)
            screen.blit(glow, (pos[0] - 15, pos[1] - 15))

class TrafficController:
    def __init__(self):
        self.state = 'horizontal_green'
        self.timer = 0
        self.green_time = LIGHT_GREEN
        self.yellow_time = LIGHT_YELLOW
        self.red_time = LIGHT_RED
        self.mode = 'static'
        self.lights = {
            'h_left': TrafficLight((-50, -50), 'horizontal'),
            'h_right': TrafficLight((50, 50), 'horizontal'),
            'v_top': TrafficLight((-50, 50), 'vertical'),
            'v_bottom': TrafficLight((50, -50), 'vertical')
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