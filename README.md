# sky_bank

### Приложение анализа транзакций

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

### Структура моего проекта

```
.
|-- README.md
|-- data
|   `-- operations.xlsx
|-- main.py
|-- poetry.lock
|-- pyproject.toml
|-- src
|   `-- sky_bank
|       |-- __init__.py
|       `-- views.py
|-- tests
|   `-- __init__.py
`-- user_settings.json
```

---

### API-key 

Нужно получить на этом ресурсе >>>
[API-ключ](https://marketplace.apilayer.com/)

---

### Пользовательские настройки
```
{
  "user_currencies": ["USD", "EUR"],
  "user_stocks": ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]
}
```