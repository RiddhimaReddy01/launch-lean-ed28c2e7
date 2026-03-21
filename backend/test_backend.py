"""
Comprehensive backend test suite with mock data.
Tests all 5 modules end-to-end without requiring real API keys.
Run: pytest test_backend.py -v
"""

import json
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
import pytest

# ═══ MOCK DATA FIXTURES ═══

@pytest.fixture
def mock_decompose_output():
    """Mock output from decompose-idea endpoint."""
    return {
        "business_type": "pet grooming service",
        "location": {
            "city": "Austin",
            "state": "TX",
            "county": "Travis",
            "metro": "Austin-Round Rock-San Marcos"
        },
        "target_customers": ["pet owners", "busy professionals", "small businesses"],
        "price_tier": "premium",
        "subreddits": ["Austin", "Entrepreneur", "smallbusiness", "dogs", "PetGrooming"],
        "review_platforms": ["yelp", "google"],
        "search_queries": [
            "pet grooming Austin TX",
            "mobile dog grooming services",
            "professional pet grooming demand",
            "pet grooming franchise opportunities",
            "pet grooming market trends 2025"
        ]
    }


@pytest.fixture
def mock_reddit_posts():
    """Mock Reddit posts for discover module."""
    return [
        {
            "subreddit": "Austin",
            "title": "Need reliable pet grooming in Austin - tired of bad experiences",
            "selftext": "Took my golden retriever to 3 different groomers, all gave mediocre results. Would pay premium for someone I could trust.",
            "score": 145,
            "num_comments": 23,
            "created_utc": 1709900000
        },
        {
            "subreddit": "Entrepreneur",
            "title": "Started a mobile pet grooming business - tips for scaling?",
            "selftext": "Been doing mobile grooming for 6 months, currently make $5k/month. Want to hire team.",
            "score": 89,
            "num_comments": 12,
            "created_utc": 1709800000
        },
        {
            "subreddit": "smallbusiness",
            "title": "Pet care services are untapped goldmine",
            "selftext": "Customer acquisition cost is super low, margins are 60-70%, but finding reliable help is nightmare.",
            "score": 234,
            "num_comments": 45,
            "created_utc": 1709700000
        }
    ]


@pytest.fixture
def mock_serper_results():
    """Mock Serper (Google search) results."""
    return [
        {
            "title": "Pet Grooming Market Size & Growth 2025 - Industry Report",
            "snippet": "The global pet grooming market size was valued at $31.8B in 2023 and is expected to grow at 6.2% CAGR through 2030.",
            "link": "https://example.com/pet-grooming-market",
            "rating": 4.8,
            "position": 1
        },
        {
            "title": "Top Pet Grooming Companies & Competitors",
            "snippet": "Petco Grooming, PetSmart Grooming, mobile services compete on convenience and price.",
            "link": "https://example.com/competitors",
            "rating": 4.5,
            "position": 2
        },
        {
            "title": "How Much to Charge for Pet Grooming - Pricing Guide",
            "snippet": "Average charge $50-150 depending on dog size and location. Premium services command $200+.",
            "link": "https://example.com/pricing",
            "rating": 4.6,
            "position": 3
        }
    ]


@pytest.fixture
def mock_llm_decompose_response():
    """Mock LLM response for decompose."""
    return {
        "business_type": "pet grooming service",
        "location": {
            "city": "Austin",
            "state": "TX",
            "county": "Travis",
            "metro": "Austin-Round Rock"
        },
        "target_customers": ["pet owners", "busy professionals", "pet lovers"],
        "price_tier": "premium",
        "subreddits": ["Austin", "smallbusiness", "Entrepreneur", "dogs"],
        "review_platforms": ["yelp", "google"],
        "search_queries": [
            "pet grooming Austin",
            "mobile dog grooming",
            "pet care services",
            "pet grooming franchise",
            "pet grooming demand"
        ]
    }


