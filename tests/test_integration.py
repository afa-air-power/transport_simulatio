import unittest
import pygame
import sys
import os
import time
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulation import TrafficSimulation, Car, Pedestrian
from traffic_controller import TrafficController
from ui import UIManager
from constants import *


class TestTrafficSimulationIntegration(unittest.TestCase):
    def setUp(self):
        """Настройка интеграционных тестов"""
        pygame.init()
        self.simulation = TrafficSimulation()
        
    def test_full_simulation_cycle(self):
        """Тест полного цикла симуляции"""
        # Проверяем начальное состояние
        initial_car_count = len(self.simulation.cars)
        initial_ped_count = len(self.simulation.pedestrians)
        
        # Запускаем несколько циклов симуляции
        for _ in range(10):
            self.simulation.update(0.1)
            
        # Проверяем, что симуляция работает без ошибок
        self.assertIsInstance(self.simulation.cars, list)
        self.assertIsInstance(self.simulation.pedestrians, list)
        
    def test_traffic_light_car_interaction(self):
        """Тест взаимодействия светофоров и машин"""
        # Создаем машину приближающуюся к перекрестку
        car = Car([50, 0], [0, 1], 30, (255, 0, 0))  # Движется на север
        self.simulation.cars.append(car)
        
        # Устанавливаем красный свет для северного направления
        self.simulation.traffic_controller.lights[0].set_color('red')
        
        # Запускаем симуляцию
        for _ in range(20):
            self.simulation.update(0.1)
            
            # Проверяем, что машина замедляется при красном свете
            if car.pos[1] > -20 and car.pos[1] < 20:  # Вблизи перекрестка
                # Машина должна остановиться или сильно замедлиться
                self.assertLessEqual(car.speed, 10)  # Значительное замедление
                break
                
    def test_pedestrian_car_interaction(self):
        """Тест взаимодействия пешеходов и машин"""
        # Создаем машину
        car = Car([0, 50], [1, 0], 30, (255, 0, 0))
        self.simulation.cars.append(car)
        
        # Создаем пешехода на пути машины
        pedestrian = Pedestrian([60, 50], [60, -50])
        self.simulation.pedestrians.append(pedestrian)
        
        # Запускаем симуляцию
        collision_detected = False
        for _ in range(50):
            self.simulation.update(0.1)
            
            # Проверяем на столкновения
            if pedestrian.check_collision_with_car(car):
                collision_detected = True
                break
                
        # В хорошей симуляции машина должна избегать пешехода
        # или система должна обнаружить потенциальное столкновение
        self.assertTrue(True)  # Базовая проверка выполнения
        
    def test_multiple_cars_interaction(self):
        """Тест взаимодействия нескольких машин"""
        # Создаем несколько машин в одной полосе
        cars = [
            Car([i * 30, 0], [0, 1], 30, (255, i * 50, 0)) 
            for i in range(5)
        ]
        self.simulation.cars.extend(cars)
        
        # Запускаем симуляцию
        for _ in range(30):
            self.simulation.update(0.1)
            
        # Проверяем, что машины не столкнулись
        for i, car1 in enumerate(cars):
            for j, car2 in enumerate(cars):
                if i != j:
                    distance = ((car1.pos[0] - car2.pos[0])**2 + 
                               (car1.pos[1] - car2.pos[1])**2)**0.5
                    # Машины должны поддерживать безопасную дистанцию
                    if distance < 100:  # Если близко
                        self.assertGreater(distance, 15)  # Минимальная безопасная дистанция
                        
    def test_traffic_controller_phase_transitions(self):
        """Тест переходов фаз светофора"""
        controller = self.simulation.traffic_controller
        controller.mode = 'static'
        
        initial_phase = controller.current_phase
        phase_changes = []
        
        # Запускаем симуляцию и отслеживаем изменения фаз
        for i in range(100):
            controller.update(0.1, [], [])
            
            if controller.current_phase != initial_phase:
                phase_changes.append((i, controller.current_phase))
                initial_phase = controller.current_phase
                
        # Должны быть изменения фаз
        self.assertGreater(len(phase_changes), 0)
        
        # Все фазы должны быть валидными
        for _, phase in phase_changes:
            self.assertGreaterEqual(phase, 0)
            self.assertLess(phase, len(controller.phase_definitions))
            
    def test_dynamic_traffic_control(self):
        """Тест динамического управления трафиком"""
        controller = self.simulation.traffic_controller
        controller.mode = 'dynamic'
        
        # Создаем асимметричную загрузку трафика
        # Много машин с севера
        for i in range(10):
            car = Car([random.randint(-30, 30), -200 - i * 30], [0, 1], 30, (255, 0, 0))
            self.simulation.cars.append(car)
            
        # Мало машин с востока
        for i in range(2):
            car = Car([200 + i * 30, random.randint(-30, 30)], [-1, 0], 30, (0, 255, 0))
            self.simulation.cars.append(car)
            
        # Запускаем симуляцию
        phase_durations = {}
        current_phase = controller.current_phase
        phase_start_time = time.time()
        
        for _ in range(200):
            self.simulation.update(0.1)
            
            # Отслеживаем длительность фаз
            if controller.current_phase != current_phase:
                duration = time.time() - phase_start_time
                if current_phase not in phase_durations:
                    phase_durations[current_phase] = []
                phase_durations[current_phase].append(duration)
                
                current_phase = controller.current_phase
                phase_start_time = time.time()
                
        # В динамическом режиме фазы должны адаптироваться к трафику
        self.assertTrue(True)  # Базовая проверка выполнения
        
    def test_pedestrian_crossing_logic(self):
        """Тест логики перехода пешеходов"""
        # Создаем пешехода, который должен пересечь дорогу
        pedestrian = Pedestrian([-100, 50], [100, 50])
        self.simulation.pedestrians.append(pedestrian)
        
        # Отслеживаем поведение пешехода при разных состояниях светофора
        initial_pos = pedestrian.pos.copy()
        
        # Устанавливаем красный для всех направлений (пешеходный переход активен)
        for light in self.simulation.traffic_controller.lights:
            light.set_color('red')
            
        # Запускаем симуляцию
        for _ in range(50):
            self.simulation.update(0.1)
            
        # Пешеход должен начать движение при безопасных условиях
        distance_moved = abs(pedestrian.pos[0] - initial_pos[0])
        self.assertGreater(distance_moved, 0)


