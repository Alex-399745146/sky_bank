"""Модуль external_api.py содержит функции работающие c валютами а волатильность обновляет API"""

import os
import apimoex
import pandas as pd
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
def get_current_stock_price(tickers_list: list) -> dict | None:
    """ Актуализируем цены на акции по API(открытый) в Мосбирже """
    url = 'https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities.json'
    params = {
        'iss.only': 'marketdata',
        'marketdata.columns': 'SECID,LAST'
    }

    # Запрос в Мосбиржу на последние цены всех акций.
    with requests.Session() as session:
        # Фильтруем столбцы(коды_акций, последние_цены)
        client = apimoex.ISSClient(session, url, params)
        data = client.get()

    # Проверка наличия данных в ответе
    if 'marketdata' in data and data['marketdata']:
        prices_df = pd.DataFrame(data['marketdata'])
        data = prices_df[prices_df['SECID'].isin(tickers_list)]
        data = data.set_index('SECID') # убираем столбец порядковых номеров
        result = data.to_dict()['LAST']

        return result
    else:
        print("Ошибка: данные о ценах не получены (пустой ответ API)")
        return None


if __name__ == "__main__":  # pragma: no cover
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))  # директ проекта
    path_file_json = os.path.join(project_root, "user_settings.json")

    config_user: dict[str, list[str]] = get_data_json(path_file_json)
    currency_codes: list[str] = config_user['user_currencies']
    stock_codes: list[str] = config_user['user_stocks']

    # Проверка работы: get_current_exchange_rate
    data_currency = get_current_exchange_rate(currency_codes)
    for price in data_currency:
        print(price)
    print()

    # Проверка работы: get_current_stock_price
    data_stock = get_current_stock_price(stock_codes)
    for key, value in data_stock.items():
        print(f'stock: {key} price: {value}')