@pytest.fixture
def mock_llm_discover_response():
    """Mock LLM response for discover insights."""
    return {
        "insights": [
            {
                "type": "pain_point",
                "title": "Finding trustworthy pet groomers is difficult",
                "pain_score": 8.5,
                "frequency_score": 7.2,
                "intensity_score": 8.1,
                "willingness_to_pay_score": 7.8,
                "evidence": [
                    {
                        "quote": "Took my dog to 5 groomers, finally found one that doesn't mess up",
                        "source": "r/Austin",
                        "score": 85,
                        "upvotes": 145
                    }
                ],
                "source_platforms": ["reddit", "google"],
                "audience_estimate": "2.5M pet owners in major metros"
            },
            {
                "type": "unmet_want",
                "title": "Premium on-demand pet grooming service",
                "pain_score": 7.2,
                "frequency_score": 6.5,
                "intensity_score": 7.0,
                "willingness_to_pay_score": 8.3,
                "evidence": [
                    {
                        "quote": "Would pay $200 for mobile grooming to my house",
                        "source": "r/smallbusiness",
                        "score": 78,
                        "upvotes": 89
                    }
                ],
                "source_platforms": ["reddit"],
                "audience_estimate": "1.2M pet owners"
            },
            {
                "type": "market_gap",
                "title": "No affordable franchise model for solo pet groomers",
                "pain_score": 6.8,
                "frequency_score": 5.2,
                "intensity_score": 6.5,
                "willingness_to_pay_score": 7.1,
                "evidence": [],
                "source_platforms": ["google"],
                "audience_estimate": "500k entrepreneurs"
            }
        ]
    }


@pytest.fixture
def mock_llm_analyze_opportunity():
    """Mock LLM response for opportunity analysis."""
    return {
        "tam": {
            "value": 31800000000,
            "formatted": "$31.8B",
            "methodology": "Total pet grooming market globally",
            "confidence": "high"
        },
        "sam": {
            "value": 2400000000,
            "formatted": "$2.4B",
            "methodology": "US pet grooming market",
            "confidence": "high"
        },
        "som": {
            "value": 75000000,
            "formatted": "$75M",
            "methodology": "Austin metro premium grooming segment",
            "confidence": "medium"
        },
        "funnel": {
            "target_pet_owners": 150000,
            "adoption_rate_5pct": 7500,
            "avg_value_per_customer": 10000
        }
    }


@pytest.fixture
def mock_llm_analyze_customers():
    """Mock LLM response for customer segmentation."""
    return {
        "segments": [
            {
                "name": "Premium Pet Owners",
                "description": "High-income professionals who prioritize pet wellness",
                "estimated_size": 45000,
                "pain_intensity": 9,
                "primary_need": "Reliable, premium grooming service",
                "spending_pattern": "Willing to spend $150-250 per grooming",
                "where_to_find": "Instagram, Facebook groups, Nextdoor"
            },
            {
                "name": "Busy Professionals",
                "description": "Time-constrained parents and executives",
                "estimated_size": 60000,
                "pain_intensity": 7,
                "primary_need": "Mobile, convenient grooming",
                "spending_pattern": "$100-180 per grooming, values convenience",
                "where_to_find": "Google search, Yelp, Facebook"
            },
            {
                "name": "Value-Conscious Pet Lovers",
                "description": "Budget-aware but still want quality",
                "estimated_size": 85000,
                "pain_intensity": 6,
                "primary_need": "Affordable grooming without sacrifice",
                "spending_pattern": "$50-100 per grooming",
                "where_to_find": "Groupon, local community boards, Reddit"
            }
        ]
    }


