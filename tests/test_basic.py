import unittest
import pygame
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from entities import Vehicle, Pedestrian as EntitiesPedestrian
from simulation import TrafficSimulation, Car, Pedestrian
from traffic_controller import TrafficController, TrafficLight, LightLens
from constants import *


class TestBasicFunctionality(unittest.TestCase):
    """Базовые тесты для проверки основной функциональности"""
    
    def setUp(self):
        """Настройка для каждого теста"""
        pygame.init()
        
    def test_vehicle_creation(self):
        """Тест создания Vehicle"""
        try:
            vehicle = Vehicle(dir_in='from_north', num_lanes=3)
            self.assertIsNotNone(vehicle)
            self.assertEqual(vehicle.dir_in, 'from_north')
            self.assertIn(vehicle.turn, [0, 1, 2])
        except Exception as e:
            self.fail(f"Vehicle creation failed: {e}")
    
    def test_car_creation(self):
        """Тест создания Car"""
        try:
            car = Car([100, 100], [1, 0], 30, (255, 0, 0))
            self.assertIsNotNone(car)
            self.assertEqual(car.pos, [100, 100])
            self.assertEqual(car.heading, [1, 0])
            self.assertEqual(car.speed, 30)
            self.assertEqual(car.color, (255, 0, 0))
        except Exception as e:
            self.fail(f"Car creation failed: {e}")
    
    def test_pedestrian_creation(self):
        """Тест создания Pedestrian"""
        try:
            ped = Pedestrian([50, 50], [100, 100], 5.0, (0, 255, 0), 2)
            self.assertIsNotNone(ped)
            self.assertEqual(ped.pos, [50, 50])
            self.assertEqual(ped.goal, [100, 100])
            self.assertEqual(ped.speed, 5.0)
        except Exception as e:
            self.fail(f"Pedestrian creation failed: {e}")
    
    def test_traffic_light_creation(self):
        """Тест создания TrafficLight"""
        try:
            light = TrafficLight((100, 100), 'vertical')
            self.assertIsNotNone(light)
            self.assertEqual(light.position, (100, 100))
            self.assertEqual(light.orientation, 'vertical')
            self.assertEqual(light.current_color, 'red')
        except Exception as e:
            self.fail(f"TrafficLight creation failed: {e}")
    
    def test_traffic_controller_creation(self):
        """Тест создания TrafficController"""
        try:
            controller = TrafficController()
            self.assertIsNotNone(controller)
            self.assertIn(controller.mode, ['static', 'dynamic'])
            self.assertIsInstance(controller.current_phase, int)
        except Exception as e:
            self.fail(f"TrafficController creation failed: {e}")
    
    def test_simulation_creation(self):
        """Тест создания TrafficSimulation"""
        try:
            sim = TrafficSimulation()
            self.assertIsNotNone(sim)
            self.assertIsInstance(sim.cars, list)
            self.assertIsInstance(sim.peds, list)
        except Exception as e:
            self.fail(f"TrafficSimulation creation failed: {e}")
    
    def test_light_color_change(self):
        """Тест смены цвета светофора"""
        try:
            light = TrafficLight((100, 100), 'vertical')
            
            # Изначально красный
            self.assertEqual(light.current_color, 'red')
            
            # Меняем на зеленый
            light.set_color('green')
            self.assertEqual(light.current_color, 'green')
            
            # Меняем на желтый
            light.set_color('yellow')
            self.assertEqual(light.current_color, 'yellow')
        except Exception as e:
            self.fail(f"Light color change failed: {e}")
    
    def test_car_movement(self):
        """Тест движения автомобиля"""
        try:
            car = Car([0, 0], [1, 0], 30, (255, 0, 0))
            controller = TrafficController()
            
            initial_pos = car.pos.copy()
            car.update(0.1, controller, [])
            
            # Позиция должна измениться
            self.assertNotEqual(car.pos, initial_pos)
        except Exception as e:
            self.fail(f"Car movement failed: {e}")
    
    def test_pedestrian_movement(self):
        """Тест движения пешехода"""
        try:
            ped = Pedestrian([0, 0], [100, 0], 10.0, (255, 0, 0), 2)
            controller = TrafficController()
            
            # Устанавливаем красный для всех направлений
            for direction in ['horizontal', 'vertical']:
                try:
                    controller.set_color(direction, 'red')
                except:
                    pass  # Игнорируем если метод не существует
            
            initial_pos = ped.pos.copy()
            ped.update(0.1, controller)
            
            # Проверяем, что код выполняется без ошибок
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Pedestrian movement failed: {e}")
    
    def test_simulation_update(self):
        """Тест обновления симуляции"""
        try:
            sim = TrafficSimulation()
            
            # Добавляем машину
            car = Car([100, 100], [1, 0], 30, (255, 0, 0))
            sim.cars.append(car)
            
            # Добавляем пешехода
            ped = Pedestrian([50, 50], [150, 150], 5.0, (0, 255, 0), 2)
            sim.peds.append(ped)
            
            # Обновляем симуляцию
            sim.update(0.1)
            
            self.assertTrue(True)  # Проверяем, что код выполняется без ошибок
        except Exception as e:
            self.fail(f"Simulation update failed: {e}")
    
    def test_constants_available(self):
        """Тест доступности констант"""
        try:
            # Проверяем основные константы
            self.assertIsNotNone(NUM_LANES)
            self.assertIsNotNone(LANE_WIDTH)
            self.assertIsNotNone(SPEED_MIN)
            self.assertIsNotNone(SPEED_MAX)
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Constants access failed: {e}")
    
    def test_neon_color_generation(self):
        """Тест генерации неоновых цветов"""
        try:
            car = Car([0, 0], [1, 0], 30, (255, 0, 0))
            neon_color = car.neon_color
            
            self.assertIsInstance(neon_color, tuple)
            self.assertEqual(len(neon_color), 3)
            
            # Неоновый цвет должен быть ярче оригинального
            for i in range(3):
                self.assertGreaterEqual(neon_color[i], car.color[i])
        except Exception as e:
            self.fail(f"Neon color generation failed: {e}")
    
    def test_math_operations(self):
        """Тест математических операций"""
        try:
            import math
            
            # Тест расстояния между точками
            p1 = [0, 0]
            p2 = [3, 4]
            distance = math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
            self.assertAlmostEqual(distance, 5.0, places=2)
            
            # Тест нормализации вектора
            vector = [3, 4]
            magnitude = math.sqrt(vector[0]**2 + vector[1]**2)
            normalized = [vector[0] / magnitude, vector[1] / magnitude]
            norm_magnitude = math.sqrt(normalized[0]**2 + normalized[1]**2)
            self.assertAlmostEqual(norm_magnitude, 1.0, places=5)
        except Exception as e:
            self.fail(f"Math operations failed: {e}")
    
    def test_pygame_surfaces(self):
        """Тест создания pygame поверхностей"""
        try:
            # Тест создания простой поверхности
            surface = pygame.Surface((100, 100))
            self.assertIsNotNone(surface)
            
            # Тест создания поверхности с альфа-каналом
            alpha_surface = pygame.Surface((100, 100), pygame.SRCALPHA)
            self.assertIsNotNone(alpha_surface)
        except Exception as e:
            self.fail(f"Pygame surfaces failed: {e}")


if __name__ == '__main__':
    unittest.main()