"""
Pydantic models for all API request/response schemas.
Used for validation, serialization, and documentation.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional


# ═══ MODULE 0: DECOMPOSE ═══


class DecomposeRequest(BaseModel):
    idea: str = Field(..., min_length=3, max_length=500, description="Raw business idea string")


class Location(BaseModel):
    city: str = ""
    state: str = ""
    county: str = ""
    metro: str = ""


class DecomposeResponse(BaseModel):
    business_type: str = ""
    location: Location = Field(default_factory=Location)
    target_customers: list[str] = Field(default_factory=list)
    price_tier: str = ""
    source_domains: list[str] = Field(default_factory=list)
    subreddits: list[str] = Field(default_factory=list)
    review_platforms: list[str] = Field(default_factory=list)
    search_queries: list[str] = Field(default_factory=list)


# ═══ MODULE 1: DISCOVER ═══


class DiscoverRequest(BaseModel):
    idea: str = Field(..., min_length=3, max_length=500, description="Raw business idea string")


class Evidence(BaseModel):
    quote: str = ""
    source: str = ""  # "reddit" | "yelp" | "google" | "twitter" | etc
    source_url: str = ""  # Clickable link to actual post/review
    score: int = 0
    upvotes: Optional[int] = None
    date: Optional[str] = None


class Insight(BaseModel):
    id: str = ""
    type: str = ""  # pain_point | unmet_want | market_gap | trend
    title: str = ""
    score: float = 0.0
    frequency_score: float = 0.0
    intensity_score: float = 0.0
    willingness_to_pay_score: float = 0.0
    mention_count: int = 0
    evidence: list[Evidence] = Field(default_factory=list)
    source_platforms: list[str] = Field(default_factory=list)
    audience_estimate: str = ""
    confidence: str = "medium"  # high | medium | low
    confidence_reason: str = ""  # "12 mentions across 2 platforms"


class SourceSummary(BaseModel):
    name: str = ""
    type: str = ""
    post_count: int = 0


class DiscoverResponse(BaseModel):
    sources: list[SourceSummary] = Field(default_factory=list)
    insights: list[Insight] = Field(default_factory=list)


# ═══ MODULE 2: ANALYZE ═══


class AnalyzeRequest(BaseModel):
    idea: str = Field(..., min_length=3, max_length=500, description="Raw business idea string")
    section: str  # opportunity | customers | competitors | rootcause | costs
    prior_context: Optional[dict] = None


class MarketSize(BaseModel):
    value: float = 0
    formatted: str = ""
    methodology: str = ""
    confidence: str = "medium"


class OpportunityResponse(BaseModel):
    tam: MarketSize = Field(default_factory=MarketSize)
    sam: MarketSize = Field(default_factory=MarketSize)
    som: MarketSize = Field(default_factory=MarketSize)
    funnel: Optional[dict] = None
    sanity_check: Optional[dict] = None  # Validation against CUSTOMERS


class CustomerSegment(BaseModel):
    name: str = ""
    description: str = ""
    estimated_size: int = 0
    pain_intensity: float = 0
    primary_need: str = ""
    spending_pattern: str = ""
    where_to_find: str = ""
    market_coverage_percent: float = 0.0  # % of SAM


class CustomersResponse(BaseModel):
    segments: list[CustomerSegment] = Field(default_factory=list)


class Competitor(BaseModel):
    name: str = ""
    location: str = ""
    rating: Optional[float] = None
    price_range: str = ""
    key_strength: str = ""
    key_gap: str = ""
    threat_level: str = "medium"
    url: str = ""


class CompetitorsResponse(BaseModel):
    competitors: list[Competitor] = Field(default_factory=list)
    unfilled_gaps: list[str] = Field(default_factory=list)


class RootCause(BaseModel):
    cause_number: int = 0
    title: str = ""
    explanation: str = ""
    your_move: str = ""
    difficulty: str = "medium"


class RootCauseResponse(BaseModel):
    root_causes: list[RootCause] = Field(default_factory=list)


class CostBreakdown(BaseModel):
    category: str = ""
    min: float = 0
    max: float = 0


class CostsPreviewResponse(BaseModel):
    total_range: dict = Field(default_factory=dict)
    breakdown: list[CostBreakdown] = Field(default_factory=list)
    note: str = ""


class AnalyzeResponse(BaseModel):
    section: str = ""
    data: dict = Field(default_factory=dict)


# ═══ MODULE 3: SETUP ═══


class SetupRequest(BaseModel):
    idea: str = Field(..., min_length=3, max_length=500, description="Raw business idea string")
    analysis_context: Optional[dict] = None
    prior_context: Optional[dict] = None  # COSTS, ROOT_CAUSES, CUSTOMERS from ANALYZE
    selected_tier: str = "MID"  # LEAN | MID | PREMIUM


class LineItem(BaseModel):
    category: str = ""
    name: str = ""
    min_cost: float = 0
    max_cost: float = 0
    notes: str = ""


class CostTier(BaseModel):
    tier: str = ""
    model: str = ""
    total_range: dict = Field(default_factory=dict)
    line_items: list[LineItem] = Field(default_factory=list)


class Supplier(BaseModel):
    category: str = ""
    name: str = ""
    description: str = ""
    location: str = ""
    website: str = ""
    why_recommended: str = ""


class TeamRole(BaseModel):
    title: str = ""
    type: str = ""
    salary_range: dict = Field(default_factory=dict)
    priority: str = "must_have"
    tier: str = "recommended"


class TimelinePhase(BaseModel):
    phase: str = ""
    weeks: str = ""
    milestones: list[str] = Field(default_factory=list)

    @field_validator("weeks", mode="before")
    @classmethod
    def convert_weeks_to_string(cls, v):
        """Convert weeks to string if it's an int."""
        if isinstance(v, int):
            return str(v)
        return v