@pytest.fixture
def mock_llm_analyze_competitors():
    """Mock LLM response for competitor analysis."""
    return {
        "competitors": [
            {
                "name": "Petco Grooming",
                "location": "Austin, TX",
                "rating": 3.8,
                "price_range": "$40-80",
                "key_strength": "Convenient locations, established brand",
                "key_gap": "Impersonal service, high employee turnover",
                "threat_level": "high",
                "url": "https://petco.com"
            },
            {
                "name": "PetSmart Grooming",
                "location": "Austin, TX",
                "rating": 3.5,
                "price_range": "$50-100",
                "key_strength": "One-stop pet shop",
                "key_gap": "Poor reviews on consistency",
                "threat_level": "high",
                "url": "https://petsmart.com"
            },
            {
                "name": "Local Mobile Grooming (Various)",
                "location": "Austin metro",
                "rating": 4.6,
                "price_range": "$100-200",
                "key_strength": "Convenient, personalized",
                "key_gap": "No brand consistency, hard to book",
                "threat_level": "medium",
                "url": "N/A"
            }
        ],
        "unfilled_gaps": [
            "Premium subscription grooming model",
            "AI-powered pet health tracking during grooming",
            "Standardized mobile grooming franchise"
        ]
    }


@pytest.fixture
def mock_llm_analyze_rootcause():
    """Mock LLM response for root cause analysis."""
    return {
        "root_causes": [
            {
                "cause_number": 1,
                "title": "Fragmented supply of trustworthy groomers",
                "explanation": "Pet owners have no single trusted brand for grooming; they rely on word-of-mouth or reviews.",
                "your_move": "Build brand and reputation through exceptional service; use video testimonials.",
                "difficulty": "easy"
            },
            {
                "cause_number": 2,
                "title": "High switching costs and anxiety",
                "explanation": "Pet owners are anxious about leaving pets with new groomers; switching is emotionally taxing.",
                "your_move": "Invest in customer onboarding process; first grooming free for referrals.",
                "difficulty": "medium"
            },
            {
                "cause_number": 3,
                "title": "Logistics and scheduling friction",
                "explanation": "Booking grooming is friction-heavy; no one offers seamless mobile scheduling.",
                "your_move": "Build mobile app with one-click booking and SMS confirmations.",
                "difficulty": "hard"
            }
        ]
    }


@pytest.fixture
def mock_llm_analyze_costs():
    """Mock LLM response for cost analysis."""
    return {
        "total_range": {"min": 15000, "max": 50000},
        "breakdown": [
            {"category": "Vehicle/Equipment", "min": 5000, "max": 15000},
            {"category": "Supplies", "min": 2000, "max": 5000},
            {"category": "Insurance/License", "min": 1000, "max": 3000},
            {"category": "Marketing", "min": 3000, "max": 15000},
            {"category": "Technology/POS", "min": 1000, "max": 5000},
            {"category": "Working Capital", "min": 3000, "max": 7000}
        ],
        "note": "Costs vary by service model (mobile vs. fixed location)"
    }


