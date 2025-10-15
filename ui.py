import pygame
from pygame.locals import *

from constants import *


class Button:
    def __init__(self, rect, text, callback):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        # Неоновые цвета вместо серых
        self.base_neon = (0, 200, 255)  # Голубой неон
        self.hover_neon = (255, 0, 200)  # Розовый неон
        self.bg_color = (10, 10, 30)  # Темный фон
        self.text_color = (255, 255, 255)
        self.is_hovered = False
        self.glow_pulse = 0

    def draw(self, screen, font):
        import math

        # Выбираем цвет на основе hover
        neon_color = self.hover_neon if self.is_hovered else self.base_neon

        # Пульсирующее свечение
        pulse = abs(math.sin(self.glow_pulse))
        glow_intensity = 0.5 + pulse * 0.5

        # Рисуем внешнее свечение (несколько слоев)
        for i in range(8, 0, -1):
            alpha = int(30 * glow_intensity * (1 - i / 8))
            glow_surf = pygame.Surface((self.rect.width + i * 4, self.rect.height + i * 4), pygame.SRCALPHA)
            glow_rect = pygame.Rect(0, 0, self.rect.width + i * 4, self.rect.height + i * 4)
            pygame.draw.rect(glow_surf, (*neon_color, alpha), glow_rect, border_radius=8)
            screen.blit(glow_surf, (self.rect.x - i * 2, self.rect.y - i * 2))

        # Основной фон кнопки (темный)
        pygame.draw.rect(screen, self.bg_color, self.rect, border_radius=6)

        # Градиент внутри кнопки
        gradient_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        for y in range(self.rect.height):
            alpha = int(50 * (1 - y / self.rect.height))
            pygame.draw.line(gradient_surf, (*neon_color, alpha), (0, y), (self.rect.width, y))
        screen.blit(gradient_surf, self.rect.topleft)

        # Неоновая окантовка (3 слоя для толщины)
        for thickness in [3, 2, 1]:
            alpha = int(255 * glow_intensity) if thickness == 1 else 180
            pygame.draw.rect(screen, (*neon_color, alpha), self.rect, thickness, border_radius=6)

        # Яркий контрастный текст
        # Сначала темная тень для глубины
        text_shadow = font.render(self.text, True, (0, 0, 0))
        text_rect = text_shadow.get_rect(center=self.rect.center)
        for offset in [(2, 2), (1, 2), (2, 1)]:
            screen.blit(text_shadow, (text_rect.x + offset[0], text_rect.y + offset[1]))

        # Затем яркое неоновое свечение
        text_glow = font.render(self.text, True, neon_color)
        for offset in [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]:
            screen.blit(text_glow, (text_rect.x + offset[0], text_rect.y + offset[1]))

        # И белый текст сверху для максимальной читаемости
        text_surface = font.render(self.text, True, (255, 255, 255))
        screen.blit(text_surface, text_rect)

        # Обновляем пульсацию
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
        # Неоновые цвета
        self.neon_inactive = (100, 200, 255)  # Голубой
        self.neon_active = (0, 255, 150)  # Зеленый
        self.bg_color = (10, 10, 30)
        self.text_color = (255, 255, 255)
        self.cursor_timer = 0
        self.cursor_visible = True
        self.glow_pulse = 0

    def get_text(self):
        return self.text

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Активируем, если кликнули на поле. Деактивируем, если кликнули вне его.
            if self.rect.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False
            # Потребляем событие, только если кликнули именно на поле
            return self.rect.collidepoint(event.pos)

        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                elif event.key == pygame.K_RETURN:
                    self.active = False
                else:
                    self.text += event.unicode
                return True  # Событие клавиатуры обработано
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

        # Внешнее свечение (если активно - ярче)
        glow_size = 6 if self.active else 4
        for i in range(glow_size, 0, -1):
            alpha = int(40 * glow_intensity * (1 - i / glow_size)) if self.active else int(20 * (1 - i / glow_size))
            glow_surf = pygame.Surface((self.rect.width + i * 3, self.rect.height + i * 3), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*neon_color, alpha), 
                           pygame.Rect(0, 0, self.rect.width + i * 3, self.rect.height + i * 3), 
                           border_radius=7)
            screen.blit(glow_surf, (self.rect.x - i * 1.5, self.rect.y - i * 1.5))

        # Темный фон
        pygame.draw.rect(screen, self.bg_color, self.rect, border_radius=6)

        # Неоновая окантовка
        border_thickness = 2 if self.active else 1
        for thickness in range(border_thickness, 0, -1):
            alpha = 255 if thickness == 1 else 150
            pygame.draw.rect(screen, (*neon_color, alpha), self.rect, thickness + 1, border_radius=6)

        # Яркий контрастный текст с тенью
        text_shadow = font.render(self.text, True, (0, 0, 0))
        text_glow = font.render(self.text, True, neon_color)
        text_surface = font.render(self.text, True, (255, 255, 255))

        # Обрезка текста, если он не помещается
        max_width = self.rect.width - 15
        if text_surface.get_width() > max_width:
            x_pos = self.rect.x + 5 - (text_surface.get_width() - max_width)
        else:
            x_pos = self.rect.x + 5

        y_pos = self.rect.y + 7

        # Тень
        screen.blit(text_shadow, (x_pos + 1, y_pos + 1))
        # Неоновое свечение
        for offset in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            screen.blit(text_glow, (x_pos + offset[0], y_pos + offset[1]))
        # Белый текст
        screen.blit(text_surface, (x_pos, y_pos))

        if self.active and self.cursor_visible:
            cursor_pos_x = self.rect.x + 5 + text_surface.get_width()
            if cursor_pos_x < self.rect.right - 5:
                # Яркий неоновый курсор с свечением
                # Свечение курсора
                for i in range(3, 0, -1):
                    pygame.draw.line(screen, (*neon_color, 80), 
                                   (cursor_pos_x - i, self.rect.y + 7), 
                                   (cursor_pos_x - i, self.rect.y + self.rect.height - 7), 1)
                    pygame.draw.line(screen, (*neon_color, 80), 
                                   (cursor_pos_x + i, self.rect.y + 7), 
                                   (cursor_pos_x + i, self.rect.y + self.rect.height - 7), 1)
                # Основной курсор
                pygame.draw.line(screen, neon_color, 
                               (cursor_pos_x, self.rect.y + 7), 
                               (cursor_pos_x, self.rect.y + self.rect.height - 7), 3)
                pygame.draw.line(screen, (255, 255, 255), 
                               (cursor_pos_x, self.rect.y + 7), 
                               (cursor_pos_x, self.rect.y + self.rect.height - 7), 1)

        self.glow_pulse += 0.08



