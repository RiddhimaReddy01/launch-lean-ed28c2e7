"""
Composite scoring and ranking for discover insights.
Balances multiple signals for intelligent ranking.
"""

import logging
from app.schemas.models import Insight

logger = logging.getLogger(__name__)


def calculate_composite_score(insight: dict) -> float:
    """
    Composite ranking score combining multiple signals.

    Formula:
    score = (frequency * 0.25) + (intensity * 0.25) +
            (willingness_to_pay * 0.20) + (market_size * 0.20) +
            (urgency * 0.10)

    All factors normalized to 0-10 scale.
    """
    # Get individual signals, defaulting to 0
    frequency = _clamp(insight.get("frequency_score", 0))
    intensity = _clamp(insight.get("intensity_score", 0))
    willingness = _clamp(insight.get("willingness_to_pay_score", 0))

    # Market size signal: derived from evidence count + source platforms
    evidence_count = len(insight.get("evidence", []))
    source_count = len(set(insight.get("source_platforms", [])))
    # Evidence = 5 sources, each on 2 platforms = market_size ~7-8
    market_size = min(10.0, (evidence_count * 1.2) + (source_count * 1.5))
    market_size = _clamp(market_size)

    # Urgency signal: recent mentions weighted higher
    # Simple heuristic: high mention count = trending/active discussion
    mention_count = insight.get("mention_count", 0)
    urgency = 8.0 if mention_count > 20 else (7.0 if mention_count > 10 else 5.0)
    urgency = _clamp(urgency)

    # Weighted composite
    composite = (
        (frequency * 0.25)
        + (intensity * 0.25)
        + (willingness * 0.20)
        + (market_size * 0.20)
        + (urgency * 0.10)
    )

    return round(min(10.0, max(0.0, composite)), 1)


def rank_insights(insights: list[dict]) -> list[dict]:
    """
    Rank insights by composite score.
    Higher scores = higher priority.
    """
    # Calculate composite score for each insight
    for insight in insights:
        insight["composite_score"] = calculate_composite_score(insight)

    # Sort by composite score descending
    insights.sort(key=lambda x: x.get("composite_score", 0), reverse=True)

    return insights


def _clamp(value: float, lo: float = 0.0, hi: float = 10.0) -> float:
    """Clamp value to range [lo, hi]."""
    try:
        v = float(value)
        # Handle 0-100 scale by dividing by 10
        if v > hi:
            v = v / 10.0
        return round(min(hi, max(lo, v)), 1)
    except (TypeError, ValueError):
        return lo
