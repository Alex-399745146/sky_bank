# test_data_extract.py
"""Модуль с тестами"""

import os
from src.data_extract import get_data_xlsx, get_df_from_xlsx, get_convert_json_in_data


def test_get_data_xlsx(fix_path_file_xlsx):
    if not os.path.exists(fix_path_file_xlsx):
        raise FileNotFoundError(f"Файл не найден: {path_file_xlsx}")

    full_tzs: list = get_data_xlsx(fix_path_file_xlsx)

    for tz in full_tzs:
        assert 'Дата операции' in tz, 'Исходные данные не корректны'
        assert 'Номер карты' in tz, 'Исходные данные не корректны'
        assert 'Статус' in tz, 'Исходные данные не корректны'
        assert 'Сумма операции' in tz, 'Исходные данные не корректны'
        assert 'Категория' in tz, 'Исходные данные не корректны'
        assert 'Сумма операции с округлением' in tz, 'Исходные данные не корректны'

        assert isinstance(tz['Дата операции'], str)
        assert isinstance(tz['Статус'], str)
        assert isinstance(tz['Сумма операции'], float)
        assert isinstance(tz['Сумма операции с округлением'], float)


def test_get_df_from_xlsx(fix_path_file_xlsx):
    full_tzs_df = get_df_from_xlsx(fix_path_file_xlsx)

    assert 'Дата операции' in full_tzs_df.columns, "Столбец 'Дата операции' не найден!"


def test_get_convert_json_in_data(fix_path_file_json):
    config_dict = get_convert_json_in_data(fix_path_file_json)

    assert isinstance(config_dict, dict)
    assert len(config_dict) == 2
    assert isinstance(config_dict['user_currencies'], list)
    assert isinstance(config_dict['user_stocks'], list)
