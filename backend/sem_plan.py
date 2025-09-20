import random
from typing import List, Dict
from url_checker import analyze_url_content
from models import PlanRequest, PlanResponse, SearchCampaignPlan, PMaxPlan, ShoppingCampaignPlan, AdGroup
from llm_calls import generate_seed_keywords, cluster_keywords, generate_pmax_themes
from keywords import get_keyword_ideas_1, get_keyword_ideas_2

async def generate_full_sem_plan(request: PlanRequest) -> PlanResponse:
    # Try Google Ads API first, fallback to mock data if not available
    try:
        if not await analyze_url_content(request.brand_url):
            seed_keywords = await generate_seed_keywords(request.brand_url)
        else:
            seed_keywords = await get_keyword_ideas_1(request.brand_url)

        keyword_ideas = await get_keyword_ideas_2(seed_keywords, request.competitor_url)
        print("✅ Using Google Ads API data")

    except Exception as e:
        error_msg = str(e)
        if "DEVELOPER_TOKEN_NOT_APPROVED" in error_msg:
            print("⚠️  Developer token not approved for production. Using mock data.")
            print("💡 Apply for Basic/Standard access at: https://developers.google.com/google-ads/api/docs/access-levels")
        else:
            print(f"⚠️  Google Ads API error: {error_msg}")

        print("🔄 Generating comprehensive mock SEM plan...")
        return await generate_mock_sem_plan(request)

    filtered_keywords = [kw for kw in keyword_ideas if kw['avg_monthly_searches'] >= 500]

    if not filtered_keywords:
        pruned_keywords = []
    else:
        volumes = [kw['avg_monthly_searches'] for kw in filtered_keywords]
        bids = [((kw['low_top_of_page_bid'] + kw['high_top_of_page_bid']) / 2) for kw in filtered_keywords]
        competitions = [kw['competition_index'] for kw in filtered_keywords]

        min_vol, max_vol = min(volumes), max(volumes)
        min_bid, max_bid = min(bids), max(bids)
        min_comp, max_comp = min(competitions), max(competitions)

        def normalize(val, min_val, max_val):
            return (val - min_val) / (max_val - min_val) if max_val > min_val else 0.0

        w1, w2, w3 = 0.4, 0.4, 0.2

        for kw in filtered_keywords:
            norm_vol = normalize(kw['avg_monthly_searches'], min_vol, max_vol)
            avg_bid = (kw['low_top_of_page_bid'] + kw['high_top_of_page_bid']) / 2
            norm_bid = normalize(avg_bid, min_bid, max_bid)
            norm_comp = normalize(kw['competition_index'], min_comp, max_comp)
            kw['roas_score'] = (w1 * norm_vol) + (w2 * norm_bid) - (w3 * norm_comp)

        pruned_keywords = sorted(filtered_keywords, key=lambda x: x['roas_score'], reverse=True)[:50]
    
    keyword_texts = [kw['text'] for kw in pruned_keywords]

    clustered_ad_groups = await cluster_keywords(keyword_texts)

    search_ad_groups = []
    for group_name, keywords in clustered_ad_groups.items():
        group_keyword_data = [kw for kw in pruned_keywords if kw['text'] in keywords]
        if not group_keyword_data:
            continue
        low_bids = [kw['low_top_of_page_bid'] for kw in group_keyword_data]
        high_bids = [kw['high_top_of_page_bid'] for kw in group_keyword_data]
        avg_low_bid = sum(low_bids) / len(low_bids)
        avg_high_bid = sum(high_bids) / len(high_bids)
        
        ad_group = AdGroup(
            ad_group_name=group_name,
            theme=f"Theme related to {keywords}",
            keywords=keywords,
            suggested_match_types=["Phrase", "Exact"],
            suggested_cpc_range=f"${avg_low_bid:.2f} - ${avg_high_bid:.2f}"
        )
        search_ad_groups.append(ad_group)

    search_plan = SearchCampaignPlan(ad_groups=search_ad_groups)

    ad_group_themes = [ag.theme for ag in search_ad_groups]
    pmax_themes = await generate_pmax_themes(ad_group_themes)
    pmax_plan = PMaxPlan(search_themes=pmax_themes)

    target_roas_ratio = request.target_roas_percentage / 100.0
    target_cpa = request.average_product_price / target_roas_ratio
    conversion_rate = 0.02
    
    target_cpc = target_cpa * conversion_rate
    
    explanation_text = (
        f"Based on an average product price of ${request.average_product_price:.2f} and a "
        f"target ROAS of {request.target_roas_percentage}%, your allowable ad spend per sale (Target CPA) "
        f"is ${target_cpa:.2f}. With an assumed 2% conversion rate, the suggested Target CPC is calculated "
        f"to be profitable while meeting your ROAS goal."
    )

    shopping_plan = ShoppingCampaignPlan(
        target_cpa=round(target_cpa, 2),
        suggested_target_cpc=round(target_cpc, 2),
        explanation=explanation_text
    )

    # 9. Assemble the final response
    return PlanResponse(
        search_campaign_plan=search_plan,
        pmax_plan=pmax_plan,
        shopping_campaign_plan=shopping_plan
    )


