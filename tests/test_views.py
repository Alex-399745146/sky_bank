# test_views.py
"""Модуль с тестами"""

from src.main_page.views import get_main_page


def test_get_main_page(fix_tzs_date, fix_user_settings_dict):
    date_filter = "02.05.2021"
    result = get_main_page(fix_tzs_date, date_filter, fix_user_settings_dict)

    assert isinstance(result, dict)
    assert isinstance(result.get("greeting"), str)
    assert isinstance(result.get("cards"), list)
    assert len(result.get("cards")) == 2
    assert isinstance(result.get("top_transactions"), list)
    assert isinstance(result.get("currency_rates"), list)
    assert len(result.get("currency_rates")) == len(fix_user_settings_dict["user_currencies"])
    assert isinstance(result.get("stock_prices"), list)
    assert len(result.get("stock_prices")) == len(fix_user_settings_dict["user_stocks"])
