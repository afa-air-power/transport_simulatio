#!/usr/bin/env python3
"""
Основной запускальщик тестов для проекта Traffic Simulation.

Этот скрипт позволяет запускать все тесты или конкретные категории тестов
с различными опциями настройки.

Использование:
    python tests/test_runner.py                    # Запуск всех тестов
    python tests/test_runner.py --unit             # Только модульные тесты
    python tests/test_runner.py --integration      # Только интеграционные тесты
    python tests/test_runner.py --verbose          # Подробный вывод
    python tests/test_runner.py --coverage         # С покрытием кода
"""

import unittest
import sys
import os
import argparse
import time
from io import StringIO

# Добавляем корневую директорию проекта в PATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Импортируем все тестовые модули
from tests.test_entities import TestVehicle, TestCar, TestPedestrian
from tests.test_traffic_controller import TestLightLens, TestTrafficLight, TestTrafficController
from tests.test_simulation import TestTrafficSimulation, TestCar as TestSimCar, TestPedestrian as TestSimPed
from tests.test_utils import TestCrosswalk, TestDrawingFunctions, TestVisualEffects, TestUtilityFunctions, TestColorUtilities
from tests.test_integration import TestTrafficSimulationIntegration, TestUIIntegration, TestSystemIntegration


class TestResult:
    """Класс для хранения результатов тестов"""
    def __init__(self):
        self.tests_run = 0
        self.failures = 0
        self.errors = 0
        self.skipped = 0
        self.success_rate = 0.0
        self.execution_time = 0.0
        self.detailed_results = []


class ColoredTestResult(unittest.TextTestResult):
    """Результат теста с цветным выводом"""
    
    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.success_count = 0
        
    def addSuccess(self, test):
        super().addSuccess(test)
        self.success_count += 1
        if self.verbosity > 1:
            self.stream.write(f"\033[92m✓ {self.getDescription(test)}\033[0m\n")
        else:
            self.stream.write('\033[92m.\033[0m')
            
    def addError(self, test, err):
        super().addError(test, err)
        self.stream.write(f"\033[91mE\033[0m")
        if self.verbosity > 1:
            self.stream.write(f"\033[91m✗ {self.getDescription(test)} - ERROR\033[0m\n")
            
    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.stream.write(f"\033[93mF\033[0m")
        if self.verbosity > 1:
            self.stream.write(f"\033[93m✗ {self.getDescription(test)} - FAIL\033[0m\n")
            
    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.stream.write(f"\033[94mS\033[0m")
        if self.verbosity > 1:
            self.stream.write(f"\033[94m- {self.getDescription(test)} - SKIPPED: {reason}\033[0m\n")


class TestSuite:
    """Основной класс для управления тестами"""
    
    def __init__(self):
        self.unit_tests = [
            TestVehicle,
            TestCar, 
            TestPedestrian,
            TestLightLens,
            TestTrafficLight,
            TestTrafficController,
            TestCrosswalk,
            TestDrawingFunctions,
            TestVisualEffects,
            TestUtilityFunctions,
            TestColorUtilities
        ]
        
        self.simulation_tests = [
            TestTrafficSimulation,
            TestSimCar,
            TestSimPed
        ]
        
        self.integration_tests = [
            TestTrafficSimulationIntegration,
            TestUIIntegration,
            TestSystemIntegration
        ]
        
    def create_suite(self, test_types=['unit', 'simulation', 'integration']):
        """Создает набор тестов на основе указанных типов"""
        suite = unittest.TestSuite()
        
        if 'unit' in test_types:
            for test_class in self.unit_tests:
                suite.addTests(unittest.TestLoader().loadTestsFromTestCase(test_class))
                
        if 'simulation' in test_types:
            for test_class in self.simulation_tests:
                suite.addTests(unittest.TestLoader().loadTestsFromTestCase(test_class))
                
        if 'integration' in test_types:
            for test_class in self.integration_tests:
                suite.addTests(unittest.TestLoader().loadTestsFromTestCase(test_class))
                
        return suite
    
    def run_tests(self, suite, verbosity=1):
        """Запускает тесты и возвращает результаты"""
        start_time = time.time()
        
        # Создаем кастомный runner с цветным выводом
        stream = sys.stdout
        runner = unittest.TextTestRunner(
            stream=stream,
            verbosity=verbosity,
            resultclass=ColoredTestResult
        )
        
        result = runner.run(suite)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Создаем объект результата
        test_result = TestResult()
        test_result.tests_run = result.testsRun
        test_result.failures = len(result.failures)
        test_result.errors = len(result.errors)
        test_result.skipped = len(result.skipped)
        test_result.execution_time = execution_time
        
        if result.testsRun > 0:
            success_count = result.testsRun - test_result.failures - test_result.errors
            test_result.success_rate = (success_count / result.testsRun) * 100
        
        return test_result, result
        
    def print_summary(self, test_result, detailed_result):
        """Выводит сводку результатов тестов"""
        print("\n" + "="*70)
        print("СВОДКА РЕЗУЛЬТАТОВ ТЕСТОВ")
        print("="*70)
        
        print(f"Всего тестов:     {test_result.tests_run}")
        print(f"Успешно:          {test_result.tests_run - test_result.failures - test_result.errors}")
        print(f"Ошибки:           {test_result.errors}")
        print(f"Неудачи:          {test_result.failures}")
        print(f"Пропущено:        {test_result.skipped}")
        print(f"Процент успеха:   {test_result.success_rate:.1f}%")
        print(f"Время выполнения: {test_result.execution_time:.2f} сек")
        
        # Цветовая индикация результата
        if test_result.success_rate >= 95:
            status_color = "\033[92m"  # Зеленый
            status = "ОТЛИЧНО"
        elif test_result.success_rate >= 80:
            status_color = "\033[93m"  # Желтый
            status = "ХОРОШО"
        else:
            status_color = "\033[91m"  # Красный
            status = "ТРЕБУЕТ ВНИМАНИЯ"
            
        print(f"\nОбщий статус: {status_color}{status}\033[0m")
        
        # Детальная информация об ошибках
        if detailed_result.errors:
            print(f"\n{status_color}ОШИБКИ:\033[0m")
            for test, error in detailed_result.errors:
                print(f"  {test}: {error.splitlines()[-1]}")
                
        if detailed_result.failures:
            print(f"\n{status_color}НЕУДАЧИ:\033[0m")
            for test, failure in detailed_result.failures:
                print(f"  {test}: {failure.splitlines()[-1]}")
        
        print("="*70)


