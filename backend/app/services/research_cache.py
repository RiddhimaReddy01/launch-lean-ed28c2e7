"""
Research caching layer - Store all analysis results in Supabase for speed.
When user analyzes same idea again, return cached results instantly.
"""

import logging
import json
from datetime import datetime, timedelta

from app.core.supabase import get_supabase

logger = logging.getLogger(__name__)


async def get_cached_research(idea_hash: str, user_id: str) -> dict | None:
    """Get cached research results for this idea (all 5 tabs at once)."""
    try:
        supabase = get_supabase()
        response = supabase.table("research_cache").select("*").eq(
            "idea_hash", idea_hash
        ).eq("user_id", user_id).order("created_at", desc=True).limit(1).execute()

        if response.data:
            cache = response.data[0]
            # Check if cache is still fresh (< 7 days)
            created = datetime.fromisoformat(cache["created_at"])
            if datetime.now() - created < timedelta(days=7):
                logger.info(f"Cache HIT for {idea_hash}")
                return {
                    "decompose": json.loads(cache.get("decompose", "{}")),
                    "discover": json.loads(cache.get("discover", "{}")),
                    "analyze": json.loads(cache.get("analyze", "{}")),
                    "setup": json.loads(cache.get("setup", "{}")),
                    "validate": json.loads(cache.get("validate", "{}"))
                }

        return None
    except Exception as e:
        logger.debug(f"Cache lookup failed: {e}")
        return None


async def cache_research(
    idea_hash: str,
    user_id: str,
    decompose: dict,
    discover: dict,
    analyze: dict,
    setup: dict,
    validate: dict
):
    """Cache all research results in Supabase."""
    try:
        supabase = get_supabase()
        supabase.table("research_cache").insert({
            "idea_hash": idea_hash,
            "user_id": user_id,
            "decompose": json.dumps(decompose),
            "discover": json.dumps(discover),
            "analyze": json.dumps(analyze),
            "setup": json.dumps(setup),
            "validate": json.dumps(validate),
            "created_at": datetime.now().isoformat(),
        }).execute()
        logger.info(f"Cached research for {idea_hash}")
    except Exception as e:
        logger.warning(f"Cache store failed: {e}")


def hash_idea(idea: str) -> str:
    """Create stable hash for caching."""
    import hashlib
    return hashlib.md5(idea.lower().strip().encode()).hexdigest()
