# external_api.py
"""Модуль external_api.py содержит функции работающие c валютами а волатильность обновляет API"""

import os
from datetime import datetime, timedelta
from typing import Any

import apimoex
import cbrapi  # type: ignore
import pandas as pd
import requests

from src.data_extract import get_convert_json_in_data


# Task_4 Курс валют
def get_current_exchange_rate(money_list: list) -> list:
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
        answer_df = cbrapi.get_time_series(symbol=code_money, first_date=begin_date, last_date=end_date, period="D")

        last_rate = answer_df.iloc[-1]

        result.append({"currency": code_money, "rate": round(float(last_rate), 2)})

    return result


# Task_5 Стоимость акций Мосбиржи
def get_current_stock_price(tickers_list: list) -> Any:
    """Актуализируем цены на акции по API(открытый) в Мосбирже"""
    url = "https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities.json"
    params: Any = {"iss.only": "marketdata", "marketdata.columns": "SECID,LAST"}

    # Запрос в Мосбиржу на последние цены всех акций.
    with requests.Session() as session:
        # Фильтруем столбцы(коды_акций, последние_цены)
        client: Any = apimoex.ISSClient(session, url, params)
        data = client.get()

    # Проверка наличия данных в ответе
    if "marketdata" in data and data["marketdata"]:
        prices_df = pd.DataFrame(data["marketdata"])
        filtered_data = prices_df[prices_df["SECID"].isin(tickers_list)]

        result = [
            {"stock": row["SECID"], "price": float(row["LAST"]) if pd.notna(row["LAST"]) else None}
            for _, row in filtered_data.iterrows()
        ]

        return result

    else:
        print("Ошибка: данные о ценах не получены (пустой ответ API)")
        return []


if __name__ == "__main__":  # pragma: no cover
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))  # директ проекта
    path_file_json = os.path.join(project_root, "user_settings.json")

    config_user = get_convert_json_in_data(path_file_json)
    currency_codes = config_user["user_currencies"]
    stock_codes = config_user["user_stocks"]
    # print(currency_codes)
    # print(stock_codes)

    # Актуальные данные пар волют с Мосбиржи
    # data_currency = get_current_exchange_rate(currency_codes)
    # print(type(data_currency))
    # for price in data_currency:
    #     print(price)
    # print()

    # Стоимость акций
    data_stock = get_current_stock_price(stock_codes)
    print(type(data_stock))
    for items in data_stock:
        print(items)
        # print(f'stock: {key} price: {value}')
