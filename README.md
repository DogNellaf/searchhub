# SearchHub

**[Русская версия](README.ru.md)**

A web application that aggregates search results from Google Custom Search and DuckDuckGo, then generates an AI-powered summary of the top results using GPT. Includes a Chrome extension for quick access.

## Features

- User registration and authentication
- Combined search across Google Custom Search API and DuckDuckGo
- Results ranked by keyword relevance
- AI-generated summary of search results (GPT-3.5-turbo via ProxyAPI)
- Per-user search history with pagination
- Repeat or delete individual history entries, or clear all history
- Chrome extension that embeds the app in a popup
- Django admin panel for data management

## Tech Stack

- **Backend:** Python 3, Django 3.2
- **Database:** SQLite (swappable via `DATABASES` setting)
- **AI:** OpenAI GPT-3.5-turbo via [ProxyAPI](https://proxyapi.ru)
- **Search APIs:** Google Custom Search API, DuckDuckGo Instant Answer API
- **Frontend:** Bootstrap 5.3
- **Browser Extension:** Chrome Manifest V3

## Prerequisites

- Python 3.9+
- Google Custom Search API key and engine ID — [create one here](https://programmablesearchengine.google.com/)
- ProxyAPI key (or direct OpenAI key) for AI summaries

## Setup

**1. Clone the repository and install dependencies:**

```bash
pip install -r requirements.txt
```

**2. Create your environment file:**

```bash
cp .env.example .env
```

Edit `.env` and fill in your credentials:

```env
SECRET_KEY=your-django-secret-key
GOOGLE_API_KEY=your-google-api-key
GOOGLE_CX=your-google-custom-search-engine-id
PROXYAI_API_KEY=your-proxyai-or-openai-key
```

**3. Apply database migrations:**

```bash
python manage.py migrate
```

**4. (Optional) Create an admin superuser:**

```bash
python manage.py createsuperuser
```

**5. Start the development server:**

```bash
python manage.py runserver
```

Open [http://localhost:8000](http://localhost:8000) in your browser.

## Chrome Extension

The extension embeds the web app in a browser popup.

> **Note:** The extension requires `SameSite=None; Secure` cookies to share the session across origins. This means you need HTTPS in development (e.g., via `django-sslserver`) or configure the settings below in `.env`:
>
> ```env
> SESSION_COOKIE_SAMESITE=None
> SESSION_COOKIE_SECURE=True
> ```

To load the extension:

1. Open `chrome://extensions/`
2. Enable **Developer mode**
3. Click **Load unpacked** and select the `extension/` directory

## Running Tests

```bash
python manage.py test app
```

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | (insecure default) | Django secret key |
| `DEBUG` | `True` | Enable debug mode |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | Comma-separated allowed hosts |
| `GOOGLE_API_KEY` | — | Google Custom Search API key |
| `GOOGLE_CX` | — | Google Custom Search Engine ID |
| `PROXYAI_API_KEY` | — | OpenAI / ProxyAPI key for summaries |
| `SESSION_COOKIE_SAMESITE` | `Lax` | Set to `None` for extension support |
| `SESSION_COOKIE_SECURE` | `False` | Set to `True` when using HTTPS |

## Project Structure

```
├── search/             # Django project configuration
│   ├── settings.py
│   └── urls.py
├── app/                # Main application
│   ├── models.py       # Query, Result, Summary models
│   ├── views.py        # View handlers
│   ├── utils.py        # Search and AI summary logic
│   ├── admin.py        # Admin panel configuration
│   ├── tests.py        # Test suite
│   ├── migrations/
│   └── templates/
├── extension/          # Chrome browser extension
├── .env.example        # Environment variable template
├── requirements.txt
└── manage.py
```

## License

[MIT](LICENSE)
