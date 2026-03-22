"""
Demo Service: Fast, realistic demo data for smooth presentations
Used when API keys unavailable or for demo mode
"""

DEMO_IDEAS = {
    "juice bar": {
        "decompose": {
            "business_type": "Local juice bar subscription",
            "location": {"city": "San Francisco", "state": "CA"},
            "target_customers": ["Health-conscious professionals", "Fitness enthusiasts"],
            "price_tier": "premium",
            "search_queries": ["juice bar subscription san francisco"],
        },
        "discover": {
            "sources": [
                {"name": "r/fitness", "type": "reddit", "post_count": 45},
                {"name": "r/nutrition", "type": "reddit", "post_count": 32},
                {"name": "Yelp - Juice Bars", "type": "yelp", "post_count": 128},
            ],
            "insights": [
                {
                    "id": "ins_001",
                    "type": "pain_point",
                    "title": "Long wait times at juice bars during rush hours",
                    "score": 8.5,
                    "frequency_score": 8,
                    "intensity_score": 7,
                    "willingness_to_pay_score": 8,
                    "mention_count": 89,
                    "evidence": [
                        {"quote": "Always have to wait 10+ min for fresh juice", "source": "reddit", "source_url": "https://reddit.com/r/fitness/comments/abc123", "score": 9},
                        {"quote": "Would switch to subscription if same-day delivery", "source": "yelp", "source_url": "https://yelp.com/biz/juice-bar-sf/reviews/xyz789", "score": 8},
                    ],
                    "source_platforms": ["reddit", "yelp"],
                    "audience_estimate": "2.3M fitness enthusiasts in Bay Area",
                },
                {
                    "id": "ins_002",
                    "type": "market_gap",
                    "title": "Lack of organic, cold-pressed juice options",
                    "score": 7.2,
                    "frequency_score": 7,
                    "intensity_score": 7,
                    "willingness_to_pay_score": 8,
                    "mention_count": 64,
                    "evidence": [
                        {"quote": "Most juice bars use pasteurized juice", "source": "reddit", "source_url": "https://reddit.com/r/nutrition/comments/def456", "score": 8},
                        {"quote": "Willing to pay premium for cold-pressed", "source": "reddit", "source_url": "https://reddit.com/r/health/comments/ghi789", "score": 8},
                    ],
                    "source_platforms": ["reddit"],
                    "audience_estimate": "1.1M premium consumers",
                },
            ],
        },
        "analyze": {
            "section": "opportunity",
            "tam": "$2.8B",
            "sam": "$340M",
            "som": "$12M",
            "key_insights": [
                "Market growing 15% YoY, health-conscious segment leading",
                "Subscription model shows 60% retention for premium beverages",
                "Cold-chain logistics is key differentiator",
            ],
        },
        "setup": {
            "phases": [
                {"phase": "MVP Launch", "weeks": 8, "focus": "Manual fulfillment, San Francisco only"},
                {"phase": "Expansion", "weeks": 12, "focus": "Automate delivery, expand to 3 cities"},
                {"phase": "Scale", "weeks": 16, "focus": "Regional partnerships, 10 cities"},
            ],
            "cost_tiers": [
                {"tier": "MVP", "total_range": {"min": 15000, "max": 25000}},
                {"tier": "Launch", "total_range": {"min": 50000, "max": 80000}},
                {"tier": "Scale", "total_range": {"min": 200000, "max": 400000}},
            ],
        },
        "validate": {
            "landing_page": {
                "headline": "Fresh cold-pressed juice. Delivered daily.",
                "subheadline": "Organic, no sugar added, subscription from $12/day",
                "benefits": [
                    "Cold-pressed within 24 hours",
                    "100% organic ingredients",
                    "Free delivery in SF",
                    "Flexible pause/resume",
                ],
            },
            "communities": [
                {"name": "SF Fitness Enthusiasts", "platform": "Facebook", "size": "8.2K members"},
                {"name": "Health-Conscious Bay Area", "platform": "Nextdoor", "size": "45K active"},
                {"name": "r/nutrition", "platform": "Reddit", "size": "2.1M subscribers"},
            ],
            "scorecard": {
                "waitlist_target": 500,
                "switch_pct_target": 40,
                "price_tolerance_min": 10,
            },
        },
    }
}


def get_demo_data(idea: str, section: str = None) -> dict:
    """Get demo data for an idea"""
    idea_key = idea.lower().split()[0]  # Get first word

    if idea_key not in DEMO_IDEAS:
        return None

    data = DEMO_IDEAS[idea_key]

    if section:
        return data.get(section)
    return data


def has_demo_data(idea: str) -> bool:
    """Check if demo data exists for idea"""
    idea_key = idea.lower().split()[0]
    return idea_key in DEMO_IDEAS
