"""Точка входа терминального приложения Sky Bank."""

from importlib.metadata import version as get_package_version
from pathlib import Path
from typing import cast

import pandas as pd
import typer
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from sky_bank.analytics import (CATEGORY_COLUMN, OPERATION_DATE_COLUMN, PAYMENT_AMOUNT_COLUMN, STATUS_COLUMN, Overview,
                                build_expenses_by_category, build_expenses_by_weekday, build_overview,
                                search_transactions)
from sky_bank.exchange_rates import DEFAULT_CURRENCIES, ExchangeRateError, get_exchange_rates
from sky_bank.exporters import export_analysis_report

app = typer.Typer(
    name="sky-bank",
    help="CLI-приложение для анализа банковских операций из Excel.",
    no_args_is_help=True,
    rich_markup_mode="rich",
)

console = Console()


def format_money(amount: float, currency: str) -> str:
    """Форматирует денежную сумму для терминального вывода."""
    formatted_amount = f"{amount:,.2f}".replace(",", " ")
    return f"{formatted_amount} {currency}"


def render_overview(
    overview_data: Overview,
    include_failed: bool = False,
) -> None:
    """Отображает сводку операций в терминале."""
    balance_style = "green" if overview_data.balance >= 0 else "red"
    status_label = "OK, FAILED" if include_failed else "OK"

    summary = Table(
        title="Сводка операций",
        box=box.ROUNDED,
        show_header=False,
        border_style="cyan",
        padding=(0, 1),
    )
    summary.add_column("Показатель", style="bold cyan")
    summary.add_column("Значение", justify="right")

    summary.add_row(
        "Период",
        f"{overview_data.period_start:%d.%m.%Y} — {overview_data.period_end:%d.%m.%Y}",
    )
    summary.add_row("Валюта", overview_data.currency)
    summary.add_row("Операций", str(overview_data.transaction_count))
    summary.add_row("Карт", str(overview_data.card_count))
    summary.add_row("Категорий", str(overview_data.category_count))
    summary.add_row("Доходы", f"[green]{format_money(overview_data.income, overview_data.currency)}[/green]")
    summary.add_row("Расходы", f"[red]{format_money(overview_data.expenses, overview_data.currency)}[/red]")
    summary.add_row(
        "Баланс",
        f"[{balance_style}]{format_money(overview_data.balance, overview_data.currency)}[/{balance_style}]",
    )

    console.print(
        Panel.fit(
            summary,
            title="[bold cyan]Sky Bank[/bold cyan]",
            subtitle=f"Статусы: {status_label}",
            border_style="cyan",
        )
    )


def render_category_report(
    report: pd.DataFrame,
    currency: str,
    include_failed: bool = False,
) -> None:
    """Отображает отчёт расходов по категориям."""
    status_label = "OK, FAILED" if include_failed else "OK"
    table = Table(
        title="Топ расходов по категориям",
        box=box.ROUNDED,
        border_style="magenta",
        header_style="bold magenta",
    )
    table.add_column("№", justify="right", style="dim", width=3)
    table.add_column("Категория", style="cyan")
    table.add_column("Расходы", justify="right", style="red")

    for index, row in enumerate(report.itertuples(index=False), start=1):
        category = str(row.category)
        expenses = cast(float, row.expenses)

        table.add_row(
            str(index),
            category,
            format_money(expenses, currency),
        )

    console.print(
        Panel.fit(
            table,
            title="[bold magenta]Sky Bank[/bold magenta]",
            subtitle=f"Валюта: {currency} · Статусы: {status_label}",
            border_style="magenta",
        )
    )


def render_weekday_report(
    report: pd.DataFrame,
    currency: str,
    include_failed: bool,
) -> None:
    """Отображает расходы по дням недели."""
    status_label = "OK, FAILED" if include_failed else "OK"

    table = Table(
        title="Расходы по дням недели",
        box=box.ROUNDED,
        border_style="blue",
        header_style="bold blue",
    )
    table.add_column("День недели", style="cyan")
    table.add_column("Операций", justify="right")
    table.add_column("Расходы", justify="right", style="red")
    table.add_column("Средний расход", justify="right", style="yellow")

    for _, weekday, operation_count, expenses, average_expense in report.itertuples(
        index=False,
        name=None,
    ):
        table.add_row(
            weekday,
            str(operation_count),
            format_money(float(expenses), currency),
            format_money(float(average_expense), currency),
        )

    console.print(
        Panel.fit(
            table,
            title="[bold blue]Sky Bank[/bold blue]",
            subtitle=f"Валюта: {currency} · Статусы: {status_label}",
            border_style="blue",
        )
    )


