# main.py
"""Запуск основных функциональностей проекта"""

import os

from src.data_extract import get_convert_json_in_data, get_data_xlsx, get_df_from_xlsx
from src.main_page.views import get_main_page
from src.reports_page.reports import spending_by_workday
from src.services_page.services import get_category_tzs, get_tzs_filter_date

if __name__ == "__main__":  # pragma: no cover
    # Директории входа инфы
    project_root = os.path.dirname(__file__)  # директ проекта
    path_file_xlsx = os.path.join(project_root, "data", "operations.xlsx")
    path_file_json = os.path.join(project_root, "user_settings.json")

    # Переменные аргументов ввода данных
    full_tzs = get_data_xlsx(path_file_xlsx)
    date_filter = "02.05.2021"
    config = get_convert_json_in_data(path_file_json)

    date_month_year = date_filter[3:]
    filter_date_tzs = get_tzs_filter_date(full_tzs, date_month_year)

    full_tzs_df = get_df_from_xlsx(path_file_xlsx)

    # Веб-страницы
    data_main = get_main_page(full_tzs, date_filter, config)
    # Сервисы
    data_services = get_category_tzs(filter_date_tzs)
    # Отчёты
    data_reports = spending_by_workday(full_tzs_df, date_filter)

    # Демонстрация данных веб-страницы
    # print(type(data_main))
    # for k, v in data_main.items():
    #     print(f"{k}: {v}")

    # Демонстрация данных по сервисам
    # for key, value in data_services.items():
    #     print(f"{key}: {value:.2f}")

    # Демонстрация данных по отчётам
    # print(data_reports)
