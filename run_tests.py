#!/usr/bin/env python3
"""
Простой скрипт для запуска автотестов Traffic Simulation.

Этот скрипт обеспечивает простой способ запуска всех тестов
с базовой отчетностью и поддержкой различных опций.

Использование:
    python run_tests.py                 # Запуск всех тестов
    python run_tests.py --fast          # Быстрые тесты (без интеграционных)
    python run_tests.py --coverage      # С покрытием кода
    python run_tests.py --html-report   # HTML отчет
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path


def run_command(command, description=""):
    """Выполняет команду и возвращает код возврата"""
    print(f"🔄 {description}")
    print(f"Команда: {' '.join(command)}")
    print("-" * 50)
    
    try:
        result = subprocess.run(command, check=False, capture_output=False)
        return result.returncode
    except FileNotFoundError:
        print(f"❌ Ошибка: команда '{command[0]}' не найдена")
        return 1


def check_dependencies():
    """Проверяет наличие необходимых зависимостей"""
    required_packages = ['pygame', 'unittest']
    optional_packages = ['pytest', 'coverage']
    
    print("🔍 Проверка зависимостей...")
    
    missing_required = []
    missing_optional = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing_required.append(package)
            print(f"❌ {package} (обязательный)")
    
    for package in optional_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing_optional.append(package)
            print(f"⚠️  {package} (опциональный)")
    
    if missing_required:
        print(f"\n❌ Отсутствуют обязательные пакеты: {', '.join(missing_required)}")
        print("Установите их командой: pip install " + " ".join(missing_required))
        return False
    
    if missing_optional:
        print(f"\n⚠️  Отсутствуют опциональные пакеты: {', '.join(missing_optional)}")
        print("Для расширенных возможностей установите: pip install " + " ".join(missing_optional))
    
    print("✅ Проверка зависимостей завершена")
    return True


def run_unittest_tests():
    """Запускает тесты через unittest"""
    command = [
        sys.executable, 
        "-m", "unittest", 
        "discover", 
        "-s", "tests", 
        "-p", "test_*.py",
        "-v"
    ]
    
    return run_command(command, "Запуск тестов через unittest")


def run_pytest_tests(args):
    """Запускает тесты через pytest"""
    command = [sys.executable, "-m", "pytest"]
    
    # Добавляем опции в зависимости от аргументов
    if args.verbose:
        command.extend(["-v", "-s"])
    
    if args.fast:
        command.extend(["-m", "not integration and not slow"])
    
    if args.coverage:
        try:
            __import__('coverage')
            command.extend(["--cov=.", "--cov-report=html", "--cov-report=term"])
        except ImportError:
            print("⚠️  Модуль coverage не установлен. Покрытие кода недоступно.")
    
    if args.html_report:
        command.extend(["--html=reports/test_report.html", "--self-contained-html"])
        # Создаем директорию для отчетов
        os.makedirs("reports", exist_ok=True)
    
    # Добавляем путь к тестам
    command.append("tests/")
    
    return run_command(command, "Запуск тестов через pytest")


def run_custom_test_runner():
    """Запускает кастомный test runner"""
    command = [sys.executable, "tests/test_runner.py"]
    return run_command(command, "Запуск через кастомный test runner")


def generate_test_report():
    """Генерирует сводный отчет о тестах"""
    print("\n📊 ГЕНЕРАЦИЯ ОТЧЕТА О ТЕСТАХ")
    print("=" * 50)
    
    # Информация о проекте
    project_root = Path(__file__).parent
    test_files = list(project_root.glob("tests/test_*.py"))
    
    print(f"Корневая директория: {project_root}")
    print(f"Количество тестовых файлов: {len(test_files)}")
    print(f"Тестовые модули:")
    for test_file in test_files:
        print(f"  - {test_file.name}")
    
    # Подсчет количества тестов (приблизительно)
    total_tests = 0
    for test_file in test_files:
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
            total_tests += content.count('def test_')
    
    print(f"\nПриблизительное количество тестов: {total_tests}")
    
    # Проверка конфигурационных файлов
    config_files = ['pytest.ini', 'tests/conftest.py']
    print(f"\nКонфигурационные файлы:")
    for config_file in config_files:
        if (project_root / config_file).exists():
            print(f"  ✅ {config_file}")
        else:
            print(f"  ❌ {config_file}")


def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(description='Запуск автотестов Traffic Simulation')
    
    parser.add_argument('--fast', action='store_true',
                       help='Быстрые тесты (пропустить интеграционные и медленные)')
    parser.add_argument('--coverage', action='store_true',
                       help='Запустить с анализом покрытия кода')
    parser.add_argument('--html-report', action='store_true',
                       help='Сгенерировать HTML отчет')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Подробный вывод')
    parser.add_argument('--runner', choices=['unittest', 'pytest', 'custom'],
                       default='pytest', help='Выбор test runner')
    parser.add_argument('--check-deps', action='store_true',
                       help='Только проверить зависимости')
    parser.add_argument('--report-only', action='store_true',
                       help='Только сгенерировать отчет о тестах')
    
    args = parser.parse_args()
    
    print("🚦 Traffic Simulation - Автотесты")
    print("=" * 50)
    
    # Только проверка зависимостей
    if args.check_deps:
        check_dependencies()
        return 0
    
    # Только отчет
    if args.report_only:
        generate_test_report()
        return 0
    
    # Проверяем зависимости
    if not check_dependencies():
        return 1
    
    print(f"\n🚀 Запуск тестов с runner: {args.runner}")
    if args.fast:
        print("⚡ Быстрый режим (без интеграционных тестов)")
    if args.coverage:
        print("📈 Анализ покрытия кода включен")
    if args.html_report:
        print("📄 Генерация HTML отчета включена")
    
    print("-" * 50)
    
    # Запускаем тесты в зависимости от выбранного runner
    if args.runner == 'unittest':
        return_code = run_unittest_tests()
    elif args.runner == 'pytest':
        return_code = run_pytest_tests(args)
    elif args.runner == 'custom':
        return_code = run_custom_test_runner()
    else:
        print(f"❌ Неизвестный runner: {args.runner}")
        return 1
    
    # Генерируем отчет
    generate_test_report()
    
    # Финальное сообщение
    print("\n" + "=" * 50)
    if return_code == 0:
        print("🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
    else:
        print("❌ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОШЛИ")
        print("Проверьте вывод выше для получения подробностей")
    print("=" * 50)
    
    return return_code


if __name__ == '__main__':
    sys.exit(main())