async def generate_mock_sem_plan(request: PlanRequest) -> PlanResponse:
    """Generate a comprehensive mock SEM plan when Google Ads API is not available."""

    # Check if we can use AI or need to use static data
    try:
        seed_keywords = await generate_seed_keywords(request.brand_url)
    except Exception as e:
        print(f"⚠️  AI API quota exceeded. Using static mock data: {e}")
        return generate_static_mock_plan(request)

    # Create realistic mock keyword data based on the brand
    mock_keywords = []
    base_keywords = seed_keywords[:20]  # Use first 20 AI-generated keywords

    for keyword in base_keywords:
        # Generate realistic metrics based on keyword characteristics
        keyword_length = len(keyword.split())

        # Longer keywords typically have lower volume but higher intent
        if keyword_length == 1:
            volume = random.randint(5000, 50000)
            competition = random.uniform(0.6, 0.9)
            low_bid = random.uniform(1.0, 3.0)
            high_bid = random.uniform(3.0, 8.0)
        elif keyword_length == 2:
            volume = random.randint(1000, 15000)
            competition = random.uniform(0.4, 0.7)
            low_bid = random.uniform(0.8, 2.5)
            high_bid = random.uniform(2.5, 6.0)
        else:  # 3+ words (long-tail)
            volume = random.randint(100, 5000)
            competition = random.uniform(0.2, 0.5)
            low_bid = random.uniform(0.5, 2.0)
            high_bid = random.uniform(2.0, 4.0)

        mock_keywords.append({
            'text': keyword,
            'avg_monthly_searches': volume,
            'low_top_of_page_bid': low_bid,
            'high_top_of_page_bid': high_bid,
            'competition_index': competition
        })

    # Add some branded keywords
    brand_name = request.brand_url.replace('https://', '').replace('http://', '').replace('www.', '').split('.')[0]
    branded_keywords = [
        f"{brand_name}",
        f"{brand_name} shoes",
        f"{brand_name} sneakers",
        f"{brand_name} store",
        f"buy {brand_name}"
    ]

    for keyword in branded_keywords:
        mock_keywords.append({
            'text': keyword,
            'avg_monthly_searches': random.randint(500, 8000),
            'low_top_of_page_bid': random.uniform(0.3, 1.5),
            'high_top_of_page_bid': random.uniform(1.5, 3.5),
            'competition_index': random.uniform(0.8, 1.0)  # High competition for branded terms
        })

    # Calculate ROAS scores and filter keywords
    volumes = [kw['avg_monthly_searches'] for kw in mock_keywords]
    bids = [(kw['low_top_of_page_bid'] + kw['high_top_of_page_bid']) / 2 for kw in mock_keywords]
    competitions = [kw['competition_index'] for kw in mock_keywords]

    min_vol, max_vol = min(volumes), max(volumes)
    min_bid, max_bid = min(bids), max(bids)
    min_comp, max_comp = min(competitions), max(competitions)

    def normalize(val, min_val, max_val):
        return (val - min_val) / (max_val - min_val) if max_val > min_val else 0.0

    w1, w2, w3 = 0.4, 0.4, 0.2

    for kw in mock_keywords:
        norm_vol = normalize(kw['avg_monthly_searches'], min_vol, max_vol)
        avg_bid = (kw['low_top_of_page_bid'] + kw['high_top_of_page_bid']) / 2
        norm_bid = normalize(avg_bid, min_bid, max_bid)
        norm_comp = normalize(kw['competition_index'], min_comp, max_comp)
        kw['roas_score'] = (w1 * norm_vol) + (w2 * norm_bid) - (w3 * norm_comp)

    # Select top keywords
    top_keywords = sorted(mock_keywords, key=lambda x: x['roas_score'], reverse=True)[:25]
    keyword_texts = [kw['text'] for kw in top_keywords]

    # Cluster keywords into ad groups
    clustered_ad_groups = await cluster_keywords(keyword_texts)

    # Create search campaign ad groups
    search_ad_groups = []
    for group_name, keywords in clustered_ad_groups.items():
        group_keyword_data = [kw for kw in top_keywords if kw['text'] in keywords]
        if not group_keyword_data:
            continue

        low_bids = [kw['low_top_of_page_bid'] for kw in group_keyword_data]
        high_bids = [kw['high_top_of_page_bid'] for kw in group_keyword_data]
        avg_low_bid = sum(low_bids) / len(low_bids)
        avg_high_bid = sum(high_bids) / len(high_bids)

        ad_group = AdGroup(
            ad_group_name=group_name,
            theme=f"Targeting customers interested in {group_name.lower()}",
            keywords=keywords,
            suggested_match_types=["Phrase", "Exact", "Broad Match Modified"],
            suggested_cpc_range=f"${avg_low_bid:.2f} - ${avg_high_bid:.2f}"
        )
        search_ad_groups.append(ad_group)

    search_plan = SearchCampaignPlan(ad_groups=search_ad_groups)

    # Generate PMax themes
    ad_group_themes = [ag.theme for ag in search_ad_groups]
    pmax_themes = await generate_pmax_themes(ad_group_themes)
    pmax_plan = PMaxPlan(search_themes=pmax_themes)

    # Calculate shopping campaign metrics
    target_roas_ratio = request.target_roas_percentage / 100.0
    target_cpa = request.average_product_price / target_roas_ratio
    conversion_rate = 0.025  # Slightly higher for mock data
    target_cpc = target_cpa * conversion_rate

    explanation_text = (
        f"📊 MOCK DATA: Based on an average product price of ${request.average_product_price:.2f} and a "
        f"target ROAS of {request.target_roas_percentage}%, your allowable ad spend per sale (Target CPA) "
        f"is ${target_cpa:.2f}. With an estimated 2.5% conversion rate, the suggested Target CPC is "
        f"${target_cpc:.2f}. This mock plan provides realistic estimates for planning purposes."
    )

    shopping_plan = ShoppingCampaignPlan(
        target_cpa=round(target_cpa, 2),
        suggested_target_cpc=round(target_cpc, 2),
        explanation=explanation_text
    )

    return PlanResponse(
        search_campaign_plan=search_plan,
        pmax_plan=pmax_plan,
        shopping_campaign_plan=shopping_plan
    )


