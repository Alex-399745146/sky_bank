# test_services.py
"""Модуль с тестами"""

import pytest

from src.services_page.services import get_tzs_filter_date


@pytest.mark.parametrize(
    "test_date,expected_min_count",
    [
        ("05.2021", 0),  # с транзакциями
        ("12.2020", 0),  # без транзакций
    ],
)
def test_get_tzs_filter_date_parametrized(fix_tzs_date, test_date, expected_min_count):
    result = get_tzs_filter_date(fix_tzs_date, test_date)

    assert isinstance(result, list)
    assert len(result) >= expected_min_count
    assert all(isinstance(item, dict) for item in result)
