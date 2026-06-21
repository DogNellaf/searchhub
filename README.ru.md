# SearchHub

**[English version](README.md)**

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

- **Backend:** Python 3, Django 3.2
- **База данных:** SQLite (заменяется через настройку `DATABASES`)
- **AI:** OpenAI GPT-3.5-turbo через [ProxyAPI](https://proxyapi.ru)
- **API поиска:** Google Custom Search API, DuckDuckGo Instant Answer API
- **Frontend:** Bootstrap 5.3
- **Расширение:** Chrome Manifest V3

## Требования

- Python 3.9+
- Ключ Google Custom Search API и идентификатор поисковой системы — [создать здесь](https://programmablesearchengine.google.com/)
- Ключ ProxyAPI (или OpenAI) для AI-резюме

## Установка

**1. Установите зависимости:**

```bash
pip install -r requirements.txt
```

**2. Создайте файл окружения:**

```bash
cp .env.example .env
```

Откройте `.env` и заполните учётные данные:

```env
SECRET_KEY=ваш-django-secret-key
GOOGLE_API_KEY=ваш-google-api-key
GOOGLE_CX=идентификатор-поисковой-системы
PROXYAI_API_KEY=ваш-proxyai-или-openai-ключ
```

**3. Примените миграции базы данных:**

```bash
python manage.py migrate
```

**4. (Опционально) Создайте суперпользователя для админки:**

```bash
python manage.py createsuperuser
```

**5. Запустите сервер разработки:**

```bash
python manage.py runserver
```

Откройте [http://localhost:8000](http://localhost:8000) в браузере.

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

## Запуск тестов

```bash
python manage.py test app
```

## Переменные окружения

| Переменная | По умолчанию | Описание |
|---|---|---|
| `SECRET_KEY` | (небезопасное) | Секретный ключ Django |
| `DEBUG` | `True` | Режим отладки |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | Разрешённые хосты через запятую |
| `GOOGLE_API_KEY` | — | Ключ Google Custom Search API |
| `GOOGLE_CX` | — | ID поисковой системы Google |
| `PROXYAI_API_KEY` | — | Ключ OpenAI / ProxyAPI |
| `SESSION_COOKIE_SAMESITE` | `Lax` | Установите `None` для расширения |
| `SESSION_COOKIE_SECURE` | `False` | Установите `True` при использовании HTTPS |

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
