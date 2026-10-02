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
UNCATEGORIZED_LABEL = "Без категории"
WEEKDAY_NAMES = {
    0: "Понедельник",
    1: "Вторник",
    2: "Среда",
    3: "Четверг",
    4: "Пятница",
    5: "Суббота",
    6: "Воскресенье",
}

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


def _filter_transactions(
    transactions: pd.DataFrame,
    currency: str,
    include_failed: bool,
) -> pd.DataFrame:
    """Проверяет, нормализует и фильтрует операции для аналитики."""
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

    return filtered_transactions


def build_overview(
    transactions: pd.DataFrame,
    currency: str = "RUB",
    include_failed: bool = False,
) -> Overview:
    """Формирует сводку по операциям указанной валюты."""
    filtered_transactions = _filter_transactions(
        transactions,
        currency=currency,
        include_failed=include_failed,
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


def build_expenses_by_category(
    transactions: pd.DataFrame,
    currency: str = "RUB",
    include_failed: bool = False,
    limit: int = 10,
) -> pd.DataFrame:
    """Возвращает крупнейшие категории расходов."""
    if limit < 1:
        raise ValueError("Количество категорий должно быть больше нуля.")

    filtered_transactions = _filter_transactions(
        transactions,
        currency=currency,
        include_failed=include_failed,
    )

    expenses = filtered_transactions[
        filtered_transactions[PAYMENT_AMOUNT_COLUMN] < 0
    ].copy()

    if expenses.empty:
        raise ValueError("Не найдено расходных операций для выбранных параметров.")

    expenses[CATEGORY_COLUMN] = expenses[CATEGORY_COLUMN].fillna(UNCATEGORIZED_LABEL)

    report = (
        expenses.groupby(CATEGORY_COLUMN, as_index=False)[PAYMENT_AMOUNT_COLUMN]
        .sum()
        .assign(**{PAYMENT_AMOUNT_COLUMN: lambda frame: frame[PAYMENT_AMOUNT_COLUMN].abs()})
        .sort_values(PAYMENT_AMOUNT_COLUMN, ascending=False)
        .head(limit)
        .rename(
            columns={
                CATEGORY_COLUMN: "category",
                PAYMENT_AMOUNT_COLUMN: "expenses",
            }
        )
        .reset_index(drop=True)
    )

    return report


def search_transactions(
    transactions: pd.DataFrame,
    query: str,
    currency: str = "RUB",
    include_failed: bool = False,
    category: str | None = None,
    limit: int = 20,
) -> pd.DataFrame:
    """Ищет операции по тексту описания."""
    if not query.strip():
        raise ValueError("Поисковый запрос не должен быть пустым.")

    if limit < 1:
        raise ValueError("Количество операций должно быть больше нуля.")

    if "Описание" not in transactions.columns:
        raise ValueError("В Excel-файле отсутствует обязательный столбец: Описание")

    filtered_transactions = _filter_transactions(
        transactions,
        currency=currency,
        include_failed=include_failed,
    )

    descriptions = filtered_transactions["Описание"].fillna("").astype(str)

    result = filtered_transactions[
        descriptions.str.contains(query.strip(), case=False, regex=False)
    ].copy()

    if category is not None:
        categories = result[CATEGORY_COLUMN].fillna("").astype(str)

        result = result[
            categories.str.contains(category.strip(), case=False, regex=False)
        ].copy()

    result = result.sort_values(
        by=OPERATION_DATE_COLUMN,
        ascending=False,
    ).head(limit)

    return result.reset_index(drop=True)


def build_expenses_by_weekday(
    transactions: pd.DataFrame,
    currency: str = "RUB",
    include_failed: bool = False,
) -> pd.DataFrame:
    """Возвращает расходы и средний чек по дням недели."""
    filtered_transactions = _filter_transactions(
        transactions,
        currency=currency,
        include_failed=include_failed,
    )

    expenses = filtered_transactions[
        filtered_transactions[PAYMENT_AMOUNT_COLUMN] < 0
    ].copy()

    if expenses.empty:
        raise ValueError("Не найдено расходных операций для выбранных параметров.")

    expenses["weekday_number"] = expenses[OPERATION_DATE_COLUMN].dt.weekday

    grouped_expenses = (
        expenses.groupby("weekday_number", as_index=False)
        .agg(
            operation_count=(PAYMENT_AMOUNT_COLUMN, "size"),
            expenses=(PAYMENT_AMOUNT_COLUMN, "sum"),
        )
        .assign(expenses=lambda frame: frame["expenses"].abs())
    )

    weekdays = pd.DataFrame({"weekday_number": range(7)})

    report = (
        weekdays.merge(grouped_expenses, on="weekday_number", how="left")
        .fillna({"operation_count": 0, "expenses": 0.0})
        .assign(
            operation_count=lambda frame: frame["operation_count"].astype(int),
            weekday=lambda frame: frame["weekday_number"].map(WEEKDAY_NAMES),
        )
    )

    report["average_expense"] = (
        report["expenses"]
        .div(report["operation_count"])
        .fillna(0.0)
    )

    return report[
        [
            "weekday_number",
            "weekday",
            "operation_count",
            "expenses",
            "average_expense",
        ]
    ]