class Dropdown:
    def __init__(self, rect, options, selected_index, label, callback):
        self.rect = pygame.Rect(rect)
        self.options = options
        self.selected_index = selected_index
        self.label = label
        self.callback = callback
        self.is_open = False
        # Неоновые цвета
        self.neon_base = (150, 100, 255)  # Фиолетовый
        self.neon_hover = (255, 150, 0)  # Оранжевый
        self.neon_selected = (0, 255, 200)  # Бирюзовый
        self.bg_color = (10, 10, 30)
        self.open_height = self.rect.height * len(self.options)
        self.glow_pulse = 0

    def draw(self, screen, font):
        import math

        neon_color = self.neon_hover if self.is_open else self.neon_base
        pulse = abs(math.sin(self.glow_pulse))
        glow_intensity = 0.5 + pulse * 0.5

        # Свечение главной кнопки
        for i in range(6, 0, -1):
            alpha = int(35 * glow_intensity * (1 - i / 6))
            glow_surf = pygame.Surface((self.rect.width + i * 3, self.rect.height + i * 3), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*neon_color, alpha), 
                           pygame.Rect(0, 0, self.rect.width + i * 3, self.rect.height + i * 3), 
                           border_radius=7)
            screen.blit(glow_surf, (self.rect.x - i * 1.5, self.rect.y - i * 1.5))

        # Темный фон
        pygame.draw.rect(screen, self.bg_color, self.rect, border_radius=6)

        # Неоновая окантовка
        for thickness in [2, 1]:
            alpha = 255 if thickness == 1 else 180
            pygame.draw.rect(screen, (*neon_color, alpha), self.rect, thickness, border_radius=6)

        text = f"{self.label}: {self.options[self.selected_index]}"

        # Яркий контрастный текст
        text_shadow = font.render(text, True, (0, 0, 0))
        text_glow = font.render(text, True, neon_color)
        text_surface = font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)

        # Тень
        screen.blit(text_shadow, (text_rect.x + 1, text_rect.y + 1))
        # Свечение
        for offset in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            screen.blit(text_glow, (text_rect.x + offset[0], text_rect.y + offset[1]))
        # Белый текст
        screen.blit(text_surface, text_rect)

        if self.is_open:
            for i, option in enumerate(self.options):
                option_rect = pygame.Rect(
                    self.rect.x,
                    self.rect.y + self.rect.height * (i + 1),
                    self.rect.width,
                    self.rect.height
                )

                # Определяем цвет опции
                if i == self.selected_index:
                    option_neon = self.neon_selected
                else:
                    option_neon = self.neon_base

                # Свечение для каждой опции
                for j in range(4, 0, -1):
                    alpha = int(25 * (1 - j / 4))
                    glow_surf = pygame.Surface((option_rect.width + j * 2, option_rect.height + j * 2), pygame.SRCALPHA)
                    pygame.draw.rect(glow_surf, (*option_neon, alpha), 
                                   pygame.Rect(0, 0, option_rect.width + j * 2, option_rect.height + j * 2), 
                                   border_radius=5)
                    screen.blit(glow_surf, (option_rect.x - j, option_rect.y - j))

                # Фон опции
                pygame.draw.rect(screen, self.bg_color, option_rect, border_radius=4)

                # Окантовка опции
                pygame.draw.rect(screen, (*option_neon, 200), option_rect, 2, border_radius=4)
                pygame.draw.rect(screen, (*option_neon, 100), option_rect, 1, border_radius=4)

                # Яркий контрастный текст опции
                option_shadow = font.render(option, True, (0, 0, 0))
                option_glow = font.render(option, True, option_neon)
                option_text = font.render(option, True, (255, 255, 255))
                option_text_rect = option_text.get_rect(center=option_rect.center)

                # Тень
                screen.blit(option_shadow, (option_text_rect.x + 1, option_text_rect.y + 1))
                # Свечение
                for offset in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    screen.blit(option_glow, (option_text_rect.x + offset[0], option_text_rect.y + offset[1]))
                # Белый текст
                screen.blit(option_text, option_text_rect)

        self.glow_pulse += 0.06

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.is_open = not self.is_open
                return True

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

        if event.type == pygame.MOUSEBUTTONDOWN and self.is_open:
            full_area = self.rect.union(pygame.Rect(self.rect.x, self.rect.y + self.rect.height, self.rect.width, self.open_height))
            if not full_area.collidepoint(event.pos):
                self.is_open = False
                return True
        return False


