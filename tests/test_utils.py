# test_utils.py
"""Модуль с тестами"""

from datetime import datetime
from unittest.mock import patch

from src.main_page.utils import get_count_carts, get_sort_by_date, get_status_time_message, get_tzs_filter_date


@patch("src.main_page.utils.datetime")
def test_get_status_time_message(mock_datetime):
    """Замокаем функцию datetime.now() проверим логику функции"""
    mock_datetime.now.return_value = datetime(2023, 1, 1, 4, 30, 0)
    result = get_status_time_message()
    assert result == "Доброй ночи"

    mock_datetime.now.return_value = datetime(2023, 1, 1, 6, 30, 0)
    result_1 = get_status_time_message()
    assert result_1 == "Доброе утро"

    mock_datetime.now.return_value = datetime(2023, 1, 1, 13, 30, 0)
    result_2 = get_status_time_message()
    assert result_2 == "Добрый день"

    mock_datetime.now.return_value = datetime(2023, 1, 1, 18, 30, 0)
    result_3 = get_status_time_message()
    assert result_3 == "Добрый вечер"


def test_get_status_time_message_2():
    """Проверим правильность типа предоставляемых данных"""
    result = get_status_time_message()

    assert isinstance(result, str)


def test_tzs_filter_date(fix_tzs_date):
    """Фильтрация трансакций по временному периоду"""
    date_filter = "02.05.2021"
    result = get_tzs_filter_date(fix_tzs_date, date_filter)

    assert isinstance(result, list)
    assert len(result) == 8


def test_count_carts(fix_tzs_date):
    """Определение уникальных номеров картв в отфильтрованных данных"""
    result = get_count_carts(fix_tzs_date)

    assert isinstance(result, list)
    assert len(result) == 2


def test_sort_by_date(fix_tzs_date):
    """Сортировки по тратам отфильтрованного массива данных"""
    result = get_sort_by_date(fix_tzs_date)

    assert isinstance(result, list)
    assert len(result) == 5
    assert abs(result[0]["amount"]) == 1675.8
    assert abs(result[-1]["amount"]) == 128.0
