# tests/test_analytics.py
"""Тесты бизнес-логики CLI-аналитики."""

from datetime import datetime

import pandas as pd
import pytest

from sky_bank.analytics import (build_expenses_by_category, build_expenses_by_weekday, build_overview,
                                search_transactions)


def test_build_overview_uses_successful_ruble_transactions(
    sample_transactions: pd.DataFrame,
) -> None:
    """Сводка по умолчанию учитывает только успешные RUB-операции."""
    overview = build_overview(sample_transactions)

    assert overview.currency == "RUB"
    assert overview.transaction_count == 2
    assert overview.card_count == 1
    assert overview.category_count == 2
    assert overview.period_start == datetime(2021, 1, 3, 10, 0)
    assert overview.period_end == datetime(2021, 1, 5, 15, 30)
    assert overview.income == 1_000.0
    assert overview.expenses == 100.0
    assert overview.balance == 900.0


def test_build_overview_can_include_failed_transactions(
    sample_transactions: pd.DataFrame,
) -> None:
    """Сводка может учитывать неуспешные операции по явной опции."""
    overview = build_overview(sample_transactions, include_failed=True)

    assert overview.transaction_count == 3
    assert overview.card_count == 2
    assert overview.category_count == 3
    assert overview.income == 1_000.0
    assert overview.expenses == 600.0
    assert overview.balance == 400.0


def test_build_overview_raises_error_for_missing_required_column() -> None:
    """Сводка сообщает об отсутствии обязательных столбцов."""
    transactions = pd.DataFrame(
        [
            {
                "Дата операции": "03.01.2021 10:00:00",
                "Сумма платежа": -100.0,
            }
        ]
    )

    with pytest.raises(ValueError, match="обязательные столбцы"):
        build_overview(transactions)


def test_build_expenses_by_category_returns_only_expenses(
    sample_transactions: pd.DataFrame,
) -> None:
    """Отчёт возвращает только успешные расходы выбранной валюты."""
    report = build_expenses_by_category(sample_transactions)

    assert report.to_dict("records") == [
        {
            "category": "Продукты",
            "expenses": 100.0,
        }
    ]


def test_build_expenses_by_category_can_include_failed_transactions(
    sample_transactions: pd.DataFrame,
) -> None:
    """Отчёт добавляет FAILED-расходы по явной опции."""
    report = build_expenses_by_category(
        sample_transactions,
        include_failed=True,
    )

    assert report.to_dict("records") == [
        {
            "category": "Транспорт",
            "expenses": 500.0,
        },
        {
            "category": "Продукты",
            "expenses": 100.0,
        },
    ]


def test_build_expenses_by_category_rejects_non_positive_limit(
    sample_transactions: pd.DataFrame,
) -> None:
    """Отчёт не принимает нулевой или отрицательный лимит."""
    with pytest.raises(ValueError, match="больше нуля"):
        build_expenses_by_category(sample_transactions, limit=0)


def test_search_transactions_finds_description_case_insensitively(
    sample_transactions: pd.DataFrame,
) -> None:
    """Поиск находит операции по описанию без учёта регистра."""
    sample_transactions.loc[0, "Описание"] = "Магнит у дома"
    sample_transactions.loc[1, "Описание"] = "Пополнение счёта"
    sample_transactions.loc[2, "Описание"] = "Магнит у дома"
    sample_transactions.loc[3, "Описание"] = "Магнит в Китае"

    result = search_transactions(sample_transactions, "МАГНИТ")

    assert len(result) == 1
    assert result.iloc[0]["Описание"] == "Магнит у дома"
    assert result.iloc[0]["Статус"] == "OK"
    assert result.iloc[0]["Валюта платежа"] == "RUB"


def test_search_transactions_can_filter_by_category(
    sample_transactions: pd.DataFrame,
) -> None:
    """Поиск ограничивает результаты указанной категорией."""
    sample_transactions.loc[0, "Описание"] = "Покупка"
    sample_transactions.loc[1, "Описание"] = "Покупка"
    sample_transactions.loc[2, "Описание"] = "Покупка"
    sample_transactions.loc[3, "Описание"] = "Покупка"

    result = search_transactions(
        sample_transactions,
        "покупка",
        category="Пополнение",
    )

    assert len(result) == 1
    assert result.iloc[0]["Категория"] == "Пополнение"


def test_search_transactions_rejects_empty_query(
    sample_transactions: pd.DataFrame,
) -> None:
    """Поиск не принимает пустой запрос."""
    with pytest.raises(ValueError, match="не должен быть пустым"):
        search_transactions(sample_transactions, "   ")


def test_build_expenses_by_weekday_returns_all_weekdays(
    sample_transactions: pd.DataFrame,
) -> None:
    """Отчёт содержит все дни недели и учитывает успешные RUB-расходы."""
    report = build_expenses_by_weekday(sample_transactions)

    assert len(report) == 7

    sunday = report.loc[report["weekday"] == "Воскресенье"].iloc[0]
    assert sunday["operation_count"] == 1
    assert sunday["expenses"] == 100.0
    assert sunday["average_expense"] == 100.0

    tuesday = report.loc[report["weekday"] == "Вторник"].iloc[0]
    assert tuesday["operation_count"] == 0
    assert tuesday["expenses"] == 0.0
    assert tuesday["average_expense"] == 0.0


def test_build_expenses_by_weekday_can_include_failed_transactions(
    sample_transactions: pd.DataFrame,
) -> None:
    """Отчёт включает FAILED-расходы только по явной опции."""
    report = build_expenses_by_weekday(
        sample_transactions,
        include_failed=True,
    )

    thursday = report.loc[report["weekday"] == "Четверг"].iloc[0]

    assert thursday["operation_count"] == 1
    assert thursday["expenses"] == 500.0