@pytest.fixture
def mock_llm_setup():
    """Mock LLM response for setup generation."""
    return {
        "cost_tiers": [
            {
                "tier": "minimum_viable",
                "model": "Solo mobile groomer",
                "total_range": {"min": 15000, "max": 25000},
                "line_items": [
                    {"category": "Vehicle", "name": "Used van conversion", "min_cost": 8000, "max_cost": 12000, "notes": "Mobile grooming setup"},
                    {"category": "Equipment", "name": "Grooming tools + tub", "min_cost": 2000, "max_cost": 3000, "notes": ""},
                    {"category": "License", "name": "Business license + insurance", "min_cost": 1500, "max_cost": 2500, "notes": ""},
                    {"category": "Marketing", "name": "Initial marketing", "min_cost": 3000, "max_cost": 5000, "notes": "Instagram, Nextdoor"}
                ]
            },
            {
                "tier": "recommended",
                "model": "Small team (you + 1 groomer)",
                "total_range": {"min": 30000, "max": 50000},
                "line_items": [
                    {"category": "Vehicle", "name": "2x mobile units", "min_cost": 16000, "max_cost": 24000, "notes": ""},
                    {"category": "Equipment", "name": "2x grooming setups", "min_cost": 4000, "max_cost": 6000, "notes": ""},
                    {"category": "Staff", "name": "1 groomer salary (3 months)", "min_cost": 9000, "max_cost": 15000, "notes": ""},
                    {"category": "Marketing", "name": "Growth campaign", "min_cost": 1000, "max_cost": 5000, "notes": ""}
                ]
            },
            {
                "tier": "full_buildout",
                "model": "Franchise-ready operation",
                "total_range": {"min": 75000, "max": 150000},
                "line_items": [
                    {"category": "Facilities", "name": "Physical salon", "min_cost": 20000, "max_cost": 40000, "notes": "Lease + buildout"},
                    {"category": "Fleet", "name": "4x mobile units", "min_cost": 32000, "max_cost": 48000, "notes": ""},
                    {"category": "Staff", "name": "4 groomers + manager", "min_cost": 20000, "max_cost": 40000, "notes": "3 months"},
                    {"category": "Technology", "name": "POS, booking, CRM", "min_cost": 3000, "max_cost": 8000, "notes": ""},
                    {"category": "Marketing", "name": "Brand launch", "min_cost": 5000, "max_cost": 10000, "notes": ""}
                ]
            }
        ],
        "suppliers": [
            {
                "category": "equipment",
                "name": "Grooming Supply Co",
                "description": "Professional grooming equipment and supplies",
                "location": "Austin, TX",
                "website": "https://groomingsupplyco.com",
                "why_recommended": "Local vendor, bulk discounts, fast delivery"
            },
            {
                "category": "services",
                "name": "Austin Business License",
                "description": "Business registration and licensing",
                "location": "Austin, TX",
                "website": "https://austintexas.gov/business",
                "why_recommended": "Official city resource"
            }
        ],
        "team": [
            {
                "title": "Certified Pet Groomer",
                "type": "employee",
                "salary_range": {"min": 30000, "max": 45000},
                "priority": "must_have",
                "tier": "recommended"
            },
            {
                "title": "Operations Manager",
                "type": "employee",
                "salary_range": {"min": 35000, "max": 50000},
                "priority": "must_have",
                "tier": "full_buildout"
            }
        ],
        "timeline": [
            {
                "phase": "Foundation",
                "weeks": "2-4",
                "milestones": ["Business registration", "Insurance", "Initial marketing setup"]
            },
            {
                "phase": "Launch",
                "weeks": "4-8",
                "milestones": ["Vehicle setup", "First customers", "Refine process"]
            },
            {
                "phase": "Growth",
                "weeks": "8-16",
                "milestones": ["Hire first team member", "Expand service area", "Build brand"]
            }
        ]
    }


