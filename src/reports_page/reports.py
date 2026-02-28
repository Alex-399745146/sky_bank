# reports.py
"""
Модуль с функциям по отчетности и с декораторами сохраняющими отчетность
"""

import os
from datetime import datetime
from typing import Optional

import pandas as pd
from dateutil.relativedelta import relativedelta

from src.data_extract import get_df_from_xlsx


def spending_by_workday(tzs_df: pd.DataFrame, date: Optional[str] = None) -> pd.DataFrame:
    """Траты в рабочий/выходной день"""
    if date is None:
        given_date = datetime.now()
    else:
        given_date = datetime.strptime(date, "%d.%m.%Y")

    # Временная дельта на 3 месяца
    three_months_ago = given_date - relativedelta(months=3)

    # Преобразование столбца 'Дата операции' в формат datetime
    tzs_df["Дата операции"] = pd.to_datetime(tzs_df["Дата операции"], dayfirst=True, errors="coerce")

    # Фильтрация данных
    three_months_tzs = tzs_df[
        (tzs_df["Дата операции"] >= three_months_ago) & (tzs_df["Дата операции"] <= given_date)
    ].copy()

    # Добавление колонки с днем недели
    three_months_tzs["День недели"] = three_months_tzs["Дата операции"].dt.weekday

    # Расчет средних трат
    average_spending = {
        "в будни": three_months_tzs[three_months_tzs["День недели"] < 5]["Сумма операции с округлением"].mean(),
        "на выходных": three_months_tzs[three_months_tzs["День недели"] >= 5]["Сумма операции с округлением"].mean(),
    }

    # Создание DataFrame для вывода
    result_df = pd.DataFrame(average_spending, index=[0])

    return result_df


if __name__ == "__main__":  # pragma: no cover
    current_dir = os.path.dirname(__file__)  # текущий директ
    project_root = os.path.dirname(os.path.dirname(current_dir))  # директ проекта
    path_file_xlsx = os.path.join(project_root, "data", "operations.xlsx")

    # Исходные данные
    tzs_df = get_df_from_xlsx(path_file_xlsx)
    date = "20.05.2021"

    avr_amount = spending_by_workday(tzs_df, date)

    print(avr_amount.head())
