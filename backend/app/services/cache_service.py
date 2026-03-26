"""
Database caching service for decompose and discover results.
Enables persistence and multi-user benefit of cached insights.
"""

import logging
from collections import OrderedDict
from datetime import datetime, timedelta, timezone
from typing import Optional
from supabase import create_client

from app.core.config import settings
from app.schemas.models import DecomposeResponse, DiscoverResponse

logger = logging.getLogger(__name__)

_SEARCH_CACHE_MAX = 128

class _BoundedCache:
    """LRU dict with a hard cap to prevent unbounded memory growth."""

    def __init__(self, maxsize: int = _SEARCH_CACHE_MAX):
        self._store: OrderedDict[str, tuple[float, list[dict]]] = OrderedDict()
        self._maxsize = maxsize

    def get(self, key: str):
        item = self._store.get(key)
        if item is not None:
            self._store.move_to_end(key)
        return item

    def set(self, key: str, value: tuple[float, list[dict]]):
        if key in self._store:
            self._store.move_to_end(key)
        self._store[key] = value
        while len(self._store) > self._maxsize:
            self._store.popitem(last=False)

    def pop(self, key: str):
        self._store.pop(key, None)

_search_cache_store = _BoundedCache()

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
        if datetime.now(timezone.utc) > expires_at:
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
                "created_at": datetime.now(timezone.utc).isoformat(),
                "expires_at": (datetime.now(timezone.utc) + timedelta(hours=ttl_hours)).isoformat(),
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
            .select("sources, insights, summary, expires_at")
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
        if datetime.now(timezone.utc) > expires_at:
            await delete_discover_cache(business_type, city, state)
            return None

        logger.debug(f"Cache hit: discover for {business_type} in {city}, {state}")
        return DiscoverResponse(
            sources=result.data["sources"],
            insights=result.data["insights"],
            summary=result.data.get("summary", {}),
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
                "summary": response.summary.model_dump(),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "expires_at": (datetime.now(timezone.utc) + timedelta(hours=ttl_hours)).isoformat(),
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


# ═══ SEARCH RESULTS CACHE ═══

async def get_cached_search(
    query_hash: str,
) -> Optional[list[dict]]:
    """
    Get cached search results by query hash.
    Returns None if cache miss, expired, or table doesn't exist.
    """
    mem_item = _search_cache_store.get(query_hash)
    if mem_item:
        expires_at_ts, cached_results = mem_item
        if datetime.now(timezone.utc).timestamp() <= expires_at_ts:
            return cached_results
        _search_cache_store.pop(query_hash)

    if not supabase:
        return None

    try:
        result = (
            supabase.table("search_results_cache")
            .select("results, expires_at")
            .eq("query_hash", query_hash)
            .single()
            .execute()
        )

        if not result.data:
            return None

        # Check expiration
        expires_at = datetime.fromisoformat(result.data["expires_at"])
        if datetime.now(timezone.utc) > expires_at:
            await delete_search_cache(query_hash)
            return None

        results = result.data.get("results", [])
        _search_cache_store.set(query_hash, (expires_at.timestamp(), results))
        return results

    except Exception as e:
        # Graceful degradation if table doesn't exist - just return None (cache miss)
        if "search_results_cache" in str(e).lower() and "not found" in str(e).lower():
            logger.debug(f"Search cache table not created yet")
        return None


async def cache_search_results(
    query_hash: str,
    results: list[dict],
    ttl_days: int = 7,
):
    """Store search results in cache (gracefully handles missing table)."""
    expires_at = datetime.now(timezone.utc) + timedelta(days=ttl_days)
    _search_cache_store.set(query_hash, (expires_at.timestamp(), results))

    if not supabase:
        return

    try:
        supabase.table("search_results_cache").upsert(
            {
                "query_hash": query_hash,
                "results": results,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "expires_at": expires_at.isoformat(),
            }
        ).execute()
        logger.debug(f"Cached {len(results)} search results")
    except Exception as e:
        # Graceful degradation if table doesn't exist
        logger.debug(f"Search cache unavailable: {str(e)[:60]}. Continuing without search caching.")


async def delete_search_cache(query_hash: str):
    """Delete expired search cache entry."""
    _search_cache_store.pop(query_hash)

    if not supabase:
        return

    try:
        supabase.table("search_results_cache").delete().eq("query_hash", query_hash).execute()
    except Exception as e:
        logger.debug(f"Search cache delete failed: {e}")


def _hash_search_query(query: str, location: str | None = None) -> str:
    """Hash search query + location for cache key."""
    import hashlib

    search_key = f"{query.lower()}:{(location or '').lower()}"
    return hashlib.sha256(search_key.encode()).hexdigest()[:16]
