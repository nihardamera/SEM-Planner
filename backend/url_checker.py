"""Fetches the brand page and extracts its visible text."""

import logging
from typing import Optional

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Pages with more words than this are seeded through Keyword Planner's URL
# seed. Thinner pages (or pages that cannot be fetched) get seed keywords
# from the language model instead.
CONTENT_RICH_MIN_WORDS = 250

USER_AGENT = "Mozilla/5.0 (compatible; SEM-Planner; +https://github.com/nihardamera/SEM-Planner)"


def fetch_page_text(url: str, timeout: float = 10) -> Optional[str]:
    """Visible text of the page, or None if it cannot be fetched or has no text."""
    try:
        response = requests.get(url, timeout=timeout, headers={"User-Agent": USER_AGENT})
        response.raise_for_status()
    except requests.RequestException as exc:
        logger.warning("Could not fetch %s: %s", url, type(exc).__name__)
        return None

    soup = BeautifulSoup(response.content, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    lines = (line.strip() for line in soup.get_text().splitlines())
    text = "\n".join(line for line in lines if line)
    return text or None


def is_content_rich(text: Optional[str]) -> bool:
    return bool(text) and len(text.split()) > CONTENT_RICH_MIN_WORDS
