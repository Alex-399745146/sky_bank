"""Точка входа терминального приложения Sky Bank."""

from importlib.metadata import version as get_package_version

import typer
from rich.console import Console
from rich.panel import Panel

app = typer.Typer(
    name="sky-bank",
    help="CLI-приложение для анализа банковских операций из Excel.",
    no_args_is_help=True,
    rich_markup_mode="rich",
)

console = Console()


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