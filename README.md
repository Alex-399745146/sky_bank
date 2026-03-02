# sky_bank

## Приложение анализа транзакций

---

`Моя курсовая работа по итогам прохождения учебных модулей в skypro. Банковский виджет фильтрующий банковские
трансакции, релевантность данных через API, применение pandas, csv, logging и тд... Приложение будет генерировать
JSON-данные для веб-страниц, формировать Excel-отчеты, а также предоставлять другие сервисы.`

---

Мои конфигурационные настройки, свои можно посмотреть командой:

```
poetry config --list
```
* cache-dir = "C:\\Users\\bache\\AppData\\Local\\pypoetry\\Cache"
* data-dir = "C:\\Users\\bache\\AppData\\Roaming\\pypoetry"
* installer.max-workers = null
* installer.no-binary = null
* installer.only-binary = null
* installer.parallel = true
* installer.re-resolve = false
* keyring.enabled = true
* python.installation-dir = "{data-dir}\\python"  # C:\Users\bache\AppData\Roaming\poetry\python
* requests.max-retries = 0
* solver.lazy-wheel = true
* system-git-client = false
* virtualenvs.create = true
* virtualenvs.in-project = true
* virtualenvs.options.always-copy = false
* virtualenvs.options.no-pip = false
* virtualenvs.options.system-site-packages = false
* virtualenvs.path = "{cache-dir}\\virtualenvs"  # C:\Users\bache\AppData\Local\poetry\Cache\virtualenvs
* virtualenvs.prompt = "{project_name}-py{python_version}"
* virtualenvs.use-poetry-python = false

---

## Структура курсового проекта
```
 tree -L 2
```

```
.
|-- README.md
|-- data
|   |-- log_reports.txt
|   `-- operations.xlsx
|-- main.py
|-- poetry.lock
|-- pyproject.toml
|-- src
|   |-- __init__.py
|   |-- __pycache__
|   |-- data_extract.py
|   |-- main_page
|   |-- reports_page
|   `-- services_page
|-- tests
|   |-- __init__.py
|   `-- test_data_extract.py
`-- user_settings.json

```

---

## API-key открытый ключь не нужен

Для стабильности работы ПО принял решение данные по парам валют и цены на акции брать из отечественных источников
таких ка ЦБ РФ, "Мосбиржа".

* Для корректной работы API-запросов установить библиотеки
```shell
import apimoex
import cbrapi  # type: ignore
```
* В проекте есть шаблон файла `.env` с указанием названий всех переменных, необходимых для работы приложения.
это сделанно для выполнения таска по курсовой работе.

---

### Пользовательские настройки
```
{
  "user_currencies": ["USD", "EUR"],
  "user_stocks": ["SBER", "YDEX", "VTBR", "OZON", "VKCO"]
}
```
* Из-за действующих ограничений политического характера API ПО выдаёт актуальные данные - цены на акции только тех 
компаний которые имеют доступ на торгуемую площадку Мосбиржи, а это как правило акции компаний соблюдающих законы РФ.'

---

## my_pyproject.toml

```
[project]
name = "sky-bank"
version = "0.1.0"
description = ""
authors = [
    {name = "Alexsandr Bachevskiy",email = "bachevskiiaa@gmail.com"}
]
readme = "README.md"
#requires-python = ">=3.13"
requires-python = ">=3.11,<4.0.0" # из-за конфликта c библ. cbrapi
dependencies = [
#    "pandas[excel] (>=3.0.0,<4.0.0)",
    "pandas[excel] (>=2.3.2,<3.0.0)", # из-за конфликта c библ. cbrapi
    "requests (>=2.32.5,<3.0.0)",
    "apimoex (>=1.4.0,<2.0.0)"
]

[tool.poetry]
packages = [{include = "sky_bank", from = "src"}]

[build-system]
requires = ["poetry-core>=2.0.0,<3.0.0"]
build-backend = "poetry.core.masonry.api"

[dependency-groups]
lint = [
    "flake8 (>=7.3.0,<8.0.0)",
    "mypy (>=1.19.1,<2.0.0)",
    "black (>=26.1.0,<27.0.0)",
    "isort (>=7.0.0,<8.0.0)"
]
dev = [
    "python-dotenv (>=1.2.1,<2.0.0)"
]

[tool.mypy]
python_version = "3.13"
disallow_untyped_defs = true
no_implicit_optional = true
warn_return_any = true
check_untyped_defs = false
strict = false
warn_unreachable = false
exclude = [".venv", "__pycache__", ".git"]

[[tool.mypy.overrides]]
module = ['tests.*'] # для какого модуля
allow_untyped_defs = true # переопределение настройки

[tool.black]
line-length = 119
exclude = '''
(
  /(
      \.eggs
    | \.git
    | \.hg
    | \.mypy_cache
    | \.tox
    | \.venv
    | dist
  )/
  | foo.py
)
'''

[tool.isort]
line_length = 119
```