class SetupResponse(BaseModel):
    cost_tiers: list[CostTier] = Field(default_factory=list)
    suppliers: list[Supplier] = Field(default_factory=list)
    team: list[TeamRole] = Field(default_factory=list)
    timeline: list[TimelinePhase] = Field(default_factory=list)


# ═══ MODULE 4: VALIDATE ═══


class ValidateRequest(BaseModel):
    idea: str = Field(..., min_length=3, max_length=500, description="Raw business idea string")
    channels: list[str] = Field(default_factory=lambda: ["landing_page", "survey"])
    analysis_context: Optional[dict] = None
    setup_context: Optional[dict] = None


class LandingPage(BaseModel):
    headline: str = ""
    subheadline: str = ""
    benefits: list[str] = Field(default_factory=list)
    cta_text: str = ""
    social_proof_quote: str = ""


class SurveyQuestion(BaseModel):
    number: int = 0
    question: str = ""
    type: str = ""
    options: Optional[list[str]] = None


class Survey(BaseModel):
    title: str = ""
    questions: list[SurveyQuestion] = Field(default_factory=list)


class WhatsAppMessage(BaseModel):
    message: str = ""
    tone_note: str = ""


class Community(BaseModel):
    name: str = ""
    platform: str = ""
    member_count: Optional[str] = None
    rationale: str = ""
    link: str = ""


class Scorecard(BaseModel):
    waitlist_target: int = 50  # Start realistic (50 not 500)
    survey_target: int = 10
    switch_pct_target: int = 60
    price_tolerance_target: float = 12.0
    # NEW: Revenue targets
    paid_signups_target: int = 5  # At least 10% conversion
    ltv_cac_ratio_target: float = 3.0  # LTV/CAC > 3x is healthy
    # Customization (NEW)
    is_custom: bool = False  # User modified targets?


class ValidationStrategy(BaseModel):
    """Recommended validation approach based on business model"""
    business_model: str = ""  # B2C SaaS, Local Service, Marketplace, etc
    recommended_methods: list[str] = Field(default_factory=list)  # What to test
    effort_estimate_hours: int = 0
    timeline_weeks: int = 0
    typical_conversion_rate: float = 0.0
    typical_cac: float = 0.0
    description: str = ""


class ValidateResponse(BaseModel):
    landing_page: Optional[LandingPage] = None
    survey: Optional[Survey] = None
    whatsapp_message: Optional[WhatsAppMessage] = None
    communities: list[Community] = Field(default_factory=list)
    scorecard: Scorecard = Field(default_factory=Scorecard)
    # NEW: Strategy guidance
    strategy: Optional[ValidationStrategy] = None


# ═══ VALIDATION EXPERIMENT TRACKING ═══


class ValidationExperimentMetrics(BaseModel):
    waitlist_signups: int = 0
    survey_completions: int = 0
    would_switch_rate: float = 0.0
    price_tolerance_avg: float = 0.0
    community_engagement: int = 0
    reddit_upvotes: int = 0
    # Revenue validation (NEW)
    paid_signups: int = 0
    revenue_collected: float = 0.0
    # Cost tracking (NEW)
    ad_spend: float = 0.0


class CreateValidationExperimentRequest(BaseModel):
    idea_id: str
    methods: list[str] = Field(default_factory=list)
    metrics: ValidationExperimentMetrics = Field(default_factory=ValidationExperimentMetrics)


class ValidationExperimentResponse(BaseModel):
    id: str = ""
    idea_id: str = ""
    methods: list[str] = Field(default_factory=list)
    waitlist_signups: int = 0
    survey_completions: int = 0
    would_switch_rate: float = 0.0
    price_tolerance_avg: float = 0.0
    community_engagement: int = 0
    reddit_upvotes: int = 0
    # Revenue validation (NEW)
    paid_signups: int = 0
    revenue_collected: float = 0.0
    # Cost tracking (NEW)
    ad_spend: float = 0.0
    # Economics (NEW - calculated)
    cac: Optional[float] = None  # Cost per acquisition
    ltv_cac_ratio: Optional[float] = None  # LTV/CAC ratio
    verdict: Optional[str] = None
    reasoning: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class UpdateValidationExperimentRequest(BaseModel):
    waitlist_signups: Optional[int] = None
    survey_completions: Optional[int] = None
    would_switch_rate: Optional[float] = None
    price_tolerance_avg: Optional[float] = None
    community_engagement: Optional[int] = None
    reddit_upvotes: Optional[int] = None
    # Revenue validation (NEW)
    paid_signups: Optional[int] = None
    revenue_collected: Optional[float] = None
    # Cost tracking (NEW)
    ad_spend: Optional[float] = None
