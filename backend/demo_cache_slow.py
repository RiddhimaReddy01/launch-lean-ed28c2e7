"""
Demo: Slow-loading cache with 6 diverse, realistic business queries
One query at a time with delays to avoid LLM rate limiting
"""

import asyncio
import time
from app.api.decompose import _cache_store, decompose_idea
from app.schemas.models import DecomposeRequest

# 6 diverse, realistic business ideas people actually ask about
TEST_IDEAS = [
    "A home cleaning service for busy professionals and families in Austin Texas",
    "A freelance graphic design marketplace for small businesses and startups",
    "A pet sitting and dog walking service for remote workers in San Francisco",
    "An affordable tutoring platform for high school students struggling with math",
    "A social media management agency for local small businesses and restaurants",
    "A virtual assistant service for busy entrepreneurs and executives",
]

async def display_cache():
    """Show current cache state."""
    print("\n" + "="*80)
    print("[CACHE STATUS]")
    print("="*80)
    print(f"Cached entries: {len(_cache_store)}\n")

    if _cache_store:
        for idx, (key, (expires_at, response)) in enumerate(_cache_store.items(), 1):
            location = f"{response.location.city}, {response.location.state}" if response.location.city else "(no location)"
            print(f"{idx}. {key[:60]}...")
            print(f"   Business: {response.business_type}")
            print(f"   Location: {location}")
            print()

async def process_one_query(idea: str, query_num: int, total: int):
    """Process a single query with detailed output."""
    print(f"\n[{query_num}/{total}] Processing: {idea}")
    print("-" * 80)

    start = time.time()
    try:
        req = DecomposeRequest(idea=idea)
        response = await decompose_idea(req, user=None)
        elapsed = time.time() - start

        location = f"{response.location.city}, {response.location.state}" if response.location.city else "(no location)"

        print(f"[OK] SUCCESS ({elapsed:.1f}s)")
        print(f"  Business Type: {response.business_type}")
        print(f"  Location: {location}")
        print(f"  Price Tier: {response.price_tier}")
        print(f"  Target Customers: {', '.join(response.target_customers[:3])}")
        print(f"  Search Queries: {', '.join(response.search_queries[:2])}...")

        return True, elapsed

    except Exception as e:
        elapsed = time.time() - start
        print(f"[FAIL] ERROR ({elapsed:.1f}s): {str(e)[:80]}")
        return False, elapsed

async def main():
    """Process 6 queries one by one with delays."""
    print("\n" + "="*80)
    print("      CACHE DEMO: 6 DIVERSE LOCAL BUSINESS QUERIES")
    print("="*80)
    print("\nProcessing one query at a time (slow mode to avoid LLM throttling)\n")

    results = []

    for i, idea in enumerate(TEST_IDEAS, 1):
        success, elapsed = await process_one_query(idea, i, len(TEST_IDEAS))
        results.append({"idea": idea, "success": success, "time": elapsed})

        # Wait between queries (avoid rate limiting)
        if i < len(TEST_IDEAS):
            wait_time = 3
            print(f"\n[WAITING {wait_time}s before next query...]")
            await asyncio.sleep(wait_time)

    # Show final cache
    await display_cache()

    # Summary
    print("\n" + "="*80)
    print("[SUMMARY]")
    print("="*80)

    successful = sum(1 for r in results if r["success"])
    total_time = sum(r["time"] for r in results)

    print(f"\n[OK] Successful: {successful}/{len(TEST_IDEAS)}")
    print(f"[FAIL] Failed: {len(TEST_IDEAS) - successful}/{len(TEST_IDEAS)}")
    print(f"[TIME] Total time: {total_time:.1f}s")
    print(f"[AVG] Average per query: {total_time/len(TEST_IDEAS):.1f}s")
    print(f"[CACHE] Entries stored: {len(_cache_store)}")

    print(f"\n[CACHE BENEFITS]")
    print(f"  - All {len(_cache_store)} queries now stored")
    print(f"  - Future identical queries: <1ms response")
    print(f"  - Reduces LLM API calls by {len(_cache_store)}")
    print(f"  - Persists across server restarts (database backup)")

    print(f"\n[BUSINESS IDEAS CACHED]")
    for idx, idea in enumerate(TEST_IDEAS[:len(_cache_store)], 1):
        print(f"  {idx}. {idea[:65]}...")

    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