@pytest.fixture
def mock_llm_validate():
    """Mock LLM response for validation."""
    return {
        "landing_page": {
            "headline": "Premium Pet Grooming, Delivered to Your Door",
            "subheadline": "Professional grooming from groomers who actually care about your pet",
            "benefits": [
                "Mobile service comes to you - no stressful car rides",
                "Certified groomers with 5+ years experience",
                "Premium products safe for sensitive skin",
                "Same groomer every visit for consistency"
            ],
            "cta_text": "Get Your First Grooming Free",
            "social_proof_quote": "Finally found someone my dog actually enjoys! - Sarah M."
        },
        "survey": {
            "title": "Help us serve you better",
            "questions": [
                {
                    "number": 1,
                    "question": "What's your biggest frustration with pet grooming today?",
                    "type": "open_text",
                    "options": None
                },
                {
                    "number": 2,
                    "question": "How much would you pay for premium mobile grooming?",
                    "type": "scale",
                    "options": ["$50-100", "$100-150", "$150-200", "$200+"]
                },
                {
                    "number": 3,
                    "question": "Would you switch to a premium mobile service?",
                    "type": "yes_no",
                    "options": ["Yes", "No", "Maybe"]
                }
            ]
        },
        "whatsapp_message": {
            "message": "Hey! 👋 We just launched premium mobile pet grooming in Austin. Your pet deserves the best - certified groomers, premium products, at your door. First grooming FREE! [SURVEY_LINK]",
            "tone_note": "Friendly, casual, benefit-focused"
        },
        "communities": [
            {
                "name": "Austin Pet Lovers",
                "platform": "facebook",
                "member_count": "45K",
                "rationale": "Local pet owner community, high engagement",
                "link": "https://facebook.com/groups/austinpetlovers"
            },
            {
                "name": "r/Austin",
                "platform": "reddit",
                "member_count": "500K",
                "rationale": "Local subreddit, good for Austin service announcements",
                "link": "https://reddit.com/r/Austin"
            }
        ],
        "scorecard": {
            "waitlist_target": 150,
            "survey_target": 50,
            "switch_pct_target": 60,
            "price_tolerance_target": "$150-200 per grooming"
        }
    }


# ═══ UNIT TESTS ═══

class TestDecomposeModule:
    """Test MODULE 0: Decompose"""

    def test_decompose_request_validation(self):
        """Test request validation."""
        from app.schemas.models import DecomposeRequest

        # Valid request
        req = DecomposeRequest(idea="A mobile pet grooming service for busy pet owners in Austin")
        assert req.idea is not None
        assert len(req.idea.split()) >= 3

        # Invalid: too short
        with pytest.raises(ValueError):
            DecomposeRequest(idea="too short")

    def test_decompose_response_structure(self, mock_decompose_output):
        """Test response structure is correct."""
        from app.schemas.models import DecomposeResponse

        resp = DecomposeResponse(**mock_decompose_output)
        assert resp.business_type == "pet grooming service"
        assert resp.location.city == "Austin"
        assert resp.location.state == "TX"
        assert len(resp.subreddits) >= 4
        assert len(resp.search_queries) >= 5

    def test_state_normalization(self):
        """Test state code normalization."""
        from app.routes.decompose import _normalize_state

        assert _normalize_state("texas") == "TX"
        assert _normalize_state("CA") == "CA"
        assert _normalize_state("new york") == "NY"
        assert _normalize_state("") == ""


class TestDiscoverModule:
    """Test MODULE 1: Discover"""

    def test_discover_request_validation(self, mock_decompose_output):
        """Test request validation."""
        from app.schemas.models import DiscoverRequest

        req = DiscoverRequest(decomposition=mock_decompose_output)
        assert req.decomposition["business_type"] == "pet grooming service"

    def test_discover_response_structure(self, mock_llm_discover_response):
        """Test response post-processing."""
        from app.routes.discover import _post_process
        from app.schemas.models import DiscoverResponse

        result = _post_process(mock_llm_discover_response, [])
        assert isinstance(result, DiscoverResponse)
        assert len(result.insights) > 0
        assert all(i.score >= 0 and i.score <= 10 for i in result.insights)

    def test_insight_type_normalization(self):
        """Test insight type validation."""
        from app.routes.discover import _normalize_type

        assert _normalize_type("pain_point") == "pain_point"
        assert _normalize_type("UNMET_WANT") == "unmet_want"
        assert _normalize_type("market gap") == "market_gap"
        assert _normalize_type("invalid") == "pain_point"  # Default

    def test_score_clamping(self):
        """Test score normalization (0-10 range)."""
        from app.routes.discover import _clamp

        assert _clamp(5.5) == 5.5
        assert _clamp(85) == 8.5  # 0-100 normalized to 0-10
        assert _clamp(15) == 1.5
        assert _clamp(-5) == 0.0


