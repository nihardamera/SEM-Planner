"""End-to-end tests of generate_full_sem_plan with Groq and Google Ads replaced by fakes."""

import estimates
import keyword_planner
import sem_plan
from conftest import (
    BRAND_URL,
    COMPETITOR_URL,
    RICH_PAGE_TEXT,
    THIN_PAGE_TEXT,
    developer_token_not_approved,
    make_idea,
)
from models import PlanRequest

REQUEST = PlanRequest(
    brand_url=BRAND_URL,
    competitor_url=COMPETITOR_URL,
    average_product_price=110,
    target_roas_percentage=400,
)

# (text, avg monthly searches, competition index, low bid, high bid)
PLANNER_IDEAS = [
    ("trail running shoes", 12000, 80, 1.20, 3.40),
    ("running shoes sale", 20000, 90, 0.50, 1.50),
    ("waterproof hiking boots", 8000, 60, 0.90, 2.10),
    ("hiking boots women", 3000, 40, 1.00, 2.00),
    ("shoe store near me", 400, 30, 0.40, 1.10),  # below the 500 searches filter
]
URL_IDEAS = [f"url idea {number}" for number in range(60)]

THEMES = "Lightweight trail running shoes\nWaterproof boots for winter hikes\n"


def planner_responder(request):
    if "url_seed" in request:
        return [make_idea(text) for text in URL_IDEAS]
    assert "keyword_and_url_seed" in request
    return [make_idea(*row) for row in PLANNER_IDEAS]


def all_keywords(plan):
    return {keyword.text: keyword for group in plan.search_campaign_plan.ad_groups for keyword in group.keywords}


def test_keyword_planner_path_joins_llm_groups_to_api_metrics(monkeypatch, fake_ads, fake_groq):
    monkeypatch.setattr(sem_plan, "fetch_page_text", lambda url: RICH_PAGE_TEXT)
    service = fake_ads(planner_responder)
    groq = fake_groq(
        groups={
            # Different casing, an invented keyword, and a keyword repeated in a second group.
            "Running Shoes": ["Trail Running Shoes", "running shoes sale", "barefoot shoes"],
            "Hiking Boots": ["waterproof hiking boots", "hiking boots women", "trail running shoes"],
        },
        themes=THEMES,
    )

    plan = sem_plan.generate_full_sem_plan(REQUEST)

    assert plan.data_source == "keyword_planner"
    assert plan.estimated_reason is None
    assert plan.seed_source == "keyword_planner"
    assert groq.prompts_containing("seed keywords") == []  # a content-rich page is seeded by Keyword Planner

    groups = {group.ad_group_name: group for group in plan.search_campaign_plan.ad_groups}
    assert list(groups) == ["Running Shoes", "Hiking Boots"]
    assert {k.text for k in groups["Running Shoes"].keywords} == {"trail running shoes", "running shoes sale"}
    assert {k.text for k in groups["Hiking Boots"].keywords} == {"waterproof hiking boots", "hiking boots women"}

    # Metrics are Keyword Planner's, not the model's.
    trail = all_keywords(plan)["trail running shoes"]
    assert (trail.avg_monthly_searches, trail.competition_index) == (12000, 80)
    assert (trail.low_top_of_page_bid, trail.high_top_of_page_bid) == (1.20, 3.40)
    assert "barefoot shoes" not in all_keywords(plan)
    assert "shoe store near me" not in all_keywords(plan)

    # CPC range = mean low bid to mean high bid of the group's keywords.
    assert (groups["Running Shoes"].cpc_range_low, groups["Running Shoes"].cpc_range_high) == (0.85, 2.45)
    assert (groups["Hiking Boots"].cpc_range_low, groups["Hiking Boots"].cpc_range_high) == (0.95, 2.05)
    assert groups["Running Shoes"].suggested_match_types == ["Phrase", "Exact"]

    ranking = plan.search_campaign_plan.ranking
    assert (ranking.candidates, ranking.kept, ranking.min_avg_monthly_searches) == (5, 4, 500)
    assert plan.pmax_plan.search_themes == ["Lightweight trail running shoes", "Waterproof boots for winter hikes"]

    # Second request: seeds and competitor URL travel together in keyword_and_url_seed.
    first, second = service.requests
    assert first.url_seed.url == BRAND_URL
    assert second.customer_id == "0000000000"
    assert second.keyword_and_url_seed.url == COMPETITOR_URL
    assert list(second.keyword_and_url_seed.keywords) == URL_IDEAS[:20]


