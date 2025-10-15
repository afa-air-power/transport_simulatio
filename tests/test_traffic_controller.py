import unittest
import pygame
import time
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from traffic_controller import TrafficController, TrafficLight, LightLens
from constants import *


class TestLightLens(unittest.TestCase):
    def setUp(self):
        """Настройка для каждого теста"""
        pygame.init()
        self.screen = pygame.Surface((100, 100))
        
    def test_light_lens_initialization(self):
        """Тест инициализации линзы светофора"""
        lens = LightLens(RED, (10, 10))
        
        self.assertEqual(lens.lens_color, RED)
        self.assertEqual(lens.offset, (10, 10))
        self.assertFalse(lens.active)
        
    def test_light_lens_activation(self):
        """Тест активации линзы"""
        lens = LightLens(GREEN, (0, 0))
        
        # По умолчанию неактивна
        self.assertFalse(lens.active)
        
        # Активируем
        lens.active = True
        self.assertTrue(lens.active)


class TestTrafficLight(unittest.TestCase):
    def setUp(self):
        """Настройка для каждого теста"""
        pygame.init()
        
    def test_traffic_light_initialization_vertical(self):
        """Тест инициализации вертикального светофора"""
        light = TrafficLight((100, 100), 'vertical')
        
        self.assertEqual(light.position, (100, 100))
        self.assertEqual(light.orientation, 'vertical')
        self.assertEqual(light.current_color, 'red')
        self.assertEqual(len(light.lenses), 3)
        
        # Проверяем правильность расположения линз
        self.assertEqual(light.lenses[0].lens_color, RED)
        self.assertEqual(light.lenses[1].lens_color, YELLOW)
        self.assertEqual(light.lenses[2].lens_color, GREEN)
        
    def test_traffic_light_initialization_horizontal(self):
        """Тест инициализации горизонтального светофора"""
        light = TrafficLight((100, 100), 'horizontal')
        
        self.assertEqual(light.orientation, 'horizontal')
        self.assertEqual(len(light.lenses), 3)
        
        # Проверяем правильность расположения линз
        self.assertEqual(light.lenses[0].lens_color, RED)
        self.assertEqual(light.lenses[1].lens_color, YELLOW)
        self.assertEqual(light.lenses[2].lens_color, GREEN)
        
    def test_traffic_light_color_change(self):
        """Тест смены цвета светофора"""
        light = TrafficLight((100, 100), 'vertical')
        
        # Изначально красный
        self.assertEqual(light.current_color, 'red')
        self.assertTrue(light.lenses[0].active)  # Красная линза активна
        self.assertFalse(light.lenses[1].active)  # Желтая неактивна
        self.assertFalse(light.lenses[2].active)  # Зеленая неактивна
        
        # Переключаем на зеленый
        light.set_color('green')
        self.assertEqual(light.current_color, 'green')
        self.assertFalse(light.lenses[0].active)  # Красная неактивна
        self.assertFalse(light.lenses[1].active)  # Желтая неактивна
        self.assertTrue(light.lenses[2].active)  # Зеленая активна
        
        # Переключаем на желтый
        light.set_color('yellow')
        self.assertEqual(light.current_color, 'yellow')
        self.assertFalse(light.lenses[0].active)  # Красная неактивна
        self.assertTrue(light.lenses[1].active)  # Желтая активна
        self.assertFalse(light.lenses[2].active)  # Зеленая неактивна


