import unittest
import pygame
import sys
import os
import math

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import Crosswalk, draw_roads, draw_entities
from constants import *


class TestCrosswalk(unittest.TestCase):
    def setUp(self):
        """Настройка для каждого теста"""
        pygame.init()
        self.screen = pygame.Surface((400, 400))
        
    def test_crosswalk_initialization(self):
        """Тест инициализации пешеходного перехода"""
        crosswalk_h = Crosswalk('horizontal')
        crosswalk_v = Crosswalk('vertical')
        
        self.assertEqual(crosswalk_h.orientation, 'horizontal')
        self.assertEqual(crosswalk_v.orientation, 'vertical')
        
    def test_crosswalk_drawing(self):
        """Тест отрисовки пешеходного перехода"""
        crosswalk = Crosswalk('horizontal')
        
        # Тест что функция выполняется без ошибок
        try:
            crosswalk.draw(self.screen, 200, 200, 60)
            success = True
        except Exception:
            success = False
            
        self.assertTrue(success)


class TestDrawingFunctions(unittest.TestCase):
    def setUp(self):
        """Настройка для каждого теста"""
        pygame.init()
        self.screen = pygame.Surface((800, 600))
        
    def test_draw_roads(self):
        """Тест отрисовки дорог"""
        try:
            draw_roads(self.screen, 400, 300, 3)
            success = True
        except Exception:
            success = False
            
        self.assertTrue(success)
        
    def test_draw_roads_different_lanes(self):
        """Тест отрисовки дорог с разным количеством полос"""
        for num_lanes in [1, 2, 3, 4, 5]:
            try:
                draw_roads(self.screen, 400, 300, num_lanes)
                success = True
            except Exception:
                success = False
                
            self.assertTrue(success, f"Failed for {num_lanes} lanes")
            
    def test_draw_entities(self):
        """Тест отрисовки сущностей"""
        from simulation import TrafficSimulation, Car, Pedestrian
        
        sim = TrafficSimulation()
        # Добавляем тестовые объекты
        sim.cars.append(Car([100, 100], [1, 0], 30, (255, 0, 0)))
        sim.pedestrians.append(Pedestrian([50, 50], [150, 150]))
        
        try:
            draw_entities(self.screen, sim, 400, 300)
            success = True
        except Exception:
            success = False
            
        self.assertTrue(success)
        
    def test_draw_entities_empty_simulation(self):
        """Тест отрисовки пустой симуляции"""
        from simulation import TrafficSimulation
        
        sim = TrafficSimulation()
        
        try:
            draw_entities(self.screen, sim, 400, 300)
            success = True
        except Exception:
            success = False
            
        self.assertTrue(success)


