from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator


class PlanRequest(BaseModel):
    brand_url: str = Field(..., examples=["https://www.example-brand.com"])
    competitor_url: str = Field(..., examples=["https://www.example-competitor.com"])
    average_product_price: float = Field(..., gt=0, examples=[75.0])
    target_roas_percentage: float = Field(..., gt=0, examples=[400])

    @field_validator("brand_url", "competitor_url")
    @classmethod
    def must_be_http_url(cls, value: str) -> str:
        value = value.strip()
        if not value.startswith(("http://", "https://")):
            raise ValueError("must start with http:// or https://")
        return value


class KeywordMetrics(BaseModel):
    """One keyword with the figures used to rank it.

    In keyword_planner mode the figures come from Google Keyword Planner.
    In estimated mode they are placeholders (see estimates.py).
    """

    text: str
    avg_monthly_searches: int
    competition_index: int = Field(..., description="0 to 100, as reported by Keyword Planner")
    low_top_of_page_bid: float
    high_top_of_page_bid: float
    score: float = Field(..., description="Weighted ranking score, see sem_plan.rank_keywords")


class AdGroup(BaseModel):
    ad_group_name: str = Field(..., description="Name chosen by the language model")
    keywords: List[KeywordMetrics]
    suggested_match_types: List[str]
    cpc_range_low: float = Field(..., description="Mean low top-of-page bid of the group's keywords")
    cpc_range_high: float = Field(..., description="Mean high top-of-page bid of the group's keywords")


class Ranking(BaseModel):
    """How keywords were filtered and ranked before grouping."""

    min_avg_monthly_searches: int
    max_keywords: int
    weight_volume: float
    weight_bid: float
    weight_competition: float
    candidates: int = Field(..., description="Keyword ideas received before filtering")
    kept: int = Field(..., description="Keywords kept after the volume filter and the cap")


class SearchCampaignPlan(BaseModel):
    ad_groups: List[AdGroup]
    ranking: Ranking


class PMaxPlan(BaseModel):
    search_themes: List[str] = Field(..., description="Written by the language model")


class ShoppingCampaignPlan(BaseModel):
    average_product_price: float
    target_roas_percentage: float
    assumed_conversion_rate: float = Field(..., description="Fraction of clicks assumed to convert")
    target_cpa: float
    suggested_target_cpc: float
    explanation: str


class PlanResponse(BaseModel):
    data_source: Literal["keyword_planner", "estimated"]
    estimated_reason: Optional[str] = Field(
        None, description="Why Keyword Planner data was not used. Null when data_source is keyword_planner."
    )
    seed_keywords: List[str]
    seed_source: Literal["keyword_planner", "language_model"]
    search_campaign_plan: SearchCampaignPlan
    pmax_plan: PMaxPlan
    shopping_campaign_plan: ShoppingCampaignPlan
