import pygame
from pygame.locals import *
from constants import *


class Button:

    def __init__(self, rect, text, callback):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.base_neon = 0, 200, 255
        self.hover_neon = 255, 0, 200
        self.bg_color = 10, 10, 30
        self.text_color = 255, 255, 255
        self.is_hovered = False
        self.glow_pulse = 0

    def draw(self, screen, font):
        import math
        neon_color = self.hover_neon if self.is_hovered else self.base_neon
        pulse = abs(math.sin(self.glow_pulse))
        glow_intensity = 0.5 + pulse * 0.5
        for i in range(8, 0, -1):
            alpha = int(30 * glow_intensity * (1 - i / 8))
            glow_surf = pygame.Surface((self.rect.width + i * 4, self.rect.
                height + i * 4), pygame.SRCALPHA)
            glow_rect = pygame.Rect(0, 0, self.rect.width + i * 4, self.
                rect.height + i * 4)
            pygame.draw.rect(glow_surf, (*neon_color, alpha), glow_rect,
                border_radius=8)
            screen.blit(glow_surf, (self.rect.x - i * 2, self.rect.y - i * 2))
        pygame.draw.rect(screen, self.bg_color, self.rect, border_radius=6)
        gradient_surf = pygame.Surface((self.rect.width, self.rect.height),
            pygame.SRCALPHA)
        for y in range(self.rect.height):
            alpha = int(50 * (1 - y / self.rect.height))
            pygame.draw.line(gradient_surf, (*neon_color, alpha), (0, y), (
                self.rect.width, y))
        screen.blit(gradient_surf, self.rect.topleft)
        for thickness in [3, 2, 1]:
            alpha = int(255 * glow_intensity) if thickness == 1 else 180
            pygame.draw.rect(screen, (*neon_color, alpha), self.rect,
                thickness, border_radius=6)
        text_shadow = font.render(self.text, True, (0, 0, 0))
        text_rect = text_shadow.get_rect(center=self.rect.center)
        for offset in [(2, 2), (1, 2), (2, 1)]:
            screen.blit(text_shadow, (text_rect.x + offset[0], text_rect.y +
                offset[1]))
        text_glow = font.render(self.text, True, neon_color)
        for offset in [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, -1),
            (1, -1), (-1, 1)]:
            screen.blit(text_glow, (text_rect.x + offset[0], text_rect.y +
                offset[1]))
        text_surface = font.render(self.text, True, (255, 255, 255))
        screen.blit(text_surface, text_rect)
        self.glow_pulse += 0.05

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.callback()
                return True
        return False


class TextInput:

    def __init__(self, rect, text=''):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.active = False
        self.neon_inactive = 100, 200, 255
        self.neon_active = 0, 255, 150
        self.bg_color = 10, 10, 30
        self.text_color = 255, 255, 255
        self.cursor_timer = 0
        self.cursor_visible = True
        self.glow_pulse = 0

    def get_text(self):
        return self.text

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False
            return self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                elif event.key == pygame.K_RETURN:
                    self.active = False
                else:
                    self.text += event.unicode
                return True
        return False

    def update(self, dt):
        if self.active:
            self.cursor_timer += dt
            if self.cursor_timer >= 0.5:
                self.cursor_timer = 0
                self.cursor_visible = not self.cursor_visible

    def draw(self, screen, font):
        import math
        neon_color = self.neon_active if self.active else self.neon_inactive
        pulse = abs(math.sin(self.glow_pulse))
        glow_intensity = 0.6 + pulse * 0.4
        glow_size = 6 if self.active else 4
        for i in range(glow_size, 0, -1):
            alpha = int(40 * glow_intensity * (1 - i / glow_size)
                ) if self.active else int(20 * (1 - i / glow_size))
            glow_surf = pygame.Surface((self.rect.width + i * 3, self.rect.
                height + i * 3), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*neon_color, alpha), pygame.Rect(0,
                0, self.rect.width + i * 3, self.rect.height + i * 3),
                border_radius=7)
            screen.blit(glow_surf, (self.rect.x - i * 1.5, self.rect.y - i *
                1.5))
        pygame.draw.rect(screen, self.bg_color, self.rect, border_radius=6)
        border_thickness = 2 if self.active else 1
        for thickness in range(border_thickness, 0, -1):
            alpha = 255 if thickness == 1 else 150
            pygame.draw.rect(screen, (*neon_color, alpha), self.rect, 
                thickness + 1, border_radius=6)
        text_shadow = font.render(self.text, True, (0, 0, 0))
        text_glow = font.render(self.text, True, neon_color)
        text_surface = font.render(self.text, True, (255, 255, 255))
        max_width = self.rect.width - 15
        if text_surface.get_width() > max_width:
            x_pos = self.rect.x + 5 - (text_surface.get_width() - max_width)
        else:
            x_pos = self.rect.x + 5
        y_pos = self.rect.y + 7
        screen.blit(text_shadow, (x_pos + 1, y_pos + 1))
        for offset in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            screen.blit(text_glow, (x_pos + offset[0], y_pos + offset[1]))
        screen.blit(text_surface, (x_pos, y_pos))
        if self.active and self.cursor_visible:
            cursor_pos_x = self.rect.x + 5 + text_surface.get_width()
            if cursor_pos_x < self.rect.right - 5:
                for i in range(3, 0, -1):
                    pygame.draw.line(screen, (*neon_color, 80), (
                        cursor_pos_x - i, self.rect.y + 7), (cursor_pos_x -
                        i, self.rect.y + self.rect.height - 7), 1)
                    pygame.draw.line(screen, (*neon_color, 80), (
                        cursor_pos_x + i, self.rect.y + 7), (cursor_pos_x +
                        i, self.rect.y + self.rect.height - 7), 1)
                pygame.draw.line(screen, neon_color, (cursor_pos_x, self.
                    rect.y + 7), (cursor_pos_x, self.rect.y + self.rect.
                    height - 7), 3)
                pygame.draw.line(screen, (255, 255, 255), (cursor_pos_x, 
                    self.rect.y + 7), (cursor_pos_x, self.rect.y + self.
                    rect.height - 7), 1)
        self.glow_pulse += 0.08


