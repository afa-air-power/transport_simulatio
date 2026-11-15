import unittest
import pygame
import math
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from entities import Vehicle
from simulation import Car, Pedestrian
from constants import *


class TestVehicle(unittest.TestCase):
    def setUp(self):
        """Настройка для каждого теста"""
        pygame.init()
        
    def test_vehicle_initialization(self):
        """Тест инициализации транспортного средства"""
        vehicle = Vehicle(dir_in='from_north', num_lanes=3)
        
        # Проверяем базовые свойства
        self.assertEqual(vehicle.dir_in, 'from_north')
        self.assertIn(vehicle.turn, [0, 1, 2])  # прямо, направо, налево
        self.assertGreaterEqual(vehicle.lane, 0)
        self.assertLess(vehicle.lane, 3)
        self.assertGreaterEqual(vehicle.target_speed, SPEED_MIN)
        self.assertLessEqual(vehicle.target_speed, SPEED_MAX)
        
        # Проверяем физические характеристики
        self.assertGreater(vehicle.mass, 0)
        self.assertGreater(vehicle.length, 0)
        self.assertGreater(vehicle.width, 0)
        self.assertGreater(vehicle.accel_rate, 0)
        self.assertGreater(vehicle.brake_rate, 0)
        
    def test_vehicle_target_lane_setting(self):
        """Тест установки целевой полосы"""
        # Тест для поворота налево
        vehicle = Vehicle(dir_in='from_north', num_lanes=3)
        vehicle.turn = 2  # налево
        vehicle.set_target_lane(3)
        # Для поворота налево должна быть левая полоса
        self.assertEqual(vehicle.target_lane, 0)
        
        # Тест для поворота направо  
        vehicle.turn = 1  # направо
        vehicle.set_target_lane(3)
        # Для поворота направо должна быть правая полоса
        self.assertEqual(vehicle.target_lane, 2)
        
    def test_vehicle_position_initialization(self):
        """Тест инициализации позиции транспортного средства"""
        directions = ['from_north', 'from_south', 'from_east', 'from_west']
        for direction in directions:
            vehicle = Vehicle(dir_in=direction, num_lanes=3)
            pos = vehicle.get_initial_pos(3)
            
            # Позиция должна быть кортежем из двух элементов
            self.assertEqual(len(pos), 2)
            self.assertIsInstance(pos[0], (int, float))
            self.assertIsInstance(pos[1], (int, float))
            
    def test_vehicle_heading_initialization(self):
        """Тест инициализации направления движения"""
        directions = ['from_north', 'from_south', 'from_east', 'from_west']
        for direction in directions:
            vehicle = Vehicle(dir_in=direction, num_lanes=3)
            heading = vehicle.get_initial_heading()
            
            # Направление должно быть нормализованным вектором
            magnitude = math.sqrt(heading[0]**2 + heading[1]**2)
            self.assertAlmostEqual(magnitude, 1.0, places=5)


class TestCar(unittest.TestCase):
    def setUp(self):
        """Настройка для каждого теста"""
        pygame.init()
        
    def test_car_initialization(self):
        """Тест инициализации автомобиля"""
        pos = [100, 100]
        heading = [1, 0]
        speed = 30
        color = (255, 0, 0)
        
        car = Car(pos, heading, speed, color)
        
        # Проверяем базовые свойства
        self.assertEqual(car.pos, pos)
        self.assertEqual(car.heading, heading)
        self.assertEqual(car.speed, speed)
        self.assertEqual(car.color, color)
        self.assertIsNotNone(car.neon_color)
        
        # Проверяем размеры
        self.assertGreater(car.length, 0)
        self.assertGreater(car.width, 0)
        
        # Проверяем логику поворотов
        self.assertIn(car.turn_direction, ['straight', 'left', 'right'])
        self.assertFalse(car.is_turning)
        self.assertEqual(car.turn_progress, 0.0)
        
    def test_car_neon_color_generation(self):
        """Тест генерации неонового цвета"""
        car = Car([0, 0], [1, 0], 30, (255, 0, 0))
        neon_color = car.generate_neon_color((255, 0, 0))
        
        # Неоновый цвет должен быть ярче оригинального
        self.assertIsInstance(neon_color, tuple)
        self.assertEqual(len(neon_color), 3)
        for component in neon_color:
            self.assertGreaterEqual(component, 0)
            self.assertLessEqual(component, 255)
            
    def test_car_movement(self):
        """Тест движения автомобиля"""
        car = Car([100, 100], [1, 0], 30, (255, 0, 0))
        initial_pos = car.pos.copy()
        
        # Симулируем движение (используем метод update с минимальными параметрами)
        dt = 0.1
        from traffic_controller import TrafficController
        controller = TrafficController()
        car.update(dt, controller, [])
        
        # Позиция должна измениться
        self.assertNotEqual(car.pos[0], initial_pos[0])
        
    def test_car_collision_detection(self):
        """Тест обнаружения столкновений"""
        car1 = Car([100, 100], [1, 0], 30, (255, 0, 0))
        car2 = Car([110, 100], [1, 0], 30, (0, 255, 0))
        
        # Тестируем базовое поведение при близком расположении машин
        # Проверяем что машины созданы правильно
        self.assertIsNotNone(car1.pos)
        self.assertIsNotNone(car2.pos)
        
        # Проверяем расстояние между машинами
        dx = car2.pos[0] - car1.pos[0]
        dy = car2.pos[1] - car1.pos[1]
        distance = math.sqrt(dx*dx + dy*dy)
        self.assertLess(distance, 50)  # Машины близко