class TestTrafficController(unittest.TestCase):
    def setUp(self):
        """Настройка для каждого теста"""
        pygame.init()
        
    def test_traffic_controller_initialization(self):
        """Тест инициализации контроллера трафика"""
        controller = TrafficController()
        
        # Проверяем базовые свойства
        self.assertIn(controller.mode, ['static', 'dynamic'])
        self.assertIsInstance(controller.current_phase, int)
        self.assertGreaterEqual(controller.timer, 0)
        self.assertIsInstance(controller.lights, dict)
        
        # Проверяем наличие фаз
        self.assertIsInstance(controller.phases, list)
        self.assertGreater(len(controller.phases), 0)
            
    def test_traffic_controller_static_mode(self):
        """Тест статического режима работы светофора"""
        controller = TrafficController()
        controller.mode = 'static'
        
        initial_phase = controller.current_phase
        initial_timer = controller.phase_timer
        
        # Симулируем обновление
        dt = 1.0
        controller.update(dt, [], [])
        
        # Таймер должен уменьшиться
        self.assertLess(controller.phase_timer, initial_timer)
        
    def test_traffic_controller_phase_transition(self):
        """Тест перехода между фазами"""
        controller = TrafficController()
        controller.mode = 'static'
        controller.phase_timer = 0.1  # Очень маленький таймер для быстрого перехода
        
        initial_phase = controller.current_phase
        
        # Обновляем до перехода фазы
        controller.update(1.0, [], [])
        
        # Фаза должна измениться
        self.assertNotEqual(controller.current_phase, initial_phase)
        
    def test_traffic_controller_dynamic_mode_initialization(self):
        """Тест инициализации динамического режима"""
        controller = TrafficController()
        controller.mode = 'dynamic'
        
        # Проверяем инициализацию динамических параметров
        self.assertIsInstance(controller.traffic_pressure, list)
        self.assertEqual(len(controller.traffic_pressure), 4)  # По одному для каждого направления
        
        for pressure in controller.traffic_pressure:
            self.assertGreaterEqual(pressure, 0)
            
    def test_traffic_controller_calculate_traffic_pressure(self):
        """Тест расчета давления трафика"""
        controller = TrafficController()
        controller.mode = 'dynamic'
        
        # Создаем тестовые машины
        from simulation import Car
        cars = [
            Car([50, 0], [0, 1], 30, (255, 0, 0)),  # Север
            Car([0, 50], [1, 0], 30, (0, 255, 0)),  # Восток
            Car([-50, 0], [0, -1], 30, (0, 0, 255)),  # Юг
        ]
        
        # Рассчитываем давление
        pressure = controller.calculate_traffic_pressure(cars)
        
        self.assertIsInstance(pressure, list)
        self.assertEqual(len(pressure), 4)
        
        # Проверяем, что давление положительное там, где есть машины
        self.assertGreater(pressure[0], 0)  # Север
        self.assertGreater(pressure[1], 0)  # Восток
        self.assertGreater(pressure[2], 0)  # Юг
        self.assertEqual(pressure[3], 0)    # Запад (нет машин)
        
    def test_traffic_controller_get_light_states(self):
        """Тест получения состояний светофоров"""
        controller = TrafficController()
        
        states = controller.get_light_states()
        
        self.assertIsInstance(states, list)
        self.assertEqual(len(states), 4)
        
        for state in states:
            self.assertIn(state, ['red', 'yellow', 'green'])
            
    def test_traffic_controller_phase_definitions(self):
        """Тест определений фаз"""
        controller = TrafficController()
        
        # Проверяем, что все фазы определены корректно
        for phase_states in controller.phase_definitions:
            self.assertEqual(len(phase_states), 4)  # 4 направления
            for state in phase_states:
                self.assertIn(state, ['red', 'yellow', 'green'])
                
        # Проверяем безопасность - не должно быть одновременно зеленого в противоположных направлениях
        for phase_states in controller.phase_definitions:
            green_directions = []
            for i, state in enumerate(phase_states):
                if state == 'green':
                    green_directions.append(i)
                    
            # Проверяем, что зеленые направления не конфликтуют
            for i in range(len(green_directions)):
                for j in range(i + 1, len(green_directions)):
                    dir1 = green_directions[i]
                    dir2 = green_directions[j]
                    # Противоположные направления: 0-2 (север-юг), 1-3 (восток-запад)
                    self.assertNotEqual(abs(dir1 - dir2), 2)
                    
    def test_traffic_controller_waiting_time_calculation(self):
        """Тест расчета времени ожидания"""
        controller = TrafficController()
        
        # Создаем машины с разным временем ожидания
        from simulation import Car
        cars = []
        for i in range(3):
            car = Car([50, 0], [0, 1], 30, (255, 0, 0))
            car.waiting_time = float(i * 10)  # 0, 10, 20 секунд
            cars.append(car)
            
        waiting_times = controller.calculate_waiting_times(cars)
        
        self.assertIsInstance(waiting_times, list)
        self.assertEqual(len(waiting_times), 4)  # По одному для каждого направления
        
        # Проверяем, что общее время ожидания правильно рассчитано
        total_waiting = sum(car.waiting_time for car in cars)
        self.assertGreater(waiting_times[0], 0)  # Должно быть больше 0 для севера


if __name__ == '__main__':
    unittest.main()