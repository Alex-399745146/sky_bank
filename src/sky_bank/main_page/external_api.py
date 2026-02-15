"""Модуль external_api.py содержит функции работающие c валютами а волатильность обновляет API"""

import os
# from http.client import responses
# import pandas as pd
import cbrapi
import requests
from src.sky_bank.data_extract import get_data_json
from datetime import datetime, timedelta


# Task_4 Курс валют
def get_current_exchange_rate(money_list: list[str]) -> list[dict[str, str | float]]:
    """
    Запрашиваем данные по API(открытый) в ЦБ РФ и выдаем актуальные
    данные указанных валют в виде списка по обновлённым данным
    """
    now_dt = datetime.now()
    delta_dt = timedelta(days=2)
    back_dt = now_dt - delta_dt

    begin_date: str = back_dt.strftime("%Y-%m-%d")
    end_date: str = now_dt.strftime("%Y-%m-%d")

    result = []

    for code_money in money_list:
        answer_df = cbrapi.get_time_series(
            symbol=code_money,
            first_date=begin_date,
            last_date=end_date,
            period='D'
        )

        last_rate = answer_df.iloc[-1]
        result.append({
            'currency': code_money,
            'rate': round(float(last_rate), 2)
        })

    return result

# Task_5 Стоимость акций Мосбиржи сегодня.
def get_current_stock_price(stocks_list):
    """ Актуализируем цены на акции по API(открытый) в Мосбирже """
    securities = ",".join(stocks_list)
    url = (
        f"https://iss.moex.com/iss/engines/stock/markets/shares/securities/"
        f"{securities}/securities.json"
    )
    response = requests.get(url, timeout=10)
    response.raise_for_status()  # Проверяем HTTP-статус
    data = response.json()
    prices = data
    # # Извлекаем цены из ответа
    # prices = {}
    # for ticker in stocks_list:
    #     # Ищем данные по тикеру в ответе
    #     found = False
    #     for row in data["securities"]["data"]:
    #         if row[0] == ticker:  # row[0] — тикер
    #             prices[ticker] = float(row[11])  # row[11] — текущая цена (LAST)
    #             found = True
    #             break
    #     if not found:
    #         prices[ticker] = None  # Если данных нет

    return prices

    # currency_codes: str = currency_codes["operationAmount"]["currency"]["code"]
    # amount: float = currency_codes["operationAmount"]["amount"]
    #
    # convert_in = tx_currency_code
    # convert_out = "RUB"


    # url = f"https://api.apilayer.com/exchangerates_data/convert?to={convert_out}&from={convert_in}&amount={amount}"
    # headers = {"apikey": os.getenv("API_KEY")}

    # try:
    #     response = requests.get(url, headers=headers, timeout=10)
    #     response.raise_for_status()  # Проверить, произошла ли ошибка во время запроса.
    #     return response.status_code
    #
    # #     if response.status_code == 200:
    # #         response_api = response.json()
    # #         print(response_api)
    # #         return round(response_api["result"], 2)
    # except requests.exceptions.RequestException as err:
    #     raise ConnectionError(f"Ошибка запроса к API: {err}")
    # except (KeyError, ValueError, TypeError) as err:
    #     raise ValueError(f"Некорректный ответ от API: {err}")


if __name__ == "__main__":  # pragma: no cover
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))  # директ проекта
    path_file_json = os.path.join(project_root, "user_settings.json")

    config_user: dict[str, list[str]] = get_data_json(path_file_json)
    currency_codes: list[str] = config_user['user_currencies']
    stock_codes: list[str] = config_user['user_stocks']

    # Проверка работы: get_current_exchange_rate
    # data_currency = get_current_exchange_rate(currency_codes)
    # print(data_currency)
    # for i in data_currency:
    #     # print(type(i))
    #     print(i)

    # Проверка работы: get_current_stock_price
    data_stock = get_current_stock_price(stock_codes)
    # print(type(data_stock))
    # print(data_stock)
    # print('---------------------')
    for key, value in data_stock.items():
        # print(type(i))
        print(key, value)


    # url = "https://iss.moex.com/iss/engines/stock/markets/shares/securities/SBER/candles.json?interval=1"
    # response = requests.get(url)
    # data = response.json()
    #
    # print(response.status_code)
    # print(type(data))
    # print(data)


    # # Парсинг данных
    # last_price = data['candles']['data'][-1][4](https: // pypi.org / project / apimoex /)  # 4 — индекс цены закрытия
    # print("Последняя цена SBER:", last_price)