from urllib.parse import quote
import logging

import requests
from django.conf import settings
from openai import OpenAI

logger = logging.getLogger(__name__)


def search_google(query):
    try:
        url = (
            f"https://www.googleapis.com/customsearch/v1"
            f"?key={settings.GOOGLE_API_KEY}&cx={settings.GOOGLE_CX}&q={quote(query)}"
        )
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json().get('items', [])
    except Exception as exc:
        logger.warning('Google search failed: %s', exc)
        return []


def search_duckduckgo(query):
    try:
        url = f"https://api.duckduckgo.com/?q={quote(query)}&format=json"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json().get('RelatedTopics', [])
    except Exception as exc:
        logger.warning('DuckDuckGo search failed: %s', exc)
        return []


def get_search_results(query):
    results = []

    for item in search_google(query):
        results.append({
            'title': item.get('title', ''),
            'url': item.get('link', ''),
            'snippet': item.get('snippet', ''),
        })

    for item in search_duckduckgo(query):
        if 'Text' in item and 'FirstURL' in item:
            results.append({
                'title': item['Text'],
                'url': item['FirstURL'],
                'snippet': item.get('Text', ''),
            })

    return results


def generate_summary(results):
    text_to_summarize = ' '.join(r['snippet'] for r in results if r.get('snippet'))

    if not text_to_summarize.strip():
        return 'Результаты отсутствуют'

    try:
        client = OpenAI(
            api_key=settings.PROXYAI_API_KEY,
            base_url="https://api.proxyapi.ru/openai/v1",
        )
        prompt = f"Сформируй краткую выжимку из этого текста на 150 символов:\n\n{text_to_summarize}"
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
        )
        return completion.choices[0].message.content.strip()
    except Exception as exc:
        logger.warning('Summary generation failed: %s', exc)
        return 'Не удалось сформировать краткий пересказ'


def count_keywords(text, keywords):
    text_lower = text.lower()
    return sum(text_lower.count(kw.lower()) for kw in keywords)
