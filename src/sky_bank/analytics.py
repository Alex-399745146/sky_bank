# src/sky_bank/analytics.py
"""Бизнес-логика аналитики банковских операций."""

from dataclasses import dataclass
from datetime import datetime

import pandas as pd

OPERATION_DATE_COLUMN = "Дата операции"
CARD_NUMBER_COLUMN = "Номер карты"
STATUS_COLUMN = "Статус"
PAYMENT_AMOUNT_COLUMN = "Сумма платежа"
PAYMENT_CURRENCY_COLUMN = "Валюта платежа"
CATEGORY_COLUMN = "Категория"

SUCCESS_STATUS = "OK"

REQUIRED_COLUMNS = {
    OPERATION_DATE_COLUMN,
    CARD_NUMBER_COLUMN,
    STATUS_COLUMN,
    PAYMENT_AMOUNT_COLUMN,
    PAYMENT_CURRENCY_COLUMN,
    CATEGORY_COLUMN,
}


@dataclass(frozen=True)
class Overview:
    """Сводные показатели по отфильтрованным операциям."""

    currency: str
    transaction_count: int
    card_count: int
    category_count: int
    period_start: datetime
    period_end: datetime
    income: float
    expenses: float
    balance: float


def build_overview(
    transactions: pd.DataFrame,
    currency: str = "RUB",
    include_failed: bool = False,
) -> Overview:
    """Формирует сводку по операциям указанной валюты."""
    missing_columns = REQUIRED_COLUMNS.difference(transactions.columns)

    if missing_columns:
        missing_columns_text = ", ".join(sorted(missing_columns))
        raise ValueError(f"В Excel-файле отсутствуют обязательные столбцы: {missing_columns_text}")

    filtered_transactions = transactions.copy()

    filtered_transactions[OPERATION_DATE_COLUMN] = pd.to_datetime(
        filtered_transactions[OPERATION_DATE_COLUMN],
        dayfirst=True,
        errors="coerce",
    )
    filtered_transactions[PAYMENT_AMOUNT_COLUMN] = pd.to_numeric(
        filtered_transactions[PAYMENT_AMOUNT_COLUMN],
        errors="coerce",
    )

    if filtered_transactions[OPERATION_DATE_COLUMN].isna().any():
        raise ValueError("В Excel-файле найдены операции с некорректной датой.")

    if filtered_transactions[PAYMENT_AMOUNT_COLUMN].isna().any():
        raise ValueError("В Excel-файле найдены операции с некорректной суммой платежа.")

    filtered_transactions = filtered_transactions[
        filtered_transactions[PAYMENT_CURRENCY_COLUMN] == currency
    ].copy()

    if not include_failed:
        filtered_transactions = filtered_transactions[
            filtered_transactions[STATUS_COLUMN] == SUCCESS_STATUS
        ].copy()

    if filtered_transactions.empty:
        raise ValueError(
            f"Не найдено операций для валюты {currency}. "
            "Проверьте параметр валюты или включите неуспешные операции."
        )

    amounts = filtered_transactions[PAYMENT_AMOUNT_COLUMN]

    income = float(amounts[amounts > 0].sum())
    expenses = float(abs(amounts[amounts < 0].sum()))
    balance = float(amounts.sum())

    return Overview(
        currency=currency,
        transaction_count=len(filtered_transactions),
        card_count=filtered_transactions[CARD_NUMBER_COLUMN].nunique(dropna=True),
        category_count=filtered_transactions[CATEGORY_COLUMN].nunique(dropna=True),
        period_start=filtered_transactions[OPERATION_DATE_COLUMN].min(),
        period_end=filtered_transactions[OPERATION_DATE_COLUMN].max(),
        income=income,
        expenses=expenses,
        balance=balance,
    )