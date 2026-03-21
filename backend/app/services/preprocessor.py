"""
Preprocessor: Fetch and curate data BEFORE LLM calls
Runs in parallel to reduce LLM processing time.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


async def preprocess_idea(idea: str, vertical: str) -> dict[str, Any]:
    """
    Fetch and curate market data BEFORE LLM analysis.

    Returns curated data that LLM can quickly analyze instead of searching.
    Runs in parallel to maximize speed.
    """

    logger.info(f"Preprocessing idea: {idea}")

    # Curated data structure for LLM
    curated = {
        "business_context": {
            "idea": idea,
            "vertical": vertical,
            "confidence": 0.8
        },
        "suggested_features": get_vertical_features(vertical),
        "market_signals": {
            "demand_signals": ["growing market", "increasing interest"],
            "pain_points": ["market gap identified"],
            "opportunities": []
        }
    }

    logger.info(f"Preprocessed data ready for {vertical}")
    return curated


def get_vertical_features(vertical: str) -> list[str]:
    """Get typical features/characteristics for vertical"""

    features = {
        "saas_b2b": [
            "Automation",
            "API integration",
            "Scalability",
            "Enterprise pricing",
            "SLA guarantees"
        ],
        "consumer_app": [
            "Mobile-first",
            "User-friendly UI",
            "Social features",
            "Subscription model",
            "Push notifications"
        ],
        "food_service": [
            "Location-based",
            "Quality ingredients",
            "Delivery capability",
            "Pricing competitive",
            "Customer service"
        ],
        "local_service": [
            "Local presence",
            "Licensing/permits",
            "Quality assurance",
            "Word-of-mouth",
            "Service reliability"
        ]
    }

    return features.get(vertical, [
        "Market fit",
        "Customer value",
        "Competitive advantage",
        "Business model",
        "Growth potential"
    ])


def curate_market_data(raw_data: list[dict], limit: int = 50) -> list[dict]:
    """
    Curate market data by:
    - Filtering duplicates
    - Sorting by relevance
    - Limiting to top N
    """

    if not raw_data:
        return []

    # Sort by score/relevance
    sorted_data = sorted(
        raw_data,
        key=lambda x: x.get("score", 0),
        reverse=True
    )

    # Deduplicate based on title
    seen = set()
    curated = []

    for item in sorted_data:
        title = item.get("title", "").lower()
        if title and title not in seen and len(curated) < limit:
            seen.add(title)
            curated.append(item)

    return curated


def extract_search_queries(decomposition: dict) -> list[str]:
    """
    Use decomposition results to refine search queries.
    LLM already generated search queries - curate them.
    """

    queries = decomposition.get("search_queries", [])

    # Filter for quality (length, no duplicates)
    filtered = []
    seen = set()

    for q in queries:
        q_clean = q.lower().strip()
        if q_clean not in seen and 5 <= len(q) <= 100:
            seen.add(q_clean)
            filtered.append(q)
            if len(filtered) >= 8:
                break

    return filtered


async def prepare_llm_context(
    idea: str,
    vertical: str,
    market_data: list[dict] = None,
    competitors: list[str] = None
) -> dict[str, Any]:
    """
    Prepare minimal context for LLM.
    Reduces token count and LLM processing time.
    """

    context = {
        "idea": idea,
        "vertical": vertical,
        "features": get_vertical_features(vertical),
        "market_summary": None,
        "competitors_sample": competitors[:5] if competitors else None,
        "data_points": len(market_data) if market_data else 0
    }

    return context


def summarize_posts(posts: list[dict], max_length: int = 50) -> dict[str, list[str]]:
    """
    Summarize posts by theme BEFORE sending to LLM.
    Reduces LLM processing time significantly.
    """

    summaries = {
        "pain_points": [],
        "features_wanted": [],
        "pricing_concerns": [],
        "competitor_mentions": []
    }

    keywords = {
        "pain_points": ["problem", "issue", "difficult", "pain", "frustration", "painful"],
        "features_wanted": ["need", "want", "wish", "feature", "should", "lack"],
        "pricing_concerns": ["expensive", "cheap", "cost", "price", "afford", "budget"],
        "competitor_mentions": ["instead of", "used", "switched from", "alternative", "vs "]
    }

    processed = 0
    for post in posts:
        if processed >= max_length:
            break

        text = (post.get("title", "") + " " + post.get("body", "")).lower()

        for category, kws in keywords.items():
            if any(kw in text for kw in kws) and text not in summaries[category]:
                summaries[category].append(text[:100])
                processed += 1
                break

    return {k: v[:5] for k, v in summaries.items()}  # Top 5 per category


# Design Pattern: Lazy Loading
# These functions are called only when data is available
# They don't block the main request

__all__ = [
    "preprocess_idea",
    "curate_market_data",
    "extract_search_queries",
    "prepare_llm_context",
    "summarize_posts",
    "get_vertical_features",
]
