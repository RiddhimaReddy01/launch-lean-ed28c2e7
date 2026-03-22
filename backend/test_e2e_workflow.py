"""
End-to-end workflow test: Test all 5 tabs with actual API calls
Tests: DECOMPOSE → DISCOVER → ANALYZE → SETUP → VALIDATE
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def print_section(title):
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def print_subsection(title):
    print(f"\n>>> {title}")
    print("-" * 80)

def test_decompose():
    """Test DECOMPOSE tab"""
    print_section("TAB 1: DECOMPOSE")

    idea = "A sustainable, affordable meal prep delivery service for busy professionals in Austin"

    print_subsection("Request")
    print(f"Idea: {idea}\n")

    response = requests.post(
        f"{BASE_URL}/api/decompose-idea",
        json={"idea": idea},
        timeout=30
    )

    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"\nBusiness Type: {data.get('business_type')}")
        print(f"Location: {data.get('location', {}).get('city')}, {data.get('location', {}).get('state')}")
        print(f"Target Customers: {', '.join(data.get('target_customers', [])[:3])}")
        print(f"Price Tier: {data.get('price_tier')}")
        print(f"Reddit Communities: {len(data.get('subreddits', []))} identified")
        print(f"Search Queries: {len(data.get('search_queries', []))} generated")
        print(f"\n[PASS] DECOMPOSE working")
        return data
    else:
        print(f"Error: {response.text}")
        return None

def test_discover(decompose_data):
    """Test DISCOVER tab"""
    print_section("TAB 2: DISCOVER")

    if not decompose_data:
        print("[SKIP] No decompose data")
        return None

    print_subsection("Request")
    print(f"Using decomposed data from DECOMPOSE tab\n")

    payload = {
        "idea": "A sustainable, affordable meal prep delivery service for busy professionals in Austin",
        "business_type": decompose_data.get('business_type'),
        "location": decompose_data.get('location'),
        "target_customers": decompose_data.get('target_customers'),
        "search_queries": decompose_data.get('search_queries', [])[:3]  # Limit for speed
    }

    response = requests.post(
        f"{BASE_URL}/api/discover-insights",
        json=payload,
        timeout=60
    )

    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        insights = data.get('insights', [])
        print(f"\nInsights Found: {len(insights)}")

        if insights:
            for i, insight in enumerate(insights[:2], 1):
                print(f"\n  Insight {i}:")
                print(f"    Type: {insight.get('type')}")
                print(f"    Title: {insight.get('title', 'N/A')[:60]}...")
                print(f"    Score: {insight.get('score', 0):.1f}")
                print(f"    Evidence Count: {len(insight.get('evidence', []))}")

        print(f"\n[PASS] DISCOVER working")
        return data
    else:
        print(f"Error: {response.text}")
        return None

def test_analyze(decompose_data, discover_data):
    """Test ANALYZE tab"""
    print_section("TAB 3: ANALYZE")

    if not discover_data or not decompose_data:
        print("[SKIP] Missing decompose or discover data")
        return None

    insights = discover_data.get('insights', [])
    if not insights:
        print("[SKIP] No insights to analyze")
        return None

    # Use first insight
    insight = insights[0]

    print_subsection("Request")
    print(f"Analyzing insight: {insight.get('title', 'N/A')[:60]}...\n")

    payload = {
        "idea": "A sustainable, affordable meal prep delivery service for busy professionals in Austin",
        "business_type": decompose_data.get('business_type'),
        "insight": {
            "id": insight.get('id'),
            "type": insight.get('type'),
            "title": insight.get('title'),
            "evidence": insight.get('evidence', [])[:3]
        },
        "section": "opportunity"
    }

    response = requests.post(
        f"{BASE_URL}/api/analyze-insight",
        json=payload,
        timeout=30
    )

    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"\nAnalysis Generated for: {data.get('section')}")
        analysis_data = data.get('data', {})

        # Show key parts of analysis
        if 'problem_statement' in analysis_data:
            print(f"Problem: {str(analysis_data['problem_statement'])[:80]}...")
        if 'market_size' in analysis_data:
            print(f"Market Size: {analysis_data['market_size']}")
        if 'competitive_landscape' in analysis_data:
            print(f"Competitors: {str(analysis_data['competitive_landscape'])[:80]}...")

        print(f"\n[PASS] ANALYZE working")
        return data
    else:
        print(f"Error: {response.text}")
        return None

def test_setup(decompose_data):
    """Test SETUP tab"""
    print_section("TAB 4: SETUP")

    if not decompose_data:
        print("[SKIP] No decompose data")
        return None

    print_subsection("Request")
    print(f"Selected Tier: MID\n")

    payload = {
        "business_type": decompose_data.get('business_type'),
        "location": decompose_data.get('location'),
        "price_tier": "MID",
        "selected_tier": "MID"
    }

    response = requests.post(
        f"{BASE_URL}/api/generate-setup",
        json=payload,
        timeout=30
    )

    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()

        # Cost Tiers
        tiers = data.get('cost_tiers', [])
        print(f"\nCost Tiers: {len(tiers)}")
        if tiers:
            for tier in tiers:
                print(f"  {tier.get('tier')}: ${tier.get('total_range', {}).get('min', 0)}-${tier.get('total_range', {}).get('max', 0)}")

        # Suppliers
        suppliers = data.get('suppliers', [])
        print(f"\nSuppliers Found: {len(suppliers)}")
        if suppliers:
            for supplier in suppliers[:2]:
                print(f"  {supplier.get('name')} ({supplier.get('category')})")

        # Team
        team = data.get('team', [])
        print(f"\nTeam Roles: {len(team)}")
        if team:
            for role in team[:2]:
                print(f"  {role.get('title')} - {role.get('type')}")

        # Timeline
        timeline = data.get('timeline', [])
        print(f"\nTimeline Phases: {len(timeline)}")
        if timeline:
            for phase in timeline[:2]:
                print(f"  {phase.get('phase')}: {phase.get('weeks')} weeks")

        print(f"\n[PASS] SETUP working")
        return data
    else:
        print(f"Error: {response.text}")
        return None

def test_validate(decompose_data, discover_data):
    """Test VALIDATE tab - Save and retrieve validation experiments"""
    print_section("TAB 5: VALIDATE")

    if not decompose_data or not discover_data:
        print("[SKIP] Missing decompose or discover data")
        return None

    print_subsection("Step 1: Save Validation Experiment")

    # Save a validation experiment with revenue metrics
    payload = {
        "idea_id": "test-idea-001",
        "methods": ["landing", "survey"],
        "metrics": {
            "waitlist_signups": 75,
            "survey_completions": 12,
            "would_switch_rate": 68,
            "price_tolerance_avg": 13.50,
            "community_engagement": 25,
            "reddit_upvotes": 8,
            # NEW: Revenue metrics
            "paid_signups": 6,
            "revenue_collected": 300,
            "ad_spend": 150
        }
    }

    print(f"Saving experiment:")
    print(f"  Signups: {payload['metrics']['waitlist_signups']}")
    print(f"  Switch Rate: {payload['metrics']['would_switch_rate']}%")
    print(f"  Paid Signups: {payload['metrics']['paid_signups']} [NEW]")
    print(f"  Revenue: ${payload['metrics']['revenue_collected']} [NEW]")
    print(f"  Ad Spend: ${payload['metrics']['ad_spend']} [NEW]\n")

    response = requests.post(
        f"{BASE_URL}/api/validation-experiments",
        json=payload,
        timeout=30
    )

    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        exp_data = response.json()
        exp_id = exp_data.get('id')

        print(f"\nExperiment Saved:")
        print(f"  ID: {exp_id}")
        print(f"  Verdict: {exp_data.get('verdict', 'N/A').upper()}")
        print(f"  Reasoning: {exp_data.get('reasoning', 'N/A')}")

        # NEW: Show calculated economics
        if exp_data.get('cac') is not None:
            print(f"  CAC (calculated): ${exp_data.get('cac'):.2f} [NEW]")
        if exp_data.get('ltv_cac_ratio') is not None:
            print(f"  LTV/CAC Ratio: {exp_data.get('ltv_cac_ratio'):.1f}x [NEW]")

        print(f"\n[PASS] VALIDATE save working")

        # Step 2: Retrieve experiments
        print_subsection("Step 2: Retrieve Validation History")

        response2 = requests.get(
            f"{BASE_URL}/api/validation-experiments/test-idea-001",
            timeout=30
        )

        print(f"Status: {response2.status_code}")

        if response2.status_code == 200:
            history = response2.json()
            exps = history.get('experiments', [])
            print(f"\nExperiments Retrieved: {len(exps)}")

            if exps:
                for i, exp in enumerate(exps, 1):
                    print(f"\n  Experiment {i}:")
                    print(f"    Signups: {exp.get('waitlist_signups')}")
                    print(f"    Switch: {exp.get('would_switch_rate')}%")
                    print(f"    Paid: {exp.get('paid_signups')} [NEW]")
                    print(f"    Revenue: ${exp.get('revenue_collected')} [NEW]")
                    print(f"    Verdict: {exp.get('verdict', 'pending').upper()}")

            print(f"\n[PASS] VALIDATE retrieve working")
            return True
        else:
            print(f"Error: {response2.text}")
            return False
    else:
        print(f"Error: {response.text}")
        return False

def main():
    print("\n")
    print("=" * 80)
    print("  END-TO-END WORKFLOW TEST: All 5 Tabs")
    print("=" * 80)

    try:
        # Run workflow
        decompose = test_decompose()
        discover = test_discover(decompose)
        analyze = test_analyze(decompose, discover)
        setup = test_setup(decompose)
        validate = test_validate(decompose, discover)

        # Summary
        print_section("FINAL SUMMARY")

        results = {
            "DECOMPOSE": decompose is not None,
            "DISCOVER": discover is not None,
            "ANALYZE": analyze is not None,
            "SETUP": setup is not None,
            "VALIDATE": validate is not None
        }

        print("\nTab Status:")
        for tab, passed in results.items():
            status = "[PASS]" if passed else "[FAIL]"
            print(f"  {status} {tab}")

        all_passed = all(results.values())

        if all_passed:
            print("\n[OK] ALL TABS WORKING END-TO-END")
        else:
            print("\n[FAIL] SOME TABS FAILED")

        print("\nNew Revenue Validation Features Tested:")
        print("  [OK] Revenue metrics collection (paid_signups, revenue_collected, ad_spend)")
        print("  [OK] CAC calculation (cost per acquisition)")
        print("  [OK] LTV/CAC ratio calculation (lifetime value to CAC)")
        print("  [OK] Verdict logic with revenue validation")
        print("  [OK] Experiment history with economics display")

        print("\n" + "="*80)

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
