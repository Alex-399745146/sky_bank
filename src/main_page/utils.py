# utils.py
"""Модуль вспомогательных функций выдающих данные основным функциям модуля views.py"""

import os
from datetime import datetime

from src.data_extract import get_data_xlsx


# Tack_1 Приветствие
def get_status_time_message() -> str:
    """Реализация приветствия в зависимости от времени суток"""
    now_hour = datetime.now().hour
    if 5 <= now_hour < 12:
        message = "Доброе утро"
    elif 12 <= now_hour < 17:
        message = "Добрый день"
    elif 17 <= now_hour < 23:
        message = "Добрый вечер"
    else:
        message = "Доброй ночи"
    return message


# Task_2_1 По каждой карте
def get_tzs_filter_date(tzs: list, date_string: str) -> list:
    """Фильтрация трансакций по временному периоду"""
    down_date_filter = datetime.strptime(date_string, "%d.%m.%Y")
    start_date_filter = datetime(down_date_filter.year, down_date_filter.month, 1)
    filter_tzs = []
    for tz in tzs:
        tz_datetime = datetime.strptime(tz["Дата операции"], "%d.%m.%Y %H:%M:%S")
        if start_date_filter <= tz_datetime <= down_date_filter:
            filter_tzs.append(tz)
        else:
            continue
    return filter_tzs


# Task_2_2 По каждой карте
def get_count_carts(tzs: list) -> list[dict]:
    """Подсчитывает количество уникальных карт у клиента с суммой оборота по ним"""
    card_sums: dict = {}

    for tz in tzs:

        card_number = tz["Номер карты"]
        amount_str = tz["Сумма платежа"]

        # Проверяем, что номер карты — строка
        if not isinstance(card_number, str):
            continue

        # Очищаем номер карты от нецифровых символов
        card_digits = "".join(filter(str.isdigit, card_number))

        # Берём последние 4 цифры (или меньше, если карта короткая)
        last_digits = card_digits[-4:] if len(card_digits) >= 4 else card_digits

        # Преобразуем сумму платежа в число
        try:
            amount = float(amount_str)

            if last_digits in card_sums:
                current_sum = card_sums[last_digits]
            else:
                current_sum = 0.0

            new_sum = current_sum + abs(amount)
            card_sums[last_digits] = new_sum

        except (ValueError, TypeError):
            continue  # Пропускаем некорректные суммы

    result = []

    for last_digits, total_spent in card_sums.items():
        cashback = round(total_spent * 0.01, 2)  # Кэшбэк 1%

        result.append({"last_digits": last_digits, "total_spent": round(total_spent, 2), "cashback": cashback})

    return result


# Tack_3 Топы транзакций по сумме платежа
def get_sort_by_date(tzs: list[dict], direct_sort: bool = True) -> list:
    """Сортировка трансакций по сумме платежа"""
    tzs_sorted = sorted(tzs, key=lambda tz: abs(tz["Сумма платежа"]), reverse=direct_sort)

    result = []

    for tz in tzs_sorted:
        date_tz = tz["Дата операции"].split(" ")[0]
        amount_tz = tz["Сумма операции"]
        category_tz = tz["Категория"]
        description_tz = tz["Описание"]

        result.append({"date": date_tz, "amount": amount_tz, "category": category_tz, "description": description_tz})

    return result[:5]


if __name__ == "__main__":  # pragma: no cover
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))  # директ проекта
    path_file_xlsx = os.path.join(project_root, "data", "operations.xlsx")

    date_filter = "02.05.2021"  # фильтр от 1 числа месяца до date_filter
    tzs = get_data_xlsx(path_file_xlsx)

    # Реализация приветствия в зависимости от времени суток
    # print(get_status_time_message())

    # Фильтрация трансакций по временному периоду
    date_filter_tzs = get_tzs_filter_date(tzs, date_filter)
    # for tz in date_filter_tzs:
    #     print(tz)

    # Подсчитывает количество уникальных карт у клиента
    carts = get_count_carts(date_filter_tzs)
    # for cart in carts:
    #     print(cart)

    # Сортировка трансакций по сумме платежа
    date_sort_tzs = get_sort_by_date(date_filter_tzs)
    for i in date_sort_tzs:
        print(i)
