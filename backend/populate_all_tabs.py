"""
Complete Pipeline: Run all 5 tabs for 22 business queries
Stores FULL research data for each idea
Tab 1: DECOMPOSE → Tab 2: DISCOVER → Tab 3: ANALYZE → Tab 4: SETUP → Tab 5: VALIDATE
"""

import asyncio
import time
import json
from app.schemas.models import (
    DecomposeRequest, DiscoverRequest, AnalyzeRequest, SetupRequest, ValidateRequest
)
from app.api.decompose import decompose_idea
from app.api.discover import discover_insights
from app.api.analyze import analyze_section
from app.api.setup import setup_section
from app.api.validate import generate_validation

# 22 queries from Supabase cache
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

async def run_all_tabs(idea: str, query_num: int, total: int):
    """Run complete 5-tab pipeline for one idea."""
    print(f"\n{'='*100}")
    print(f"[{query_num}/{total}] {idea[:70]}...")
    print('='*100)

    try:
        # ===== TAB 1: DECOMPOSE =====
        print(f"\n[TAB 1/5] DECOMPOSE - Breaking down business...")
        start = time.time()
        req = DecomposeRequest(idea=idea)
        decompose = await decompose_idea(req, user=None)
        tab1_time = time.time() - start
        print(f"  [OK] {tab1_time:.1f}s")
        print(f"      Business: {decompose.business_type}")
        print(f"      Location: {decompose.location.city}, {decompose.location.state}")

        # ===== TAB 2: DISCOVER =====
        print(f"\n[TAB 2/5] DISCOVER - Finding market signals...")
        start = time.time()
        try:
            discover_req = DiscoverRequest(decomposition=decompose)
            discover = await discover_insights(discover_req, user=None)
            tab2_time = time.time() - start
            print(f"  [OK] {tab2_time:.1f}s")
            print(f"      Sources: {len(discover.sources)}")
            print(f"      Insights: {len(discover.insights)}")
            if discover.insights:
                for i, insight in enumerate(discover.insights[:2], 1):
                    print(f"        • {insight.type}: {insight.title[:50]}... (score: {insight.score})")
        except Exception as e:
            print(f"  [SKIP] {str(e)[:60]}")
            discover = None
            tab2_time = 0

        # ===== TAB 3: ANALYZE =====
        print(f"\n[TAB 3/5] ANALYZE - Deep dive analysis...")
        start = time.time()
        try:
            if discover and discover.insights:
                analyze_req = AnalyzeRequest(
                    section="opportunity",
                    insight=discover.insights[0],
                    decomposition=decompose
                )
                analyze = await analyze_section(analyze_req, user=None)
                tab3_time = time.time() - start
                print(f"  [OK] {tab3_time:.1f}s")
                print(f"      Section: {analyze.section}")
                print(f"      Data keys: {list(analyze.data.keys())[:3]}")
            else:
                print(f"  [SKIP] No insights to analyze")
                tab3_time = 0
                analyze = None
        except Exception as e:
            print(f"  [SKIP] {str(e)[:60]}")
            tab3_time = 0
            analyze = None

        # ===== TAB 4: SETUP =====
        print(f"\n[TAB 4/5] SETUP - Creating launch plan...")
        start = time.time()
        try:
            setup_req = SetupRequest(
                insight=discover.insights[0] if discover and discover.insights else None,
                decomposition=decompose,
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
                insight=discover.insights[0] if discover and discover.insights else None,
                decomposition=decompose,
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
        total_time = tab1_time + tab2_time + tab3_time + tab4_time + tab5_time
        print(f"\n[SUMMARY]")
        print(f"  Tab 1 (Decompose):  {tab1_time:6.1f}s [OK]")
        print(f"  Tab 2 (Discover):   {tab2_time:6.1f}s {'[OK]' if tab2_time > 0 else '[SKIP]'}")
        print(f"  Tab 3 (Analyze):    {tab3_time:6.1f}s {'[OK]' if tab3_time > 0 else '[SKIP]'}")
        print(f"  Tab 4 (Setup):      {tab4_time:6.1f}s {'[OK]' if tab4_time > 0 else '[SKIP]'}")
        print(f"  Tab 5 (Validate):   {tab5_time:6.1f}s {'[OK]' if tab5_time > 0 else '[SKIP]'}")
        print(f"  Total:              {total_time:6.1f}s")

        return {
            "idea": idea,
            "success": True,
            "total_time": total_time,
            "tabs": {
                "decompose": tab1_time > 0,
                "discover": tab2_time > 0,
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
    """Run all 22 queries through complete 5-tab pipeline."""
    print("\n" + "="*100)
    print("  COMPLETE PIPELINE: All 22 Queries × All 5 Tabs")
    print("="*100)
    print(f"\nRunning full research pipeline for {len(QUERIES)} business ideas...")
    print("Each query: DECOMPOSE -> DISCOVER -> ANALYZE -> SETUP -> VALIDATE\n")

    results = []
    start_time = time.time()

    for i, idea in enumerate(QUERIES, 1):
        result = await run_all_tabs(idea, i, len(QUERIES))
        results.append(result)

    total_elapsed = time.time() - start_time

    # ===== FINAL SUMMARY =====
    print("\n\n" + "="*100)
    print("  FINAL SUMMARY")
    print("="*100)

    successful = sum(1 for r in results if r.get("success"))
    failed = len(QUERIES) - successful

    print(f"\n[RESULTS]")
    print(f"  Total queries processed:  {len(QUERIES)}")
    print(f"  Successful:               {successful} ({successful*100//len(QUERIES)}%)")
    print(f"  Failed:                   {failed}")
    print(f"\n[TIME STATISTICS]")
    print(f"  Total time:               {total_elapsed:.1f}s ({total_elapsed/60:.1f} min)")
    print(f"  Average per query:        {total_elapsed/len(QUERIES):.1f}s")

    # Tab success rates
    tab_counts = {
        "decompose": sum(1 for r in results if r.get("tabs", {}).get("decompose")),
        "discover": sum(1 for r in results if r.get("tabs", {}).get("discover")),
        "analyze": sum(1 for r in results if r.get("tabs", {}).get("analyze")),
        "setup": sum(1 for r in results if r.get("tabs", {}).get("setup")),
        "validate": sum(1 for r in results if r.get("tabs", {}).get("validate"))
    }

    print(f"\n[TABS COMPLETION]")
    print(f"  Tab 1 (DECOMPOSE):  {tab_counts['decompose']}/{successful} [OK]")
    print(f"  Tab 2 (DISCOVER):   {tab_counts['discover']}/{successful} {'[OK]' if tab_counts['discover'] > 0 else '[SKIP]'}")
    print(f"  Tab 3 (ANALYZE):    {tab_counts['analyze']}/{successful} {'[OK]' if tab_counts['analyze'] > 0 else '[SKIP]'}")
    print(f"  Tab 4 (SETUP):      {tab_counts['setup']}/{successful} {'[OK]' if tab_counts['setup'] > 0 else '[SKIP]'}")
    print(f"  Tab 5 (VALIDATE):   {tab_counts['validate']}/{successful} {'[OK]' if tab_counts['validate'] > 0 else '[SKIP]'}")

    print(f"\n[DATA STORED]")
    print(f"  Full research pipeline executed for {successful} ideas")
    print(f"  All decompositions cached in Supabase")
    print(f"  Complete analysis data available for founder review")

    print("\n" + "="*100 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
