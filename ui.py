# ui.py
import pygame
from pygame.locals import *
from constants import *


class Slider:
    def __init__(self, rect, min_val, max_val, cur_val, label, callback):
        self.rect = pygame.Rect(rect)
        self.min_val = min_val
        self.max_val = max_val
        self.cur_val = cur_val
        self.label = label
        self.callback = callback
        self.is_dragging = False

        # Вычисляем позицию ползунка
        self.slider_width = 10
        self.slider_pos = self.value_to_pos(cur_val)

    def value_to_pos(self, value):
        """Преобразует значение в позицию на слайдере"""
        ratio = (value - self.min_val) / (self.max_val - self.min_val)
        return self.rect.x + ratio * self.rect.width

    def pos_to_value(self, pos):
        """Преобразует позицию в значение"""
        relative_pos = max(0, min(pos - self.rect.x, self.rect.width))
        ratio = relative_pos / self.rect.width
        value = self.min_val + ratio * (self.max_val - self.min_val)
        return round(value, 1)  # Округляем для удобства

    def draw(self, screen, font):
        # Отрисовка линии слайдера
        line_rect = pygame.Rect(self.rect.x, self.rect.y + self.rect.height // 2 - 1,
                                self.rect.width, 2)
        pygame.draw.rect(screen, (200, 200, 200), line_rect)

        # Отрисовка ползунка
        slider_rect = pygame.Rect(self.slider_pos - self.slider_width // 2,
                                  self.rect.y,
                                  self.slider_width,
                                  self.rect.height)
        pygame.draw.rect(screen, (100, 150, 255), slider_rect)
        pygame.draw.rect(screen, (255, 255, 255), slider_rect, 1)

        # Отрисовка текста
        label_text = f"{self.label}: {self.cur_val}"
        text_surface = font.render(label_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(midleft=(self.rect.x, self.rect.y - 10))
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Проверяем клик по ползунку
            slider_rect = pygame.Rect(self.slider_pos - self.slider_width // 2,
                                      self.rect.y,
                                      self.slider_width,
                                      self.rect.height)
            if slider_rect.collidepoint(event.pos):
                self.is_dragging = True
                return True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_dragging:
                self.is_dragging = False
                return True

        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging:
                # Обновляем позицию ползунка и значение
                self.slider_pos = max(self.rect.x, min(event.pos[0], self.rect.x + self.rect.width))
                new_value = self.pos_to_value(self.slider_pos)
                if new_value != self.cur_val:
                    self.cur_val = new_value
                    self.callback(new_value)
                return True

        return False

class Button:
    def __init__(self, rect, text, callback):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.color = (100, 100, 100)
        self.hover_color = (150, 150, 150)
        self.text_color = (255, 255, 255)
        self.is_hovered = False

    def draw(self, screen, font):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)

        text_surface = font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.callback()
                return True
        return False

class PhaseItem:
    def __init__(self, rect, phase, index, callback):
        self.rect = pygame.Rect(rect)
        self.phase = phase
        self.index = index
        self.callback = callback
        self.hovered = False
        self.dragging = False
        self.offset = (0, 0)

    def draw(self, screen, font):
        color = UI_HOVER if self.hovered else UI_ACTIVE
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, UI_BORDER, self.rect, 2, border_radius=5)
        text = f"{self.phase['duration']}s H: {self.phase['horiz']} V: {self.phase['vert']}"
        text_surf = font.render(text, True, UI_TEXT)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
            if self.dragging:
                self.rect.move_ip(event.rel)
        if event.type == MOUSEBUTTONDOWN:
            if self.hovered:
                self.dragging = True
                self.offset = (event.pos[0] - self.rect.x, event.pos[1] - self.rect.y)
        if event.type == MOUSEBUTTONUP:
            if self.dragging:
                self.dragging = False
                if self.callback:
                    self.callback(self)

class UIManager:
    def __init__(self, sim):
        self.sim = sim
        self.elements = []
        self.phase_items = []
        self.font = pygame.font.SysFont('Arial', 20, bold=True)
        y = 50
        self.add_button((SCREEN_WIDTH - UI_PANEL_WIDTH + 50, y, 200, 40), 'Pause/Resume', self.toggle_pause)
        y += 60
        self.add_button((SCREEN_WIDTH - UI_PANEL_WIDTH + 50, y, 200, 40), 'Switch Mode', self.switch_mode)
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
        # Phase management
        self.phase_y_start = y
        self.update_phase_items()
        # Add phase button
        y += len(sim.controller.phases) * 50 + 20
        self.add_button((SCREEN_WIDTH - UI_PANEL_WIDTH + 50, y, 200, 40), 'Add Phase', self.add_phase)

    def update_phase_items(self):
        self.phase_items = []
        y = self.phase_y_start
        for i, phase in enumerate(self.sim.controller.phases):
            rect = (SCREEN_WIDTH - UI_PANEL_WIDTH + 50, y, 200, 40)
            item = PhaseItem(rect, phase, i, self.on_drop_phase)
            self.phase_items.append(item)
            y += 50

    def on_drop_phase(self, dropped_item):
        # Reorder phases based on y positions
        self.phase_items.sort(key=lambda item: item.rect.y)
        new_order = [item.index for item in self.phase_items]
        self.sim.controller.reorder_phases(new_order)
        self.update_phase_items()

    def add_phase(self):
        # Simple addition, perhaps with default
        added = self.sim.controller.add_phase(10, 'red', 'red')  # All red example
        if added:
            self.update_phase_items()

    def add_button(self, rect, text, callback):
        self.elements.append(Button(rect, text, callback))

    def add_slider(self, rect, min_val, max_val, cur_val, label, callback):
        self.elements.append(Slider(rect, min_val, max_val, cur_val, label, callback))

    def handle_event(self, event):
        for el in self.elements:
            el.handle_event(event)
        for item in self.phase_items:
            item.handle_event(event)

    def draw(self, screen):
        pygame.draw.rect(screen, UI_BG, (SCREEN_WIDTH - UI_PANEL_WIDTH, 0, UI_PANEL_WIDTH, SCREEN_HEIGHT))
        title = self.font.render('Control Panel', True, UI_TEXT)
        screen.blit(title, (SCREEN_WIDTH - UI_PANEL_WIDTH + 50, 10))
        for el in self.elements:
            el.draw(screen, self.font)
        for item in self.phase_items:
            item.draw(screen, self.font)
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