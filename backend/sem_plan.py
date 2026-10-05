"""Builds the plan.

Division of work:
- Keyword Planner (or, in estimated mode, estimates.py) supplies search
  volumes, competition and top-of-page bids.
- rank_keywords() ranks keywords with a fixed weighted score.
- The language model groups the ranked keywords into named ad groups and
  writes Performance Max themes. It also suggests seed keywords when the
  brand page is too thin for a Keyword Planner URL seed, or when Keyword
  Planner is unavailable.
- CPC ranges are averages of Keyword Planner bids, and the Shopping bid is
  a formula. The model never sets a number.
"""

import logging
from typing import Callable, Dict, List, Sequence

import estimates
import keyword_planner
import llm_calls
from models import (
    AdGroup,
    KeywordMetrics,
    PlanRequest,
    PlanResponse,
    PMaxPlan,
    Ranking,
    SearchCampaignPlan,
    ShoppingCampaignPlan,
)
from url_checker import fetch_page_text, is_content_rich

logger = logging.getLogger(__name__)

# Ranking: score = 0.4 * volume + 0.4 * bid - 0.2 * competition, each term
# min-max normalised to 0..1 across the keywords that pass the volume filter.
MIN_AVG_MONTHLY_SEARCHES = 500
MAX_RANKED_KEYWORDS = 50
WEIGHT_VOLUME = 0.4
WEIGHT_BID = 0.4
WEIGHT_COMPETITION = 0.2

SUGGESTED_MATCH_TYPES = ["Phrase", "Exact"]
UNGROUPED_AD_GROUP = "Ungrouped keywords"

# Share of Shopping clicks assumed to end in a sale. This is an assumption,
# not a figure from any account; change it here if you know your own rate.
ASSUMED_CONVERSION_RATE = 0.02


def _average_bid(keyword: Dict) -> float:
    return (keyword["low_top_of_page_bid"] + keyword["high_top_of_page_bid"]) / 2


def _normaliser(values: Sequence[float]) -> Callable[[float], float]:
    low, high = min(values), max(values)
    if high == low:
        return lambda value: 0.0
    return lambda value: (value - low) / (high - low)


def rank_keywords(ideas: List[Dict]) -> List[Dict]:
    """Filter by volume, score, and return the top MAX_RANKED_KEYWORDS (highest score first)."""
    eligible = [idea for idea in ideas if idea["avg_monthly_searches"] >= MIN_AVG_MONTHLY_SEARCHES]
    if not eligible:
        return []

    volume = _normaliser([idea["avg_monthly_searches"] for idea in eligible])
    bid = _normaliser([_average_bid(idea) for idea in eligible])
    competition = _normaliser([idea["competition_index"] for idea in eligible])

    scored = []
    for idea in eligible:
        score = (
            WEIGHT_VOLUME * volume(idea["avg_monthly_searches"])
            + WEIGHT_BID * bid(_average_bid(idea))
            - WEIGHT_COMPETITION * competition(idea["competition_index"])
        )
        scored.append({**idea, "score": round(score, 4)})

    scored.sort(key=lambda idea: (-idea["score"], idea["text"].lower()))
    return scored[:MAX_RANKED_KEYWORDS]


def _ad_group(name: str, members: List[Dict]) -> AdGroup:
    members = sorted(members, key=lambda keyword: (-keyword["score"], keyword["text"].lower()))
    return AdGroup(
        ad_group_name=name,
        keywords=[KeywordMetrics(**keyword) for keyword in members],
        suggested_match_types=list(SUGGESTED_MATCH_TYPES),
        cpc_range_low=round(sum(k["low_top_of_page_bid"] for k in members) / len(members), 2),
        cpc_range_high=round(sum(k["high_top_of_page_bid"] for k in members) / len(members), 2),
    )


