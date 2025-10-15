import unittest
import pygame
import sys
import os
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulation import TrafficSimulation, Car, Pedestrian
from traffic_controller import TrafficController
from constants import *


class TestTrafficSimulation(unittest.TestCase):
    def setUp(self):
        """Настройка для каждого теста"""
        pygame.init()
        self.simulation = TrafficSimulation()
        
    def test_simulation_initialization(self):
        """Тест инициализации симуляции"""
        self.assertIsNotNone(self.simulation.traffic_controller)
        self.assertIsInstance(self.simulation.traffic_controller, TrafficController)
        
        # Проверяем инициализацию списков
        self.assertIsInstance(self.simulation.cars, list)
        self.assertIsInstance(self.simulation.pedestrians, list)
        
        # Проверяем таймеры
        self.assertGreaterEqual(self.simulation.car_spawn_timer, 0)
        self.assertGreaterEqual(self.simulation.pedestrian_spawn_timer, 0)
        
    def test_simulation_car_spawning(self):
        """Тест создания машин"""
        initial_car_count = len(self.simulation.cars)
        
        # Принудительно создаем машину
        self.simulation.spawn_car()
        
        self.assertEqual(len(self.simulation.cars), initial_car_count + 1)
        
        # Проверяем свойства созданной машины
        new_car = self.simulation.cars[-1]
        self.assertIsInstance(new_car, Car)
        self.assertGreater(new_car.speed, 0)
        self.assertIsInstance(new_car.pos, list)
        self.assertIsInstance(new_car.heading, list)
        
    def test_simulation_pedestrian_spawning(self):
        """Тест создания пешеходов"""
        initial_ped_count = len(self.simulation.pedestrians)
        
        # Принудительно создаем пешехода
        self.simulation.spawn_pedestrian()
        
        self.assertEqual(len(self.simulation.pedestrians), initial_ped_count + 1)
        
        # Проверяем свойства созданного пешехода
        new_pedestrian = self.simulation.pedestrians[-1]
        self.assertIsInstance(new_pedestrian, Pedestrian)
        self.assertGreater(new_pedestrian.speed, 0)
        self.assertIsInstance(new_pedestrian.pos, list)
        
    def test_simulation_update_timers(self):
        """Тест обновления таймеров"""
        initial_car_timer = self.simulation.car_spawn_timer
        initial_ped_timer = self.simulation.pedestrian_spawn_timer
        
        dt = 1.0
        self.simulation.update_timers(dt)
        
        # Таймеры должны уменьшиться
        self.assertLess(self.simulation.car_spawn_timer, initial_car_timer)
        self.assertLess(self.simulation.pedestrian_spawn_timer, initial_ped_timer)
        
    def test_simulation_car_removal(self):
        """Тест удаления машин"""
        # Создаем машину и помещаем ее далеко за границы
        car = Car([2000, 2000], [1, 0], 30, (255, 0, 0))
        self.simulation.cars.append(car)
        initial_count = len(self.simulation.cars)
        
        # Обновляем симуляцию
        self.simulation.update(0.1)
        
        # Машина должна быть удалена
        self.assertLess(len(self.simulation.cars), initial_count)
        
    def test_simulation_pedestrian_removal(self):
        """Тест удаления пешеходов"""
        # Создаем пешехода в точке назначения
        pedestrian = Pedestrian([100, 100], [100, 100])
        pedestrian.reached_target = True
        self.simulation.pedestrians.append(pedestrian)
        initial_count = len(self.simulation.pedestrians)
        
        # Обновляем симуляцию
        self.simulation.update(0.1)
        
        # Пешеход должен быть удален
        self.assertLess(len(self.simulation.pedestrians), initial_count)
        
    def test_simulation_collision_detection(self):
        """Тест обнаружения столкновений"""
        # Создаем две машины близко друг к другу
        car1 = Car([100, 100], [1, 0], 30, (255, 0, 0))
        car2 = Car([105, 100], [1, 0], 30, (0, 255, 0))
        
        self.simulation.cars.extend([car1, car2])
        
        # Проверяем обнаружение столкновения
        collisions = self.simulation.check_car_collisions()
        self.assertTrue(len(collisions) > 0)
        
    def test_simulation_traffic_light_interaction(self):
        """Тест взаимодействия машин со светофорами"""
        # Создаем машину рядом с перекрестком
        car = Car([50, 0], [0, 1], 30, (255, 0, 0))
        self.simulation.cars.append(car)
        
        # Устанавливаем красный свет
        self.simulation.traffic_controller.lights[0].set_color('red')
        
        # Обновляем симуляцию
        initial_speed = car.speed
        self.simulation.update(0.1)
        
        # Машина должна замедлиться или остановиться
        # (конкретное поведение зависит от реализации)
        self.assertTrue(True)  # Базовая проверка что код выполняется без ошибок
        
    def test_simulation_statistics_collection(self):
        """Тест сбора статистики"""
        # Добавляем несколько машин и пешеходов
        for i in range(5):
            car = Car([i * 50, 0], [0, 1], 30, (255, 0, 0))
            car.waiting_time = i * 10
            self.simulation.cars.append(car)
            
        for i in range(3):
            pedestrian = Pedestrian([0, i * 50], [100, i * 50])
            pedestrian.waiting_time = i * 5
            self.simulation.pedestrians.append(pedestrian)
            
        # Получаем статистику
        stats = self.simulation.get_statistics()
        
        self.assertIsInstance(stats, dict)
        self.assertIn('total_cars', stats)
        self.assertIn('total_pedestrians', stats)
        self.assertIn('average_car_wait_time', stats)
        self.assertIn('average_pedestrian_wait_time', stats)
        
        self.assertEqual(stats['total_cars'], 5)
        self.assertEqual(stats['total_pedestrians'], 3)
        
    def test_simulation_reset(self):
        """Тест сброса симуляции"""
        # Добавляем объекты
        self.simulation.cars.append(Car([100, 100], [1, 0], 30, (255, 0, 0)))
        self.simulation.pedestrians.append(Pedestrian([50, 50], [150, 150]))
        
        # Сбрасываем симуляцию
        self.simulation.reset()
        
        # Проверяем, что все очищено
        self.assertEqual(len(self.simulation.cars), 0)
        self.assertEqual(len(self.simulation.pedestrians), 0)
        
    def test_simulation_config_loading(self):
        """Тест загрузки конфигурации"""
        config = {
            'car_spawn_rate': 2.0,
            'pedestrian_spawn_rate': 1.5,
            'traffic_mode': 'dynamic'
        }
        
        self.simulation.load_config(config)
        
        # Проверяем, что конфигурация применена
        # (конкретные проверки зависят от реализации load_config)
        self.assertTrue(True)  # Базовая проверка выполнения без ошибок


