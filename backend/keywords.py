import os
from typing import List, Dict
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from dotenv import load_dotenv

load_dotenv()

async def get_keyword_ideas_1(url: str) -> List[Dict]:
    client = GoogleAdsClient.load_from_storage()
    customer_id = os.getenv("GOOGLE_ADS_CUSTOMER_ID")

    keyword_plan_idea_service = client.get_service("KeywordPlanIdeaService")
    request = client.get_type("GenerateKeywordIdeasRequest")
    request.customer_id = customer_id
    if url:
        request.url_seed.url = url

    try:
        response = keyword_plan_idea_service.generate_keyword_ideas(request=request)
        results = []
        for idea in response.results:
            results.append(idea.text)
        return results
    except GoogleAdsException as ex:
        print(f"Google Ads API error: {ex}")
        raise



async def get_keyword_ideas_2(seed_keywords: List[str], competitor_url: str) -> List[Dict]:
    client = GoogleAdsClient.load_from_storage()
    customer_id = os.getenv("GOOGLE_ADS_CUSTOMER_ID")

    keyword_plan_idea_service = client.get_service("KeywordPlanIdeaService")
    request = client.get_type("GenerateKeywordIdeasRequest")
    request.customer_id = customer_id
    request.keyword_seed.keywords.extend(seed_keywords)
    if competitor_url:
        request.url_seed.url = competitor_url

    try:
        response = keyword_plan_idea_service.generate_keyword_ideas(request=request)
        results = []
        for idea in response.results:
            results.append({
                "text": idea.text,
                "avg_monthly_searches": idea.keyword_idea_metrics.avg_monthly_searches,
                "competition_level": idea.keyword_idea_metrics.competition.name,
                "competition_index": idea.keyword_idea_metrics.competition_index,
                "low_top_of_page_bid": idea.keyword_idea_metrics.low_top_of_page_bid_micros / 1e6,
                "high_top_of_page_bid": idea.keyword_idea_metrics.high_top_of_page_bid_micros / 1e6,
            })
        return results
    except GoogleAdsException as ex:
        print(f"Google Ads API error: {ex}")
        raise
