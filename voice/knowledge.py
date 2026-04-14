"""Simple Wikipedia-backed knowledge fetcher.

Provides `get_summary(query)` which tries to fetch a short (2-3 sentence)
summary from Wikipedia. Tries English first, then Hindi when appropriate.

Requires the `wikipedia` package: `pip install wikipedia`.
"""
import re
from typing import Optional

try:
    import wikipedia
except Exception:
    wikipedia = None


def _contains_devanagari(text: str) -> bool:
    return bool(re.search(r"[\u0900-\u097F]", text))


def get_summary(query: str, sentences: int = 2) -> Optional[str]:
    """Return a short summary for `query` or None if not found.

    Tries English Wikipedia first; if no result and query contains Devanagari
    characters, tries Hindi Wikipedia.
    """
    if wikipedia is None:
        raise RuntimeError("wikipedia package not installed. Install with: pip install wikipedia")

    text = query.strip()
    # remove common question words to improve search hits
    text = re.sub(r"\b(kaun|kon|kya|bataye|batayein|who|what|tell me about|describe)\b", "", text, flags=re.I)
    text = text.strip()
    if not text:
        text = query

    # Helper to try search+summary with given language code
    def try_lang(lang: str) -> Optional[str]:
        try:
            wikipedia.set_lang(lang)
            results = wikipedia.search(text)
            if not results:
                return None
            page_title = results[0]
            summary = wikipedia.summary(page_title, sentences=sentences)
            # Collapse whitespace and limit length
            summary = re.sub(r"\s+", " ", summary).strip()
            return summary
        except Exception:
            return None

    # If contains Devanagari try Hindi first
    if _contains_devanagari(query):
        res = try_lang('hi')
        if res:
            return res
        # fallback to English
        return try_lang('en')

    # Default: try English, then Hindi
    res = try_lang('en')
    if res:
        return res
    return try_lang('hi')