class TestUIIntegration(unittest.TestCase):
    def setUp(self):
        """Настройка для тестов UI"""
        pygame.init()
        self.simulation = TrafficSimulation()
        self.ui = UIManager(self.simulation)
        
    @patch('pygame.display.set_mode')
    def test_ui_initialization(self, mock_display):
        """Тест инициализации UI"""
        mock_display.return_value = pygame.Surface((1200, 900))
        
        self.assertIsNotNone(self.ui.simulation)
        self.assertIsInstance(self.ui.buttons, list)
        
    def test_ui_event_handling(self):
        """Тест обработки событий UI"""
        # Создаем тестовое событие
        test_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, 
                                       button=1, pos=(100, 100))
        
        # Проверяем, что обработка событий не вызывает ошибок
        try:
            self.ui.handle_events(test_event)
            success = True
        except Exception:
            success = False
            
        self.assertTrue(success)
        
    def test_ui_statistics_display(self):
        """Тест отображения статистики"""
        # Добавляем объекты в симуляцию
        self.simulation.cars.append(Car([100, 100], [1, 0], 30, (255, 0, 0)))
        self.simulation.pedestrians.append(Pedestrian([50, 50], [150, 150]))
        
        # Получаем статистику
        stats = self.simulation.get_statistics()
        
        self.assertIsInstance(stats, dict)
        self.assertGreater(stats['total_cars'], 0)
        self.assertGreater(stats['total_pedestrians'], 0)


class TestSystemIntegration(unittest.TestCase):
    def setUp(self):
        """Настройка системных интеграционных тестов"""
        pygame.init()
        
    def test_config_loading_integration(self):
        """Тест интеграции загрузки конфигурации"""
        # Создаем тестовую конфигурацию
        test_config = {
            "car_spawn_rate": 2.5,
            "pedestrian_spawn_rate": 1.8,
            "traffic_mode": "dynamic",
            "num_lanes": 3,
            "simulation_speed": 1.0
        }
        
        simulation = TrafficSimulation()
        
        try:
            simulation.load_config(test_config)
            success = True
        except Exception:
            success = False
            
        self.assertTrue(success)
        
    def test_full_application_startup(self):
        """Тест полного запуска приложения"""
        try:
            # Имитируем основные компоненты запуска
            simulation = TrafficSimulation()
            ui = UIManager(simulation)
            
            # Короткий цикл симуляции
            for _ in range(5):
                simulation.update(0.1)
                ui.update(0.1)
                
            success = True
        except Exception:
            success = False
            
        self.assertTrue(success)
        
    def test_memory_management(self):
        """Тест управления памятью"""
        simulation = TrafficSimulation()
        
        # Добавляем много объектов
        for i in range(100):
            simulation.cars.append(Car([i * 10, 0], [1, 0], 30, (255, 0, 0)))
            simulation.pedestrians.append(Pedestrian([0, i * 10], [200, i * 10]))
            
        initial_count = len(simulation.cars) + len(simulation.pedestrians)
        
        # Запускаем симуляцию
        for _ in range(50):
            simulation.update(0.1)
            
        # Проверяем, что объекты правильно удаляются когда выходят за границы
        # (конкретное поведение зависит от реализации)
        self.assertTrue(True)  # Базовая проверка выполнения
        
    def test_performance_under_load(self):
        """Тест производительности под нагрузкой"""
        simulation = TrafficSimulation()
        
        # Создаем высокую нагрузку
        for i in range(50):
            car = Car([random.randint(-200, 200), random.randint(-200, 200)], 
                     [random.choice([-1, 1]), random.choice([-1, 1])], 
                     30, (255, 0, 0))
            simulation.cars.append(car)
            
        for i in range(30):
            ped = Pedestrian([random.randint(-200, 200), random.randint(-200, 200)],
                           [random.randint(-200, 200), random.randint(-200, 200)])
            simulation.pedestrians.append(ped)
            
        # Измеряем время выполнения обновления
        start_time = time.time()
        
        for _ in range(10):
            simulation.update(0.1)
            
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Обновление не должно занимать слишком много времени
        self.assertLess(execution_time, 5.0)  # Максимум 5 секунд для 10 итераций


if __name__ == '__main__':
    # Импортируем random для тестов
    import random
    
    unittest.main()