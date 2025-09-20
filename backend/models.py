from pydantic import BaseModel, Field
from typing import List, Dict

class PlanRequest(BaseModel):
    brand_url: str = Field(..., example="https://www.mybrand.com")
    competitor_url: str = Field(..., example="https://www.competitor.com")
    service_locations: str = Field(..., example="New York, San Francisco")
    search_ads_budget: float = Field(..., gt=0, example=1000.0)
    shopping_ads_budget: float = Field(..., gt=0, example=1500.0)
    pmax_ads_budget: float = Field(..., gt=0, example=2000.0)
    average_product_price: float = Field(..., gt=0, example=75.0)
    target_roas_percentage: int = Field(..., gt=0, example=400)

class AdGroup(BaseModel):
    ad_group_name: str
    theme: str
    keywords: List[str]
    suggested_match_types: List[str]
    suggested_cpc_range: str

class SearchCampaignPlan(BaseModel):
    ad_groups: List[AdGroup]

class PMaxPlan(BaseModel):
    search_themes: List[str]

class ShoppingCampaignPlan(BaseModel):
    target_cpa: float
    suggested_target_cpc: float
    explanation: str

class PlanResponse(BaseModel):
    search_campaign_plan: SearchCampaignPlan
    pmax_plan: PMaxPlan
    shopping_campaign_plan: ShoppingCampaignPlan