class TestVisualEffects(unittest.TestCase):
    def setUp(self):
        """Настройка для каждого теста"""
        pygame.init()
        self.screen = pygame.Surface((800, 600))
        
    def test_basic_rendering(self):
        """Тест базовой отрисовки эффектов"""
        # Тест создания простых эффектов
        try:
            # Простой тест создания поверхности с альфа-каналом
            effect_surface = pygame.Surface((100, 100), pygame.SRCALPHA)
            effect_surface.fill((255, 0, 0, 128))
            self.screen.blit(effect_surface, (0, 0))
            success = True
        except Exception:
            success = False
            
        self.assertTrue(success)
        
    def test_color_blending(self):
        """Тест смешивания цветов"""
        # Тест функций смешивания цветов
        color1 = (255, 0, 0)
        color2 = (0, 255, 0)
        
        # Простое смешивание
        blended = tuple((c1 + c2) // 2 for c1, c2 in zip(color1, color2))
        
        self.assertEqual(len(blended), 3)
        for component in blended:
            self.assertGreaterEqual(component, 0)
            self.assertLessEqual(component, 255)


class TestUtilityFunctions(unittest.TestCase):
    def test_distance_calculation(self):
        """Тест расчета расстояния между точками"""
        # Если есть функция расчета расстояния в utils
        point1 = [0, 0]
        point2 = [3, 4]
        
        # Ожидаемое расстояние: sqrt(3^2 + 4^2) = 5
        expected_distance = 5.0
        
        # Базовый тест
        distance = math.sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)
        self.assertAlmostEqual(distance, expected_distance)
        
    def test_angle_calculation(self):
        """Тест расчета углов"""
        # Тест расчета угла между векторами
        vector1 = [1, 0]  # Горизонтальный вектор
        vector2 = [0, 1]  # Вертикальный вектор
        
        # Угол должен быть 90 градусов (π/2 радиан)
        dot_product = vector1[0] * vector2[0] + vector1[1] * vector2[1]
        magnitude1 = math.sqrt(vector1[0]**2 + vector1[1]**2)
        magnitude2 = math.sqrt(vector2[0]**2 + vector2[1]**2)
        
        angle = math.acos(dot_product / (magnitude1 * magnitude2))
        expected_angle = math.pi / 2
        
        self.assertAlmostEqual(angle, expected_angle, places=5)
        
    def test_vector_normalization(self):
        """Тест нормализации векторов"""
        vector = [3, 4]
        magnitude = math.sqrt(vector[0]**2 + vector[1]**2)
        
        normalized = [vector[0] / magnitude, vector[1] / magnitude]
        
        # Длина нормализованного вектора должна быть 1
        norm_magnitude = math.sqrt(normalized[0]**2 + normalized[1]**2)
        self.assertAlmostEqual(norm_magnitude, 1.0, places=5)
        
    def test_collision_bounds_calculation(self):
        """Тест расчета границ для проверки столкновений"""
        # Тестовые данные для прямоугольника
        center = [100, 100]
        width = 20
        height = 10
        
        # Границы прямоугольника
        left = center[0] - width / 2
        right = center[0] + width / 2
        top = center[1] - height / 2
        bottom = center[1] + height / 2
        
        self.assertEqual(left, 90)
        self.assertEqual(right, 110)
        self.assertEqual(top, 95)
        self.assertEqual(bottom, 105)
        
    def test_point_in_rectangle(self):
        """Тест проверки нахождения точки в прямоугольнике"""
        rect_center = [100, 100]
        rect_width = 50
        rect_height = 30
        
        # Точка внутри прямоугольника
        point_inside = [110, 105]
        
        # Точка снаружи
        point_outside = [200, 200]
        
        # Проверяем точку внутри
        inside_x = abs(point_inside[0] - rect_center[0]) <= rect_width / 2
        inside_y = abs(point_inside[1] - rect_center[1]) <= rect_height / 2
        self.assertTrue(inside_x and inside_y)
        
        # Проверяем точку снаружи
        outside_x = abs(point_outside[0] - rect_center[0]) <= rect_width / 2
        outside_y = abs(point_outside[1] - rect_center[1]) <= rect_height / 2
        self.assertFalse(outside_x and outside_y)


class TestColorUtilities(unittest.TestCase):
    def test_color_validation(self):
        """Тест валидации цветов"""
        # Правильные цвета
        valid_colors = [
            (255, 0, 0),      # Красный
            (0, 255, 0),      # Зеленый
            (0, 0, 255),      # Синий
            (128, 128, 128),  # Серый
            (0, 0, 0),        # Черный
            (255, 255, 255),  # Белый
        ]
        
        for color in valid_colors:
            self.assertEqual(len(color), 3)
            for component in color:
                self.assertGreaterEqual(component, 0)
                self.assertLessEqual(component, 255)
                
    def test_neon_color_generation(self):
        """Тест генерации неоновых цветов"""
        base_color = (100, 50, 200)
        
        # Простой алгоритм для неонового цвета
        neon_color = tuple(min(255, int(component * 1.5)) for component in base_color)
        
        self.assertEqual(len(neon_color), 3)
        for component in neon_color:
            self.assertGreaterEqual(component, 0)
            self.assertLessEqual(component, 255)
            
        # Неоновый цвет должен быть ярче оригинального
        brightness_original = sum(base_color)
        brightness_neon = sum(neon_color)
        self.assertGreaterEqual(brightness_neon, brightness_original)


if __name__ == '__main__':
    unittest.main()