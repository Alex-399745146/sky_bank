# views.py
""" Модуль набора основных функций выдающих информацию для главной страницы """

import os

from src.sky_bank.data_extract import get_data_xlsx

if __name__ == "__main__":  # pragma: no cover
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))) # директ проекта
    path_file_xlsx = os.path.join(project_root, "data", "operations.xlsx")

    transactions = get_data_xlsx(path_file_xlsx)


    x = get_count_carts(transactions)
    print(x)
    for k, v in x.items():
        print(f"{k}: {round(v, 2)}")