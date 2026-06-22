# SearchHub

> [🇬🇧 English](README.md) | 🇷🇺 Русский

Веб-приложение, которое агрегирует результаты поиска из Google Custom Search и DuckDuckGo, а затем генерирует AI-резюме найденных материалов с помощью GPT. Включает расширение для Chrome.

## Возможности

- Регистрация и авторизация пользователей
- Объединённый поиск через Google Custom Search API и DuckDuckGo
- Ранжирование результатов по релевантности ключевых слов
- Автоматическое AI-резюме результатов поиска (GPT-3.5-turbo через ProxyAPI)
- История поиска с постраничной навигацией
- Повтор или удаление отдельных запросов, очистка всей истории
- Расширение для Chrome с встроенным попапом
- Панель администратора Django

## Технологии

| Слой | Технология |
|---|---|
| Backend | Python 3, Django 3.2 |
| База данных | SQLite (заменяется через настройку `DATABASES`) |
| AI | OpenAI GPT-3.5-turbo через [ProxyAPI](https://proxyapi.ru) |
| API поиска | Google Custom Search API, DuckDuckGo Instant Answer API |
| Frontend | Bootstrap 5.3 |
| Расширение | Chrome Manifest V3 |

## Требования

- Python 3.9+
- Ключ Google Custom Search API и идентификатор поисковой системы — [создать здесь](https://programmablesearchengine.google.com/)
- Ключ ProxyAPI (или OpenAI) для AI-резюме

## Установка

```bash
# Клонировать репозиторий
git clone <repository-url>
cd searchhub

# Создать и активировать виртуальное окружение
python -m venv .venv
source .venv/bin/activate      # Linux / macOS
.venv\Scripts\activate         # Windows

# Установить зависимости
pip install -r requirements.txt

# Создать файл окружения и заполнить учётные данные (см. Переменные окружения)
cp .env.example .env

# Применить миграции базы данных
python manage.py migrate

# (Опционально) Создать суперпользователя для админки
python manage.py createsuperuser

# Запустить сервер разработки
python manage.py runserver
```

Приложение будет доступно по адресу `http://127.0.0.1:8000/`.

## Расширение Chrome

Расширение встраивает веб-приложение в попап браузера.

> **Важно:** Расширению нужны куки с `SameSite=None; Secure` для работы сессий между источниками. Это требует HTTPS в разработке (например, через `django-sslserver`) или следующих настроек в `.env`:
>
> ```env
> SESSION_COOKIE_SAMESITE=None
> SESSION_COOKIE_SECURE=True
> ```

Установка расширения:

1. Откройте `chrome://extensions/`
2. Включите **Режим разработчика**
3. Нажмите **Загрузить распакованное** и выберите папку `extension/`

## Переменные окружения

| Переменная | Описание | По умолчанию |
|---|---|---|
| `SECRET_KEY` | Секретный ключ Django | небезопасное значение |
| `DEBUG` | Режим отладки (`True`/`False`) | `True` |
| `ALLOWED_HOSTS` | Разрешённые хосты через запятую | `localhost,127.0.0.1` |
| `GOOGLE_API_KEY` | Ключ Google Custom Search API | — |
| `GOOGLE_CX` | ID поисковой системы Google | — |
| `PROXYAI_API_KEY` | Ключ OpenAI / ProxyAPI | — |
| `SESSION_COOKIE_SAMESITE` | Установите `None` для расширения | `Lax` |
| `SESSION_COOKIE_SECURE` | Установите `True` при использовании HTTPS | `False` |

## Запуск тестов

```bash
python manage.py test app
```

## Структура проекта

```
├── search/             # Конфигурация проекта Django
│   ├── settings.py
│   └── urls.py
├── app/                # Основное приложение
│   ├── models.py       # Модели Query, Result, Summary
│   ├── views.py        # Обработчики запросов
│   ├── utils.py        # Логика поиска и AI-резюме
│   ├── admin.py        # Настройка панели администратора
│   ├── tests.py        # Тесты
│   ├── migrations/
│   └── templates/
├── extension/          # Расширение для Chrome
├── .env.example        # Шаблон переменных окружения
├── requirements.txt
└── manage.py
```

## Лицензия

[MIT](LICENSE)
