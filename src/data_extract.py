# data_extract.py
"""
В модуле data_extract.py реализованы функции считывания данных
из файлов разного формата.
"""

import json
import os
from typing import Any

import pandas as pd


def get_data_xlsx(path_file: str) -> Any:
    """Считывание данных из файла.xlsx и возвращение в виде списка словарей"""
    df = pd.read_excel(path_file)
    result = df.to_dict("records")  # 'records' определяет одну запись в одну строку
    return result


def get_convert_json_in_data(path_file: str) -> Any:
    """Считывание данных из файла.json c конфигами и возвращение в виде словаря"""
    with open(path_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def get_convert_data_in_json(data: dict, name_file: str) -> Any:
    """Вводимые данные сохраняем в json формате"""
    with open(name_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def get_df_from_xlsx(path_file: str) -> pd.DataFrame:
    """Вывод данных из файла.xlsx в виде DataFrame таблицы"""
    df = pd.read_excel(path_file)
    return df


if __name__ == "__main__":  # pragma: no cover
    # Директории
    current_dir = os.path.dirname(__file__)  # текущий директ
    project_root = os.path.dirname(current_dir)  # директ проекта

    path_file_xlsx = os.path.join(project_root, "data", "operations.xlsx")
    path_file_json = os.path.join(project_root, "user_settings.json")

    # Проверка считанных данных из файла.xlsx
    tzs = get_data_xlsx(path_file_xlsx)

    # print(type(tzs))
    # for tz in tzs[:5]:
    #     print(type(tz['Номер карты']))

    # Просмотреть конфиги пользователя
    # config_user = get_convert_json_in_data(path_file_json)
    # print(config_user)
    # print(type(config_user))

    # Просмотр DataFrame
    data_df = get_df_from_xlsx(path_file_xlsx)
    print(data_df.head())
