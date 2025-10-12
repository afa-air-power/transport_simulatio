import pygame
from pygame.locals import *

from constants import *

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
        pygame.draw.rect(screen, color, self.rect, border_radius=6)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2, border_radius=6)

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


class Dropdown:
    def __init__(self, rect, options, selected_index, label, callback):
        self.rect = pygame.Rect(rect)
        self.options = options
        self.selected_index = selected_index
        self.label = label
        self.callback = callback
        self.is_open = False
        self.color = (80, 80, 80)
        self.hover_color = (120, 120, 120)

    def draw(self, screen, font):
        # Рисуем основную кнопку
        color = self.hover_color if self.is_open else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=6)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2, border_radius=6)

        # Текст выбранной опции
        text = f"{self.label}: {self.options[self.selected_index]}"
        text_surface = font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

        # Рисуем выпадающий список если открыт
        if self.is_open:
            for i, option in enumerate(self.options):
                option_rect = pygame.Rect(
                    self.rect.x,
                    self.rect.y + self.rect.height * (i + 1),
                    self.rect.width,
                    self.rect.height
                )
                option_color = (100, 100, 150) if i == self.selected_index else self.color
                pygame.draw.rect(screen, option_color, option_rect, border_radius=4)
                pygame.draw.rect(screen, (255, 255, 255), option_rect, 1, border_radius=4)

                option_text = font.render(option, True, (255, 255, 255))
                option_text_rect = option_text.get_rect(center=option_rect.center)
                screen.blit(option_text, option_text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Проверяем клик по основной кнопке
            if self.rect.collidepoint(event.pos):
                self.is_open = not self.is_open
                return True

            # Проверяем клик по опциям если открыто
            if self.is_open:
                for i in range(len(self.options)):
                    option_rect = pygame.Rect(
                        self.rect.x,
                        self.rect.y + self.rect.height * (i + 1),
                        self.rect.width,
                        self.rect.height
                    )
                    if option_rect.collidepoint(event.pos):
                        self.selected_index = i
                        self.is_open = False
                        self.callback(self.options[i])
                        return True

        # Закрываем при клике вне dropdown
        if event.type == pygame.MOUSEBUTTONDOWN and self.is_open:
            if not self.rect.collidepoint(event.pos):
                dropdown_area = pygame.Rect(
                    self.rect.x,
                    self.rect.y,
                    self.rect.width,
                    self.rect.height * (len(self.options) + 1)
                )
                if not dropdown_area.collidepoint(event.pos):
                    self.is_open = False
                    return True

        return False


class UIManager:
    def __init__(self, sim):
        self.sim = sim
        self.elements = []
        self.font = pygame.font.Font(None, 20)
        self.input_active = False
        self.input_text = ""
        self.panel_rect = pygame.Rect(SCREEN_WIDTH - UI_PANEL_WIDTH, 0, UI_PANEL_WIDTH, SCREEN_HEIGHT)
        self.last_known_phase = -1
        self.info_texts = []
        self.input_rect = pygame.Rect(0, 0, 0, 0) # Инициализация
        self.rebuild_ui_elements()

    def rebuild_ui_elements(self):
        self.elements.clear()
        self.info_texts.clear()
        y = 20

        self.add_button((SCREEN_WIDTH - UI_PANEL_WIDTH + 50, y, 200, 40), 'Pause/Resume', self.toggle_pause)
        y += 50

        self.add_text((SCREEN_WIDTH - UI_PANEL_WIDTH + 20, y), "Ручное управление (горизонт.):")
        y += 25
        self.add_dropdown((SCREEN_WIDTH - UI_PANEL_WIDTH + 20, y, 260, 30),
                          ["Красный", "Желтый", "Зеленый"], 0, "Цвет", self.set_traffic_color)
        y += 40

        # Информация о симуляции
        info_y = y
        self.info_texts.append(self.add_text((SCREEN_WIDTH - UI_PANEL_WIDTH + 20, info_y), f"Текущая фаза: {self.sim.current_phase}"))
        info_y += 25
        self.info_texts.append(self.add_text((SCREEN_WIDTH - UI_PANEL_WIDTH + 20, info_y), f"Время: {self.sim.phase_time:.1f}"))
        info_y += 25
        self.info_texts.append(self.add_text((SCREEN_WIDTH - UI_PANEL_WIDTH + 20, info_y), f"Людей: {len(self.sim.pedestrians)}"))
        y = info_y + 40

        # --- Редактор Фаз ---
        self.add_text((SCREEN_WIDTH - UI_PANEL_WIDTH + 20, y), "Редактор Фаз:")
        y += 25

        colors_eng = ["green", "yellow", "red"]

        for i, phase in enumerate(self.sim.controller.phases):
            phase_y = y + i * 50

            if i == self.sim.controller.current_phase:
                highlight_rect = pygame.Rect(SCREEN_WIDTH - UI_PANEL_WIDTH + 10, phase_y - 5, UI_PANEL_WIDTH - 20, 48)
                self.elements.append({'type': 'rect', 'rect': highlight_rect, 'color': (90, 90, 70)})

            self.add_text((SCREEN_WIDTH - UI_PANEL_WIDTH + 20, phase_y), f"Длительность: {phase['duration']}s")

            self.add_button((SCREEN_WIDTH - UI_PANEL_WIDTH + 150, phase_y - 2, 25, 20), "+5", lambda index=i: self.change_phase_duration(index, 5))
            self.add_button((SCREEN_WIDTH - UI_PANEL_WIDTH + 180, phase_y - 2, 25, 20), "-5", lambda index=i: self.change_phase_duration(index, -5))

            h_color_idx = colors_eng.index(phase['horiz'])
            self.add_dropdown((SCREEN_WIDTH - UI_PANEL_WIDTH + 20, phase_y + 18, 85, 25), colors_eng, h_color_idx, "Horiz", lambda color, index=i: self.update_phase_color(index, 'horiz', color))

            v_color_idx = colors_eng.index(phase['vert'])
            self.add_dropdown((SCREEN_WIDTH - UI_PANEL_WIDTH + 110, phase_y + 18, 85, 25), colors_eng, v_color_idx, "Vert", lambda color, index=i: self.update_phase_color(index, 'vert', color))

            self.add_button((SCREEN_WIDTH - UI_PANEL_WIDTH + 210, phase_y - 2, 30, 22), "↑", lambda index=i: self.move_phase(index, -1))
            self.add_button((SCREEN_WIDTH - UI_PANEL_WIDTH + 245, phase_y - 2, 30, 22), "↓", lambda index=i: self.move_phase(index, 1))
            self.add_button((SCREEN_WIDTH - UI_PANEL_WIDTH + 210, phase_y + 21, 65, 22), "X", lambda index=i: self.delete_phase(index))

        y += len(self.sim.controller.phases) * 50 + 10
        self.add_button((SCREEN_WIDTH - UI_PANEL_WIDTH + 50, y, 200, 30), "Добавить фазу", self.add_new_phase)

    def add_button(self, rect, text, callback):
        button = Button(rect, text, callback)
        self.elements.append(button)
        return button

    def add_dropdown(self, rect, options, selected_index, label, callback):
        dropdown = Dropdown(rect, options, selected_index, label, callback)
        self.elements.append(dropdown)
        return dropdown

    def add_text(self, pos, text):
        text_element = {'type': 'text', 'pos': pos, 'text': text}
        self.elements.append(text_element)
        return text_element

    def draw(self, screen, font):
        pygame.draw.rect(screen, (50, 50, 50), self.panel_rect)
        pygame.draw.rect(screen, (255, 255, 255), self.panel_rect, 2)

        for element in self.elements:
            if isinstance(element, dict) and element['type'] == 'rect':
                pygame.draw.rect(screen, element['color'], element['rect'], border_radius=4)

        for element in self.elements:
            if isinstance(element, Button):
                element.draw(screen, self.font)
            elif isinstance(element, Dropdown):
                element.draw(screen, self.font)
            elif isinstance(element, dict) and element['type'] == 'text':
                text_surface = self.font.render(element['text'], True, (255, 255, 255))
                screen.blit(text_surface, element['pos'])

    def handle_events(self, event):
        if event.type == pygame.MOUSEMOTION:
            over_interactive = False
            for element in self.elements:
                if isinstance(element, Button):
                    element.check_hover(event.pos)
                    if element.rect.collidepoint(event.pos):
                        over_interactive = True
                elif isinstance(element, Dropdown) and element.rect.collidepoint(event.pos):
                    over_interactive = True
            try:
                cursor = pygame.SYSTEM_CURSOR_HAND if over_interactive else pygame.SYSTEM_CURSOR_ARROW
                pygame.mouse.set_cursor(cursor)
            except pygame.error:
                pass

        for element in self.elements:
            if isinstance(element, (Button, Dropdown)):
                if element.handle_event(event):
                    return True
        return False

    def toggle_pause(self):
        self.sim.toggle_pause()

    def set_traffic_color(self, color):
        color_map = {"Красный": "red", "Желтый": "yellow", "Зеленый": "green"}
        self.sim.set_traffic_color(color_map[color])

    def update(self):
        self.info_texts[0]['text'] = f"Текущая фаза: {self.sim.current_phase}"
        self.info_texts[1]['text'] = f"Время: {self.sim.phase_time:.1f} / {self.sim.controller.phases[self.sim.current_phase]['duration']}"
        self.info_texts[2]['text'] = f"Людей: {len(self.sim.pedestrians)}"

        if self.sim.controller.current_phase != self.last_known_phase:
            self.last_known_phase = self.sim.controller.current_phase
            self.rebuild_ui_elements()

    def change_phase_duration(self, index, delta):
        self.sim.controller.change_phase_duration(index, delta)
        self.rebuild_ui_elements()

    def update_phase_color(self, index, direction, color):
        self.sim.controller.update_phase_color(index, direction, color)
        self.rebuild_ui_elements()

    def move_phase(self, index, move_by):
        self.sim.controller.move_phase(index, move_by)
        self.rebuild_ui_elements()

    def delete_phase(self, index):
        self.sim.controller.remove_phase(index)
        self.rebuild_ui_elements()

    def add_new_phase(self):
        self.sim.controller.add_phase()
        self.rebuild_ui_elements()