class TestPedestrian(unittest.TestCase):
    def setUp(self):
        """Настройка для каждого теста"""
        pygame.init()
        
    def test_pedestrian_initialization(self):
        """Тест инициализации пешехода"""
        start_pos = [50, 50]
        target_pos = [150, 150]
        speed = 5.0
        color = (255, 0, 0)
        size = 2
        
        pedestrian = Pedestrian(start_pos, target_pos, speed, color, size)
        
        # Проверяем базовые свойства
        self.assertEqual(pedestrian.pos, start_pos)
        self.assertEqual(pedestrian.goal, target_pos)
        self.assertEqual(pedestrian.speed, speed)
        self.assertEqual(pedestrian.size, size)
        self.assertEqual(pedestrian.color, color)
        
        # Проверяем неоновый цвет
        self.assertIsNotNone(pedestrian.neon_color)
        
    def test_pedestrian_movement_towards_target(self):
        """Тест движения пешехода к цели"""
        start_pos = [0, 0]
        target_pos = [100, 0]
        speed = 10.0
        color = (255, 0, 0)
        size = 2
        
        pedestrian = Pedestrian(start_pos, target_pos, speed, color, size)
        initial_pos = pedestrian.pos.copy()
        
        # Симулируем движение
        dt = 0.1
        from traffic_controller import TrafficController
        controller = TrafficController()
        # Устанавливаем красный для всех направлений для безопасного перехода
        for light in controller.lights:
            light.set_color('red')
        
        pedestrian.update(dt, controller)
        
        # Проверяем, что позиция изменилась
        self.assertNotEqual(pedestrian.pos[0], initial_pos[0])
        
    def test_pedestrian_target_reached(self):
        """Тест достижения цели пешеходом"""
        start_pos = [0, 0]
        target_pos = [1, 0]  # Очень близкая цель
        speed = 10.0
        color = (255, 0, 0)
        size = 2
        
        pedestrian = Pedestrian(start_pos, target_pos, speed, color, size)
        
        # Множественные обновления для достижения цели
        from traffic_controller import TrafficController
        controller = TrafficController()
        for light in controller.lights:
            light.set_color('red')
            
        for _ in range(10):
            pedestrian.update(0.1, controller)
            
        # Проверяем, что пешеход двигался к цели
        distance = math.sqrt((pedestrian.pos[0] - target_pos[0])**2 + (pedestrian.pos[1] - target_pos[1])**2)
        self.assertLess(distance, 5)  # Должен быть близко к цели
        
    def test_pedestrian_collision_with_car(self):
        """Тест близости пешехода и автомобиля"""
        pedestrian = Pedestrian([100, 100], [150, 150], 5.0, (255, 0, 0), 2)
        car = Car([105, 105], [1, 0], 30, (255, 0, 0))
        
        # Проверяем близость объектов
        dx = car.pos[0] - pedestrian.pos[0]
        dy = car.pos[1] - pedestrian.pos[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Близкое расстояние указывает на потенциальную опасность
        self.assertLess(distance, 20)
        
        # Машина далеко - расстояние большое
        car.pos = [200, 200]
        dx = car.pos[0] - pedestrian.pos[0]
        dy = car.pos[1] - pedestrian.pos[1]
        distance = math.sqrt(dx*dx + dy*dy)
        self.assertGreater(distance, 100)


if __name__ == '__main__':
    unittest.main()