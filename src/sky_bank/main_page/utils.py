# utils.py
""" Модуль вспомогательных функций выдающих данные основным функциям модуля views.py """

import os
from src.sky_bank.data_extract import get_data_xlsx
from datetime import datetime
from collections import defaultdict


# Tack_1 Приветствие
def get_status_time_message() -> str:
    """ Реализация приветствия в зависимости от времени суток """
    now_hour = datetime.now().hour
    if 5 <= now_hour < 12:
        message = "утро"
    elif 12 <= now_hour < 17:
        message = "день"
    elif 17 <= now_hour < 23:
        message = "вечер"
    else:
        message = "ночи"
    return message


# Task_2_1 По каждой карте
def get_tzs_filter_date(tzs: list, date_string: str) -> list:
    """ Фильтрация трансакций по временному периоду """
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
def get_count_carts(tzs: list) -> dict[str, float]:
    """ Подсчитывает количество уникальных карт у клиента с суммой оборота по ним """
    card_sums = defaultdict(float)
    for tz in tzs:
        card_number = tz["Номер карты"]
        if not isinstance(card_number, str):
            continue
        amount = float(tz["Сумма платежа"])
        card_sums[card_number] += abs(amount)
    return dict(card_sums)


# Tack_3 Топы транзакций по сумме платежа, отсортированы если надо 5 то [:5]
def get_sort_by_date(tzs: list[dict], direct_sort: bool = True) -> list:
    """
    Принимает список словарей и параметр сортировки (по умолчанию — убывание).
    Возвращает новый список, отсортированный по сумме платежа.
    """
    tzs_sorted = sorted(tzs, key=lambda tz: abs(tz["Сумма платежа"]), reverse=direct_sort)
    return tzs_sorted


if __name__ == "__main__":  # pragma: no cover
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))) # директ проекта
    path_file_xlsx = os.path.join(project_root, "data", "operations.xlsx")

    date_filter = '20.05.2020'  # %d.%m.%Y конечная дата текущего месяца выборки
    transactions = get_data_xlsx(path_file_xlsx)

    date_filter_tzs = get_tzs_filter_date(transactions, date_filter)
    for tz in date_filter_tzs:
        print(tz)

    # carts = get_count_carts(date_filter_tzs)
    # for k, v in carts.items():
    #     print(f"{k}: {round(v, 2)}")

    # date_sort_tzs = get_sort_by_date(transactions)
    # for i in range(5):
    #     print(date_sort_tzs[i])