class Dropdown:

    def __init__(self, rect, options, selected_index, label, callback):
        self.rect = pygame.Rect(rect)
        self.options = options
        self.selected_index = selected_index
        self.label = label
        self.callback = callback
        self.is_open = False
        self.neon_base = 150, 100, 255
        self.neon_hover = 255, 150, 0
        self.neon_selected = 0, 255, 200
        self.bg_color = 10, 10, 30
        self.open_height = self.rect.height * len(self.options)
        self.glow_pulse = 0

    def draw(self, screen, font):
        import math
        neon_color = self.neon_hover if self.is_open else self.neon_base
        pulse = abs(math.sin(self.glow_pulse))
        glow_intensity = 0.5 + pulse * 0.5
        for i in range(6, 0, -1):
            alpha = int(35 * glow_intensity * (1 - i / 6))
            glow_surf = pygame.Surface((self.rect.width + i * 3, self.rect.
                height + i * 3), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*neon_color, alpha), pygame.Rect(0,
                0, self.rect.width + i * 3, self.rect.height + i * 3),
                border_radius=7)
            screen.blit(glow_surf, (self.rect.x - i * 1.5, self.rect.y - i *
                1.5))
        pygame.draw.rect(screen, self.bg_color, self.rect, border_radius=6)
        for thickness in [2, 1]:
            alpha = 255 if thickness == 1 else 180
            pygame.draw.rect(screen, (*neon_color, alpha), self.rect,
                thickness, border_radius=6)
        text = f'{self.label}: {self.options[self.selected_index]}'
        text_shadow = font.render(text, True, (0, 0, 0))
        text_glow = font.render(text, True, neon_color)
        text_surface = font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_shadow, (text_rect.x + 1, text_rect.y + 1))
        for offset in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            screen.blit(text_glow, (text_rect.x + offset[0], text_rect.y +
                offset[1]))
        screen.blit(text_surface, text_rect)
        if self.is_open:
            for i, option in enumerate(self.options):
                option_rect = pygame.Rect(self.rect.x, self.rect.y + self.
                    rect.height * (i + 1), self.rect.width, self.rect.height)
                if i == self.selected_index:
                    option_neon = self.neon_selected
                else:
                    option_neon = self.neon_base
                for j in range(4, 0, -1):
                    alpha = int(25 * (1 - j / 4))
                    glow_surf = pygame.Surface((option_rect.width + j * 2, 
                        option_rect.height + j * 2), pygame.SRCALPHA)
                    pygame.draw.rect(glow_surf, (*option_neon, alpha),
                        pygame.Rect(0, 0, option_rect.width + j * 2, 
                        option_rect.height + j * 2), border_radius=5)
                    screen.blit(glow_surf, (option_rect.x - j, option_rect.
                        y - j))
                pygame.draw.rect(screen, self.bg_color, option_rect,
                    border_radius=4)
                pygame.draw.rect(screen, (*option_neon, 200), option_rect, 
                    2, border_radius=4)
                pygame.draw.rect(screen, (*option_neon, 100), option_rect, 
                    1, border_radius=4)
                option_shadow = font.render(option, True, (0, 0, 0))
                option_glow = font.render(option, True, option_neon)
                option_text = font.render(option, True, (255, 255, 255))
                option_text_rect = option_text.get_rect(center=option_rect.
                    center)
                screen.blit(option_shadow, (option_text_rect.x + 1, 
                    option_text_rect.y + 1))
                for offset in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    screen.blit(option_glow, (option_text_rect.x + offset[0
                        ], option_text_rect.y + offset[1]))
                screen.blit(option_text, option_text_rect)
        self.glow_pulse += 0.06

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.is_open = not self.is_open
                return True
            if self.is_open:
                for i in range(len(self.options)):
                    option_rect = pygame.Rect(self.rect.x, self.rect.y + 
                        self.rect.height * (i + 1), self.rect.width, self.
                        rect.height)
                    if option_rect.collidepoint(event.pos):
                        self.selected_index = i
                        self.is_open = False
                        self.callback(self.options[i])
                        return True
        if event.type == pygame.MOUSEBUTTONDOWN and self.is_open:
            full_area = self.rect.union(pygame.Rect(self.rect.x, self.rect.
                y + self.rect.height, self.rect.width, self.open_height))
            if not full_area.collidepoint(event.pos):
                self.is_open = False
                return True
        return False


