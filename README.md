# SearchHub

> 🇬🇧 English | [🇷🇺 Русский](README.ru.md)

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

| Layer | Technology |
|---|---|
| Backend | Python 3, Django 3.2 |
| Database | SQLite (swappable via `DATABASES` setting) |
| AI | OpenAI GPT-3.5-turbo via [ProxyAPI](https://proxyapi.ru) |
| Search APIs | Google Custom Search API, DuckDuckGo Instant Answer API |
| Frontend | Bootstrap 5.3 |
| Browser Extension | Chrome Manifest V3 |

## Requirements

- Python 3.9+
- Google Custom Search API key and engine ID — [create one here](https://programmablesearchengine.google.com/)
- ProxyAPI key (or direct OpenAI key) for AI summaries

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd searchhub

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate      # Linux / macOS
.venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt

# Create your environment file and fill in credentials (see Environment Variables)
cp .env.example .env

# Apply database migrations
python manage.py migrate

# (Optional) Create an admin superuser
python manage.py createsuperuser

# Run the development server
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`.

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

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `SECRET_KEY` | Django secret key | insecure dev key |
| `DEBUG` | Enable debug mode (`True`/`False`) | `True` |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hosts | `localhost,127.0.0.1` |
| `GOOGLE_API_KEY` | Google Custom Search API key | — |
| `GOOGLE_CX` | Google Custom Search Engine ID | — |
| `PROXYAI_API_KEY` | OpenAI / ProxyAPI key for summaries | — |
| `SESSION_COOKIE_SAMESITE` | Set to `None` for extension support | `Lax` |
| `SESSION_COOKIE_SECURE` | Set to `True` when using HTTPS | `False` |

## Running Tests

```bash
python manage.py test app
```

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
