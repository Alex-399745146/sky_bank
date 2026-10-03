# src/sky_bank/exchange_rates.py
"""Получение официальных курсов иностранных валют Банка России."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Sequence
from xml.etree import ElementTree

import requests

CBR_DAILY_URL = "https://www.cbr.ru/scripts/XML_daily.asp"
DEFAULT_CURRENCIES = ("USD", "EUR", "CNY")
REQUEST_TIMEOUT_SECONDS = 10


class ExchangeRateError(Exception):
    """Базовая ошибка получения курсов валют."""


class CurrencyNotFoundError(ExchangeRateError):
    """Запрошенная валюта отсутствует в ответе Банка России."""


@dataclass(frozen=True)
class ExchangeRate:
    """Официальный курс одной единицы иностранной валюты к RUB."""

    code: str
    name: str
    rate: Decimal
    rate_date: datetime


def _normalize_currency_codes(currencies: Sequence[str]) -> tuple[str, ...]:
    """Нормализует коды валют и удаляет повторяющиеся значения."""
    normalized_codes = tuple(dict.fromkeys(currency.strip().upper() for currency in currencies if currency.strip()))

    if not normalized_codes:
        raise ValueError("Укажите хотя бы один код валюты.")

    return normalized_codes


def get_exchange_rates(
    currencies: Sequence[str],
    session: requests.Session | None = None,
) -> list[ExchangeRate]:
    """Возвращает официальные курсы Банка России для указанных валют."""
    requested_codes = _normalize_currency_codes(currencies)
    http_session = session or requests.Session()

    try:
        response = http_session.get(CBR_DAILY_URL, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
    except requests.RequestException as error:
        raise ExchangeRateError(
            "Не удалось получить курсы Банка России. Проверьте подключение к интернету."
        ) from error

    try:
        root = ElementTree.fromstring(response.content)
        rate_date = datetime.strptime(root.attrib["Date"], "%d.%m.%Y")
    except (ElementTree.ParseError, KeyError, ValueError) as error:
        raise ExchangeRateError("Банк России вернул некорректный ответ.") from error

    rates_by_code: dict[str, ExchangeRate] = {}

    for currency in root.findall("Valute"):
        code = currency.findtext("CharCode")
        name = currency.findtext("Name")
        nominal_text = currency.findtext("Nominal")
        value_text = currency.findtext("Value")

        if code is None or name is None or nominal_text is None or value_text is None:
            continue

        try:
            nominal = Decimal(nominal_text)
            value = Decimal(value_text.replace(",", "."))
        except InvalidOperation as error:
            raise ExchangeRateError(f"Банк России вернул некорректный курс для валюты {code}.") from error

        if nominal == 0:
            raise ExchangeRateError(f"Банк России вернул нулевой номинал для валюты {code}.")

        rates_by_code[code] = ExchangeRate(
            code=code,
            name=name,
            rate=value / nominal,
            rate_date=rate_date,
        )

    missing_codes = [code for code in requested_codes if code not in rates_by_code]
    if missing_codes:
        missing_codes_text = ", ".join(missing_codes)
        raise CurrencyNotFoundError(f"Курсы для валют не найдены: {missing_codes_text}.")

    return [rates_by_code[code] for code in requested_codes]
