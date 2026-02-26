# test_external_api.py
"""Модуль с тестами"""

from src.main_page.external_api import get_current_exchange_rate, get_current_stock_price


def test_get_current_exchange_rate(fix_user_settings_dict):
    """Тест функции запрашивающей по api инфу по паром валют"""
    set_config = fix_user_settings_dict["user_currencies"]

    assert isinstance(set_config, list)

    result = get_current_exchange_rate(set_config)

    assert isinstance(result, list)

    if len(result) != 0:
        assert isinstance(result[0], dict)
        for item in result:
            assert item["currency"].isupper()
            assert isinstance(item["rate"], float)


def test_get_current_stock_price(fix_user_settings_dict):
    """Тест функции запрашивающей по api инфу по ценам акций"""
    set_config = fix_user_settings_dict["user_stocks"]
    len_set_config = len(set_config)

    assert isinstance(set_config, list)

    result = get_current_stock_price(set_config)

    assert isinstance(result, dict)
    if len_set_config > 0:
        assert len_set_config == len(result)
        for key, value in result.items():
            assert isinstance(key, str)
            assert key.isupper()
            assert isinstance(value, float)
