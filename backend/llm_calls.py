"""Language model calls (Groq).

The model only produces text: seed keyword phrases, ad group names with the
keywords that belong in each, and Performance Max search themes. No number
in the plan comes from the model.

Every failure raises LLMError with a plain message that is safe to return to
the client. Raw exception text is logged on the server only.
"""

import json
import logging
import os
import re
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "llama-3.1-8b-instant"

# How much extracted page text is sent with the seed keyword prompt.
PAGE_TEXT_LIMIT = 3000

# Google Ads limits a Performance Max search theme to 80 characters.
MAX_THEME_LENGTH = 80
PMAX_THEME_COUNT = 6

_LIST_MARKER = re.compile(r"^\s*(?:\d+\s*[.)]|[-*•])\s*")


class LLMError(Exception):
    """A language model call failed. The message is plain text that is safe to show to users."""


def is_configured() -> bool:
    return bool(os.getenv("GROQ_API_KEY"))


def _model() -> str:
    return os.getenv("GROQ_MODEL") or DEFAULT_MODEL


def _get_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise LLMError("The language model is not configured: GROQ_API_KEY is not set on the backend.")
    from groq import Groq

    return Groq(api_key=api_key)


def _complete(system: str, prompt: str, max_tokens: int, task: str) -> str:
    client = _get_client()
    try:
        response = client.chat.completions.create(
            model=_model(),
            messages=[{"role": "system", "content": system}, {"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0,
        )
        text = response.choices[0].message.content
    except Exception:
        logger.exception("Groq request failed while %s", task)
        raise LLMError(f"The language model request failed while {task}. Try again in a moment.") from None
    if not text or not text.strip():
        raise LLMError(f"The language model returned an empty response while {task}.")
    return text.strip()


def _clean_phrase(text: str) -> str:
    text = _LIST_MARKER.sub("", text).strip().strip("\"'`").strip()
    return " ".join(text.split())


def _parse_list(text: str, separators: str, max_length: int) -> List[str]:
    items: List[str] = []
    seen = set()
    for part in re.split(f"[{separators}]", text):
        phrase = _clean_phrase(part)
        # Skip empty items, preambles such as "Here are the keywords:" and overlong lines.
        if not phrase or phrase.endswith(":") or len(phrase) > max_length:
            continue
        if phrase.lower() not in seen:
            seen.add(phrase.lower())
            items.append(phrase)
    return items


def generate_seed_keywords(url: str, page_text: Optional[str]) -> List[str]:
    """Up to 15 seed keyword phrases for the brand, from its page text when available."""
    if page_text:
        excerpt = page_text[:PAGE_TEXT_LIMIT]
        source = (
            f"Below is the visible text of the page at {url}, truncated to {PAGE_TEXT_LIMIT} characters.\n"
            f"Based on the products and services described in this text"
        )
        appendix = f"\n\nPage text:\n{excerpt}"
    else:
        source = (
            f"The page at {url} could not be fetched, so only its URL is available.\n"
            f"Based on the URL and domain name alone"
        )
        appendix = ""

    prompt = (
        f"{source}, list 15 seed keywords for a Google Ads search campaign. "
        "Prefer phrases a customer ready to buy would type into Google. "
        "Return only the keywords as one comma-separated list, with no numbering and no other text."
        f"{appendix}"
    )
    text = _complete(
        "You are a search engine marketing specialist.",
        prompt,
        max_tokens=500,
        task="suggesting seed keywords",
    )
    keywords = [keyword.lower() for keyword in _parse_list(text, ",\n", max_length=80)][:15]
    if not keywords:
        raise LLMError("The language model returned no usable seed keywords.")
    return keywords


def _extract_json_object(text: str) -> str:
    fenced = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    if fenced:
        text = fenced.group(1)
    start, end = text.find("{"), text.rfind("}")
    return text[start : end + 1] if start != -1 and end > start else text


def cluster_keywords(keywords: List[str]) -> Dict[str, List[str]]:
    """Ad group name -> keywords, as proposed by the model. Membership is checked by the caller."""
    prompt = f"""Group these Google Ads keywords into 5 to 7 tightly themed ad groups by search intent.
Useful kinds of groups:
- Brand terms: keywords that contain the brand's own name.
- Category or generic terms: broader product or service categories.
- Competitor terms: keywords that contain a competitor's brand name.
- Location terms: keywords that name a place.
- Long-tail or informational queries: longer, more specific or question-style keywords.
Rules:
- Use only keywords from the list, exactly as written. Put each keyword in exactly one group.
- Give each group a short descriptive name.
- Return only a JSON object whose keys are group names and whose values are lists of keywords. No other text.

Keywords: {json.dumps(keywords)}

Example: {{"Brand Terms": ["keyword one", "keyword two"], "Product Category": ["keyword three"]}}"""

    text = _complete(
        "You are a Google Ads specialist. Reply with valid JSON only.",
        prompt,
        max_tokens=1500,
        task="grouping keywords into ad groups",
    )
    try:
        data = json.loads(_extract_json_object(text))
    except ValueError:
        logger.warning("Ad group response was not valid JSON: %.200s", text)
        raise LLMError("The language model returned ad groups that could not be read as JSON.") from None

    if not isinstance(data, dict):
        raise LLMError("The language model returned ad groups in an unexpected format.")
    groups: Dict[str, List[str]] = {}
    for name, members in data.items():
        if isinstance(members, list):
            groups[" ".join(str(name).split())] = [str(member) for member in members]
    if not groups:
        raise LLMError("The language model returned no ad groups.")
    return groups


def generate_pmax_themes(ad_groups: Dict[str, List[str]]) -> List[str]:
    """Performance Max search themes written from the ad group names and their top keywords."""
    summary = "\n".join(f"- {name}: {', '.join(keywords[:5])}" for name, keywords in ad_groups.items())
    prompt = f"""Write {PMAX_THEME_COUNT} search themes for a Google Ads Performance Max campaign.
Base them on these ad groups and their top keywords:
{summary}

Each theme is a short phrase of at most {MAX_THEME_LENGTH} characters describing what customers search for:
product categories, use cases, audiences or seasonal needs. Do not include prices.
Return only the themes, one per line, with no numbering and no other text."""

    text = _complete(
        "You are a Google Ads specialist.",
        prompt,
        max_tokens=400,
        task="writing Performance Max themes",
    )
    themes = _parse_list(text, "\n", max_length=MAX_THEME_LENGTH)[:PMAX_THEME_COUNT]
    if not themes:
        raise LLMError("The language model returned no usable Performance Max themes.")
    return themes
