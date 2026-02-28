# services.py
"""Модуль набора основных функций выдающих информацию для страницы сервисов"""

import os
from collections import defaultdict
from datetime import datetime

from src.data_extract import get_convert_data_in_json, get_data_xlsx
from src.services_page.decorators import log


def get_tzs_filter_date(full_tzs: list, date_string: str) -> list:
    """Фильтрация трансакций в указанном периоде, период 3 месяца"""
    obj_date = datetime.strptime(date_string, "%m.%Y")

    filter_month = obj_date.month
    filter_year = obj_date.year

    filter_tzs = []

    for tz in full_tzs:
        tz_parser_datetime = datetime.strptime(tz["Дата операции"], "%d.%m.%Y %H:%M:%S")
        parser_month = tz_parser_datetime.month
        parser_year = tz_parser_datetime.year

        if filter_year == parser_year and filter_month == parser_month:
            filter_tzs.append(tz)
        else:
            continue

    return filter_tzs


@log()
def get_category_tzs(filter_tzs: list, sort_direct: bool = True) -> dict:
    """Реализация отчетов по отфильтрованному списку 3х месяцев"""
    category_sums: defaultdict = defaultdict(float)

    for tz in filter_tzs:
        category = str(tz["Категория"])
        amount = round(tz["Сумма операции с округлением"], 2)

        category_sums[category] += amount

    result = dict(sorted(category_sums.items(), key=lambda item: item[1], reverse=sort_direct))

    get_convert_data_in_json(result, "services_page.json")
    return result


if __name__ == "__main__":  # pragma: no cover
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))  # директ проекта
    path_file_xlsx = os.path.join(project_root, "data", "operations.xlsx")

    # Вводные данные
    date_month_year = "05.2021"
    tzs = get_data_xlsx(path_file_xlsx)

    # Для упрощения и чистоты кода ввод данных 2 а не 3 аргумента
    filter_date_tzs = get_tzs_filter_date(tzs, date_month_year)
    result = get_category_tzs(filter_date_tzs)

    for key, value in result.items():
        print(f"{key}: {value:.2f}")