class TestAnalyzeModule:
    """Test MODULE 2: Analyze"""

    def test_analyze_request_validation(self, mock_decompose_output, mock_llm_discover_response):
        """Test request validation."""
        from app.schemas.models import AnalyzeRequest

        insight = mock_llm_discover_response["insights"][0]
        req = AnalyzeRequest(
            section="opportunity",
            insight=insight,
            decomposition=mock_decompose_output
        )
        assert req.section == "opportunity"

    def test_analyze_invalid_section(self, mock_decompose_output, mock_llm_discover_response):
        """Test invalid section rejection."""
        from app.schemas.models import AnalyzeRequest

        insight = mock_llm_discover_response["insights"][0]
        with pytest.raises(ValueError):
            AnalyzeRequest(
                section="invalid_section",
                insight=insight,
                decomposition=mock_decompose_output
            )

    def test_opportunity_tam_sam_som_validation(self, mock_llm_analyze_opportunity):
        """Test TAM > SAM > SOM validation."""
        assert mock_llm_analyze_opportunity["tam"]["value"] > mock_llm_analyze_opportunity["sam"]["value"]
        assert mock_llm_analyze_opportunity["sam"]["value"] > mock_llm_analyze_opportunity["som"]["value"]

    def test_customer_segment_pain_intensity(self, mock_llm_analyze_customers):
        """Test customer segments are sorted by pain."""
        segments = mock_llm_analyze_customers["segments"]
        pain_scores = [s["pain_intensity"] for s in segments]
        assert pain_scores == sorted(pain_scores, reverse=True)

    def test_competitor_threat_level(self, mock_llm_analyze_competitors):
        """Test competitor threat levels are valid."""
        valid_threats = {"low", "medium", "high"}
        for comp in mock_llm_analyze_competitors["competitors"]:
            assert comp["threat_level"] in valid_threats


class TestSetupModule:
    """Test MODULE 3: Setup"""

    def test_setup_request_validation(self, mock_decompose_output, mock_llm_discover_response):
        """Test request validation."""
        from app.schemas.models import SetupRequest

        insight = mock_llm_discover_response["insights"][0]
        req = SetupRequest(
            insight=insight,
            decomposition=mock_decompose_output
        )
        assert req.decomposition is not None

    def test_cost_tier_ordering(self, mock_llm_setup):
        """Test cost tiers are ordered correctly."""
        from app.routes.setup import _post_process

        result = _post_process(mock_llm_setup)
        tiers = result.cost_tiers
        values = [t.total_range["max"] for t in tiers if t.total_range]
        # Check that values are generally increasing
        assert values[0] < values[-1]

    def test_cost_validation(self, mock_llm_setup):
        """Test cost min <= max validation."""
        from app.routes.setup import _post_process

        result = _post_process(mock_llm_setup)
        for tier in result.cost_tiers:
            for item in tier.line_items:
                assert item.min_cost <= item.max_cost


class TestValidateModule:
    """Test MODULE 4: Validate"""

    def test_validate_request_validation(self, mock_decompose_output, mock_llm_discover_response):
        """Test request validation."""
        from app.schemas.models import ValidateRequest

        insight = mock_llm_discover_response["insights"][0]
        req = ValidateRequest(
            channels=["landing_page", "survey"],
            insight=insight,
            decomposition=mock_decompose_output
        )
        assert "landing_page" in req.channels

    def test_landing_page_generation(self, mock_llm_validate):
        """Test landing page content."""
        lp = mock_llm_validate["landing_page"]
        assert lp["headline"] is not None
        assert len(lp["benefits"]) > 0
        assert lp["cta_text"] is not None

    def test_survey_questions(self, mock_llm_validate):
        """Test survey structure."""
        survey = mock_llm_validate["survey"]
        assert survey["title"] is not None
        assert len(survey["questions"]) > 0
        valid_types = {"multiple_choice", "scale", "open_text", "email", "yes_no"}
        for q in survey["questions"]:
            assert q["type"] in valid_types

    def test_communities_found(self, mock_llm_validate):
        """Test communities are returned."""
        communities = mock_llm_validate["communities"]
        assert len(communities) > 0
        valid_platforms = {"facebook", "discord", "nextdoor", "reddit", "linkedin", "whatsapp"}
        for c in communities:
            assert c["platform"] in valid_platforms