def generate_static_mock_plan(request: PlanRequest) -> PlanResponse:
    """Generate a static mock SEM plan without any API calls."""

    # Extract brand name from URL
    brand_name = request.brand_url.replace('https://', '').replace('http://', '').replace('www.', '').split('.')[0]

    # Static mock ad groups with realistic keywords
    mock_ad_groups = [
        AdGroup(
            ad_group_name=f"{brand_name.title()} Brand Terms",
            theme=f"Targeting customers searching specifically for {brand_name}",
            keywords=[f"{brand_name}", f"{brand_name} shoes", f"buy {brand_name}", f"{brand_name} store"],
            suggested_match_types=["Exact", "Phrase"],
            suggested_cpc_range="$0.75 - $2.50"
        ),
        AdGroup(
            ad_group_name="Sustainable Footwear",
            theme="Targeting eco-conscious consumers interested in sustainable shoes",
            keywords=["sustainable shoes", "eco friendly sneakers", "organic footwear", "green shoes"],
            suggested_match_types=["Phrase", "Broad Match Modified"],
            suggested_cpc_range="$1.20 - $3.80"
        ),
        AdGroup(
            ad_group_name="Comfortable Sneakers",
            theme="Targeting customers looking for comfortable everyday shoes",
            keywords=["comfortable sneakers", "walking shoes", "all day comfort shoes", "soft sole shoes"],
            suggested_match_types=["Phrase", "Exact"],
            suggested_cpc_range="$0.95 - $2.75"
        ),
        AdGroup(
            ad_group_name="Athletic Footwear",
            theme="Targeting active lifestyle and fitness enthusiasts",
            keywords=["running shoes", "workout sneakers", "athletic footwear", "gym shoes"],
            suggested_match_types=["Phrase", "Broad Match Modified"],
            suggested_cpc_range="$1.50 - $4.20"
        )
    ]

    search_plan = SearchCampaignPlan(ad_groups=mock_ad_groups)

    # Static PMax themes
    pmax_themes = [
        f"Premium {brand_name.title()} Collection",
        "Sustainable & Comfortable Footwear",
        "Everyday Casual Sneakers",
        "Active Lifestyle Shoes",
        "Eco-Friendly Fashion Forward",
        "All-Day Comfort Technology"
    ]

    pmax_plan = PMaxPlan(search_themes=pmax_themes)

    # Calculate shopping campaign metrics
    target_roas_ratio = request.target_roas_percentage / 100.0
    target_cpa = request.average_product_price / target_roas_ratio
    conversion_rate = 0.025
    target_cpc = target_cpa * conversion_rate

    explanation_text = (
        f"🎯 DEMO PLAN: Based on an average product price of ${request.average_product_price:.2f} and a "
        f"target ROAS of {request.target_roas_percentage}%, your allowable ad spend per sale (Target CPA) "
        f"is ${target_cpa:.2f}. With an estimated 2.5% conversion rate, the suggested Target CPC is "
        f"${target_cpc:.2f}. This comprehensive demo plan showcases the full capabilities of your SEM Planning Engine!"
    )

    shopping_plan = ShoppingCampaignPlan(
        target_cpa=round(target_cpa, 2),
        suggested_target_cpc=round(target_cpc, 2),
        explanation=explanation_text
    )

    return PlanResponse(
        search_campaign_plan=search_plan,
        pmax_plan=pmax_plan,
        shopping_campaign_plan=shopping_plan
    )