def render_search_results(
    results: pd.DataFrame,
    query: str,
    currency: str,
    include_failed: bool,
) -> None:
    """Отображает найденные операции в терминале."""
    if results.empty:
        console.print(
            Panel.fit(
                f"По запросу [bold yellow]{query}[/bold yellow] операций не найдено.",
                title="[bold yellow]Ничего не найдено[/bold yellow]",
                border_style="yellow",
            )
        )
        return

    status_label = "OK, FAILED" if include_failed else "OK"

    table = Table(
        title=f"Найдено операций: {len(results)}",
        box=box.ROUNDED,
        border_style="green",
        header_style="bold green",
    )
    table.add_column("Дата", style="cyan")
    table.add_column("Описание")
    table.add_column("Категория")
    table.add_column("Статус", justify="center")
    table.add_column("Сумма", justify="right")

    display_columns = [
        OPERATION_DATE_COLUMN,
        "Описание",
        CATEGORY_COLUMN,
        STATUS_COLUMN,
        PAYMENT_AMOUNT_COLUMN,
    ]

    for operation_date, description, category, status, amount in results[display_columns].itertuples(
        index=False, name=None
    ):
        category_text = "Без категории" if pd.isna(category) else str(category)
        status_style = "green" if status == "OK" else "yellow"
        amount_style = "green" if amount > 0 else "red"

        table.add_row(
            operation_date.strftime("%d.%m.%Y %H:%M"),
            str(description),
            category_text,
            f"[{status_style}]{status}[/{status_style}]",
            f"[{amount_style}]{format_money(float(amount), currency)}[/{amount_style}]",
        )

    console.print(
        Panel.fit(
            table,
            title="[bold green]Sky Bank[/bold green]",
            subtitle=f"Запрос: {query} · Валюта: {currency} · Статусы: {status_label}",
            border_style="green",
        )
    )


@app.callback()
def main() -> None:
    """Запускает команды Sky Bank."""


@app.command()
def version() -> None:
    """Показывает версию приложения."""
    project_version = get_package_version("sky-bank")

    console.print(
        Panel.fit(
            f"[bold cyan]Sky Bank[/bold cyan]\nВерсия: [green]{project_version}[/green]",
            title="Информация",
            border_style="cyan",
        )
    )


@app.command()
def rates(
    currencies: list[str] | None = typer.Argument(
        None,
        metavar="[CURRENCY]...",
        help="Коды валют для запроса, например: CNY USD EUR.",
    ),
) -> None:
    """Показывает официальные курсы валют Банка России."""
    requested_currencies = currencies or list(DEFAULT_CURRENCIES)

    try:
        with console.status(
            "[bold blue]Получаем официальные курсы Банка России...[/bold blue]",
            spinner="dots",
            spinner_style="blue",
        ):
            exchange_rates = get_exchange_rates(requested_currencies)
    except (ExchangeRateError, ValueError) as error:
        console.print(
            Panel(
                str(error),
                title="[bold red]Ошибка получения курсов[/bold red]",
                border_style="red",
            )
        )
        raise typer.Exit(code=1) from error

    table = Table(
        title="Официальные курсы валют",
        box=box.ROUNDED,
        border_style="blue",
        header_style="bold blue",
    )
    table.add_column("Код", style="cyan", justify="center")
    table.add_column("Валюта")
    table.add_column("Курс за 1 единицу, RUB", justify="right", style="green")
    table.add_column("Дата ЦБ РФ", justify="center")

    for exchange_rate in exchange_rates:
        formatted_rate = f"{exchange_rate.rate:.4f}".replace(".", ",")

        table.add_row(
            exchange_rate.code,
            exchange_rate.name,
            formatted_rate,
            exchange_rate.rate_date.strftime("%d.%m.%Y"),
        )

    console.print(
        Panel.fit(
            table,
            title="[bold blue]Sky Bank[/bold blue]",
            subtitle="Источник: Банк России",
            border_style="blue",
        )
    )


@app.command()
def overview(
    file_path: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        help="Путь к Excel-файлу с банковскими операциями.",
    ),
    currency: str = typer.Option(
        "RUB",
        "--currency",
        "-c",
        help="Валюта операций для сводки.",
    ),
    include_failed: bool = typer.Option(
        False,
        "--include-failed",
        help="Учитывать операции со статусом FAILED.",
    ),
) -> None:
    """Показывает сводку операций из Excel-файла."""
    try:
        transactions = pd.read_excel(file_path)
        overview_data = build_overview(
            transactions,
            currency=currency.upper(),
            include_failed=include_failed,
        )
    except (OSError, ValueError) as error:
        console.print(
            Panel(
                str(error),
                title="[bold red]Ошибка анализа[/bold red]",
                border_style="red",
            )
        )
        raise typer.Exit(code=1) from error

    render_overview(
        overview_data,
        include_failed=include_failed,
    )