class ScrollablePanel:

    def __init__(self, viewport_rect):
        self.viewport_rect = pygame.Rect(viewport_rect)
        self.elements = []
        self.content_height = 0
        self.scroll_y = 0
        self.scrollbar_track_rect = None
        self.scrollbar_thumb_rect = None
        self.is_dragging = False
        self.drag_start_y = 0
        self.drag_start_scroll_y = 0
        self.glow_pulse = 0

    def add_element(self, element):
        self.elements.append(element)
        return element

    def clear_elements(self):
        self.elements.clear()
        self.content_height = 0
        self.scroll_y = 0

    def set_content_height(self, height):
        self.content_height = height
        max_scroll = max(0, self.content_height - self.viewport_rect.height)
        self.scroll_y = max(0, min(self.scroll_y, max_scroll))

    def handle_wheel(self, event):
        if self.viewport_rect.collidepoint(pygame.mouse.get_pos()):
            self.scroll_y -= event.y * 20
            self.scroll_y = max(0, min(self.scroll_y, max(0, self.
                content_height - self.viewport_rect.height)))
            return True
        return False

    def handle_scrollbar_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if (self.scrollbar_thumb_rect and self.scrollbar_thumb_rect.
                collidepoint(event.pos)):
                self.is_dragging = True
                self.drag_start_y = event.pos[1]
                self.drag_start_scroll_y = self.scroll_y
                return True
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.is_dragging = False
        if event.type == pygame.MOUSEMOTION and self.is_dragging:
            dy = event.pos[1] - self.drag_start_y
            scroll_delta = dy * (self.content_height / self.viewport_rect.
                height)
            self.scroll_y = self.drag_start_scroll_y + scroll_delta
            self.scroll_y = max(0, min(self.scroll_y, max(0, self.
                content_height - self.viewport_rect.height)))
            return True
        return False

    def draw(self, screen, font, background_pulse=0):
        import math
        self.glow_pulse += 0.03
        original_clip = screen.get_clip()
        screen.set_clip(self.viewport_rect)
        open_dropdowns = []
        for element in self.elements:
            if isinstance(element, dict) and element.get('type') == 'rect':
                scrolled_rect = element['rect'].copy()
                scrolled_rect.y -= self.scroll_y
                if (scrolled_rect.bottom < self.viewport_rect.top or 
                    scrolled_rect.top > self.viewport_rect.bottom):
                    continue
                pulse = abs(math.sin(background_pulse * 2))
                neon_highlight = 100, 200, 255
                for i in range(6, 0, -1):
                    alpha = int(30 * pulse * (1 - i / 6))
                    glow_rect = scrolled_rect.inflate(i * 2, i * 2)
                    glow_surf = pygame.Surface((glow_rect.width, glow_rect.
                        height), pygame.SRCALPHA)
                    pygame.draw.rect(glow_surf, (*neon_highlight, alpha),
                        pygame.Rect(0, 0, glow_rect.width, glow_rect.height
                        ), border_radius=6)
                    screen.blit(glow_surf, glow_rect.topleft)
                pygame.draw.rect(screen, (20, 20, 40), scrolled_rect,
                    border_radius=4)
                pygame.draw.rect(screen, (*neon_highlight, int(150 + 100 *
                    pulse)), scrolled_rect, 2, border_radius=4)
            elif isinstance(element, (Button, Dropdown)):
                original_rect = element.rect.copy()
                element.rect.y -= self.scroll_y
                if (element.rect.bottom >= self.viewport_rect.top and 
                    element.rect.top <= self.viewport_rect.bottom):
                    if isinstance(element, Dropdown) and element.is_open:
                        open_dropdowns.append((element, original_rect))
                        was_open = element.is_open
                        element.is_open = False
                        element.draw(screen, font)
                        element.is_open = was_open
                    else:
                        element.draw(screen, font)
                element.rect = original_rect
            elif isinstance(element, dict) and element.get('type') == 'text':
                scrolled_pos = element['pos'][0], element['pos'][1
                    ] - self.scroll_y
                if scrolled_pos[1
                    ] < self.viewport_rect.top - 30 or scrolled_pos[1
                    ] > self.viewport_rect.bottom:
                    continue
                neon_text_color = 0, 220, 255
                text_shadow = font.render(element['text'], True, (0, 0, 0))
                text_glow = font.render(element['text'], True, neon_text_color)
                text_surface = font.render(element['text'], True, (255, 255,
                    255))
                screen.blit(text_shadow, (scrolled_pos[0] + 1, scrolled_pos
                    [1] + 1))
                for offset in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-
                    1, -1)]:
                    screen.blit(text_glow, (scrolled_pos[0] + offset[0], 
                        scrolled_pos[1] + offset[1]))
                screen.blit(text_surface, scrolled_pos)
        for dropdown, original_rect in open_dropdowns:
            dropdown.rect.y -= self.scroll_y
            self._draw_dropdown_menu(screen, font, dropdown)
            dropdown.rect = original_rect
        screen.set_clip(original_clip)
        if self.content_height > self.viewport_rect.height:
            pulse = abs(math.sin(self.glow_pulse))
            self.scrollbar_track_rect = pygame.Rect(self.viewport_rect.
                right - 12, self.viewport_rect.top, 10, self.viewport_rect.
                height)
            pygame.draw.rect(screen, (15, 15, 30), self.
                scrollbar_track_rect, border_radius=5)
            pygame.draw.rect(screen, (0, 150, 200, 100), self.
                scrollbar_track_rect, 1, border_radius=5)
            viewable_ratio = self.viewport_rect.height / self.content_height
            thumb_h = max(20, self.viewport_rect.height * viewable_ratio)
            scrollable_dist = self.content_height - self.viewport_rect.height
            scroll_ratio = self.scroll_y / max(1, scrollable_dist)
            thumb_y = self.scrollbar_track_rect.top + scroll_ratio * (self.
                scrollbar_track_rect.height - thumb_h)
            self.scrollbar_thumb_rect = pygame.Rect(self.
                scrollbar_track_rect.x + 1, thumb_y, 8, thumb_h)
            neon_scrollbar = 0, 255, 200
            for i in range(3, 0, -1):
                alpha = int(60 * (1 - i / 3))
                glow_rect = self.scrollbar_thumb_rect.inflate(i * 2, 0)
                glow_surf = pygame.Surface((glow_rect.width, glow_rect.
                    height), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (*neon_scrollbar, alpha),
                    pygame.Rect(0, 0, glow_rect.width, glow_rect.height),
                    border_radius=5)
                screen.blit(glow_surf, glow_rect.topleft)
            pygame.draw.rect(screen, neon_scrollbar, self.
                scrollbar_thumb_rect, border_radius=4)
            pygame.draw.rect(screen, (150, 255, 255), self.
                scrollbar_thumb_rect, 1, border_radius=4)

    def get_adjusted_event_pos(self, event_pos):
        return event_pos[0], event_pos[1] + self.scroll_y

    def _draw_dropdown_menu(self, screen, font, dropdown):
        import math
        for i, option in enumerate(dropdown.options):
            option_rect = pygame.Rect(dropdown.rect.x, dropdown.rect.y + 
                dropdown.rect.height * (i + 1), dropdown.rect.width,
                dropdown.rect.height)
            if i == dropdown.selected_index:
                option_neon = dropdown.neon_selected
            else:
                option_neon = dropdown.neon_base
            for j in range(4, 0, -1):
                alpha = int(25 * (1 - j / 4))
                glow_surf = pygame.Surface((option_rect.width + j * 2, 
                    option_rect.height + j * 2), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (*option_neon, alpha), pygame.
                    Rect(0, 0, option_rect.width + j * 2, option_rect.
                    height + j * 2), border_radius=5)
                screen.blit(glow_surf, (option_rect.x - j, option_rect.y - j))
            pygame.draw.rect(screen, dropdown.bg_color, option_rect,
                border_radius=4)
            pygame.draw.rect(screen, (*option_neon, 200), option_rect, 2,
                border_radius=4)
            pygame.draw.rect(screen, (*option_neon, 100), option_rect, 1,
                border_radius=4)
            option_shadow = font.render(option, True, (0, 0, 0))
            option_glow = font.render(option, True, option_neon)
            option_text = font.render(option, True, (255, 255, 255))
            option_text_rect = option_text.get_rect(center=option_rect.center)
            screen.blit(option_shadow, (option_text_rect.x + 1, 
                option_text_rect.y + 1))
            for offset in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                screen.blit(option_glow, (option_text_rect.x + offset[0], 
                    option_text_rect.y + offset[1]))
            screen.blit(option_text, option_text_rect)