def test_seed_keywords_are_capped_at_20(monkeypatch, fake_ads, fake_groq):
    monkeypatch.setattr(sem_plan, "fetch_page_text", lambda url: RICH_PAGE_TEXT)
    service = fake_ads(planner_responder)
    fake_groq(groups={"Shoes": [row[0] for row in PLANNER_IDEAS]}, themes=THEMES)

    plan = sem_plan.generate_full_sem_plan(REQUEST)

    sent = list(service.requests[1].keyword_and_url_seed.keywords)
    assert len(URL_IDEAS) == 60
    assert len(sent) == keyword_planner.MAX_SEED_KEYWORDS == 20
    assert plan.seed_keywords == sent


def test_planner_never_sends_more_than_20_seeds(fake_ads):
    service = fake_ads(lambda request: [])
    planner = keyword_planner.KeywordPlanner.from_config()

    planner.ideas_from_seeds([f"keyword {n}" for n in range(50)] + ["keyword 1"], COMPETITOR_URL)

    assert len(service.requests[0].keyword_and_url_seed.keywords) == 20


def test_google_ads_failure_uses_estimated_data_with_reason(fake_ads, fake_groq):
    def responder(request):
        raise developer_token_not_approved()

    fake_ads(responder)
    groq = fake_groq(
        seeds="Running Shoes, trail running shoes for women, hiking boots",
        groups={
            "Brand Terms": ["example-brand", "example-brand store", "buy example-brand"],
            "Running": ["running shoes"],
        },
        themes=THEMES,
    )

    first = sem_plan.generate_full_sem_plan(REQUEST)
    second = sem_plan.generate_full_sem_plan(REQUEST)

    assert first.data_source == "estimated"
    assert "DEVELOPER_TOKEN_NOT_APPROVED" in first.estimated_reason
    assert first.seed_source == "language_model"
    assert first.seed_keywords == ["running shoes", "trail running shoes for women", "hiking boots"]
    # The seed prompt carried the extracted page text, not just the URL.
    assert THIN_PAGE_TEXT in groq.prompts_containing("seed keywords")[0]

    # Same input, same plan.
    assert first.model_dump() == second.model_dump()

    keywords = all_keywords(first)
    expected = estimates.estimate_keyword("running shoes", estimates.WORD_COUNT_BANDS[2])
    assert keywords["running shoes"].avg_monthly_searches == expected["avg_monthly_searches"]
    assert keywords["running shoes"].low_top_of_page_bid == expected["low_top_of_page_bid"]

    # Brand terms are generic, not tied to one product category.
    for term in estimates.brand_terms("example-brand"):
        assert term in keywords
    assert not any(text.startswith("example-brand ") and "shoe" in text for text in keywords)
    assert "example-rival alternative" in keywords
    # Ranked keywords the model left out are kept visible, not dropped.
    assert first.search_campaign_plan.ad_groups[-1].ad_group_name == sem_plan.UNGROUPED_AD_GROUP


def test_missing_google_ads_config_uses_estimated_data(fake_groq):
    fake_groq(seeds="running shoes", groups={"Running": ["running shoes"]}, themes=THEMES)

    plan = sem_plan.generate_full_sem_plan(REQUEST)

    assert plan.data_source == "estimated"
    assert plan.estimated_reason == "The Google Ads API is not configured (absent-google-ads.yaml not found)."


def test_unreachable_page_sends_only_the_url_and_says_so(monkeypatch, fake_groq):
    monkeypatch.setattr(sem_plan, "fetch_page_text", lambda url: None)
    groq = fake_groq(seeds="running shoes", groups={"Running": ["running shoes"]}, themes=THEMES)

    sem_plan.generate_full_sem_plan(REQUEST)

    prompt = groq.prompts_containing("seed keywords")[0]
    assert "could not be fetched" in prompt
    assert "Page text:" not in prompt


def test_no_keyword_above_volume_filter_skips_grouping(fake_ads, fake_groq):
    fake_ads(lambda request: [make_idea("tiny keyword", searches=10, competition=5, low=0.1, high=0.2)])
    groq = fake_groq(seeds="tiny keyword")

    plan = sem_plan.generate_full_sem_plan(REQUEST)

    assert plan.data_source == "keyword_planner"
    assert plan.search_campaign_plan.ad_groups == []
    assert plan.pmax_plan.search_themes == []
    assert groq.prompts_containing("Group these Google Ads keywords") == []
