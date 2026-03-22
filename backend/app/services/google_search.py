"""
Google Search via Serper.dev API with Tavily fallback.
Serper: 2,500 free searches/month
Tavily: Fallback when Serper is rate-limited (limited credits)
Returns clean JSON with organic results, snippets, and metadata.
Runs queries in PARALLEL for speed.
"""

import logging
import httpx
import asyncio

from app.core.config import settings
from app.services.cache_service import get_cached_search, cache_search_results, _hash_search_query

logger = logging.getLogger(__name__)

SERPER_URL = "https://google.serper.dev/search"
TAVILY_URL = "https://api.tavily.com/search"
REQUEST_TIMEOUT = 10.0


async def serper_search(
    client: httpx.AsyncClient,
    query: str,
    num: int = 10,
    location: str | None = None,
) -> list[dict]:
    """
    Run a single Google search via Serper.dev.
    Returns list of organic results with title, snippet, link.
    """
    if not settings.SERPER_API_KEY:
        logger.warning("SERPER_API_KEY not set, skipping search")
        return []

    body = {"q": query, "num": num}
    if location:
        body["location"] = location

    try:
        resp = await client.post(
            SERPER_URL,
            headers={
                "X-API-KEY": settings.SERPER_API_KEY,
                "Content-Type": "application/json",
            },
            json=body,
            timeout=REQUEST_TIMEOUT,
        )

        if resp.status_code == 429:
            logger.warning("Serper rate limit hit")
            return []
        if resp.status_code != 200:
            logger.warning(f"Serper returned {resp.status_code}: {resp.text[:200]}")
            return []

        data = resp.json()
        organic = data.get("organic", [])

        results = []
        for r in organic:
            results.append({
                "title": r.get("title", ""),
                "snippet": r.get("snippet", ""),
                "link": r.get("link", ""),
                "position": r.get("position", 0),
                "source": "google_search",
            })

        return results

    except (httpx.TimeoutException, httpx.HTTPError) as e:
        logger.warning(f"Serper search failed for '{query}': {e}")
        return []


async def tavily_search(
    client: httpx.AsyncClient,
    query: str,
    num: int = 10,
) -> list[dict]:
    """
    Fallback search via Tavily.com when Serper is rate-limited.
    Limited to 1000 free searches, use sparingly.
    """
    if not settings.TAVILY_API_KEY:
        logger.debug("TAVILY_API_KEY not set, skipping fallback search")
        return []

    try:
        resp = await client.post(
            TAVILY_URL,
            json={
                "api_key": settings.TAVILY_API_KEY,
                "query": query,
                "max_results": num,
                "include_answer": False,
            },
            timeout=REQUEST_TIMEOUT,
        )

        if resp.status_code != 200:
            logger.warning(f"Tavily returned {resp.status_code}: {resp.text[:200]}")
            return []

        data = resp.json()
        results_data = data.get("results", [])

        results = []
        for r in results_data:
            results.append({
                "title": r.get("title", ""),
                "snippet": r.get("content", ""),
                "link": r.get("url", ""),
                "position": len(results) + 1,
                "source": "tavily_search",
            })

        logger.info(f"Tavily fallback: {len(results)} results for '{query}'")
        return results

    except (httpx.TimeoutException, httpx.HTTPError) as e:
        logger.warning(f"Tavily search failed for '{query}': {e}")
        return []


async def _search_single_query(
    client: httpx.AsyncClient,
    query: str,
    location: str | None = None,
    num_per_query: int = 10,
) -> list[dict]:
    """Search a single query with cache + Serper + Tavily fallback."""
    # Check cache first
    query_hash = _hash_search_query(query, location)
    cached = await get_cached_search(query_hash)
    if cached:
        logger.debug(f"Cache hit for '{query[:40]}...'")
        return cached

    # Try Serper first
    results = await serper_search(client, query, num=num_per_query, location=location)

    # Fallback to Tavily if Serper returns empty
    if not results:
        logger.debug(f"Serper empty for '{query}', trying Tavily fallback...")
        results = await tavily_search(client, query, num=num_per_query)

    for r in results:
        r["query"] = query

    # Cache the results
    if results:
        await cache_search_results(query_hash, results, ttl_days=7)

    return results


