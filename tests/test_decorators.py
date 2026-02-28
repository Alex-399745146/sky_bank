# test_decorators.py
"""Модуль с тестами"""

import os

from src.services_page.decorators import log


def test_log() -> None:
    """Тест декораторной функции"""
    # Создаём временный файл для логов
    test_log_file = "test_file.log"

    @log(test_log_file)
    def test_function(x, y):
        return x + y

    result = test_function(5, 3)

    # Проверяем результат функции
    assert result == 8

    # Проверяем файл логов
    with open(test_log_file, "r", encoding="utf-8") as f:
        log_content = f.read()

    assert "test_function ok" in log_content

    os.remove(test_log_file)