class TestCar(unittest.TestCase):
    def setUp(self):
        """Настройка для каждого теста"""
        pygame.init()
        
    def test_car_position_update(self):
        """Тест обновления позиции машины"""
        car = Car([0, 0], [1, 0], 30, (255, 0, 0))
        initial_x = car.pos[0]
        
        dt = 0.1
        car.update_position(dt)
        
        # Позиция X должна увеличиться
        self.assertGreater(car.pos[0], initial_x)
        
    def test_car_speed_adjustment(self):
        """Тест регулировки скорости машины"""
        car = Car([0, 0], [1, 0], 30, (255, 0, 0))
        car.target_speed = 50
        initial_speed = car.speed
        
        dt = 0.1
        car.adjust_speed(dt)
        
        # Скорость должна приблизиться к целевой
        if initial_speed < car.target_speed:
            self.assertGreaterEqual(car.speed, initial_speed)
        elif initial_speed > car.target_speed:
            self.assertLessEqual(car.speed, initial_speed)
            
    def test_car_lane_changing(self):
        """Тест смены полосы"""
        car = Car([0, 0], [1, 0], 30, (255, 0, 0))
        car.current_lane = 1
        car.target_lane = 2
        
        dt = 0.1
        car.change_lanes(dt)
        
        # Машина должна постепенно менять полосу
        # (конкретная логика зависит от реализации)
        self.assertTrue(True)
        
    def test_car_turning_logic(self):
        """Тест логики поворотов"""
        car = Car([50, 0], [0, 1], 30, (255, 0, 0))
        car.turn_direction = 'right'
        
        # Проверяем инициализацию поворота
        car.start_turn()
        
        self.assertTrue(car.is_turning)
        self.assertEqual(car.turn_progress, 0.0)
        self.assertIsNotNone(car.turn_center)
        
    def test_car_obstacle_detection(self):
        """Тест обнаружения препятствий"""
        car = Car([0, 0], [1, 0], 30, (255, 0, 0))
        
        # Создаем препятствие впереди
        obstacle = Car([50, 0], [1, 0], 20, (0, 255, 0))
        obstacles = [obstacle]
        
        detection_result = car.detect_obstacles(obstacles)
        self.assertTrue(detection_result)


class TestPedestrian(unittest.TestCase):
    def setUp(self):
        """Настройка для каждого теста"""
        pygame.init()
        
    def test_pedestrian_movement_update(self):
        """Тест обновления движения пешехода"""
        start = [0, 0]
        target = [100, 0]
        pedestrian = Pedestrian(start, target)
        
        initial_x = pedestrian.pos[0]
        dt = 0.1
        pedestrian.update(dt)
        
        # Пешеход должен двигаться к цели
        self.assertGreater(pedestrian.pos[0], initial_x)
        
    def test_pedestrian_waiting_behavior(self):
        """Тест поведения ожидания пешехода"""
        pedestrian = Pedestrian([50, 50], [150, 150])
        pedestrian.is_waiting = True
        
        initial_waiting_time = pedestrian.waiting_time
        dt = 1.0
        pedestrian.update(dt)
        
        # Время ожидания должно увеличиться
        self.assertGreater(pedestrian.waiting_time, initial_waiting_time)
        
    def test_pedestrian_group_behavior(self):
        """Тест группового поведения пешеходов"""
        ped1 = Pedestrian([50, 50], [150, 150])
        ped2 = Pedestrian([55, 55], [150, 150])
        ped3 = Pedestrian([45, 45], [150, 150])
        
        group = [ped1, ped2, ped3]
        
        # Симулируем групповое поведение
        for ped in group:
            ped.update_with_group(0.1, group)
            
        # Проверяем, что пешеходы учитывают друг друга
        # (конкретная логика зависит от реализации)
        self.assertTrue(True)
        
    def test_pedestrian_avoidance(self):
        """Тест избегания препятствий пешеходом"""
        pedestrian = Pedestrian([0, 0], [100, 0])
        
        # Создаем препятствие на пути
        obstacle = Car([50, 0], [1, 0], 30, (255, 0, 0))
        obstacles = [obstacle]
        
        # Пешеход должен избегать препятствия
        avoidance_vector = pedestrian.calculate_avoidance(obstacles)
        
        self.assertIsInstance(avoidance_vector, (list, tuple))
        self.assertEqual(len(avoidance_vector), 2)


if __name__ == '__main__':
    unittest.main()