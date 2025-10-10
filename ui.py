# ui.py
import pygame
from pygame.locals import *
from constants import *

class UIElement:
    def __init__(self, rect, text='', callback=None):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.hovered = False

class Button(UIElement):
    def draw(self, screen, font):
        color = UI_HOVER if self.hovered else UI_ACTIVE
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, UI_BORDER, self.rect, 3, border_radius=10)
        text_surf = font.render(self.text, True, UI_TEXT)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        if event.type == MOUSEBUTTONDOWN and self.hovered:
            if self.callback:
                self.callback()

class Slider(UIElement):
    def __init__(self, rect, min_val, max_val, current_val, label, callback):
        super().__init__(rect, label)
        self.min_val = min_val
        self.max_val = max_val
        self.value = current_val
        self.callback = callback
        self.dragging = False

    def draw(self, screen, font):
        pygame.draw.rect(screen, UI_ACTIVE, self.rect, border_radius=10)
        pygame.draw.rect(screen, UI_BORDER, self.rect, 2, border_radius=10)
        handle_pos = self.rect.x + (self.value - self.min_val) / (self.max_val - self.min_val) * self.rect.width
        pygame.draw.circle(screen, UI_HOVER, (int(handle_pos), self.rect.centery), 12)
        text = f"{self.text}: {int(self.value) if self.text == 'Num Lanes' else self.value:.1f}"
        text_surf = font.render(text, True, UI_TEXT)
        screen.blit(text_surf, (self.rect.x + 10, self.rect.y - 25))

    def handle_event(self, event):
        if event.type == MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == MOUSEMOTION and self.dragging:
            x = max(self.rect.x, min(event.pos[0], self.rect.x + self.rect.width))
            self.value = self.min_val + (x - self.rect.x) / self.rect.width * (self.max_val - self.min_val)
            if self.callback:
                self.callback(self.value)

class UIManager:
    def __init__(self, sim):
        self.sim = sim
        self.elements = []
        self.font = pygame.font.SysFont('Arial', 20, bold=True)
        y = 50
        self.add_button((SCREEN_WIDTH - UI_PANEL_WIDTH + 50, y, 200, 40), 'Pause/Resume', self.toggle_pause)
        y += 60
        self.add_button((SCREEN_WIDTH - UI_PANEL_WIDTH + 50, y, 200, 40), 'Switch Mode', self.switch_mode)
        y += 60
        self.add_button((SCREEN_WIDTH - UI_PANEL_WIDTH + 50, y, 200, 40), 'Reset Sim', self.reset_sim)
        y += 60
        self.add_slider((SCREEN_WIDTH - UI_PANEL_WIDTH + 50, y, 200, 20), 1, 10, sim.interval_min, 'Min Interval', self.set_min_interval)
        y += 50
        self.add_slider((SCREEN_WIDTH - UI_PANEL_WIDTH + 50, y, 200, 20), 1, 20, sim.interval_max, 'Max Interval', self.set_max_interval)
        y += 50
        self.add_slider((SCREEN_WIDTH - UI_PANEL_WIDTH + 50, y, 200, 20), 5, 20, sim.speed_min, 'Min Speed (m/s)', self.set_min_speed)
        y += 50
        self.add_slider((SCREEN_WIDTH - UI_PANEL_WIDTH + 50, y, 200, 20), 20, 40, sim.speed_max, 'Max Speed (m/s)', self.set_max_speed)
        y += 50
        self.add_slider((SCREEN_WIDTH - UI_PANEL_WIDTH + 50, y, 200, 20), 10, 60, sim.green_time, 'Green Time', self.set_green_time)
        y += 50
        self.add_slider((SCREEN_WIDTH - UI_PANEL_WIDTH + 50, y, 200, 20), 1, 5, sim.yellow_time, 'Yellow Time', self.set_yellow_time)
        y += 50
        self.add_slider((SCREEN_WIDTH - UI_PANEL_WIDTH + 50, y, 200, 20), 10, 60, sim.red_time, 'Red Time (Static)', self.set_red_time)
        y += 50
        self.add_slider((SCREEN_WIDTH - UI_PANEL_WIDTH + 50, y, 200, 20), 2, 5, sim.num_lanes, 'Num Lanes', self.set_num_lanes)

    def add_button(self, rect, text, callback):
        self.elements.append(Button(rect, text, callback))

    def add_slider(self, rect, min_val, max_val, cur_val, label, callback):
        self.elements.append(Slider(rect, min_val, max_val, cur_val, label, callback))

    def handle_event(self, event):
        for el in self.elements:
            el.handle_event(event)

    def draw(self, screen):
        pygame.draw.rect(screen, UI_BG, (SCREEN_WIDTH - UI_PANEL_WIDTH, 0, UI_PANEL_WIDTH, SCREEN_HEIGHT))
        title = self.font.render('Control Panel', True, UI_TEXT)
        screen.blit(title, (SCREEN_WIDTH - UI_PANEL_WIDTH + 50, 10))
        for el in self.elements:
            el.draw(screen, self.font)
        mode_text = self.font.render(f'Mode: {self.sim.controller.mode.capitalize()}', True, UI_TEXT)
        screen.blit(mode_text, (SCREEN_WIDTH - UI_PANEL_WIDTH + 50, 800))
        if self.sim.completed_wait_times:
            avg_wait = sum(self.sim.completed_wait_times) / len(self.sim.completed_wait_times)
            wait_text = self.font.render(f'Avg Wait: {avg_wait:.2f}s | Cars: {len(self.sim.cars)}', True, UI_TEXT)
            screen.blit(wait_text, (SCREEN_WIDTH - UI_PANEL_WIDTH + 50, 830))

    def toggle_pause(self):
        self.sim.paused = not self.sim.paused

    def switch_mode(self):
        self.sim.controller.mode = 'dynamic' if self.sim.controller.mode == 'static' else 'static'

    def reset_sim(self):
        self.sim.cars = []
        self.sim.peds = []
        self.sim.completed_wait_times = []

    def set_min_interval(self, val):
        self.sim.interval_min = val
        if val > self.sim.interval_max:
            self.sim.interval_max = val

    def set_max_interval(self, val):
        self.sim.interval_max = val
        if val < self.sim.interval_min:
            self.sim.interval_min = val

    def set_min_speed(self, val):
        self.sim.speed_min = val
        if val > self.sim.speed_max:
            self.sim.speed_max = val

    def set_max_speed(self, val):
        self.sim.speed_max = val
        if val < self.sim.speed_min:
            self.sim.speed_min = val

    def set_green_time(self, val):
        self.sim.green_time = val

    def set_yellow_time(self, val):
        self.sim.yellow_time = val

    def set_red_time(self, val):
        self.sim.red_time = val

    def set_num_lanes(self, val):
        self.sim.num_lanes = int(val)
        self.sim.cars = []
        self.sim.peds = []