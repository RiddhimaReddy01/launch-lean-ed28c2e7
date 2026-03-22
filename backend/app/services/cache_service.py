"""
Database caching service for decompose and discover results.
Enables persistence and multi-user benefit of cached insights.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional
from supabase import create_client

from app.core.config import settings
from app.schemas.models import DecomposeResponse, DiscoverResponse

logger = logging.getLogger(__name__)

# Initialize Supabase client
try:
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
except Exception as e:
    logger.warning(f"Supabase client init failed: {e}. Caching disabled.")
    supabase = None


async def get_cached_decompose(idea: str) -> Optional[DecomposeResponse]:
    """
    Get cached decompose result for exact idea match.
    Returns None if cache miss or expired.
    """
    if not supabase:
        return None

    try:
        result = (
            supabase.table("decompose_cache")
            .select("result, expires_at")
            .eq("idea_hash", _hash_idea(idea))
            .single()
            .execute()
        )

        if not result.data:
            return None

        # Check expiration
        expires_at = datetime.fromisoformat(result.data["expires_at"])
        if datetime.utcnow() > expires_at:
            await delete_decompose_cache(idea)
            return None

        # Reconstruct DecomposeResponse from JSON
        cached_data = result.data["result"]
        return DecomposeResponse(
            business_type=cached_data.get("business_type", ""),
            location=cached_data.get("location", {}),
            target_customers=cached_data.get("target_customers", []),
            price_tier=cached_data.get("price_tier", ""),
            source_domains=cached_data.get("source_domains", []),
            subreddits=cached_data.get("subreddits", []),
            review_platforms=cached_data.get("review_platforms", []),
            search_queries=cached_data.get("search_queries", []),
        )
    except Exception as e:
        logger.debug(f"Decompose cache lookup failed: {e}")
        return None


async def cache_decompose(idea: str, response: DecomposeResponse, ttl_hours: int = 24):
    """Store decompose result in cache."""
    if not supabase:
        return

    try:
        supabase.table("decompose_cache").upsert(
            {
                "idea_hash": _hash_idea(idea),
                "idea": idea,
                "result": response.model_dump(),
                "created_at": datetime.utcnow().isoformat(),
                "expires_at": (datetime.utcnow() + timedelta(hours=ttl_hours)).isoformat(),
            }
        ).execute()
        logger.debug(f"Cached decompose result for idea")
    except Exception as e:
        logger.debug(f"Decompose cache store failed: {e}")


async def delete_decompose_cache(idea: str):
    """Delete expired decompose cache entry."""
    if not supabase:
        return

    try:
        supabase.table("decompose_cache").delete().eq(
            "idea_hash", _hash_idea(idea)
        ).execute()
    except Exception as e:
        logger.debug(f"Decompose cache delete failed: {e}")


async def get_cached_discover(
    business_type: str, city: str = "", state: str = ""
) -> Optional[DiscoverResponse]:
    """
    Get cached discover result for similar queries.
    Matches by business_type + city + state (case-insensitive).
    """
    if not supabase:
        return None

    try:
        result = (
            supabase.table("discover_insights_cache")
            .select("sources, insights, expires_at")
            .eq("business_type", business_type.lower())
            .eq("city", (city.lower() or None))
            .eq("state", (state.lower() or None))
            .single()
            .execute()
        )

        if not result.data:
            return None

        # Check expiration
        expires_at = datetime.fromisoformat(result.data["expires_at"])
        if datetime.utcnow() > expires_at:
            await delete_discover_cache(business_type, city, state)
            return None

        logger.debug(f"Cache hit: discover for {business_type} in {city}, {state}")
        return DiscoverResponse(
            sources=result.data["sources"], insights=result.data["insights"]
        )
    except Exception as e:
        logger.debug(f"Discover cache lookup failed: {e}")
        return None


async def cache_discover(
    business_type: str,
    city: str,
    state: str,
    response: DiscoverResponse,
    ttl_hours: int = 24,
):
    """Store discover result in cache."""
    if not supabase:
        return

    try:
        supabase.table("discover_insights_cache").upsert(
            {
                "business_type": business_type.lower(),
                "city": (city.lower() or None),
                "state": (state.lower() or None),
                "sources": [s.model_dump() for s in response.sources],
                "insights": [i.model_dump() for i in response.insights],
                "created_at": datetime.utcnow().isoformat(),
                "expires_at": (datetime.utcnow() + timedelta(hours=ttl_hours)).isoformat(),
            }
        ).execute()
        logger.debug(f"Cached discover results for {business_type}")
    except Exception as e:
        logger.debug(f"Discover cache store failed: {e}")


async def delete_discover_cache(business_type: str, city: str = "", state: str = ""):
    """Delete expired discover cache entry."""
    if not supabase:
        return

    try:
        supabase.table("discover_insights_cache").delete().eq(
            "business_type", business_type.lower()
        ).eq("city", (city.lower() or None)).eq("state", (state.lower() or None)).execute()
    except Exception as e:
        logger.debug(f"Discover cache delete failed: {e}")


def _hash_idea(idea: str) -> str:
    """Hash idea string for cache key."""
    import hashlib

    return hashlib.sha256(idea.lower().encode()).hexdigest()[:16]
