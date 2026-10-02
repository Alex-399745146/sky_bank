"""Точка входа терминального приложения Sky Bank."""

from importlib.metadata import version as get_package_version
from pathlib import Path

import pandas as pd
import typer
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from sky_bank.analytics import Overview, build_overview

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