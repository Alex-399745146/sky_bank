# tests/test_cli.py
"""Тесты команд терминального интерфейса."""

from pathlib import Path

import pandas as pd
from typer.testing import CliRunner

from sky_bank.cli import app

runner = CliRunner()


def test_overview_command_displays_summary(
    sample_transactions: pd.DataFrame,
    tmp_path: Path,  # Создание временной тестовой папки.
    monkeypatch,
) -> None:
    """Команда overview отображает сводку операций."""
    excel_file = tmp_path / "operations.xlsx"
    excel_file.touch()

    monkeypatch.setattr(
        "sky_bank.cli.pd.read_excel",
        lambda _: sample_transactions.copy(),
    )

    result = runner.invoke(app, ["overview", str(excel_file)])

    assert result.exit_code == 0
    assert "Сводка операций" in result.stdout
    assert "Операций" in result.stdout
    assert "2" in result.stdout
    assert "Доходы" in result.stdout
    assert "1 000.00 RUB" in result.stdout
    assert "Расходы" in result.stdout
    assert "100.00 RUB" in result.stdout
    assert "Баланс" in result.stdout
    assert "900.00 RUB" in result.stdout


def test_categories_command_displays_expense_report(
    sample_transactions: pd.DataFrame,
    tmp_path: Path,
    monkeypatch,
) -> None:
    """Команда categories отображает отчёт расходов по категориям."""
    excel_file = tmp_path / "operations.xlsx"
    excel_file.touch()

    monkeypatch.setattr(
        "sky_bank.cli.pd.read_excel",
        lambda _: sample_transactions.copy(),
    )

    result = runner.invoke(app, ["categories", str(excel_file)])

    assert result.exit_code == 0
    assert "Топ расходов по категориям" in result.stdout
    assert "Продукты" in result.stdout
    assert "100.00 RUB" in result.stdout


def test_search_command_displays_matching_operations(
    sample_transactions: pd.DataFrame,
    tmp_path: Path,
    monkeypatch,
) -> None:
    """Команда search отображает найденные операции."""
    sample_transactions["Описание"] = [
        "Магнит у дома",
        "Пополнение счёта",
        "Магнит у дома",
        "Магнит в Китае",
    ]

    excel_file = tmp_path / "operations.xlsx"
    excel_file.touch()

    monkeypatch.setattr(
        "sky_bank.cli.pd.read_excel",
        lambda _: sample_transactions.copy(),
    )

    result = runner.invoke(app, ["search", str(excel_file), "магнит"])

    assert result.exit_code == 0
    assert "Найдено операций: 1" in result.stdout
    assert "Магнит у дома" in result.stdout
    assert "Продукты" in result.stdout
    assert "-100.00 RUB" in result.stdout


def test_search_command_displays_message_when_nothing_found(
    sample_transactions: pd.DataFrame,
    tmp_path: Path,
    monkeypatch,
) -> None:
    """Команда search сообщает, если совпадения отсутствуют."""
    sample_transactions["Описание"] = [
        "Магнит у дома",
        "Пополнение счёта",
        "Магнит у дома",
        "Магнит в Китае",
    ]

    excel_file = tmp_path / "operations.xlsx"
    excel_file.touch()

    monkeypatch.setattr(
        "sky_bank.cli.pd.read_excel",
        lambda _: sample_transactions.copy(),
    )

    result = runner.invoke(app, ["search", str(excel_file), "несуществующий запрос"])

    assert result.exit_code == 0
    assert "Ничего не найдено" in result.stdout
    assert "операций не найдено" in result.stdout


def test_weekdays_command_displays_weekday_report(
    sample_transactions: pd.DataFrame,
    tmp_path: Path,
    monkeypatch,
) -> None:
    """Команда weekdays отображает расходы по дням недели."""
    excel_file = tmp_path / "operations.xlsx"
    excel_file.touch()

    monkeypatch.setattr(
        "sky_bank.cli.pd.read_excel",
        lambda _: sample_transactions.copy(),
    )

    result = runner.invoke(app, ["weekdays", str(excel_file)])

    assert result.exit_code == 0
    assert "Расходы по дням недели" in result.stdout
    assert "Воскресенье" in result.stdout
    assert "1" in result.stdout
    assert "100.00 RUB" in result.stdout


def test_export_excel_command_creates_report(
    sample_transactions: pd.DataFrame,
    tmp_path: Path,
    monkeypatch,
) -> None:
    """Команда export-excel создаёт Excel-отчёт."""
    excel_file = tmp_path / "operations.xlsx"
    excel_file.touch()

    output_path = tmp_path / "report.xlsx"

    monkeypatch.setattr(
        "sky_bank.cli.pd.read_excel",
        lambda _: sample_transactions.copy(),
    )

    result = runner.invoke(
        app,
        [
            "export-excel",
            str(excel_file),
            "--output",
            str(output_path),
        ],
    )

    assert result.exit_code == 0
    assert output_path.exists()
    assert "Экспорт завершён" in result.stdout
    assert "Отчёт успешно сохранён" in result.stdout
