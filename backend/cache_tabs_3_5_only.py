"""
Cache ONLY Tabs 3-5 (ANALYZE, SETUP, VALIDATE)
- Skip Tabs 1-2 (already cached)
- Use cached decomposition + discover insights
- One query at a time, wait 60s between
"""

import asyncio
import time
from app.schemas.models import (
    AnalyzeRequest, SetupRequest, ValidateRequest
)
from app.api.analyze import analyze_section
from app.api.setup import setup_section
from app.api.validate import generate_validation

# 22 queries
QUERIES = [
    "A sustainable meal prep delivery service for busy professionals in Austin Texas",
    "An AI-powered fitness coaching app for remote workers",
    "A marketplace for second-hand luxury goods in San Francisco",
    "A virtual interior design consultation platform for real estate agents",
    "An eco-friendly packaging supply company for e-commerce businesses",
    "A mental health coaching app specifically for healthcare workers",
    "A local organic vegetable delivery service in Portland Oregon",
    "A corporate team building event platform using virtual reality",
    "A premium pet grooming and daycare service for pet owners in Denver Colorado",
    "A subscription vegan meal planning service for health-conscious professionals in Seattle Washington",
    "A freelance bookkeeping service for small restaurants and cafes in Miami Florida",
    "An eco-friendly packaging supply company for local e-commerce businesses in Boston Massachusetts",
    "A mental health coaching app specifically for remote workers in Austin Texas",
    "A corporate team building event planning service in Chicago Illinois",
    "A personal fitness coaching service for busy executives in New York City",
    "A freelance graphic design marketplace for small businesses and startups",
    "A pet sitting and dog walking service for remote workers in San Francisco",
    "A social media management agency for local small businesses and restaurants",
    "A virtual assistant service for busy entrepreneurs and executives",
    "A home cleaning service for busy professionals and families in Austin Texas",
    "An affordable tutoring platform for high school students struggling with math",
    "A subscription pet grooming and daycare service for busy parents",
]

async def cache_tabs_3_5(decomposition: dict, insight: dict, idea: str, query_num: int, total: int):
    """Cache only Tabs 3-5 for one query using cached decomposition + insight."""
    print(f"\n{'='*100}")
    print(f"[{query_num}/{total}] {idea[:70]}...")
    print('='*100)

    try:
        # ===== TAB 3: ANALYZE =====
        print(f"\n[TAB 3/5] ANALYZE - Deep dive analysis...")
        start = time.time()
        try:
            analyze_req = AnalyzeRequest(
                section="opportunity",
                insight=insight,
                decomposition=decomposition
            )
            analyze = await analyze_section(analyze_req, user=None)
            tab3_time = time.time() - start
            print(f"  [OK] {tab3_time:.1f}s")
            print(f"      Section: {analyze.section}")
            print(f"      Data keys: {list(analyze.data.keys())[:3]}")
        except Exception as e:
            print(f"  [SKIP] {str(e)[:60]}")
            tab3_time = 0
            analyze = None

        # ===== TAB 4: SETUP =====
        print(f"\n[TAB 4/5] SETUP - Creating launch plan...")
        start = time.time()
        try:
            setup_req = SetupRequest(
                insight=insight,
                decomposition=decomposition,
                selected_tier="MID"
            )
            setup = await setup_section(setup_req, user=None)
            tab4_time = time.time() - start
            print(f"  [OK] {tab4_time:.1f}s")
            print(f"      Cost Tiers: {len(setup.cost_tiers)}")
            print(f"      Suppliers: {len(setup.suppliers)}")
            print(f"      Team Roles: {len(setup.team)}")
            print(f"      Timeline: {len(setup.timeline)} phases")
        except Exception as e:
            print(f"  [SKIP] {str(e)[:60]}")
            tab4_time = 0
            setup = None

        # ===== TAB 5: VALIDATE =====
        print(f"\n[TAB 5/5] VALIDATE - Testing demand...")
        start = time.time()
        try:
            validate_req = ValidateRequest(
                insight=insight,
                decomposition=decomposition,
                channels=["landing_page", "survey"]
            )
            validate = await generate_validation(validate_req, user=None)
            tab5_time = time.time() - start
            print(f"  [OK] {tab5_time:.1f}s")
            print(f"      Communities: {len(validate.communities)}")
            if validate.landing_page:
                print(f"      Landing Page: Configured")
            if validate.survey:
                print(f"      Survey: Configured")
        except Exception as e:
            print(f"  [SKIP] {str(e)[:60]}")
            tab5_time = 0
            validate = None

        # ===== SUMMARY =====
        total_time = tab3_time + tab4_time + tab5_time
        print(f"\n[SUMMARY]")
        print(f"  Tab 3 (Analyze):    {tab3_time:6.1f}s {'[OK]' if tab3_time > 0 else '[SKIP]'}")
        print(f"  Tab 4 (Setup):      {tab4_time:6.1f}s {'[OK]' if tab4_time > 0 else '[SKIP]'}")
        print(f"  Tab 5 (Validate):   {tab5_time:6.1f}s {'[OK]' if tab5_time > 0 else '[SKIP]'}")
        print(f"  Total:              {total_time:6.1f}s")

        return {
            "idea": idea,
            "success": True,
            "total_time": total_time,
            "tabs": {
                "analyze": tab3_time > 0,
                "setup": tab4_time > 0,
                "validate": tab5_time > 0
            }
        }

    except Exception as e:
        print(f"\n[ERROR] Pipeline failed: {str(e)[:80]}")
        return {
            "idea": idea,
            "success": False,
            "error": str(e)
        }

