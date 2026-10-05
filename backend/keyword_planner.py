"""Keyword ideas and metrics from Google Keyword Planner (Google Ads API).

Every search volume, competition index and top-of-page bid in a
keyword_planner plan comes from KeywordPlanIdeaService.GenerateKeywordIdeas.
Any failure here raises KeywordPlannerError, which makes the planner switch
to estimated-data mode.
"""

import logging
import os
from pathlib import Path
from typing import Dict, Iterable, List

logger = logging.getLogger(__name__)

# GenerateKeywordIdeasRequest accepts at least 1 and at most 20 keyword seeds.
MAX_SEED_KEYWORDS = 20

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent / "google-ads.yaml"


class KeywordPlannerError(Exception):
    """Keyword Planner could not be used. The message is safe to show to users."""


def config_path() -> Path:
    return Path(os.getenv("GOOGLE_ADS_CONFIGURATION_FILE_PATH") or DEFAULT_CONFIG_PATH)


def customer_id() -> str:
    return (os.getenv("GOOGLE_ADS_CUSTOMER_ID") or "").replace("-", "").strip()


def is_configured() -> bool:
    return config_path().is_file() and bool(customer_id())


def cap_seeds(keywords: Iterable[str], limit: int = MAX_SEED_KEYWORDS) -> List[str]:
    """Return at most `limit` unique, non-empty keywords, keeping their order."""
    seeds: List[str] = []
    seen = set()
    for keyword in keywords:
        cleaned = " ".join(str(keyword).split())
        key = cleaned.lower()
        if not cleaned or key in seen:
            continue
        seen.add(key)
        seeds.append(cleaned)
        if len(seeds) == limit:
            break
    return seeds


def _load_client():
    from google.ads.googleads.client import GoogleAdsClient

    return GoogleAdsClient.load_from_storage(path=str(config_path()))


def _error_codes(exc) -> List[str]:
    codes = []
    for error in getattr(getattr(exc, "failure", None), "errors", []) or []:
        try:
            error_code = error.error_code
            # Works for proto-plus messages (what the library builds) and raw protobuf.
            raw = type(error_code).pb(error_code) if hasattr(type(error_code), "pb") else error_code
            for field, value in raw.ListFields():
                if field.enum_type is not None:
                    codes.append(field.enum_type.values_by_number[value].name)
        except Exception:  # an unexpected failure shape should not hide the original error
            continue
    return sorted(set(codes))


def describe_failure(exc: Exception) -> str:
    """A short, user-facing reason for a failed Google Ads call (no raw error text)."""
    from google.ads.googleads.errors import GoogleAdsException

    if isinstance(exc, GoogleAdsException):
        codes = _error_codes(exc)
        if "DEVELOPER_TOKEN_NOT_APPROVED" in codes:
            return (
                "The Google Ads developer token is not approved for production accounts yet "
                "(DEVELOPER_TOKEN_NOT_APPROVED)."
            )
        if codes:
            return f"The Google Ads API rejected the Keyword Planner request ({', '.join(codes)})."
        return "The Google Ads API rejected the Keyword Planner request."
    return f"The Google Ads API request failed ({type(exc).__name__})."


class KeywordPlanner:
    def __init__(self, client, customer_id: str):
        self._client = client
        self._customer_id = customer_id

    @classmethod
    def from_config(cls) -> "KeywordPlanner":
        path = config_path()
        if not path.is_file():
            raise KeywordPlannerError(f"The Google Ads API is not configured ({path.name} not found).")
        cid = customer_id()
        if not cid:
            raise KeywordPlannerError("The Google Ads API is not configured (GOOGLE_ADS_CUSTOMER_ID is not set).")
        try:
            client = _load_client()
        except Exception as exc:
            logger.warning("Could not load the Google Ads configuration: %s", type(exc).__name__)
            raise KeywordPlannerError(f"The Google Ads configuration in {path.name} could not be loaded.") from exc
        return cls(client, cid)

    def ideas_from_url(self, url: str) -> List[str]:
        """Keyword idea texts for a page, from a URL seed."""
        request = self._new_request()
        request.url_seed.url = url
        return [idea["text"] for idea in self._generate(request)]

    def ideas_from_seeds(self, seed_keywords: Iterable[str], url: str) -> List[Dict]:
        """Keyword ideas with metrics for up to MAX_SEED_KEYWORDS seeds plus a URL.

        The keywords and the URL go into one keyword_and_url_seed. Setting
        keyword_seed and url_seed separately does not work: they belong to the
        same oneof, so the second assignment clears the first.
        """
        seeds = cap_seeds(seed_keywords)
        if not seeds:
            raise ValueError("At least one seed keyword is required.")
        request = self._new_request()
        request.keyword_and_url_seed.url = url
        request.keyword_and_url_seed.keywords.extend(seeds)
        return self._generate(request)

    def _new_request(self):
        request = self._client.get_type("GenerateKeywordIdeasRequest")
        request.customer_id = self._customer_id
        return request

    def _generate(self, request) -> List[Dict]:
        service = self._client.get_service("KeywordPlanIdeaService")
        try:
            # Iterating the pager follows next_page_token across pages.
            results = list(service.generate_keyword_ideas(request=request))
        except Exception as exc:
            reason = describe_failure(exc)
            logger.warning("Keyword Planner request failed: %s", reason)
            raise KeywordPlannerError(reason) from exc

        ideas: List[Dict] = []
        seen = set()
        for idea in results:
            key = idea.text.lower()
            if key in seen:
                continue
            seen.add(key)
            metrics = idea.keyword_idea_metrics
            ideas.append(
                {
                    "text": idea.text,
                    "avg_monthly_searches": int(metrics.avg_monthly_searches),
                    "competition_index": int(metrics.competition_index),
                    "low_top_of_page_bid": metrics.low_top_of_page_bid_micros / 1e6,
                    "high_top_of_page_bid": metrics.high_top_of_page_bid_micros / 1e6,
                }
            )
        return ideas