import threading
from llm_generator import generate_config_with_llm

class UIManager:
    def __init__(self, sim):
        self.sim = sim
        self.elements = []
        self.font = pygame.font.Font(None, 20)
        self.panel_rect = pygame.Rect(0, 0, 0, 0)
        self.last_known_phase = -1
        self.ai_status_message = ""
        self.ai_status_timer = 0
        self.ai_thread = None
        self.ai_thread_result = None
        self.ai_scenario_input = None
        self.info_texts = []
        self.scroll_y = 0
        self.phases_viewport_rect = None
        self.total_phases_height = 0
        self.scrollbar_track_rect = None
        self.scrollbar_thumb_rect = None
        self.is_dragging_scrollbar = False
        self.drag_start_y = 0
        self.drag_start_scroll_y = 0
        self.background_pulse = 0
        self.rebuild_ui_elements()

    def rebuild_ui_elements(self):
        from constants import screen_config
        self.panel_rect = pygame.Rect(screen_config.width - UI_PANEL_WIDTH, 0, UI_PANEL_WIDTH, screen_config.height)

        open_dropdown_rect = None
        for el in self.elements:
            if isinstance(el, Dropdown) and el.is_open and el.rect.y > 200:
                open_dropdown_rect = el.rect
                break

        self.elements.clear()
        self.info_texts.clear()

        y = 20
        self.add_button((screen_config.width - UI_PANEL_WIDTH + 50, y, 200, 40), 'Pause/Resume', self.toggle_pause)
        y += 50

        mode_text = "Режим: " + ("Динамический" if self.sim.controller.mode == 'dynamic' else "Статический")
        self.add_button((screen_config.width - UI_PANEL_WIDTH + 20, y, 260, 30), mode_text, self.toggle_mode)
        y += 40

        self.add_button((screen_config.width - UI_PANEL_WIDTH + 20, y, 125, 30), "Сохранить", self.export_config)
        self.add_button((screen_config.width - UI_PANEL_WIDTH + 155, y, 125, 30), "Сбросить", self.reset_settings)
        y += 40

        self.add_text((screen_config.width - UI_PANEL_WIDTH + 20, y), "Описание AI-сценария:")
        y += 25
        self.ai_scenario_input = self.add_text_input(
            (screen_config.width - UI_PANEL_WIDTH + 20, y, 260, 30),
            "Вечерний час пик, пробка с запада"
        )
        y += 40
        self.add_button((screen_config.width - UI_PANEL_WIDTH + 20, y, 260, 30), "Сгенерировать по описанию", self.trigger_ai_generation_from_input)
        y += 35

        if self.ai_status_message:
            self.add_text((screen_config.width - UI_PANEL_WIDTH + 20, y), self.ai_status_message)
            y += 20


        info_y = y
        if self.sim.controller.mode == 'dynamic':
            self.info_texts.append(self.add_text((screen_config.width - UI_PANEL_WIDTH + 20, info_y), f"Людей: {len(self.sim.pedestrians)}", add_to_list=False))
            info_y += 25
            self.info_texts.append(self.add_text((screen_config.width - UI_PANEL_WIDTH + 20, info_y), f"Ожидают (H/V): {self.sim.waiting_cars_h} / {self.sim.waiting_cars_v}", add_to_list=False))
            info_y += 25
            self.info_texts.append(self.add_text((screen_config.width - UI_PANEL_WIDTH + 20, info_y), f"Видимые (H/V): {self.sim.controller.visible_cars_h} / {self.sim.controller.visible_cars_v}", add_to_list=False))
            info_y += 25
            self.info_texts.append(self.add_text((screen_config.width - UI_PANEL_WIDTH + 20, info_y), f"Давление (H/V): {self.sim.controller.pressure_h:.1f} / {self.sim.controller.pressure_v:.1f}", add_to_list=False))
            info_y += 25
            self.info_texts.append(self.add_text((screen_config.width - UI_PANEL_WIDTH + 20, info_y), f"Штраф (H/V): {self.sim.h_wait_time_sq_sum:.1f} / {self.sim.v_wait_time_sq_sum:.1f}", add_to_list=False))
            y = info_y + 30

            self.add_text((screen_config.width - UI_PANEL_WIDTH + 20, y), f"Фактор: {self.sim.controller.dynamic_logic_factor:.3f}")
            self.add_button((screen_config.width - UI_PANEL_WIDTH + 180, y - 2, 45, 20), "+", lambda: self.change_dynamic_factor(0.001))
            self.add_button((screen_config.width - UI_PANEL_WIDTH + 230, y - 2, 45, 20), "-", lambda: self.change_dynamic_factor(-0.001))
            y += 25

        else:
            self.info_texts.append(self.add_text((screen_config.width - UI_PANEL_WIDTH + 20, info_y), f"Фаза: {self.sim.current_phase}", add_to_list=False))
            info_y += 25
            self.info_texts.append(self.add_text((screen_config.width - UI_PANEL_WIDTH + 20, info_y), f"Время: {self.sim.phase_time:.1f}", add_to_list=False))
            info_y += 25
            self.info_texts.append(self.add_text((screen_config.width - UI_PANEL_WIDTH + 20, info_y), f"Людей: {len(self.sim.pedestrians)}", add_to_list=False))
            info_y += 25
            self.info_texts.append(self.add_text((screen_config.width - UI_PANEL_WIDTH + 20, info_y), f"Ожидают (H/V): {self.sim.waiting_cars_h} / {self.sim.waiting_cars_v}", add_to_list=False))
            info_y += 25
            self.info_texts.append(self.add_text((screen_config.width - UI_PANEL_WIDTH + 20, info_y), f"Штраф (H/V): {self.sim.h_wait_time_sq_sum:.1f} / {self.sim.v_wait_time_sq_sum:.1f}", add_to_list=False))
            y = info_y + 20

        y += 20
        self.add_text((screen_config.width - UI_PANEL_WIDTH + 20, y), "Плотность (машин/10с):")
        y += 25

        dir_map = {'from_north': 'Север', 'from_south': 'Юг', 'from_west': 'Запад', 'from_east': 'Восток'}
        for direction, name in dir_map.items():
            density = self.sim.controller.traffic_density.get(direction, 0)
            self.add_text((screen_config.width - UI_PANEL_WIDTH + 20, y), f"{name}: {density:.1f}")
            self.add_button((screen_config.width - UI_PANEL_WIDTH + 180, y - 2, 45, 20), "+", lambda d=direction: self.change_traffic_density(d, 1.0))
            self.add_button((screen_config.width - UI_PANEL_WIDTH + 230, y - 2, 45, 20), "-", lambda d=direction: self.change_traffic_density(d, -1.0))
            y += 25
        y += 15

        # В динамическом режиме редактор фаз не нужен
        if self.sim.controller.mode == 'static':
            self.add_text((screen_config.width - UI_PANEL_WIDTH + 20, y), "Редактор Фаз:")
            y += 25
            phases_area_start_y = y

            add_phase_button_h = 40
            self.phases_viewport_rect = pygame.Rect(screen_config.width - UI_PANEL_WIDTH, phases_area_start_y, UI_PANEL_WIDTH, screen_config.height - phases_area_start_y - add_phase_button_h - 15)

            colors_eng = ["green", "yellow", "red"]
            y_content_offset = 0
            for i, phase in enumerate(self.sim.controller.phases):
                block_y = phases_area_start_y + y_content_offset - self.scroll_y

                if i == self.sim.controller.current_phase:
                    highlight_rect = pygame.Rect(screen_config.width - UI_PANEL_WIDTH + 10, block_y - 5, UI_PANEL_WIDTH - 20, 48)
                    self.elements.append({'type': 'rect', 'rect': highlight_rect, 'color': (90, 90, 70)})

                self.add_text((screen_config.width - UI_PANEL_WIDTH + 20, block_y), f"Длительность: {phase['duration']}s")
                self.add_button((screen_config.width - UI_PANEL_WIDTH + 150, block_y - 2, 25, 20), "+5", lambda index=i: self.change_phase_duration(index, 5))
                self.add_button((screen_config.width - UI_PANEL_WIDTH + 180, block_y - 2, 25, 20), "-5", lambda index=i: self.change_phase_duration(index, -5))

                h_color_idx = colors_eng.index(phase['horiz'])
                dd_h = self.add_dropdown((screen_config.width - UI_PANEL_WIDTH + 20, block_y + 18, 85, 25), colors_eng, h_color_idx, "Horiz", lambda color, index=i: self.update_phase_color(index, 'horiz', color))
                v_color_idx = colors_eng.index(phase['vert'])
                dd_v = self.add_dropdown((screen_config.width - UI_PANEL_WIDTH + 110, block_y + 18, 85, 25), colors_eng, v_color_idx, "Vert", lambda color, index=i: self.update_phase_color(index, 'vert', color))

                self.add_button((screen_config.width - UI_PANEL_WIDTH + 210, block_y - 2, 30, 22), "↑", lambda index=i: self.move_phase(index, -1))
                self.add_button((screen_config.width - UI_PANEL_WIDTH + 245, block_y - 2, 30, 22), "↓", lambda index=i: self.move_phase(index, 1))
                self.add_button((screen_config.width - UI_PANEL_WIDTH + 210, block_y + 21, 65, 22), "X", lambda index=i: self.delete_phase(index))

                y_content_offset += 50
                if open_dropdown_rect and open_dropdown_rect == dd_h.rect:
                    dd_h.is_open = True
                    y_content_offset += dd_h.open_height
                if open_dropdown_rect and open_dropdown_rect == dd_v.rect:
                    dd_v.is_open = True
                    y_content_offset += dd_v.open_height

            self.total_phases_height = y_content_offset
            max_scroll = max(0, self.total_phases_height - self.phases_viewport_rect.height)
            self.scroll_y = max(0, min(self.scroll_y, max_scroll))

            self.add_button((screen_config.width - UI_PANEL_WIDTH + 50, self.phases_viewport_rect.bottom + 10, 200, 30), "Добавить", self.add_new_phase)
        else:
            self.phases_viewport_rect = None
            self.total_phases_height = 0
            self.scroll_y = 0

    def add_button(self, rect, text, callback):
        button = Button(rect, text, callback)
        self.elements.append(button)
        return button

    def add_dropdown(self, rect, options, selected_index, label, callback):
        dropdown = Dropdown(rect, options, selected_index, label, callback)
        self.elements.append(dropdown)
        return dropdown

    def add_text_input(self, rect, initial_text=""):
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

        # Неоновый пульсирующий фон панели
        self.background_pulse += 0.03
        pulse = abs(math.sin(self.background_pulse))

        # Темный фон с градиентом
        bg_surf = pygame.Surface((self.panel_rect.width, self.panel_rect.height), pygame.SRCALPHA)
        for y in range(self.panel_rect.height):
            alpha = int(200 + 30 * pulse * (1 - y / self.panel_rect.height))
            color_val = int(15 + 10 * pulse)
            pygame.draw.line(bg_surf, (color_val, color_val, color_val + 20, alpha), 
                           (0, y), (self.panel_rect.width, y))
        screen.blit(bg_surf, self.panel_rect.topleft)

        # Неоновая окантовка панели
        neon_border = (0, 200, 255)
        for i in range(3, 0, -1):
            alpha = int(100 + 100 * pulse) if i == 1 else 80
            pygame.draw.rect(screen, (*neon_border, alpha), self.panel_rect, i)

        # --- Element Segregation ---
        non_scrollable_elements = []
        scrollable_elements = []
        if self.phases_viewport_rect:
            for el in self.elements:
                y = -1
                if hasattr(el, 'rect'):  # Button, Dropdown
                    y = el.rect.y
                elif isinstance(el, dict):
                    if 'pos' in el:  # text dict
                        y = el['pos'][1]
                    elif 'rect' in el:  # rect dict
                        y = el['rect'].y

                if y != -1 and y >= self.phases_viewport_rect.top:
                    scrollable_elements.append(el)
                else:
                    non_scrollable_elements.append(el)
        else:
            non_scrollable_elements = self.elements

        # --- Drawing Logic ---
        original_clip = screen.get_clip()

        # 1. Draw non-scrollable elements
        for element in non_scrollable_elements:
            if hasattr(element, 'draw'):
                element.draw(screen, self.font)
            elif isinstance(element, dict) and element.get('type') == 'text':
                # Яркий контрастный текст
                neon_text_color = (0, 220, 255)
                text_shadow = self.font.render(element['text'], True, (0, 0, 0))
                text_glow = self.font.render(element['text'], True, neon_text_color)
                text_surface = self.font.render(element['text'], True, (255, 255, 255))

                # Тень для глубины
                screen.blit(text_shadow, (element['pos'][0] + 1, element['pos'][1] + 1))
                # Яркое неоновое свечение
                for offset in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1)]:
                    screen.blit(text_glow, (element['pos'][0] + offset[0], element['pos'][1] + offset[1]))
                # Белый текст сверху
                screen.blit(text_surface, element['pos'])

        # 2. Draw scrollable elements with clipping
        if self.phases_viewport_rect:
            screen.set_clip(self.phases_viewport_rect)

            # Draw highlight rects first (background) с неоновым эффектом
            for element in scrollable_elements:
                 if isinstance(element, dict) and element.get('type') == 'rect':
                    import math
                    # Неоновая подсветка текущей фазы
                    pulse = abs(math.sin(self.background_pulse * 2))
                    neon_highlight = (100, 200, 255)

                    # Свечение
                    for i in range(6, 0, -1):
                        alpha = int(30 * pulse * (1 - i / 6))
                        glow_rect = element['rect'].inflate(i * 2, i * 2)
                        glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
                        pygame.draw.rect(glow_surf, (*neon_highlight, alpha), 
                                       pygame.Rect(0, 0, glow_rect.width, glow_rect.height), 
                                       border_radius=6)
                        screen.blit(glow_surf, glow_rect.topleft)

                    # Темный фон с неоновой окантовкой
                    pygame.draw.rect(screen, (20, 20, 40), element['rect'], border_radius=4)
                    pygame.draw.rect(screen, (*neon_highlight, int(150 + 100 * pulse)), element['rect'], 2, border_radius=4)

            # Draw other scrollable elements on top
            for element in scrollable_elements:
                if isinstance(element, (Button, Dropdown)):
                    element.draw(screen, self.font)
                elif isinstance(element, dict) and element.get('type') == 'text':
                    # Яркий контрастный текст
                    neon_text_color = (0, 220, 255)
                    text_shadow = self.font.render(element['text'], True, (0, 0, 0))
                    text_glow = self.font.render(element['text'], True, neon_text_color)
                    text_surface = self.font.render(element['text'], True, (255, 255, 255))

                    # Тень для глубины
                    screen.blit(text_shadow, (element['pos'][0] + 1, element['pos'][1] + 1))
                    # Яркое неоновое свечение
                    for offset in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1)]:
                        screen.blit(text_glow, (element['pos'][0] + offset[0], element['pos'][1] + offset[1]))
                    # Белый текст сверху
                    screen.blit(text_surface, element['pos'])

            screen.set_clip(original_clip)

        # 3. Draw panel border and scrollbar on top (уже не нужна белая граница, есть неоновая)

        if self.phases_viewport_rect and self.total_phases_height > self.phases_viewport_rect.height:
            import math
            pulse = abs(math.sin(self.background_pulse))

            self.scrollbar_track_rect = pygame.Rect(self.phases_viewport_rect.right - 12, self.phases_viewport_rect.top, 10, self.phases_viewport_rect.height)
            # Темный трек с неоновой окантовкой
            pygame.draw.rect(screen, (15, 15, 30), self.scrollbar_track_rect, border_radius=5)
            pygame.draw.rect(screen, (0, 150, 200, 100), self.scrollbar_track_rect, 1, border_radius=5)

            viewable_ratio = self.phases_viewport_rect.height / self.total_phases_height
            thumb_h = max(20, self.phases_viewport_rect.height * viewable_ratio)

            scrollable_dist = self.total_phases_height - self.phases_viewport_rect.height
            scroll_ratio = self.scroll_y / max(1, scrollable_dist)

            thumb_y = self.scrollbar_track_rect.top + scroll_ratio * (self.scrollbar_track_rect.height - thumb_h)

            self.scrollbar_thumb_rect = pygame.Rect(self.scrollbar_track_rect.x + 1, thumb_y, 8, thumb_h)

            # Неоновый ползунок с свечением
            neon_scrollbar = (0, 255, 200)
            for i in range(3, 0, -1):
                alpha = int(60 * (1 - i / 3))
                glow_rect = self.scrollbar_thumb_rect.inflate(i * 2, 0)
                glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (*neon_scrollbar, alpha), 
                               pygame.Rect(0, 0, glow_rect.width, glow_rect.height), 
                               border_radius=5)
                screen.blit(glow_surf, glow_rect.topleft)

            pygame.draw.rect(screen, neon_scrollbar, self.scrollbar_thumb_rect, border_radius=4)
            pygame.draw.rect(screen, (150, 255, 255), self.scrollbar_thumb_rect, 1, border_radius=4)

    def handle_events(self, event):
        if self.panel_rect.collidepoint(pygame.mouse.get_pos()):
            if event.type == pygame.MOUSEWHEEL:
                self.scroll_y -= event.y * 20
                self.rebuild_ui_elements()
                return True
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.scrollbar_thumb_rect and self.scrollbar_thumb_rect.collidepoint(event.pos):
                    self.is_dragging_scrollbar = True
                    self.drag_start_y = event.pos[1]
                    self.drag_start_scroll_y = self.scroll_y
                    return True
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.is_dragging_scrollbar = False
            if event.type == pygame.MOUSEMOTION and self.is_dragging_scrollbar:
                dy = event.pos[1] - self.drag_start_y
                scroll_delta = dy * (self.total_phases_height / self.phases_viewport_rect.height)
                self.scroll_y = self.drag_start_scroll_y + scroll_delta
                self.rebuild_ui_elements()
                return True

        if event.type == pygame.MOUSEMOTION:
            for element in self.elements:
                if isinstance(element, Button): element.check_hover(event.pos)

        # Открытый дропдаун получает приоритет
        active_dropdown = next((el for el in self.elements if isinstance(el, Dropdown) and el.is_open), None)
        if active_dropdown:
            if active_dropdown.handle_event(event):
                self.rebuild_ui_elements()
                return True

        # Активное текстовое поле получает события клавиатуры
        active_input = next((el for el in self.elements if isinstance(el, TextInput) and el.active), None)
        if active_input and event.type == pygame.KEYDOWN:
            if active_input.handle_event(event):
                return True

        # Общая обработка для всех остальных элементов (в основном, клики)
        for element in self.elements:
            if element != active_dropdown:  # Не обрабатывать снова
                if hasattr(element, 'handle_event'):
                    if element.handle_event(event):
                        if isinstance(element, Dropdown): self.rebuild_ui_elements()
                        return True
        return False

    def change_dynamic_factor(self, delta):
        new_factor = self.sim.controller.dynamic_logic_factor + delta
        self.sim.controller.dynamic_logic_factor = round(max(0.9, min(0.999, new_factor)), 3)
        self.rebuild_ui_elements()

    def change_traffic_density(self, direction, delta):
        """Изменяет плотность трафика (машин/10 сек) для заданного направления."""
        current_density = self.sim.controller.traffic_density[direction]
        new_density = max(0.0, current_density + delta) # Плотность может быть 0
        self.sim.controller.traffic_density[direction] = round(new_density, 1)
        self.rebuild_ui_elements()

    def toggle_pause(self): self.sim.toggle_pause()
    def update_phase_color(self, i, d, c): self.sim.controller.update_phase_color(i, d, c); self.rebuild_ui_elements()
    def change_phase_duration(self, i, d): self.sim.controller.change_phase_duration(i, d); self.rebuild_ui_elements()
    def move_phase(self, i, d): self.sim.controller.move_phase(i, d); self.rebuild_ui_elements()
    def delete_phase(self, i): self.sim.controller.remove_phase(i); self.rebuild_ui_elements()
    def add_new_phase(self): self.sim.controller.add_phase(); self.rebuild_ui_elements()
    def toggle_mode(self): self.sim.controller.set_mode('static' if self.sim.controller.mode == 'dynamic' else 'dynamic'); self.rebuild_ui_elements()
    def refresh_window(self): self.sim.update_screen_size(); self.rebuild_ui_elements()

    def reset_settings(self):
        """Resets traffic controller to default settings."""
        self.sim.controller.reset_to_defaults()
        self.rebuild_ui_elements()

    def update(self, dt):
        # Обновляем только те элементы, у которых есть метод update (например, TextInput)
        if self.ai_scenario_input:
            self.ai_scenario_input.update(dt)

        # --- Обработка результата AI-генерации ---
        if self.ai_thread and not self.ai_thread.is_alive():
            if isinstance(self.ai_thread_result, dict):
                self.sim.controller.import_config_dict(self.ai_thread_result)
                self.ai_status_message = "Успешно сгенерировано!"
            else: # Это исключение
                error_message = str(self.ai_thread_result)
                self.ai_status_message = f"Ошибка: {error_message[:40]}..."
                print(f"Ошибка генерации AI-сценария: {error_message}")

            self.ai_thread = None # Сбрасываем поток
            self.ai_thread_result = None
            self.ai_status_timer = 5.0 # Показываем сообщение 5 секунд
            self.rebuild_ui_elements()

        # --- Таймер для статус-сообщения ---
        if self.ai_status_timer > 0:
            self.ai_status_timer -= dt
            if self.ai_status_timer <= 0:
                self.ai_status_message = ""
                self.rebuild_ui_elements()

        # --- Обновление информационных текстов ---
        if self.sim.controller.mode == 'dynamic':
            self.info_texts[0]['text'] = f"Людей: {len(self.sim.pedestrians)}"
            self.info_texts[1]['text'] = f"Ожидают (H/V): {self.sim.waiting_cars_h} / {self.sim.waiting_cars_v}"
            self.info_texts[2]['text'] = f"Видимые (H/V): {self.sim.controller.visible_cars_h} / {self.sim.controller.visible_cars_v}"
            self.info_texts[3]['text'] = f"Давление (H/V): {self.sim.controller.pressure_h:.1f} / {self.sim.controller.pressure_v:.1f}"
            self.info_texts[4]['text'] = f"Штраф (H/V): {self.sim.controller.weighted_h_penalty:.0f} / {self.sim.controller.weighted_v_penalty:.0f}"
        else:  # static
            phase_duration = self.sim.controller.phases[self.sim.current_phase]['duration']
            self.info_texts[0]['text'] = f"Текущая фаза: {self.sim.current_phase}"
            self.info_texts[1]['text'] = f"Время: {self.sim.phase_time:.1f} / {phase_duration}"
            self.info_texts[2]['text'] = f"Людей: {len(self.sim.pedestrians)}"
            self.info_texts[3]['text'] = f"Ожидают (H/V): {self.sim.waiting_cars_h} / {self.sim.waiting_cars_v}"
            self.info_texts[4]['text'] = f"Штраф (H/V): {self.sim.h_wait_time_sq_sum:.1f} / {self.sim.v_wait_time_sq_sum:.1f}"

        if self.sim.controller.current_phase != self.last_known_phase:
            self.last_known_phase = self.sim.controller.current_phase
            self.rebuild_ui_elements()

    def trigger_ai_generation_from_input(self):
        if self.ai_scenario_input:
            scenario_text = self.ai_scenario_input.get_text()
            if scenario_text:
                self.generate_ai_config(scenario_text)

    def _ai_worker(self, scenario: str):
        """Worker-функция для вызова LLM в фоновом потоке."""
        try:
            new_config = generate_config_with_llm(scenario)
            self.ai_thread_result = new_config
        except (ConnectionError, ValueError, Exception) as e:
            self.ai_thread_result = e

    def generate_ai_config(self, scenario: str):
        """Запускает фоновый процесс для генерации AI-сценария."""
        if self.ai_thread and self.ai_thread.is_alive():
            return  # Уже в процессе

        self.ai_status_message = "⟳ Генерация..."
        self.ai_status_timer = 0  # Чтобы сообщение "Генерация..." не исчезло по таймеру
        self.ai_thread_result = None
        self.rebuild_ui_elements()
        pygame.display.flip()  # Немедленно показать "Генерация..."

        self.ai_thread = threading.Thread(target=self._ai_worker, args=(scenario,))
        self.ai_thread.start()


    # Add import/export from previous patch if missing
    def export_config(self):
        import json
        data = self.sim.controller.export_config_dict()
        try:
            with open("traffic_config.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка: {e}")

    def import_config(self):
        import json, os
        if not os.path.exists("traffic_config.json"): return
        try:
            with open("traffic_config.json", "r", encoding="utf-8") as f:
                self.sim.controller.import_config_dict(json.load(f))
            self.rebuild_ui_elements()
        except Exception as e:
            print(f"Ошибка: {e}")