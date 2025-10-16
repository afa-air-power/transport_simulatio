"""
Конфигурация для pytest.
Содержит общие фикстуры и настройки для всех тестов.
"""

import pytest
import pygame
import sys
import os
from unittest.mock import MagicMock, patch

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Глобальные импорты для тестов
from simulation import TrafficSimulation, Car, Pedestrian
from traffic_controller import TrafficController
from constants import *


@pytest.fixture(scope="session", autouse=True)
def pygame_init():
    """Автоматическая инициализация pygame для всех тестов"""
    pygame.init()
    # Устанавливаем headless режим для CI/CD
    os.environ['SDL_VIDEODRIVER'] = 'dummy'
    yield
    pygame.quit()


@pytest.fixture
def mock_screen():
    """Мок объект экрана pygame"""
    screen = MagicMock()
    screen.get_width.return_value = 800
    screen.get_height.return_value = 600
    return screen


@pytest.fixture
def traffic_simulation():
    """Фикстура для создания экземпляра симуляции трафика"""
    return TrafficSimulation()


@pytest.fixture
def traffic_controller():
    """Фикстура для создания контроллера трафика"""
    return TrafficController()


@pytest.fixture
def sample_car():
    """Фикстура для создания тестового автомобиля"""
    return Car([100, 100], [1, 0], 30, (255, 0, 0))


@pytest.fixture
def sample_pedestrian():
    """Фикстура для создания тестового пешехода"""
    return Pedestrian([50, 50], [150, 150])


@pytest.fixture
def multiple_cars():
    """Фикстура для создания нескольких тестовых автомобилей"""
    cars = []
    for i in range(5):
        car = Car([i * 30, 0], [0, 1], 30, (255, i * 50, 0))
        cars.append(car)
    return cars


@pytest.fixture
def multiple_pedestrians():
    """Фикстура для создания нескольких тестовых пешеходов"""
    pedestrians = []
    for i in range(3):
        ped = Pedestrian([0, i * 40], [200, i * 40])
        pedestrians.append(ped)
    return pedestrians


@pytest.fixture
def simulation_with_entities(traffic_simulation, multiple_cars, multiple_pedestrians):
    """Фикстура для симуляции с предустановленными объектами"""
    traffic_simulation.cars.extend(multiple_cars)
    traffic_simulation.pedestrians.extend(multiple_pedestrians)
    return traffic_simulation


@pytest.fixture(scope="function")
def temp_config_file(tmp_path):
    """Фикстура для создания временного конфигурационного файла"""
    config_content = '''
    {
        "car_spawn_rate": 2.0,
        "pedestrian_spawn_rate": 1.5,
        "traffic_mode": "dynamic",
        "num_lanes": 3,
        "simulation_speed": 1.0
    }
    '''
    config_file = tmp_path / "test_config.json"
    config_file.write_text(config_content)
    return str(config_file)


@pytest.fixture
def mock_time():
    """Мок для функций времени"""
    with patch('time.time') as mock:
        mock.return_value = 1000.0  # Фиксированное время
        yield mock


@pytest.fixture
def no_pygame_display():
    """Отключает pygame display для headless тестирования"""
    with patch('pygame.display.set_mode') as mock_display:
        mock_surface = MagicMock()
        mock_surface.get_width.return_value = 800
        mock_surface.get_height.return_value = 600
        mock_display.return_value = mock_surface
        yield mock_surface


# Маркеры для категоризации тестов
def pytest_configure(config):
    """Конфигурация pytest с кастомными маркерами"""
    config.addinivalue_line("markers", "unit: Модульные тесты")
    config.addinivalue_line("markers", "integration: Интеграционные тесты") 
    config.addinivalue_line("markers", "simulation: Тесты симуляции")
    config.addinivalue_line("markers", "slow: Медленные тесты")


def pytest_collection_modifyitems(config, items):
    """Автоматическое назначение маркеров на основе имени файла/класса"""
    for item in items:
        # Автоматически назначаем маркеры на основе пути к файлу
        if "test_integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        elif any(name in item.nodeid for name in ["test_entities", "test_traffic_controller", "test_utils"]):
            item.add_marker(pytest.mark.unit)
        elif "test_simulation" in item.nodeid:
            item.add_marker(pytest.mark.simulation)
            
        # Маркируем медленные тесты
        if any(slow_test in item.name for slow_test in ["full_cycle", "performance", "load"]):
            item.add_marker(pytest.mark.slow)


# Хелперные функции для тестов
class TestHelpers:
    """Вспомогательные функции для тестов"""
    
    @staticmethod
    def create_test_car(x=0, y=0, heading_x=1, heading_y=0, speed=30, color=(255, 0, 0)):
        """Создает тестовый автомобиль с заданными параметрами"""
        return Car([x, y], [heading_x, heading_y], speed, color)
    
    @staticmethod
    def create_test_pedestrian(start_x=0, start_y=0, target_x=100, target_y=100):
        """Создает тестового пешехода с заданными параметрами"""
        return Pedestrian([start_x, start_y], [target_x, target_y])
    
    @staticmethod
    def distance_between_points(point1, point2):
        """Вычисляет расстояние между двумя точками"""
        return ((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)**0.5
    
    @staticmethod
    def normalize_vector(vector):
        """Нормализует вектор"""
        magnitude = (vector[0]**2 + vector[1]**2)**0.5
        if magnitude == 0:
            return [0, 0]
        return [vector[0] / magnitude, vector[1] / magnitude]


@pytest.fixture
def test_helpers():
    """Фикстура для предоставления вспомогательных функций"""
    return TestHelpers()


# Настройки для headless тестирования в CI/CD
@pytest.fixture(autouse=True)
def setup_headless_mode():
    """Настройка headless режима для CI/CD систем"""
    if os.environ.get('CI') or os.environ.get('GITHUB_ACTIONS'):
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        os.environ['SDL_AUDIODRIVER'] = 'dummy'


# Фикстура для проверки производительности
@pytest.fixture
def performance_timer():
    """Фикстура для измерения времени выполнения тестов"""
    import time
    start_time = time.time()
    yield
    end_time = time.time()
    execution_time = end_time - start_time
    if execution_time > 1.0:  # Предупреждение для медленных тестов
        pytest.warns(UserWarning, f"Тест выполнялся {execution_time:.2f} секунд")


# Пропуск тестов в зависимости от окружения
def pytest_runtest_setup(item):
    """Пропуск тестов в зависимости от условий окружения"""
    # Пропускаем GUI тесты в headless режиме
    if item.get_closest_marker("gui") and os.environ.get('SDL_VIDEODRIVER') == 'dummy':
        pytest.skip("GUI тест пропущен в headless режиме")
    
    # Пропускаем медленные тесты если указано
    if item.get_closest_marker("slow") and item.config.getoption("--skip-slow"):
        pytest.skip("Медленный тест пропущен")


def pytest_addoption(parser):
    """Добавление кастомных опций командной строки"""
    parser.addoption(
        "--skip-slow", action="store_true", default=False,
        help="Пропустить медленные тесты"
    )
    parser.addoption(
        "--run-integration", action="store_true", default=False,
        help="Запустить интеграционные тесты"
    )