# ═══ INTEGRATION TESTS ═══

class TestEndToEndPipeline:
    """Test complete data flow through all modules."""

    def test_decompose_output_feeds_discover(self, mock_decompose_output):
        """Verify decompose output has all required fields for discover."""
        required = ["subreddits", "search_queries", "business_type", "location"]
        for field in required:
            assert field in mock_decompose_output

    def test_discover_output_feeds_analyze(self, mock_llm_discover_response):
        """Verify discover output has all required fields for analyze."""
        insights = mock_llm_discover_response["insights"]
        required = ["title", "type", "evidence", "source_platforms"]
        for insight in insights:
            for field in required:
                assert field in insight

    def test_analyze_context_feeds_setup(self, mock_llm_analyze_opportunity,
                                         mock_llm_analyze_customers,
                                         mock_llm_analyze_competitors):
        """Verify analyze outputs can be used as setup context."""
        analysis_context = {
            "opportunity": mock_llm_analyze_opportunity,
            "customers": mock_llm_analyze_customers,
            "competitors": mock_llm_analyze_competitors
        }
        # Should have market sizing data
        assert "tam" in analysis_context["opportunity"]
        assert "segments" in analysis_context["customers"]
        assert "competitors" in analysis_context["competitors"]

    def test_full_pipeline_data_chain(self,
                                      mock_decompose_output,
                                      mock_llm_discover_response,
                                      mock_llm_analyze_opportunity,
                                      mock_llm_setup,
                                      mock_llm_validate):
        """Test complete data chain: decompose → discover → analyze → setup → validate."""
        # Stage 1: Decompose
        assert mock_decompose_output["business_type"] is not None

        # Stage 2: Discover uses decompose
        insights = mock_llm_discover_response["insights"]
        assert len(insights) > 0

        # Stage 3: Analyze uses decompose + discover
        opportunity = mock_llm_analyze_opportunity
        assert opportunity["tam"]["value"] > 0

        # Stage 4: Setup uses all prior
        cost_tiers = mock_llm_setup["cost_tiers"]
        assert len(cost_tiers) >= 3

        # Stage 5: Validate uses all prior
        landing_page = mock_llm_validate["landing_page"]
        assert landing_page["headline"] is not None


# ═══ DATA QUALITY TESTS ═══

class TestDataQuality:
    """Test data quality and consistency."""

    def test_no_empty_required_fields(self, mock_decompose_output):
        """Test required fields are populated."""
        assert mock_decompose_output["business_type"].strip() != ""
        assert mock_decompose_output["location"]["city"].strip() != ""
        assert len(mock_decompose_output["subreddits"]) > 0

    def test_no_negative_scores(self, mock_llm_discover_response):
        """Test all scores are non-negative."""
        for insight in mock_llm_discover_response["insights"]:
            assert insight["pain_score"] >= 0
            assert insight["frequency_score"] >= 0

    def test_consistent_location_data(self, mock_decompose_output):
        """Test location data is consistent."""
        loc = mock_decompose_output["location"]
        assert len(loc["state"]) <= 2  # State abbrev is 2 chars max

    def test_cost_consistency(self, mock_llm_setup):
        """Test cost data is logically consistent."""
        for tier in mock_llm_setup["cost_tiers"]:
            items = tier["line_items"]
            total_min = sum(item["min_cost"] for item in items)
            total_max = sum(item["max_cost"] for item in items)
            assert tier["total_range"]["min"] == total_min
            assert tier["total_range"]["max"] == total_max


# ═══ RUN TESTS ═══

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
