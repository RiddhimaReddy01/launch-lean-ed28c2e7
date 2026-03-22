"""
Reddit data ingestion via the public .json endpoint.
No authentication required. ~60 requests/minute with User-Agent header.
"""

import asyncio
import logging
from datetime import datetime
from base64 import b64encode
from typing import Optional

import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)

REDDIT_BASE = "https://www.reddit.com"
REDDIT_OAUTH = "https://oauth.reddit.com"
# Explicit UA keeps Reddit happy; raw_json=1 avoids escaped HTML issues
USER_AGENT = "LaunchLens/1.0 (github.com/RiddhimaReddy01/launch-lean-ed28c2e7)"
HEADERS = {"User-Agent": USER_AGENT}
REQUEST_TIMEOUT = 8.0
DELAY_BETWEEN_REQUESTS = 1.2  # seconds, to stay well under rate limits
SUBREDDIT_LIMIT = 5  # keep data light to reduce 403s/rate limits
FETCH_HOT_DEFAULT = False  # only fetch hot when top is too thin
TOP_LIMIT = 50
HOT_LIMIT = 25
MIN_POSTS_BEFORE_HOT = 30
_token_cache: Optional[tuple[str, float]] = None  # (token, expires_at)
_token_lock = asyncio.Lock()


async def fetch_subreddit_posts(
    client: httpx.AsyncClient,
    subreddit: str,
    sort: str = "top",
    time_filter: str = "year",
    limit: int = 100,
    bearer: str | None = None,
) -> list[dict]:
    """Fetch posts from a single subreddit endpoint."""
    base = REDDIT_OAUTH if bearer else REDDIT_BASE
    url = f"{base}/r/{subreddit}/{sort}.json"
    params = {"limit": min(limit, 100), "t": time_filter, "raw_json": 1}

    try:
        headers = dict(HEADERS)
        if bearer:
            headers["Authorization"] = f"bearer {bearer}"
        resp = await client.get(url, params=params, headers=headers, timeout=REQUEST_TIMEOUT)
        if resp.status_code == 429:
            logger.warning(f"Rate limited on r/{subreddit}")
            return []
        if resp.status_code != 200:
            logger.warning(f"r/{subreddit} returned {resp.status_code}")
            return []

        data = resp.json()
        children = data.get("data", {}).get("children", [])
        return [child["data"] for child in children if child.get("kind") == "t3"]

    except (httpx.TimeoutException, httpx.HTTPError) as e:
        logger.warning(f"Failed to fetch r/{subreddit}: {e}")
        return []


async def fetch_all_subreddits(subreddits: list[str], fetch_hot: bool = FETCH_HOT_DEFAULT) -> list[dict]:
    """
    Fetch posts from multiple subreddits with two sorts each (top + hot).
    Returns combined raw post list.
    """
    all_posts = []
    # Deduplicate and limit
    subreddits = list(dict.fromkeys(subreddits))[:SUBREDDIT_LIMIT]
    bearer = await _maybe_token()

    async with httpx.AsyncClient(follow_redirects=True) as client:
        for sub in subreddits:
            # Fetch top posts (past year) - best for pain points
            top_posts = await fetch_subreddit_posts(
                client, sub, sort="top", time_filter="year", limit=TOP_LIMIT, bearer=bearer
            )
            all_posts.extend(top_posts)
            await asyncio.sleep(DELAY_BETWEEN_REQUESTS)

            # Fetch hot posts only if top was thin
            if fetch_hot or len(top_posts) < MIN_POSTS_BEFORE_HOT:
                hot_posts = await fetch_subreddit_posts(
                    client, sub, sort="hot", limit=HOT_LIMIT, bearer=bearer
                )
                all_posts.extend(hot_posts)
                await asyncio.sleep(DELAY_BETWEEN_REQUESTS)

    logger.info(f"Fetched {len(all_posts)} total Reddit posts from {len(subreddits)} subreddits")
    return all_posts


async def fetch_search_posts(query: str, limit: int = 50, sort: str = "relevance", time_filter: str = "month") -> list[dict]:
    """Fallback: search Reddit globally."""
    bearer = await _maybe_token()
    base = REDDIT_OAUTH if bearer else REDDIT_BASE
    url = f"{base}/search.json"
    params = {
        "q": query,
        "limit": min(limit, 100),
        "sort": sort,
        "t": time_filter,
        "raw_json": 1,
        "type": "link",
    }
    headers = dict(HEADERS)
    if bearer:
        headers["Authorization"] = f"bearer {bearer}"

    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            resp = await client.get(url, params=params, headers=headers, timeout=REQUEST_TIMEOUT)
            if resp.status_code != 200:
                logger.warning(f"Reddit search returned {resp.status_code}")
                return []
            data = resp.json()
            return [child["data"] for child in data.get("data", {}).get("children", []) if child.get("kind") == "t3"]
    except (httpx.TimeoutException, httpx.HTTPError) as e:
        logger.warning(f"Reddit search failed: {e}")
        return []


async def _maybe_token() -> Optional[str]:
    """Fetch OAuth token if creds exist; cache it with lock for thread-safety."""
    global _token_cache
    if not settings.REDDIT_CLIENT_ID or not settings.REDDIT_CLIENT_SECRET:
        return None

    async with _token_lock:
        now = asyncio.get_event_loop().time()
        if _token_cache and _token_cache[1] > now + 60:
            return _token_cache[0]
        creds = b64encode(f"{settings.REDDIT_CLIENT_ID}:{settings.REDDIT_CLIENT_SECRET}".encode()).decode()
        headers = {
            "Authorization": f"Basic {creds}",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": USER_AGENT,
        }
        data = "grant_type=client_credentials"
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post("https://www.reddit.com/api/v1/access_token", headers=headers, data=data, timeout=REQUEST_TIMEOUT)
                if resp.status_code != 200:
                    logger.warning(f"Reddit token failed {resp.status_code}: {resp.text[:200]}")
                    return None
                js = resp.json()
                token = js.get("access_token")
                expires_in = js.get("expires_in", 3600)
                _token_cache = (token, now + expires_in)
                return token
        except (httpx.TimeoutException, httpx.HTTPError) as e:
            logger.warning(f"Reddit token error: {e}")
            return None


def extract_post_fields(raw_post: dict) -> dict:
    """Extract and normalize relevant fields from a raw Reddit post."""
    created = raw_post.get("created_utc", 0)
    try:
        date_str = datetime.utcfromtimestamp(created).strftime("%Y-%m-%d")
    except (ValueError, OSError):
        date_str = "unknown"

    return {
        "title": raw_post.get("title", ""),
        "body": raw_post.get("selftext", "") or "",
        "score": raw_post.get("score", 0),
        "num_comments": raw_post.get("num_comments", 0),
        "subreddit": raw_post.get("subreddit", ""),
        "created_date": date_str,
        "permalink": raw_post.get("permalink", ""),
        "author": raw_post.get("author", "[deleted]"),
        "is_video": raw_post.get("is_video", False),
        "post_hint": raw_post.get("post_hint", ""),
        "source": "reddit",
    }
