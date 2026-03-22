"""
Test revenue validation and CAC/LTV calculations
Tests the new validation metrics and verdict logic
"""

import json
from app.api.tracking import _calculate_cac_ltv, _calculate_verdict

def test_cac_ltv_calculation():
    """Test CAC and LTV/CAC ratio calculations"""
    print("\n" + "="*60)
    print("TEST 1: CAC & LTV/CAC Calculation")
    print("="*60)

    # Scenario 1: Healthy economics (LTV/CAC > 3)
    cac, ltv_cac = _calculate_cac_ltv(
        paid_signups=10,
        revenue_collected=500,  # $50 per customer
        ad_spend=300,
        price_tolerance=50,
        months_expected=12
    )
    print(f"\nScenario 1: Healthy Economics")
    print(f"  Paid signups: 10, Revenue: $500, Ad spend: $300")
    print(f"  CAC: ${cac:.2f}")
    print(f"  LTV/CAC Ratio: {ltv_cac:.2f}x")
    assert cac == 30, f"Expected CAC $30, got ${cac}"
    assert ltv_cac >= 3, f"Expected LTV/CAC >= 3, got {ltv_cac}x"
    print(f"  [PASS] Healthy ratio (>3x)")

    # Scenario 2: Challenging economics (LTV/CAC ~1.5x)
    cac, ltv_cac = _calculate_cac_ltv(
        paid_signups=10,
        revenue_collected=200,  # $20 per customer
        ad_spend=1000,  # $100 CAC (high spend)
        price_tolerance=20,
        months_expected=12
    )
    print(f"\nScenario 2: Challenging Economics")
    print(f"  Paid signups: 10, Revenue: $200, Ad spend: $1000")
    print(f"  CAC: ${cac:.2f}")
    print(f"  LTV/CAC Ratio: {ltv_cac:.2f}x")
    assert cac == 100, f"Expected CAC $100, got ${cac}"
    assert ltv_cac < 3, f"Expected LTV/CAC < 3, got {ltv_cac}x"
    print(f"  [PASS] Challenging ratio (1.5x, below 3x threshold)")

    # Scenario 3: No revenue yet
    cac, ltv_cac = _calculate_cac_ltv(
        paid_signups=0,
        revenue_collected=0,
        ad_spend=100,
        price_tolerance=0,
        months_expected=12
    )
    print(f"\nScenario 3: No Revenue Yet")
    print(f"  Paid signups: 0, Revenue: $0, Ad spend: $100")
    print(f"  CAC: {cac}")
    print(f"  LTV/CAC Ratio: {ltv_cac}")
    assert cac is None
    assert ltv_cac is None
    print(f"  [OK] PASS: Both metrics are None")


def test_verdict_logic():
    """Test verdict calculation with revenue validation"""
    print("\n" + "="*60)
    print("TEST 2: Verdict Logic (Interest vs Revenue)")
    print("="*60)

    # Test 1: High interest but no paid conversions → PIVOT
    verdict, reasoning = _calculate_verdict(
        signups=100,
        switch_rate=75,
        price_tolerance=15,
        paid_signups=0,
        revenue_collected=0,
        cac=None,
        ltv_cac_ratio=None
    )
    print(f"\nTest 2.1: High Interest, Zero Conversions")
    print(f"  Inputs: 100 signups, 75% switch, $15 price, 0 paid")
    print(f"  Verdict: {verdict.upper()}")
    print(f"  Reasoning: {reasoning}")
    assert verdict == "pivot", f"Expected PIVOT, got {verdict}"
    assert "zero conversions" in reasoning.lower() or "0" in reasoning
    print(f"  [OK] PASS: Correctly identified lack of paid intent")

    # Test 2: Good signups + paid conversions + healthy CAC → GO
    verdict, reasoning = _calculate_verdict(
        signups=60,
        switch_rate=70,
        price_tolerance=14,
        paid_signups=8,
        revenue_collected=400,
        cac=50,
        ltv_cac_ratio=4.8
    )
    print(f"\nTest 2.2: Strong Metrics + Healthy Economics")
    print(f"  Inputs: 60 signups, 70% switch, $14 price, 8 paid, LTV/CAC 4.8x")
    print(f"  Verdict: {verdict.upper()}")
    print(f"  Reasoning: {reasoning}")
    assert verdict == "go", f"Expected GO, got {verdict}"
    assert "4.8" in reasoning
    print(f"  [OK] PASS: Correctly identified GO signal with economics")

    # Test 3: No data → AWAITING
    verdict, reasoning = _calculate_verdict(
        signups=0,
        switch_rate=0,
        price_tolerance=0,
        paid_signups=0,
        revenue_collected=0,
        cac=None,
        ltv_cac_ratio=None
    )
    print(f"\nTest 2.3: No Data Entered")
    print(f"  Inputs: 0 signups, 0% switch, $0 price, 0 paid")
    print(f"  Verdict: {verdict.upper()}")
    print(f"  Reasoning: {reasoning}")
    assert verdict == "awaiting", f"Expected AWAITING, got {verdict}"
    print(f"  [OK] PASS: Correctly awaits user data")

    # Test 4: Moderate interest + some paid → PIVOT
    verdict, reasoning = _calculate_verdict(
        signups=45,
        switch_rate=55,
        price_tolerance=10,
        paid_signups=3,
        revenue_collected=150,
        cac=100,
        ltv_cac_ratio=1.8
    )
    print(f"\nTest 2.4: Moderate Interest with Paid Traction")
    print(f"  Inputs: 45 signups, 55% switch, $10 price, 3 paid, LTV/CAC 1.8x")
    print(f"  Verdict: {verdict.upper()}")
    print(f"  Reasoning: {reasoning}")
    assert verdict == "pivot", f"Expected PIVOT, got {verdict}"
    print(f"  [OK] PASS: Correctly identified PIVOT signal")


def test_scorecard_targets():
    """Test that scorecard targets are realistic"""
    print("\n" + "="*60)
    print("TEST 3: Realistic Scorecard Targets")
    print("="*60)

    from app.schemas.models import Scorecard

    scorecard = Scorecard()
    print(f"\nDefault Scorecard Targets:")
    print(f"  Waitlist signups: {scorecard.waitlist_target} (realistic Phase 1)")
    print(f"  Survey completions: {scorecard.survey_target}")
    print(f"  Switch rate: {scorecard.switch_pct_target}%")
    print(f"  Price tolerance: ${scorecard.price_tolerance_target:.2f}")
    print(f"  Paid signups: {scorecard.paid_signups_target}")
    print(f"  LTV/CAC ratio: {scorecard.ltv_cac_ratio_target:.1f}x")

    assert scorecard.waitlist_target == 50, "Signups target should be 50"
    assert scorecard.survey_target == 10, "Survey target should be 10"
    assert scorecard.paid_signups_target == 5, "Paid target should be 5"
    assert scorecard.ltv_cac_ratio_target == 3.0, "LTV/CAC target should be 3.0x"
    print(f"\n[OK] PASS: All targets are realistic")


if __name__ == "__main__":
    try:
        test_cac_ltv_calculation()
        test_verdict_logic()
        test_scorecard_targets()

        print("\n" + "="*60)
        print("[SUCCESS] ALL TESTS PASSED")
        print("="*60)
        print("\nSummary:")
        print("  [OK] CAC/LTV calculations working correctly")
        print("  [OK] Verdict logic validates both interest and revenue")
        print("  [OK] Scorecard targets are realistic")
        print("  [OK] Revenue validation feature is functional")

    except AssertionError as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        exit(1)
    except Exception as e:
        print(f"\n[FAIL] ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