def main():
    """Главная функция запуска тестов"""
    parser = argparse.ArgumentParser(description='Запуск автотестов для Traffic Simulation')
    
    parser.add_argument('--unit', action='store_true', 
                       help='Запустить только модульные тесты')
    parser.add_argument('--simulation', action='store_true',
                       help='Запустить только тесты симуляции')
    parser.add_argument('--integration', action='store_true',
                       help='Запустить только интеграционные тесты')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Подробный вывод')
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='Минимальный вывод')
    parser.add_argument('--coverage', action='store_true',
                       help='Запустить с анализом покрытия кода')
    parser.add_argument('--pattern', type=str,
                       help='Паттерн для фильтрации тестов')
    
    args = parser.parse_args()
    
    # Определяем типы тестов для запуска
    test_types = []
    if args.unit:
        test_types.append('unit')
    if args.simulation:
        test_types.append('simulation')
    if args.integration:
        test_types.append('integration')
        
    # Если ничего не указано, запускаем все
    if not test_types:
        test_types = ['unit', 'simulation', 'integration']
    
    # Определяем уровень детализации вывода
    verbosity = 1
    if args.verbose:
        verbosity = 2
    elif args.quiet:
        verbosity = 0
    
    print("🚦 Traffic Simulation - Автотесты")
    print("="*50)
    print(f"Запуск тестов: {', '.join(test_types)}")
    print(f"Уровень детализации: {verbosity}")
    
    if args.coverage:
        print("📊 Анализ покрытия кода: ВКЛ")
        try:
            import coverage
            cov = coverage.Coverage()
            cov.start()
        except ImportError:
            print("⚠️  Модуль coverage не найден. Установите: pip install coverage")
            args.coverage = False
    
    print("-"*50)
    
    # Создаем и запускаем тесты
    test_suite = TestSuite()
    suite = test_suite.create_suite(test_types)
    
    # Фильтрация по паттерну
    if args.pattern:
        filtered_suite = unittest.TestSuite()
        for test in suite:
            if args.pattern.lower() in str(test).lower():
                filtered_suite.addTest(test)
        suite = filtered_suite
    
    # Запускаем тесты
    test_result, detailed_result = test_suite.run_tests(suite, verbosity)
    
    # Выводим сводку
    test_suite.print_summary(test_result, detailed_result)
    
    # Покрытие кода
    if args.coverage:
        print("\n📊 АНАЛИЗ ПОКРЫТИЯ КОДА")
        print("-"*30)
        try:
            cov.stop()
            cov.save()
            print("Отчет о покрытии сохранен. Запустите:")
            print("  coverage report")
            print("  coverage html")
        except:
            print("Ошибка при сохранении данных покрытия")
    
    # Возвращаем код выхода
    if test_result.errors or test_result.failures:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()