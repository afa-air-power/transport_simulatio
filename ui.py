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
        self.open_height = self.rect.height * len(self.options)

    def draw(self, screen, font):
        color = self.hover_color if self.is_open else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=6)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2, border_radius=6)

        text = f"{self.label}: {self.options[self.selected_index]}"
        text_surface = font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

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


class UIManager:
    def __init__(self, sim):
        self.sim = sim
        self.elements = []
        self.font = pygame.font.Font(None, 20)
        self.panel_rect = pygame.Rect(0, 0, 0, 0)
        self.last_known_phase = -1
        self.info_texts = []
        self.scroll_y = 0
        self.phases_viewport_rect = None
        self.total_phases_height = 0
        self.scrollbar_track_rect = None
        self.scrollbar_thumb_rect = None
        self.is_dragging_scrollbar = False
        self.drag_start_y = 0
        self.drag_start_scroll_y = 0
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
        self.add_button((screen_config.width - UI_PANEL_WIDTH + 20, y, 260, 30), "Обновить окно", self.refresh_window)
        y += 40
        mode_text = "Режим: " + ("Динамический" if self.sim.controller.mode == 'dynamic' else "Статический")
        self.add_button((screen_config.width - UI_PANEL_WIDTH + 20, y, 260, 30), mode_text, self.toggle_mode)
        y += 40

        # Manually add import/export buttons here from previous patch if they are missing
        self.add_button((screen_config.width - UI_PANEL_WIDTH + 20, y, 125, 30), "Импорт JSON", self.import_config)
        self.add_button((screen_config.width - UI_PANEL_WIDTH + 155, y, 125, 30), "Экспорт JSON", self.export_config)
        y += 40

        self.add_text((screen_config.width - UI_PANEL_WIDTH + 20, y), "Ручное управление (горизонт.):")
        y += 25
        self.add_dropdown((screen_config.width - UI_PANEL_WIDTH + 20, y, 260, 30), ["Красный", "Желтый", "Зеленый"], 0, "Цвет", self.set_traffic_color)
        y += 40

        info_y = y
        self.info_texts.append(self.add_text((screen_config.width - UI_PANEL_WIDTH + 20, info_y), f"Текущая фаза: {self.sim.current_phase}"))
        info_y += 25
        self.info_texts.append(self.add_text((screen_config.width - UI_PANEL_WIDTH + 20, info_y), f"Время: {self.sim.phase_time:.1f}"))
        info_y += 25
        self.info_texts.append(self.add_text((screen_config.width - UI_PANEL_WIDTH + 20, info_y), f"Людей: {len(self.sim.pedestrians)}"))
        y = info_y + 40

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

        self.add_button((screen_config.width - UI_PANEL_WIDTH + 50, self.phases_viewport_rect.bottom + 10, 200, 30), "Добавить фазу", self.add_new_phase)

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
            if isinstance(element, (Button, Dropdown)):
                element.draw(screen, self.font)
            elif isinstance(element, dict) and element.get('type') == 'text':
                screen.blit(self.font.render(element['text'], True, (255, 255, 255)), element['pos'])

        # 2. Draw scrollable elements with clipping
        if self.phases_viewport_rect:
            screen.set_clip(self.phases_viewport_rect)

            # Draw highlight rects first (background)
            for element in scrollable_elements:
                 if isinstance(element, dict) and element.get('type') == 'rect':
                    pygame.draw.rect(screen, element['color'], element['rect'], border_radius=4)

            # Draw other scrollable elements on top
            for element in scrollable_elements:
                if isinstance(element, (Button, Dropdown)):
                    element.draw(screen, self.font)
                elif isinstance(element, dict) and element.get('type') == 'text':
                    screen.blit(self.font.render(element['text'], True, (255, 255, 255)), element['pos'])

            screen.set_clip(original_clip)

        # 3. Draw panel border and scrollbar on top
        pygame.draw.rect(screen, (255, 255, 255), self.panel_rect, 2)

        if self.phases_viewport_rect and self.total_phases_height > self.phases_viewport_rect.height:
            self.scrollbar_track_rect = pygame.Rect(self.phases_viewport_rect.right - 12, self.phases_viewport_rect.top, 10, self.phases_viewport_rect.height)
            pygame.draw.rect(screen, (40, 40, 40), self.scrollbar_track_rect, border_radius=5)

            viewable_ratio = self.phases_viewport_rect.height / self.total_phases_height
            thumb_h = max(20, self.phases_viewport_rect.height * viewable_ratio)

            scrollable_dist = self.total_phases_height - self.phases_viewport_rect.height
            scroll_ratio = self.scroll_y / max(1, scrollable_dist)

            thumb_y = self.scrollbar_track_rect.top + scroll_ratio * (self.scrollbar_track_rect.height - thumb_h)

            self.scrollbar_thumb_rect = pygame.Rect(self.scrollbar_track_rect.x + 1, thumb_y, 8, thumb_h)
            pygame.draw.rect(screen, (150, 150, 150), self.scrollbar_thumb_rect, border_radius=4)

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

        active_dropdown = next((el for el in self.elements if isinstance(el, Dropdown) and el.is_open), None)
        if active_dropdown:
            if active_dropdown.handle_event(event):
                self.rebuild_ui_elements()
                return True

        for element in self.elements:
            if element != active_dropdown and isinstance(element, (Button, Dropdown)):
                if element.handle_event(event):
                    if isinstance(element, Dropdown): self.rebuild_ui_elements()
                    return True
        return False

    def toggle_pause(self): self.sim.toggle_pause()
    def set_traffic_color(self, color): self.sim.set_traffic_color({"Красный": "red", "Желтый": "yellow", "Зеленый": "green"}[color])
    def update_phase_color(self, i, d, c): self.sim.controller.update_phase_color(i, d, c); self.rebuild_ui_elements()
    def change_phase_duration(self, i, d): self.sim.controller.change_phase_duration(i, d); self.rebuild_ui_elements()
    def move_phase(self, i, d): self.sim.controller.move_phase(i, d); self.rebuild_ui_elements()
    def delete_phase(self, i): self.sim.controller.remove_phase(i); self.rebuild_ui_elements()
    def add_new_phase(self): self.sim.controller.add_phase(); self.rebuild_ui_elements()
    def toggle_mode(self): self.sim.controller.set_mode('static' if self.sim.controller.mode == 'dynamic' else 'dynamic'); self.rebuild_ui_elements()
    def refresh_window(self): self.sim.update_screen_size(); self.rebuild_ui_elements()

    def update(self):
        self.info_texts[0]['text'] = f"Текущая фаза: {self.sim.current_phase}"
        self.info_texts[1]['text'] = f"Время: {self.sim.phase_time:.1f} / {self.sim.controller.phases[self.sim.current_phase]['duration']}"
        self.info_texts[2]['text'] = f"Людей: {len(self.sim.pedestrians)}"
        if self.sim.controller.current_phase != self.last_known_phase:
            self.last_known_phase = self.sim.controller.current_phase
            self.rebuild_ui_elements()

    # Add import/export from previous patch if missing
    def export_config(self):
        import json
        data = self.sim.controller.export_config_dict()
        try:
            with open("traffic_config.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка экспорта: {e}")

    def import_config(self):
        import json, os
        if not os.path.exists("traffic_config.json"): return
        try:
            with open("traffic_config.json", "r", encoding="utf-8") as f:
                self.sim.controller.import_config_dict(json.load(f))
            self.rebuild_ui_elements()
        except Exception as e:
            print(f"Ошибка импорта: {e}")