async def main():
    """Cache Tabs 3-5 only, one query at a time."""
    print("\n" + "="*100)
    print("  CACHE TABS 3-5 ONLY: Reusing cached Tabs 1-2")
    print("="*100)
    print(f"\nCaching Tabs 3-5 for {len(QUERIES)} queries (60s wait between)\n")

    results = []
    start_time = time.time()

    # Load Supabase client
    from supabase import create_client
    from app.core.config import settings
    supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

    for i, idea in enumerate(QUERIES, 1):
        try:
            # Helper to hash idea (same pattern as cache_service.py)
            import hashlib
            def _hash_idea(idea_text):
                return hashlib.sha256(idea_text.lower().encode()).hexdigest()[:16]

            # Load cached decomposition for this query
            # Query decompose_cache table by idea_hash (limit 1 to handle multiple matches)
            decomp_resp = supabase_client.table("decompose_cache").select("result").eq("idea_hash", _hash_idea(idea)).limit(1).execute()
            if not decomp_resp.data or len(decomp_resp.data) == 0:
                print(f"\n[{i}/{len(QUERIES)}] No cached decomposition for: {idea[:50]}...")
                continue

            decomposition_data = decomp_resp.data[0].get("result", {})
            # Extract business type, location from cached result
            business_type = decomposition_data.get("business_type", "")
            location = decomposition_data.get("location", {})
            city = location.get("city", "").lower() if location else ""
            state = location.get("state", "").lower() if location else ""

            # Query discover_insights_cache table by business_type, city, state (limit 1)
            insight_resp = supabase_client.table("discover_insights_cache").select("insights").eq("business_type", business_type.lower()).eq("city", city or None).eq("state", state or None).limit(1).execute()
            if not insight_resp.data or len(insight_resp.data) == 0:
                print(f"\n[{i}/{len(QUERIES)}] No cached insights for: {idea[:50]}...")
                continue

            insights = insight_resp.data[0].get("insights", [])
            insight = insights[0] if insights else {}

            # Cache Tabs 3-5 using cached decomposition dict
            result = await cache_tabs_3_5(decomposition_data, insight, idea, i, len(QUERIES))
            results.append(result)

            # Wait between queries
            if i < len(QUERIES):
                print(f"\n[WAITING 60s before next query...]")
                await asyncio.sleep(60)

        except Exception as e:
            print(f"\n[{i}/{len(QUERIES)}] Error loading cache: {str(e)[:80]}")
            results.append({
                "idea": idea,
                "success": False,
                "error": str(e)
            })

    total_elapsed = time.time() - start_time

    # ===== FINAL SUMMARY =====
    print("\n\n" + "="*100)
    print("  FINAL SUMMARY - TABS 3-5")
    print("="*100)

    successful = sum(1 for r in results if r.get("success"))
    failed = len(results) - successful

    print(f"\n[RESULTS]")
    print(f"  Total queries processed:  {len(results)}")
    print(f"  Successful:               {successful} ({successful*100//len(results) if results else 0}%)")
    print(f"  Failed:                   {failed}")
    print(f"\n[TIME STATISTICS]")
    print(f"  Total time:               {total_elapsed:.1f}s ({total_elapsed/60:.1f} min)")
    if results:
        print(f"  Average per query:        {total_elapsed/len(results):.1f}s")

    # Tab success rates
    tab_counts = {
        "analyze": sum(1 for r in results if r.get("tabs", {}).get("analyze")),
        "setup": sum(1 for r in results if r.get("tabs", {}).get("setup")),
        "validate": sum(1 for r in results if r.get("tabs", {}).get("validate"))
    }

    print(f"\n[TABS COMPLETION]")
    print(f"  Tab 3 (ANALYZE):    {tab_counts['analyze']}/{successful} {'[OK]' if tab_counts['analyze'] > 0 else '[SKIP]'}")
    print(f"  Tab 4 (SETUP):      {tab_counts['setup']}/{successful} {'[OK]' if tab_counts['setup'] > 0 else '[SKIP]'}")
    print(f"  Tab 5 (VALIDATE):   {tab_counts['validate']}/{successful} {'[OK]' if tab_counts['validate'] > 0 else '[SKIP]'}")

    print(f"\n[STATUS]")
    print(f"  Tab 1 (DECOMPOSE): 22/22 [Already cached]")
    print(f"  Tab 2 (DISCOVER):  22/22 [Already cached]")
    print(f"  Tab 3 (ANALYZE):   {tab_counts['analyze']}/22 {'[OK]' if tab_counts['analyze'] > 0 else '[NEEDS WORK]'}")
    print(f"  Tab 4 (SETUP):     {tab_counts['setup']}/22 {'[OK]' if tab_counts['setup'] > 0 else '[NEEDS WORK]'}")
    print(f"  Tab 5 (VALIDATE):  {tab_counts['validate']}/22 {'[OK]' if tab_counts['validate'] > 0 else '[NEEDS WORK]'}")

    print("\n" + "="*100 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
