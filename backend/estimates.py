"""Estimated-data mode.

Used when Keyword Planner cannot be called, usually because the Google Ads
developer token has not been approved yet. The figures produced here are
placeholders, not market data. They exist so the rest of the pipeline
(ranking, grouping, CPC ranges, themes) can run end to end, and every plan
built from them is marked data_source="estimated".

Each keyword gets figures from a band chosen by its word count, drawn from a
random generator seeded with a SHA-256 hash of the keyword text. The same
keyword therefore always gets the same figures, on every run and machine.
"""

import hashlib
import random
from typing import Dict, Iterable, List
from urllib.parse import urlparse

# (min, max) ranges per band. Competition uses Keyword Planner's 0-100 index.
WORD_COUNT_BANDS = {
    1: {"volume": (5000, 50000), "competition": (60, 90), "low_bid": (1.00, 3.00), "high_bid": (3.00, 8.00)},
    2: {"volume": (1000, 15000), "competition": (40, 70), "low_bid": (0.80, 2.50), "high_bid": (2.50, 6.00)},
    3: {"volume": (100, 5000), "competition": (20, 50), "low_bid": (0.50, 2.00), "high_bid": (2.00, 4.00)},
}
BRAND_TERM_BAND = {"volume": (500, 8000), "competition": (80, 100), "low_bid": (0.30, 1.50), "high_bid": (1.50, 3.50)}


def site_name(url: str) -> str:
    """First label of the host name, without www. https://www.acme.com/x -> acme."""
    host = (urlparse(url).hostname or "").lower()
    if host.startswith("www."):
        host = host[4:]
    return host.split(".")[0] if host else ""


def brand_terms(name: str) -> List[str]:
    return [name, f"{name} store", f"{name} online", f"buy {name}", f"{name} reviews"]


def competitor_terms(name: str) -> List[str]:
    return [name, f"{name} alternative"]


def _rng(keyword: str) -> random.Random:
    digest = hashlib.sha256(keyword.lower().encode("utf-8")).digest()
    return random.Random(int.from_bytes(digest[:8], "big"))


def estimate_keyword(keyword: str, band: Dict) -> Dict:
    rng = _rng(keyword)
    return {
        "text": keyword,
        "avg_monthly_searches": rng.randint(*band["volume"]),
        "competition_index": rng.randint(*band["competition"]),
        "low_top_of_page_bid": round(rng.uniform(*band["low_bid"]), 2),
        "high_top_of_page_bid": round(rng.uniform(*band["high_bid"]), 2),
    }


def estimate_keyword_metrics(seed_keywords: Iterable[str], brand_url: str, competitor_url: str) -> List[Dict]:
    """Placeholder metrics for the seed keywords plus brand and competitor name terms."""
    keywords: List[Dict] = []
    seen = set()

    def add(keyword: str, band: Dict) -> None:
        keyword = " ".join(keyword.split())
        if keyword and keyword.lower() not in seen:
            seen.add(keyword.lower())
            keywords.append(estimate_keyword(keyword, band))

    for keyword in seed_keywords:
        add(keyword, WORD_COUNT_BANDS[min(len(keyword.split()), 3)])

    brand = site_name(brand_url)
    competitor = site_name(competitor_url)
    if brand:
        for keyword in brand_terms(brand):
            add(keyword, BRAND_TERM_BAND)
    if competitor and competitor != brand:
        for keyword in competitor_terms(competitor):
            add(keyword, BRAND_TERM_BAND)
    return keywords
