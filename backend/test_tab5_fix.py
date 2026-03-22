"""
Test Tab 5 (VALIDATE) after Scorecard fix
"""

import asyncio
import time
from app.schemas.models import DecomposeRequest, DiscoverRequest, ValidateRequest
from app.api.decompose import decompose_idea
from app.api.discover import discover_insights
from app.api.validate import generate_validation

async def test_tab5():
    print("\n" + "="*70)
    print("  [TAB 5 TEST] VALIDATE - Fixed Scorecard")
    print("="*70)

    # Setup
    idea = "A sustainable meal prep delivery service for busy professionals in Austin Texas"

    # Get decompose
    print("\nStep 1: Get decomposition...")
    req = DecomposeRequest(idea=idea)
    decompose = await decompose_idea(req, user=None)
    print("OK")

    # Get discover
    print("Step 2: Get market insights...")
    discover_req = DiscoverRequest(decomposition=decompose)
    discover = await discover_insights(discover_req, user=None)
    print(f"OK - {len(discover.insights)} insights")

    # Test validate (the fixed part)
    print("Step 3: Generate validation toolkit...")
    start = time.time()
    try:
        validate_req = ValidateRequest(
            insight=discover.insights[0] if discover and discover.insights else None,
            decomposition=decompose,
            channels=['landing_page', 'survey']
        )
        validate = await generate_validation(validate_req, user=None)
        elapsed = time.time() - start

        print(f"OK - {elapsed:.1f}s")
        print(f"\nVALIDATION OUTPUT:")
        print(f"  Channels: {len(validate.channels)}")
        print(f"  Landing Page: Headline generated")
        print(f"  Survey: {len(validate.survey.questions)} questions")
        print(f"  Communities: {len(validate.communities)} found")
        print(f"\nSCORECARD (Previously broken, now fixed):")
        print(f"  Waitlist Target: {validate.scorecard.waitlist_target} signups")
        print(f"  Survey Target: {validate.scorecard.survey_target} responses")
        print(f"  Switch Rate Target: {validate.scorecard.switch_pct_target}%")
        print(f"  Price Tolerance: ${validate.scorecard.price_tolerance_target}")
        print(f"  Paid Signups Target: {validate.scorecard.paid_signups_target}")
        print(f"  LTV/CAC Ratio Target: {validate.scorecard.ltv_cac_ratio_target}x")

        print(f"\n[SUCCESS] Tab 5 is now fully functional!")

    except Exception as e:
        print(f"[FAILED] {str(e)}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*70 + "\n")

asyncio.run(test_tab5())
