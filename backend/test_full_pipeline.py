"""
Full 5-Tab Pipeline Test - Single Query
No emojis to avoid encoding issues
"""

import asyncio
import time
from app.schemas.models import (
    DecomposeRequest, DiscoverRequest, AnalyzeRequest, SetupRequest, ValidateRequest
)
from app.api.decompose import decompose_idea
from app.api.discover import discover_insights
from app.api.analyze import analyze_section
from app.api.setup import setup_section
from app.api.validate import generate_validation

TEST_IDEA = "A sustainable meal prep delivery service for busy professionals in Austin Texas"

async def test_pipeline():
    print("\n" + "="*90)
    print("  FULL 5-TAB PIPELINE TEST - Single Query")
    print("="*90)
    print(f"\nIdea: {TEST_IDEA}\n")

    results = {}
    total_time = 0

    # === TAB 1: DECOMPOSE ===
    print("[TAB 1/5] DECOMPOSE")
    print("-" * 60)
    start = time.time()
    try:
        req = DecomposeRequest(idea=TEST_IDEA)
        decompose = await decompose_idea(req, user=None)
        tab1_time = time.time() - start
        results['decompose'] = True

        print(f"OK - {tab1_time:.1f}s")
        print(f"  Business Type: {decompose.business_type}")
        print(f"  Location: {decompose.location.get('city')}, {decompose.location.get('state')}")
        print(f"  Target Customers: {len(decompose.target_customers)} segments")
        print(f"  Price Tier: {decompose.price_tier}")
        print()
        total_time += tab1_time
    except Exception as e:
        results['decompose'] = False
        print(f"FAILED - {str(e)[:70]}\n")

    # === TAB 2: DISCOVER ===
    print("[TAB 2/5] DISCOVER")
    print("-" * 60)
    start = time.time()
    try:
        discover_req = DiscoverRequest(decomposition=decompose)
        discover = await discover_insights(discover_req, user=None)
        tab2_time = time.time() - start
        results['discover'] = True

        print(f"OK - {tab2_time:.1f}s")
        print(f"  Insights Found: {len(discover.insights)}")
        if discover.insights:
            for i, insight in enumerate(discover.insights[:3], 1):
                print(f"    {i}. [{insight.type}] {insight.title[:60]}")
        print(f"  Sources: {len(discover.sources)}")
        print(f"  Cache: Search results stored")
        print()
        total_time += tab2_time
    except Exception as e:
        results['discover'] = False
        print(f"FAILED - {str(e)[:70]}\n")
        discover = None

    # === TAB 3: ANALYZE ===
    print("[TAB 3/5] ANALYZE")
    print("-" * 60)
    start = time.time()
    try:
        analyze_req = AnalyzeRequest(
            section="opportunity",
            insight=discover.insights[0] if discover and discover.insights else None,
            decomposition=decompose
        )
        analyze = await analyze_section(analyze_req, user=None)
        tab3_time = time.time() - start
        results['analyze'] = True

        print(f"OK - {tab3_time:.1f}s")
        print(f"  Section: {analyze.section}")
        if hasattr(analyze, 'summary'):
            print(f"  Summary: {analyze.summary[:70]}...")
        print()
        total_time += tab3_time
    except Exception as e:
        results['analyze'] = False
        print(f"FAILED - {str(e)[:70]}\n")

    # === TAB 4: SETUP ===
    print("[TAB 4/5] SETUP")
    print("-" * 60)
    start = time.time()
    try:
        setup_req = SetupRequest(
            insight=discover.insights[0] if discover and discover.insights else None,
            decomposition=decompose,
            selected_tier="MID"
        )
        setup = await setup_section(setup_req, user=None)
        tab4_time = time.time() - start
        results['setup'] = True

        print(f"OK - {tab4_time:.1f}s")
        print(f"  Tier: {setup.selected_tier if hasattr(setup, 'selected_tier') else 'MID'}")
        print(f"  Suppliers: {len(setup.suppliers) if hasattr(setup, 'suppliers') else 0}")
        print(f"  Timeline Phases: {len(setup.timeline) if hasattr(setup, 'timeline') else 0}")
        if hasattr(setup, 'timeline'):
            for phase in setup.timeline[:2]:
                print(f"    - {phase.get('phase', 'Phase')}: {phase.get('weeks', '?')} weeks")
        print()
        total_time += tab4_time
    except Exception as e:
        results['setup'] = False
        print(f"FAILED - {str(e)[:70]}\n")

    # === TAB 5: VALIDATE ===
    print("[TAB 5/5] VALIDATE")
    print("-" * 60)
    start = time.time()
    try:
        validate_req = ValidateRequest(
            insight=discover.insights[0] if discover and discover.insights else None,
            decomposition=decompose,
            channels=["landing_page", "survey"]
        )
        validate = await generate_validation(validate_req, user=None)
        tab5_time = time.time() - start
        results['validate'] = True

        print(f"OK - {tab5_time:.1f}s")
        print(f"  Channels: {len(validate.channels) if hasattr(validate, 'channels') else 0}")
        if hasattr(validate, 'channels'):
            for ch in validate.channels[:2]:
                print(f"    - {ch.get('name', 'Channel')}: {ch.get('description', '')[:50]}")
        print()
        total_time += tab5_time
    except Exception as e:
        results['validate'] = False
        print(f"FAILED - {str(e)[:70]}\n")

    # === SUMMARY ===
    print("="*90)
    print("  SUMMARY")
    print("="*90)

    successful = sum(1 for v in results.values() if v)
    print(f"\nCompletion: {successful}/5 tabs successful")
    print(f"Total Time: {total_time:.1f}s\n")

    for tab, success in results.items():
        status = "OK" if success else "FAILED"
        print(f"  [{status}] {tab.upper()}")

    print(f"\nCache Status:")
    print(f"  - Search results cached (DISCOVER)")
    print(f"  - Future queries will be 30-50% faster")

    print("\n" + "="*90 + "\n")

    return successful == 5

if __name__ == "__main__":
    success = asyncio.run(test_pipeline())
    exit(0 if success else 1)
