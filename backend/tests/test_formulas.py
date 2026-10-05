"""The numeric parts of the plan: ranking score, CPC join, Shopping bid, estimates."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

import estimates
import keyword_planner
import sem_plan


def idea(text, searches, competition, low, high):
    return {
        "text": text,
        "avg_monthly_searches": searches,
        "competition_index": competition,
        "low_top_of_page_bid": low,
        "high_top_of_page_bid": high,
    }


def test_shopping_bid_formula_uses_named_conversion_rate():
    plan = sem_plan.shopping_bid(average_product_price=110, target_roas_percentage=400)

    assert sem_plan.ASSUMED_CONVERSION_RATE == 0.02
    assert plan.assumed_conversion_rate == sem_plan.ASSUMED_CONVERSION_RATE
    assert plan.target_cpa == 27.50  # 110 / 4.00
    assert plan.suggested_target_cpc == 0.55  # 27.50 x 2%
    assert "2.0%" in plan.explanation
    assert "2.5%" not in plan.explanation


def test_shopping_bid_formula_with_other_conversion_rate():
    plan = sem_plan.shopping_bid(average_product_price=80, target_roas_percentage=250, conversion_rate=0.05)

    assert plan.target_cpa == 32.00  # 80 / 2.50
    assert plan.suggested_target_cpc == 1.60  # 32.00 x 5%
    assert "5.0%" in plan.explanation


def test_ranking_score_is_weighted_and_normalised():
    ranked = sem_plan.rank_keywords(
        [
            idea("low", 1000, 0, 1.0, 1.0),
            idea("high", 2000, 100, 3.0, 3.0),
            idea("middle", 1500, 50, 2.0, 2.0),
            idea("too small", 499, 0, 9.0, 9.0),
        ]
    )

    # score = 0.4 * volume + 0.4 * bid - 0.2 * competition, each min-max normalised.
    assert [(k["text"], k["score"]) for k in ranked] == [("high", 0.6), ("middle", 0.3), ("low", 0.0)]


def test_ranking_keeps_top_50():
    ranked = sem_plan.rank_keywords([idea(f"kw {n}", 1000 + n, 50, 1.0, 2.0) for n in range(80)])

    assert len(ranked) == sem_plan.MAX_RANKED_KEYWORDS == 50
    assert ranked[0]["text"] == "kw 79"


def test_ad_groups_only_contain_ranked_keywords():
    ranked = sem_plan.rank_keywords(
        [idea("a", 1000, 10, 1.0, 2.0), idea("b", 2000, 20, 2.0, 4.0), idea("c", 3000, 30, 3.0, 6.0)]
    )

    groups = sem_plan.build_ad_groups({"G1": ["A", "invented"], "G2": ["a", "b"], "Empty": ["nope"]}, ranked)

    assert [(g.ad_group_name, [k.text for k in g.keywords]) for g in groups] == [
        ("G1", ["a"]),
        ("G2", ["b"]),
        (sem_plan.UNGROUPED_AD_GROUP, ["c"]),
    ]
    assert (groups[0].cpc_range_low, groups[0].cpc_range_high) == (1.0, 2.0)


def test_cap_seeds_dedupes_and_limits():
    seeds = keyword_planner.cap_seeds(["Shoes", "shoes", "  ", "running  shoes"] + [f"k{n}" for n in range(30)])

    assert seeds[:2] == ["Shoes", "running shoes"]
    assert len(seeds) == 20


def test_estimates_are_deterministic_across_processes():
    seeds = ["running shoes", "boots", "waterproof hiking boots for women"]
    here = estimates.estimate_keyword_metrics(seeds, "https://www.acme.com", "https://rival.com")

    code = (
        "import json, estimates;"
        f"print(json.dumps(estimates.estimate_keyword_metrics({seeds!r}, 'https://www.acme.com', 'https://rival.com')))"
    )
    backend = Path(__file__).resolve().parents[1]
    env = {**os.environ, "PYTHONHASHSEED": "12345"}
    out = subprocess.run([sys.executable, "-c", code], cwd=backend, env=env, capture_output=True, text=True, check=True)

    assert json.loads(out.stdout) == here
    assert [k["text"] for k in here] == seeds + estimates.brand_terms("acme") + estimates.competitor_terms("rival")


@pytest.mark.parametrize(
    "url, name",
    [("https://www.acme.com/shop", "acme"), ("http://shop.acme.co.uk", "shop"), ("https://acme.io", "acme")],
)
def test_site_name(url, name):
    assert estimates.site_name(url) == name
