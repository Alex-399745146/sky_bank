# views.py
"""Модуль набора основных функций выдающих информацию для главной страницы"""

import os

from src.data_extract import get_convert_data_in_json, get_convert_json_in_data, get_data_xlsx
from src.main_page.external_api import get_current_exchange_rate, get_current_stock_price
from src.main_page.utils import (
    get_count_carts,
    get_sort_by_date,
    get_status_time_message,
    get_tzs_filter_date,
)


def get_main_page(tzs: list, date: str, config_user: dict) -> dict:
    result: dict = {}

    # Приветствие
    result["greeting"] = get_status_time_message()

    # По каждой карте
    tzs_filter_datetime: list = get_tzs_filter_date(tzs, date)
    unique_date: list = get_count_carts(tzs_filter_datetime)
    result["cards"] = unique_date

    # Топ транзакций по сумме платежа в указанный период
    result["top_transactions"] = get_sort_by_date(tzs_filter_datetime)

    # Курс валют
    currency_codes: list[str] = config_user["user_currencies"]
    result["currency_rates"] = get_current_exchange_rate(currency_codes)
    # Тайм слип или Asing библиотека по потокам.
    # Стоимость акций
    stock_codes: list[str] = config_user["user_stocks"]
    result["stock_prices"] = get_current_stock_price(stock_codes)

    get_convert_data_in_json(result)
    return result


if __name__ == "__main__":  # pragma: no cover
    # Директории
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))  # директ проекта
    path_file_xlsx = os.path.join(project_root, "data", "operations.xlsx")
    path_file_json = os.path.join(project_root, "user_settings.json")

    # Вводные данные
    transactions = get_data_xlsx(path_file_xlsx)
    date_filter = "20.05.2020"
    config = get_convert_json_in_data(path_file_json)

    data_page = get_main_page(transactions, date_filter, config)
    # print(data_page)
    for k, v in data_page.items():
        print(f"{k}: {v}")
