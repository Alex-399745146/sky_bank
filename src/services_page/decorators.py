# decorators.py
"""Для размещения декораторов"""

import os
from datetime import datetime
from functools import wraps
from typing import Any, Callable


def log(path_filename: str | None = None) -> Callable:

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:

            timer_start = datetime.now()
            func_name: str = str(func.__name__)
            message = f"{func_name} ok"

            try:
                result = func(*args, **kwargs)
                return result

            except ValueError as error_1:
                message = f"{func_name} error: {error_1}. Inputs: {args}, {kwargs}"
                raise

            except Exception as error_2:
                message = f"{func_name} unexpected error: {error_2}. Inputs: {args}, {kwargs}"
                raise

            finally:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                timer_delta = datetime.now() - timer_start
                data_log = f"{timestamp} {message} {timer_delta.microseconds} мксек\n"

                if path_filename:
                    with open(path_filename, "a", encoding="utf-8") as file:
                        file.write(data_log)
                else:
                    with open(f"local_log_{func_name}", "a", encoding="utf-8") as file:
                        file.write(data_log)

        return wrapper

    return decorator


if __name__ == "__main__":  # pragma: no cover
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))  # директ проекта
    path_file_log = os.path.join(project_root, "data", "log_reports.txt")

    log_file = "mylog.txt"

    @log()
    def my_function(x: int, y: int) -> int:
        """Простая функция суммирования аргументов"""
        return x + y

    my_function(1, 2)
