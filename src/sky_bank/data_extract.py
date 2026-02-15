# data_extract.py
"""
В модуле data_extract.py реализованы функции считывания данных
из файлов разного формата.
"""
import json
import os
import pandas as pd


def get_data_xlsx(path_file: str) -> list[dict]:
    """ Считывание данных из файла.xlsx и возвращение в виде списка словарей """
    df = pd.read_excel(path_file)
    # Параметр 'records' определяет - одна запись, одна строка таблицы.
    result = df.to_dict('records')
    return result


def get_data_json(path_file: str) -> dict:
    """ Считывание данных из файла.json и возвращение в виде словаря """
    with open(path_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


if __name__ == "__main__":  # pragma: no cover
    current_dir = os.path.dirname(__file__) # текущий директ
    project_root = os.path.dirname(os.path.dirname(current_dir)) # директ проекта
    # Абсолютный путь C:\Python\Projects\sky_bank\data\operations.xlsx
    path_file_xlsx = os.path.join(project_root, "data", "operations.xlsx")
    path_file_json = os.path.join(project_root, "user_settings.json")

    tzs = get_data_xlsx(path_file_xlsx)
    # for tz in tzs[:5]:
    #     print(tz)

    config_user = get_data_json(path_file_json)
    print(config_user)
    print(config_user['user_currencies'])
    print(config_user['user_stocks'])