def build_ad_groups(clusters: Dict[str, List[str]], ranked: List[Dict]) -> List[AdGroup]:
    """Join the model's groups to the ranked keyword metrics.

    Keywords the model invented or altered are dropped, a keyword listed in
    several groups stays in the first one, and ranked keywords the model left
    out are collected in an "Ungrouped keywords" group.
    """
    by_text = {keyword["text"].lower(): keyword for keyword in ranked}
    assigned = set()
    groups: List[AdGroup] = []
    for name, texts in clusters.items():
        members = []
        for text in texts:
            key = " ".join(text.split()).lower()
            if key in by_text and key not in assigned:
                assigned.add(key)
                members.append(by_text[key])
        if members:
            groups.append(_ad_group(name, members))

    leftover = [keyword for keyword in ranked if keyword["text"].lower() not in assigned]
    if leftover:
        groups.append(_ad_group(UNGROUPED_AD_GROUP, leftover))
    return groups


def shopping_bid(
    average_product_price: float,
    target_roas_percentage: float,
    conversion_rate: float = ASSUMED_CONVERSION_RATE,
) -> ShoppingCampaignPlan:
    """Target CPA = price / (ROAS / 100); target CPC = target CPA x conversion rate."""
    roas_ratio = target_roas_percentage / 100.0
    target_cpa = average_product_price / roas_ratio
    target_cpc = target_cpa * conversion_rate
    explanation = (
        f"Target CPA = average product price / (target ROAS / 100) = "
        f"${average_product_price:.2f} / {roas_ratio:.2f} = ${target_cpa:.2f}. "
        f"Suggested target CPC = target CPA x assumed conversion rate = "
        f"${target_cpa:.2f} x {conversion_rate:.1%} = ${target_cpc:.2f}. "
        f"The {conversion_rate:.1%} conversion rate is an assumption, not a figure from your account."
    )
    return ShoppingCampaignPlan(
        average_product_price=average_product_price,
        target_roas_percentage=target_roas_percentage,
        assumed_conversion_rate=conversion_rate,
        target_cpa=round(target_cpa, 2),
        suggested_target_cpc=round(target_cpc, 2),
        explanation=explanation,
    )


def generate_full_sem_plan(request: PlanRequest) -> PlanResponse:
    """Build the plan. Raises llm_calls.LLMError if a language model call fails."""
    page_text = fetch_page_text(request.brand_url)

    seeds: List[str] = []
    seed_source = "keyword_planner"
    data_source = "keyword_planner"
    estimated_reason = None

    try:
        planner = keyword_planner.KeywordPlanner.from_config()
        if is_content_rich(page_text):
            seeds = keyword_planner.cap_seeds(planner.ideas_from_url(request.brand_url))
        if not seeds:
            seeds = keyword_planner.cap_seeds(llm_calls.generate_seed_keywords(request.brand_url, page_text))
            seed_source = "language_model"
        ideas = planner.ideas_from_seeds(seeds, request.competitor_url)
    except keyword_planner.KeywordPlannerError as exc:
        data_source = "estimated"
        estimated_reason = str(exc)
        logger.warning("Using estimated data: %s", estimated_reason)
        if not seeds:
            seeds = keyword_planner.cap_seeds(llm_calls.generate_seed_keywords(request.brand_url, page_text))
            seed_source = "language_model"
        ideas = estimates.estimate_keyword_metrics(seeds, request.brand_url, request.competitor_url)

    ranked = rank_keywords(ideas)

    ad_groups: List[AdGroup] = []
    themes: List[str] = []
    if ranked:
        clusters = llm_calls.cluster_keywords([keyword["text"] for keyword in ranked])
        ad_groups = build_ad_groups(clusters, ranked)
        themes = llm_calls.generate_pmax_themes(
            {group.ad_group_name: [keyword.text for keyword in group.keywords] for group in ad_groups}
        )

    ranking = Ranking(
        min_avg_monthly_searches=MIN_AVG_MONTHLY_SEARCHES,
        max_keywords=MAX_RANKED_KEYWORDS,
        weight_volume=WEIGHT_VOLUME,
        weight_bid=WEIGHT_BID,
        weight_competition=WEIGHT_COMPETITION,
        candidates=len(ideas),
        kept=len(ranked),
    )

    return PlanResponse(
        data_source=data_source,
        estimated_reason=estimated_reason,
        seed_keywords=seeds,
        seed_source=seed_source,
        search_campaign_plan=SearchCampaignPlan(ad_groups=ad_groups, ranking=ranking),
        pmax_plan=PMaxPlan(search_themes=themes),
        shopping_campaign_plan=shopping_bid(request.average_product_price, request.target_roas_percentage),
    )
