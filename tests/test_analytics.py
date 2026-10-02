# tests/test_analytics.py
"""Тесты бизнес-логики CLI-аналитики."""

from datetime import datetime

import pandas as pd
import pytest

from sky_bank.analytics import build_overview


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