import threading
from llm_generator import generate_config_with_llm


class UIManager:

    def __init__(self, sim):
        self.sim = sim
        self.elements = []
        self.font = pygame.font.Font(None, 20)
        self.panel_rect = pygame.Rect(0, 0, 0, 0)
        self.last_known_phase = -1
        self.ai_status_message = ''
        self.ai_status_timer = 0
        self.ai_thread = None
        self.ai_thread_result = None
        self.ai_scenario_input = None
        self.info_texts = []
        self.scrollable_panel = None
        self.background_pulse = 0
        self.zoom_level = 1.0
        self.rebuild_ui_elements()

    def rebuild_ui_elements(self):
        from constants import screen_config
        self.panel_rect = pygame.Rect(screen_config.width - UI_PANEL_WIDTH,
            0, UI_PANEL_WIDTH, screen_config.height)
        open_dropdown_rect = None
        for el in self.elements:
            if isinstance(el, Dropdown) and el.is_open and el.rect.y > 200:
                open_dropdown_rect = el.rect
                break
        self.elements.clear()
        self.info_texts.clear()
        y = 20
        self.add_button((screen_config.width - UI_PANEL_WIDTH + 50, y, 200,
            40), 'Pause/Resume', self.toggle_pause)
        y += 50
        mode_text = 'Режим: ' + ('Динамический' if self.sim.controller.mode ==
            'dynamic' else 'Статический')
        self.add_button((screen_config.width - UI_PANEL_WIDTH + 20, y, 260,
            30), mode_text, self.toggle_mode)
        y += 40
        self.add_button((screen_config.width - UI_PANEL_WIDTH + 20, y, 125,
            30), 'Сохранить', self.export_config)
        self.add_button((screen_config.width - UI_PANEL_WIDTH + 155, y, 125,
            30), 'Сбросить', self.reset_settings)
        y += 40
        self.add_text((screen_config.width - UI_PANEL_WIDTH + 20, y),
            'Описание AI-сценария:')
        y += 25
        self.ai_scenario_input = self.add_text_input((screen_config.width -
            UI_PANEL_WIDTH + 20, y, 260, 30),
            'Вечерний час пик, пробка с запада')
        y += 40
        self.add_button((screen_config.width - UI_PANEL_WIDTH + 20, y, 260,
            30), 'Сгенерировать по описанию', self.
            trigger_ai_generation_from_input)
        y += 35
        if self.ai_status_message:
            self.add_text((screen_config.width - UI_PANEL_WIDTH + 20, y),
                self.ai_status_message)
            y += 20
        info_y = y
        if self.sim.controller.mode == 'dynamic':
            self.info_texts.append(self.add_text((screen_config.width -
                UI_PANEL_WIDTH + 20, info_y),
                f'Людей: {len(self.sim.pedestrians)}', add_to_list=False))
            info_y += 25
            self.info_texts.append(self.add_text((screen_config.width -
                UI_PANEL_WIDTH + 20, info_y),
                f'Ожидают (H/V): {self.sim.waiting_cars_h} / {self.sim.waiting_cars_v}'
                , add_to_list=False))
            info_y += 25
            self.info_texts.append(self.add_text((screen_config.width -
                UI_PANEL_WIDTH + 20, info_y),
                f'Видимые (H/V): {self.sim.controller.visible_cars_h} / {self.sim.controller.visible_cars_v}'
                , add_to_list=False))
            info_y += 25
            self.info_texts.append(self.add_text((screen_config.width -
                UI_PANEL_WIDTH + 20, info_y),
                f'Давление (H/V): {self.sim.controller.pressure_h:.1f} / {self.sim.controller.pressure_v:.1f}'
                , add_to_list=False))
            info_y += 25
            self.info_texts.append(self.add_text((screen_config.width -
                UI_PANEL_WIDTH + 20, info_y),
                f'Штраф (H/V): {self.sim.h_wait_time_sq_sum:.1f} / {self.sim.v_wait_time_sq_sum:.1f}'
                , add_to_list=False))
            self.add_text((screen_config.width - UI_PANEL_WIDTH + 20, y),
                f'Фактор: {self.sim.controller.dynamic_logic_factor:.3f}')
            self.add_button((screen_config.width - UI_PANEL_WIDTH + 180, y -
                2, 45, 20), '+', lambda : self.change_dynamic_factor(0.001))
            self.add_button((screen_config.width - UI_PANEL_WIDTH + 230, y -
                2, 45, 20), '-', lambda : self.change_dynamic_factor(-0.001))
        else:
            self.info_texts.append(self.add_text((screen_config.width -
                UI_PANEL_WIDTH + 20, info_y),
                f'Фаза: {self.sim.current_phase}', add_to_list=False))
            info_y += 25
            self.info_texts.append(self.add_text((screen_config.width -
                UI_PANEL_WIDTH + 20, info_y),
                f'Время: {self.sim.phase_time:.1f}', add_to_list=False))
            info_y += 25
            self.info_texts.append(self.add_text((screen_config.width -
                UI_PANEL_WIDTH + 20, info_y),
                f'Людей: {len(self.sim.pedestrians)}', add_to_list=False))
            info_y += 25
            self.info_texts.append(self.add_text((screen_config.width -
                UI_PANEL_WIDTH + 20, info_y),
                f'Ожидают (H/V): {self.sim.waiting_cars_h} / {self.sim.waiting_cars_v}'
                , add_to_list=False))
            info_y += 25
            self.info_texts.append(self.add_text((screen_config.width -
                UI_PANEL_WIDTH + 20, info_y),
                f'Штраф (H/V): {self.sim.h_wait_time_sq_sum:.1f} / {self.sim.v_wait_time_sq_sum:.1f}'
                , add_to_list=False))
        y += 20
        self.add_text((screen_config.width - UI_PANEL_WIDTH + 20, y),
            'Плотность (машин/10с):')
        y += 25
        dir_map = {'from_north': 'Север', 'from_south': 'Юг', 'from_west':
            'Запад', 'from_east': 'Восток'}
        for direction, name in dir_map.items():
            density = self.sim.controller.traffic_density.get(direction, 0)
            self.add_text((screen_config.width - UI_PANEL_WIDTH + 20, y),
                f'{name}: {density:.1f}')
            self.add_button((screen_config.width - UI_PANEL_WIDTH + 180, y -
                2, 45, 20), '+', lambda d=direction: self.
                change_traffic_density(d, 1.0))
            self.add_button((screen_config.width - UI_PANEL_WIDTH + 230, y -
                2, 45, 20), '-', lambda d=direction: self.
                change_traffic_density(d, -1.0))
            y += 25
        y += 15
        if self.sim.controller.mode == 'static':
            self.add_text((screen_config.width - UI_PANEL_WIDTH + 20, y),
                'Редактор Фаз:')
            y += 25
            phases_area_start_y = y
            add_phase_button_h = 40
            viewport_rect = pygame.Rect(screen_config.width -
                UI_PANEL_WIDTH, phases_area_start_y, UI_PANEL_WIDTH, 
                screen_config.height - phases_area_start_y -
                add_phase_button_h - 15)
            self.scrollable_panel = ScrollablePanel(viewport_rect)
            colors_eng = ['green', 'yellow', 'red']
            y_content_offset = 0
            for i, phase in enumerate(self.sim.controller.phases):
                block_y = phases_area_start_y + y_content_offset
                west = phase.get('west', phase.get('horiz', 'red'))
                east = phase.get('east', phase.get('horiz', 'red'))
                north = phase.get('north', phase.get('vert', 'red'))
                south = phase.get('south', phase.get('vert', 'red'))
                if i == self.sim.controller.current_phase:
                    highlight_rect = pygame.Rect(screen_config.width -
                        UI_PANEL_WIDTH + 10, block_y - 5, UI_PANEL_WIDTH - 
                        20, 98)
                    self.scrollable_panel.add_element({'type': 'rect',
                        'rect': highlight_rect, 'color': (90, 90, 70)})
                text_elem = {'type': 'text', 'pos': (screen_config.width -
                    UI_PANEL_WIDTH + 20, block_y), 'text':
                    f"Длительность: {phase['duration']}s"}
                self.scrollable_panel.add_element(text_elem)
                btn1 = Button((screen_config.width - UI_PANEL_WIDTH + 150, 
                    block_y - 2, 25, 20), '+5', lambda index=i: self.
                    change_phase_duration(index, 5))
                self.scrollable_panel.add_element(btn1)
                btn2 = Button((screen_config.width - UI_PANEL_WIDTH + 180, 
                    block_y - 2, 25, 20), '-5', lambda index=i: self.
                    change_phase_duration(index, -5))
                self.scrollable_panel.add_element(btn2)
                west_idx = colors_eng.index(west)
                dd_west = Dropdown((screen_config.width - UI_PANEL_WIDTH + 
                    20, block_y + 18, 60, 25), colors_eng, west_idx, 'W', 
                    lambda color, index=i: self.update_phase_color(index,
                    'west', color))
                self.scrollable_panel.add_element(dd_west)
                east_idx = colors_eng.index(east)
                dd_east = Dropdown((screen_config.width - UI_PANEL_WIDTH + 
                    85, block_y + 18, 60, 25), colors_eng, east_idx, 'E', 
                    lambda color, index=i: self.update_phase_color(index,
                    'east', color))
                self.scrollable_panel.add_element(dd_east)
                north_idx = colors_eng.index(north)
                dd_north = Dropdown((screen_config.width - UI_PANEL_WIDTH +
                    150, block_y + 18, 60, 25), colors_eng, north_idx, 'N',
                    lambda color, index=i: self.update_phase_color(index,
                    'north', color))
                self.scrollable_panel.add_element(dd_north)
                south_idx = colors_eng.index(south)
                dd_south = Dropdown((screen_config.width - UI_PANEL_WIDTH +
                    215, block_y + 18, 60, 25), colors_eng, south_idx, 'S',
                    lambda color, index=i: self.update_phase_color(index,
                    'south', color))
                self.scrollable_panel.add_element(dd_south)
                btn3 = Button((screen_config.width - UI_PANEL_WIDTH + 20, 
                    block_y + 48, 30, 22), '↑', lambda index=i: self.
                    move_phase(index, -1))
                self.scrollable_panel.add_element(btn3)
                btn4 = Button((screen_config.width - UI_PANEL_WIDTH + 55, 
                    block_y + 48, 30, 22), '↓', lambda index=i: self.
                    move_phase(index, 1))
                self.scrollable_panel.add_element(btn4)
                btn5 = Button((screen_config.width - UI_PANEL_WIDTH + 210, 
                    block_y + 48, 65, 22), 'X', lambda index=i: self.
                    delete_phase(index))
                self.scrollable_panel.add_element(btn5)
                y_content_offset += 75
                for dd in [dd_west, dd_east, dd_north, dd_south]:
                    if open_dropdown_rect and open_dropdown_rect == dd.rect:
                        dd.is_open = True
                        y_content_offset += dd.open_height
            self.scrollable_panel.set_content_height(y_content_offset)
            self.add_button((screen_config.width - UI_PANEL_WIDTH + 50, 
                viewport_rect.bottom + 10, 200, 30), 'Добавить фазу', self.
                add_new_phase)
        else:
            self.scrollable_panel = None

    def add_button(self, rect, text, callback):
        button = Button(rect, text, callback)
        self.elements.append(button)
        return button

    def add_dropdown(self, rect, options, selected_index, label, callback):
        dropdown = Dropdown(rect, options, selected_index, label, callback)
        self.elements.append(dropdown)
        return dropdown

    def add_text_input(self, rect, initial_text=''):
        text_input = TextInput(rect, initial_text)
        self.elements.append(text_input)
        return text_input

    def add_text(self, pos, text, add_to_list=True):
        text_element = {'type': 'text', 'pos': pos, 'text': text}
        if add_to_list:
            self.elements.append(text_element)
        return text_element

    def draw(self, screen, font):
        import math
        self.background_pulse += 0.03
        pulse = abs(math.sin(self.background_pulse))
        bg_surf = pygame.Surface((self.panel_rect.width, self.panel_rect.
            height), pygame.SRCALPHA)
        for y in range(self.panel_rect.height):
            alpha = int(200 + 30 * pulse * (1 - y / self.panel_rect.height))
            color_val = int(15 + 10 * pulse)
            pygame.draw.line(bg_surf, (color_val, color_val, color_val + 20,
                alpha), (0, y), (self.panel_rect.width, y))
        screen.blit(bg_surf, self.panel_rect.topleft)
        neon_border = 0, 200, 255
        for i in range(3, 0, -1):
            alpha = int(100 + 100 * pulse) if i == 1 else 80
            pygame.draw.rect(screen, (*neon_border, alpha), self.panel_rect, i)
        for element in self.elements:
            if hasattr(element, 'draw'):
                element.draw(screen, self.font)
            elif isinstance(element, dict) and element.get('type') == 'text':
                neon_text_color = 0, 220, 255
                text_shadow = self.font.render(element['text'], True, (0, 0, 0)
                    )
                text_glow = self.font.render(element['text'], True,
                    neon_text_color)
                text_surface = self.font.render(element['text'], True, (255,
                    255, 255))
                screen.blit(text_shadow, (element['pos'][0] + 1, element[
                    'pos'][1] + 1))
                for offset in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-
                    1, -1)]:
                    screen.blit(text_glow, (element['pos'][0] + offset[0], 
                        element['pos'][1] + offset[1]))
                screen.blit(text_surface, element['pos'])
        if self.scrollable_panel:
            self.scrollable_panel.draw(screen, self.font, self.background_pulse
                )

    def handle_events(self, event):
        if self.scrollable_panel:
            if event.type == pygame.MOUSEWHEEL:
                if self.scrollable_panel.handle_wheel(event):
                    return True
            if self.scrollable_panel.handle_scrollbar_event(event):
                return True
            if event.type == pygame.MOUSEMOTION:
                mouse_pos = pygame.mouse.get_pos()
                if self.scrollable_panel.viewport_rect.collidepoint(mouse_pos):
                    for element in self.scrollable_panel.elements:
                        if isinstance(element, Button):
                            scrolled_rect = element.rect.copy()
                            scrolled_rect.y -= self.scrollable_panel.scroll_y
                            element.check_hover(mouse_pos if scrolled_rect.
                                collidepoint(mouse_pos) else (-9999, -9999))
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                for element in self.scrollable_panel.elements:
                    if isinstance(element, Dropdown) and element.is_open:
                        scrolled_rect = element.rect.copy()
                        scrolled_rect.y -= self.scrollable_panel.scroll_y
                        if scrolled_rect.collidepoint(mouse_pos):
                            original_rect = element.rect
                            element.rect = scrolled_rect
                            element.is_open = False
                            element.rect = original_rect
                            return True
                        for i in range(len(element.options)):
                            option_rect = pygame.Rect(scrolled_rect.x, 
                                scrolled_rect.y + scrolled_rect.height * (i +
                                1), scrolled_rect.width, scrolled_rect.height)
                            if option_rect.collidepoint(mouse_pos):
                                element.selected_index = i
                                element.callback(element.options[i])
                                element.is_open = False
                                self.rebuild_ui_elements()
                                return True
                        full_area = scrolled_rect.union(pygame.Rect(
                            scrolled_rect.x, scrolled_rect.y +
                            scrolled_rect.height, scrolled_rect.width,
                            element.open_height))
                        if not full_area.collidepoint(mouse_pos):
                            element.is_open = False
                            return True
                if self.scrollable_panel.viewport_rect.collidepoint(mouse_pos):
                    for element in self.scrollable_panel.elements:
                        if isinstance(element, (Button, Dropdown)):
                            scrolled_rect = element.rect.copy()
                            scrolled_rect.y -= self.scrollable_panel.scroll_y
                            if scrolled_rect.collidepoint(mouse_pos):
                                adjusted_event = pygame.event.Event(event.
                                    type, event.dict)
                                adjusted_event.pos = mouse_pos
                                original_rect = element.rect
                                element.rect = scrolled_rect
                                result = element.handle_event(adjusted_event)
                                element.rect = original_rect
                                if result:
                                    return True
        if event.type == pygame.MOUSEMOTION:
            for element in self.elements:
                if isinstance(element, Button):
                    element.check_hover(event.pos)
        active_dropdown = next((el for el in self.elements if isinstance(el,
            Dropdown) and el.is_open), None)
        if active_dropdown:
            if active_dropdown.handle_event(event):
                self.rebuild_ui_elements()
                return True
        active_input = next((el for el in self.elements if isinstance(el,
            TextInput) and el.active), None)
        if active_input and event.type == pygame.KEYDOWN:
            if active_input.handle_event(event):
                return True
        for element in self.elements:
            if element != active_dropdown:
                if hasattr(element, 'handle_event'):
                    if element.handle_event(event):
                        if isinstance(element, Dropdown):
                            self.rebuild_ui_elements()
                        return True
        return False

    def change_dynamic_factor(self, delta):
        new_factor = self.sim.controller.dynamic_logic_factor + delta
        self.sim.controller.dynamic_logic_factor = round(max(0.9, min(0.999,
            new_factor)), 3)
        self.rebuild_ui_elements()

    def change_traffic_density(self, direction, delta):
        current_density = self.sim.controller.traffic_density[direction]
        new_density = min(max(0.0, current_density + delta), 5)
        self.sim.controller.traffic_density[direction] = round(new_density, 1)
        self.rebuild_ui_elements()

    def zoom_in(self):
        from constants import screen_config
        self.zoom_level = min(3.0, self.zoom_level + 0.1)

    def zoom_out(self):
        from constants import screen_config
        self.zoom_level = max(0.5, self.zoom_level - 0.1)

    def zoom_reset(self):
        self.zoom_level = 1.0

    def toggle_pause(self):
        self.sim.toggle_pause()

    def update_phase_color(self, i, d, c):
        self.sim.controller.update_phase_color(i, d, c)
        self.rebuild_ui_elements()

    def change_phase_duration(self, i, d):
        self.sim.controller.change_phase_duration(i, d)
        self.rebuild_ui_elements()

    def move_phase(self, i, d):
        self.sim.controller.move_phase(i, d)
        self.rebuild_ui_elements()

    def delete_phase(self, i):
        self.sim.controller.remove_phase(i)
        self.rebuild_ui_elements()

    def add_new_phase(self):
        self.sim.controller.add_phase()
        self.rebuild_ui_elements()

    def toggle_mode(self):
        self.sim.controller.set_mode('static' if self.sim.controller.mode ==
            'dynamic' else 'dynamic')
        self.rebuild_ui_elements()

    def refresh_window(self):
        self.sim.update_screen_size()
        self.rebuild_ui_elements()

    def reset_settings(self):
        self.sim.controller.reset_to_defaults()
        self.rebuild_ui_elements()

    def update(self, dt):
        if self.ai_scenario_input:
            self.ai_scenario_input.update(dt)
        if self.ai_thread and not self.ai_thread.is_alive():
            if isinstance(self.ai_thread_result, dict):
                self.sim.controller.import_config_dict(self.ai_thread_result)
                self.ai_status_message = 'Успешно сгенерировано!'
            else:
                error_message = str(self.ai_thread_result)
                self.ai_status_message = f'Ошибка: {error_message[:40]}...'
                print(f'Ошибка генерации AI-сценария: {error_message}')
            self.ai_thread = None
            self.ai_thread_result = None
            self.ai_status_timer = 5.0
            self.rebuild_ui_elements()
        if self.ai_status_timer > 0:
            self.ai_status_timer -= dt
            if self.ai_status_timer <= 0:
                self.ai_status_message = ''
                self.rebuild_ui_elements()
        if self.sim.controller.mode == 'dynamic':
            self.info_texts[0]['text'] = f'Людей: {len(self.sim.pedestrians)}'
            self.info_texts[1]['text'] = (
                f'Ожидают (H/V): {self.sim.waiting_cars_h} / {self.sim.waiting_cars_v}'
                )
            self.info_texts[2]['text'] = (
                f'Видимые (H/V): {self.sim.controller.visible_cars_h} / {self.sim.controller.visible_cars_v}'
                )
            self.info_texts[3]['text'] = (
                f'Давление (H/V): {self.sim.controller.pressure_h:.1f} / {self.sim.controller.pressure_v:.1f}'
                )
            self.info_texts[4]['text'] = (
                f'Штраф (H/V): {self.sim.controller.weighted_h_penalty:.0f} / {self.sim.controller.weighted_v_penalty:.0f}'
                )
        else:
            phase_duration = self.sim.controller.phases[self.sim.current_phase
                ]['duration']
            self.info_texts[0]['text'
                ] = f'Текущая фаза: {self.sim.current_phase}'
            self.info_texts[1]['text'
                ] = f'Время: {self.sim.phase_time:.1f} / {phase_duration}'
            self.info_texts[2]['text'] = f'Людей: {len(self.sim.pedestrians)}'
            self.info_texts[3]['text'] = (
                f'Ожидают (H/V): {self.sim.waiting_cars_h} / {self.sim.waiting_cars_v}'
                )
            self.info_texts[4]['text'] = (
                f'Штраф (H/V): {self.sim.h_wait_time_sq_sum:.1f} / {self.sim.v_wait_time_sq_sum:.1f}'
                )
        if self.sim.controller.current_phase != self.last_known_phase:
            self.last_known_phase = self.sim.controller.current_phase
            self.rebuild_ui_elements()

    def trigger_ai_generation_from_input(self):
        if self.ai_scenario_input:
            scenario_text = self.ai_scenario_input.get_text()
            if scenario_text:
                self.generate_ai_config(scenario_text)

    def _ai_worker(self, scenario: str):
        try:
            new_config = generate_config_with_llm(scenario)
            self.ai_thread_result = new_config
        except (ConnectionError, ValueError, Exception) as e:
            self.ai_thread_result = e

    def generate_ai_config(self, scenario: str):
        if self.ai_thread and self.ai_thread.is_alive():
            return
        self.ai_status_message = '⟳ Генерация...'
        self.ai_status_timer = 0
        self.ai_thread_result = None
        self.rebuild_ui_elements()
        pygame.display.flip()
        self.ai_thread = threading.Thread(target=self._ai_worker, args=(
            scenario,))
        self.ai_thread.start()

    def export_config(self):
        import json
        data = self.sim.controller.export_config_dict()
        try:
            with open('traffic_config.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f'Ошибка: {e}')

    def import_config(self):
        import json, os
        if not os.path.exists('traffic_config.json'):
            return
        try:
            with open('traffic_config.json', 'r', encoding='utf-8') as f:
                self.sim.controller.import_config_dict(json.load(f))
            self.rebuild_ui_elements()
        except Exception as e:
            print(f'Ошибка: {e}')