async def run_search_queries(
    queries: list[str],
    location: str | None = None,
    num_per_query: int = 10,
) -> list[dict]:
    """
    Run multiple search queries in PARALLEL for speed.
    Tries Serper first, falls back to Tavily if Serper fails/rate-limits.
    Tags each result with the query that produced it.
    """
    async with httpx.AsyncClient() as client:
        # Run all queries in parallel instead of sequential
        search_tasks = [
            _search_single_query(client, q, location=location, num_per_query=num_per_query)
            for q in queries
        ]
        search_results = await asyncio.gather(*search_tasks)
        all_results = [r for results in search_results for r in results]

    source_count = {}
    for r in all_results:
        src = r.get("source", "unknown")
        source_count[src] = source_count.get(src, 0) + 1

    logger.info(
        f"Parallel search: {len(all_results)} results from {len(queries)} queries. "
        f"Sources: {source_count}"
    )
    return all_results


def build_discover_queries(decomposition: dict) -> list[str]:
    """Build search queries for Module 1 (Discover) based on idea decomposition."""
    btype = decomposition.get("business_type", "")
    loc = decomposition.get("location", {})
    city = loc.get("city", "")
    state = loc.get("state", "")
    metro = loc.get("metro", "")
    domains = decomposition.get("source_domains", []) or []

    default_domains = [
        "yelp.com", "google.com/maps", "trustpilot.com",
        "g2.com", "capterra.com", "producthunt.com",
        "news.ycombinator.com", "stackoverflow.com",
        "craigslist.org", "meetup.com", "eventbrite.com",
        "tripadvisor.com", "city-data.com/forum", "amazon.com",
    ]

    if not domains:
        domains = default_domains

    queries = []

    # Top priority: site searches on review platforms (most relevant)
    review_domains = [d for d in domains[:6] if any(r in d for r in ["yelp", "google", "trustpilot", "tripadvisor"])]
    for d in review_domains[:3]:
        queries.append(f"{btype} {city} {state} site:{d}")

    # Pain point queries (high signal for market research)
    queries.append(f'"{btype}" "{city}" complaints bad reviews -site:reddit.com')
    queries.append(f'"{btype}" "{city}" problems issues frustration')
    queries.append(f'"{btype}" "{city}" alternatives competitors pricing')

    # Local and pricing queries
    queries.append(f"best {btype} near {city} {state}")
    queries.append(f"{btype} {city} {state} prices cost overpriced")
    queries.append(f"{btype} {city} {state} hours location wait times")

    return queries[:8]


def build_competitor_queries(decomposition: dict) -> list[str]:
    """Build search queries for Module 2 Section C (Competitors)."""
    btype = decomposition.get("business_type", "")
    loc = decomposition.get("location", {})
    city = loc.get("city", "")
    state = loc.get("state", "")

    queries = [
        f"{btype} near {city} {state} site:yelp.com",
        f"best {btype} {city} {state}",
        f"{btype} {city} {state} reviews",
        f"new {btype} opening {city} 2025 2026",
    ]
    return queries


def build_setup_queries(decomposition: dict) -> list[str]:
    """Build search queries for Module 3 (Setup) - suppliers, costs, permits."""
    btype = decomposition.get("business_type", "")
    loc = decomposition.get("location", {})
    city = loc.get("city", "")
    state = loc.get("state", "")
    metro = loc.get("metro", "")

    queries = [
        f"{btype} equipment supplier {metro}",
        f"commercial lease {city} {state} 2026",
        f"{btype} permits licenses {city} {state}",
        f"wholesale supplier {btype} {state}",
        f"{btype} POS system point of sale",
    ]
    return queries


def build_community_queries(decomposition: dict) -> list[str]:
    """Build search queries for Module 4 (Validate) - community discovery."""
    btype = decomposition.get("business_type", "")
    loc = decomposition.get("location", {})
    city = loc.get("city", "")
    state = loc.get("state", "")
    metro = loc.get("metro", "")

    queries = [
        f"{btype} {city} Facebook group",
        f"{btype} {metro} Discord server",
        f"{city} entrepreneurs small business network",
        f"{city} {state} food community OR recommendations Nextdoor",
    ]
    return queries
