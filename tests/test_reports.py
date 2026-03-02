# test_reports.py
"""Модуль с тестами"""

import pandas as pd

from src.reports_page.reports import spending_by_workday


def test_spending_by_workday(fix_data_df):
    """Тест модуля reports.py"""
    date = "05.01.2021"
    result = spending_by_workday(fix_data_df, date)

    assert "Дата операции" in fix_data_df.columns
    assert "Сумма операции с округлением" in fix_data_df.columns
    assert isinstance(result, pd.DataFrame)
    assert result.shape == (1, 2)
