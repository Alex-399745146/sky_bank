# tests/test_exchange_rates.py
from decimal import Decimal

import pytest
import requests

from sky_bank.exchange_rates import CurrencyNotFoundError, ExchangeRateError, get_exchange_rates

CBR_XML_RESPONSE = """<?xml version="1.0" encoding="windows-1251"?>
<ValCurs Date="03.10.2026" name="Foreign Currency Market">
    <Valute ID="R01235">
        <NumCode>840</NumCode>
        <CharCode>USD</CharCode>
        <Nominal>1</Nominal>
        <Name>Доллар США</Name>
        <Value>80,2500</Value>
        <VunitRate>80,2500</VunitRate>
    </Valute>
    <Valute ID="R01375">
        <NumCode>156</NumCode>
        <CharCode>CNY</CharCode>
        <Nominal>10</Nominal>
        <Name>Китайских юаней</Name>
        <Value>114,3000</Value>
        <VunitRate>11,4300</VunitRate>
    </Valute>
</ValCurs>
""".encode("windows-1251")


class FakeResponse:
    """Тестовый HTTP-ответ Банка России."""

    def __init__(self, content: bytes) -> None:
        self.content = content

    def raise_for_status(self) -> None:
        """Имитирует успешный HTTP-ответ."""


class FakeSession:
    """Тестовая HTTP-сессия без реального сетевого запроса."""

    def __init__(self, response: FakeResponse | None = None, error: Exception | None = None) -> None:
        self.response = response
        self.error = error

    def get(self, url: str, timeout: int) -> FakeResponse:
        if self.error is not None:
            raise self.error

        assert self.response is not None
        return self.response


def test_get_exchange_rates_returns_requested_currencies() -> None:
    session = FakeSession(response=FakeResponse(CBR_XML_RESPONSE))

    rates = get_exchange_rates(["CNY", "USD"], session=session)  # type: ignore[arg-type]

    assert [rate.code for rate in rates] == ["CNY", "USD"]
    assert rates[0].name == "Китайских юаней"
    assert rates[0].rate == Decimal("11.43")
    assert rates[1].rate == Decimal("80.25")
    assert rates[0].rate_date.strftime("%d.%m.%Y") == "03.10.2026"


def test_get_exchange_rates_normalizes_currency_codes() -> None:
    session = FakeSession(response=FakeResponse(CBR_XML_RESPONSE))

    rates = get_exchange_rates([" cny ", "USD", "CNY"], session=session)  # type: ignore[arg-type]

    assert [rate.code for rate in rates] == ["CNY", "USD"]


def test_get_exchange_rates_raises_error_for_unknown_currency() -> None:
    session = FakeSession(response=FakeResponse(CBR_XML_RESPONSE))

    with pytest.raises(CurrencyNotFoundError, match="ABC"):
        get_exchange_rates(["ABC"], session=session)  # type: ignore[arg-type]


def test_get_exchange_rates_handles_network_error() -> None:
    session = FakeSession(error=requests.ConnectionError("Connection failed"))

    with pytest.raises(ExchangeRateError, match="Не удалось получить курсы"):
        get_exchange_rates(["CNY"], session=session)  # type: ignore[arg-type]