@app.command()
def categories(
    file_path: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        help="Путь к Excel-файлу с банковскими операциями.",
    ),
    limit: int = typer.Option(
        10,
        "--limit",
        "-l",
        min=1,
        help="Максимальное количество категорий в отчёте.",
    ),
    currency: str = typer.Option(
        "RUB",
        "--currency",
        "-c",
        help="Валюта операций для отчёта.",
    ),
    include_failed: bool = typer.Option(
        False,
        "--include-failed",
        help="Учитывать операции со статусом FAILED.",
    ),
) -> None:
    """Показывает крупнейшие категории расходов."""
    try:
        transactions = pd.read_excel(file_path)
        report = build_expenses_by_category(
            transactions,
            currency=currency.upper(),
            include_failed=include_failed,
            limit=limit,
        )
    except (OSError, ValueError) as error:
        console.print(
            Panel(
                str(error),
                title="[bold red]Ошибка анализа[/bold red]",
                border_style="red",
            )
        )
        raise typer.Exit(code=1) from error

    render_category_report(
        report,
        currency.upper(),
        include_failed=include_failed,
    )


@app.command()
def weekdays(
    file_path: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        help="Путь к Excel-файлу с банковскими операциями.",
    ),
    currency: str = typer.Option(
        "RUB",
        "--currency",
        "-c",
        help="Валюта операций для отчёта.",
    ),
    include_failed: bool = typer.Option(
        False,
        "--include-failed",
        help="Учитывать операции со статусом FAILED.",
    ),
) -> None:
    """Показывает расходы по дням недели."""
    try:
        transactions = pd.read_excel(file_path)
        report = build_expenses_by_weekday(
            transactions,
            currency=currency.upper(),
            include_failed=include_failed,
        )
    except (OSError, ValueError) as error:
        console.print(
            Panel(
                str(error),
                title="[bold red]Ошибка анализа[/bold red]",
                border_style="red",
            )
        )
        raise typer.Exit(code=1) from error

    render_weekday_report(
        report,
        currency=currency.upper(),
        include_failed=include_failed,
    )


@app.command()
def search(
    file_path: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        help="Путь к Excel-файлу с банковскими операциями.",
    ),
    query: str = typer.Argument(
        ...,
        help="Текст для поиска в описании операций.",
    ),
    category: str | None = typer.Option(
        None,
        "--category",
        help="Дополнительный фильтр по категории.",
    ),
    limit: int = typer.Option(
        20,
        "--limit",
        "-l",
        min=1,
        help="Максимальное количество операций в результате.",
    ),
    currency: str = typer.Option(
        "RUB",
        "--currency",
        "-c",
        help="Валюта операций для поиска.",
    ),
    include_failed: bool = typer.Option(
        False,
        "--include-failed",
        help="Учитывать операции со статусом FAILED.",
    ),
) -> None:
    """Ищет операции по тексту в описании."""
    try:
        transactions = pd.read_excel(file_path)
        results = search_transactions(
            transactions,
            query=query,
            currency=currency.upper(),
            include_failed=include_failed,
            category=category,
            limit=limit,
        )
    except (OSError, ValueError) as error:
        console.print(
            Panel(
                str(error),
                title="[bold red]Ошибка поиска[/bold red]",
                border_style="red",
            )
        )
        raise typer.Exit(code=1) from error

    render_search_results(
        results,
        query=query,
        currency=currency.upper(),
        include_failed=include_failed,
    )


@app.command()
def export_excel(
    file_path: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        help="Путь к Excel-файлу с банковскими операциями.",
    ),
    output: Path = typer.Option(
        ...,
        "--output",
        "-o",
        file_okay=True,
        dir_okay=False,
        writable=True,
        help="Путь для сохранения Excel-отчёта.",
    ),
    currency: str = typer.Option(
        "RUB",
        "--currency",
        "-c",
        help="Валюта операций для отчёта.",
    ),
    include_failed: bool = typer.Option(
        False,
        "--include-failed",
        help="Учитывать операции со статусом FAILED.",
    ),
    limit: int = typer.Option(
        10,
        "--limit",
        "-l",
        min=1,
        help="Максимальное количество категорий в отчёте.",
    ),
) -> None:
    """Экспортирует аналитический отчёт в Excel."""
    normalized_currency = currency.upper()

    try:
        transactions = pd.read_excel(file_path)

        overview_data = build_overview(
            transactions,
            currency=normalized_currency,
            include_failed=include_failed,
        )
        categories_report = build_expenses_by_category(
            transactions,
            currency=normalized_currency,
            include_failed=include_failed,
            limit=limit,
        )
        weekdays_report = build_expenses_by_weekday(
            transactions,
            currency=normalized_currency,
            include_failed=include_failed,
        )

        output_path = export_analysis_report(
            output,
            overview_data,
            categories_report,
            weekdays_report,
        )
    except (OSError, ValueError) as error:
        console.print(
            Panel(
                str(error),
                title="[bold red]Ошибка экспорта[/bold red]",
                border_style="red",
            )
        )
        raise typer.Exit(code=1) from error

    console.print(
        Panel.fit(
            f"Отчёт успешно сохранён:\n[bold green]{output_path}[/bold green]",
            title="[bold green]Экспорт завершён[/bold green]",
            border_style="green",
        )
    )
