#!/usr/bin/env python3
"""
Manual Testing Script - Complete workflow test with mock data.
This simulates a user going through all 5 modules end-to-end.
No pytest required - can be run directly: python test_manual.py

To actually test the API:
1. Start the backend: uvicorn app.main:app --reload
2. In another terminal: python test_manual.py
"""

import json
import httpx
import sys
from typing import Optional

# ═══ CONFIGURATION ═══

API_BASE_URL = "http://localhost:8000"
TIMEOUT = 30.0

# ANSI colors for output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# ═══ TEST DATA ═══

TEST_IDEA = "A premium mobile pet grooming service that comes to your house for busy Austin professionals who want trustworthy, high-quality grooming for their pets"

SAMPLE_DECOMPOSE_OUTPUT = {
    "business_type": "pet grooming service",
    "location": {
        "city": "Austin",
        "state": "TX",
        "county": "Travis",
        "metro": "Austin-Round Rock-San Marcos"
    },
    "target_customers": ["pet owners", "busy professionals", "small businesses"],
    "price_tier": "premium",
    "subreddits": ["Austin", "Entrepreneur", "smallbusiness", "dogs", "PetGrooming"],
    "review_platforms": ["yelp", "google"],
    "search_queries": [
        "pet grooming Austin TX",
        "mobile dog grooming services",
        "professional pet grooming demand",
        "pet grooming franchise opportunities"
    ]
}

SAMPLE_INSIGHT = {
    "type": "pain_point",
    "title": "Finding trustworthy pet groomers is difficult",
    "score": 8.5,
    "frequency_score": 7.2,
    "intensity_score": 8.1,
    "willingness_to_pay_score": 7.8,
    "mention_count": 125,
    "evidence": [
        {
            "quote": "Took my dog to 5 different groomers before finding one that doesn't mess up",
            "source": "r/Austin",
            "score": 85,
            "upvotes": 145,
            "date": "2025-03-01"
        }
    ],
    "source_platforms": ["reddit", "google"],
    "audience_estimate": "2.5M pet owners in major metros"
}


# ═══ LOGGING UTILITIES ═══

def print_header(text: str):
    """Print section header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}")
    print(f"{text}")
    print(f"{'='*70}{Colors.ENDC}\n")


def print_success(text: str):
    """Print success message."""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_error(text: str):
    """Print error message."""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


def print_info(text: str):
    """Print info message."""
    print(f"{Colors.OKCYAN}→ {text}{Colors.ENDC}")


def print_warning(text: str):
    """Print warning message."""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")


def print_json(data, indent=2):
    """Pretty-print JSON data."""
    print(json.dumps(data, indent=indent, default=str))


# ═══ HTTP CLIENT ═══

class APITester:
    """Helper for making API requests."""

    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.client = httpx.Client(timeout=TIMEOUT)

    def get(self, endpoint: str) -> tuple[int, Optional[dict]]:
        """Make GET request."""
        try:
            url = f"{self.base_url}{endpoint}"
            resp = self.client.get(url)
            try:
                data = resp.json()
            except:
                data = {"text": resp.text}
            return resp.status_code, data
        except Exception as e:
            print_error(f"Request failed: {e}")
            return None, None

    def post(self, endpoint: str, payload: dict) -> tuple[int, Optional[dict]]:
        """Make POST request."""
        try:
            url = f"{self.base_url}{endpoint}"
            resp = self.client.post(url, json=payload)
            try:
                data = resp.json()
            except:
                data = {"text": resp.text}
            return resp.status_code, data
        except Exception as e:
            print_error(f"Request failed: {e}")
            return None, None

    def close(self):
        """Close client."""
        self.client.close()


# ═══ TEST FUNCTIONS ═══

def test_health_check(tester: APITester) -> bool:
    """Test health check endpoints."""
    print_header("TEST 0: Health Check")

    # Test root endpoint
    print_info("Checking GET /")
    status, data = tester.get("/")
    if status != 200:
        print_error(f"Root endpoint failed: {status}")
        return False

    print_success(f"Service: {data.get('service')}")
    print_success(f"Status: {data.get('status')}")
    print_success(f"Version: {data.get('version')}")
    print(f"Endpoints: {len(data.get('endpoints', []))} available")

    # Test health endpoint
    print_info("Checking GET /health")
    status, data = tester.get("/health")
    if status != 200:
        print_error(f"Health endpoint failed: {status}")
        return False

    print_success(f"Health status: {data.get('status')}")
    providers = data.get('providers', {})
    print(f"Providers configured: {json.dumps(providers, indent=2)}")

    return True


def test_decompose(tester: APITester) -> Optional[dict]:
    """Test MODULE 0: Decompose Idea."""
    print_header("TEST 1: DECOMPOSE - Parse Idea into Structure")

    payload = {"idea": TEST_IDEA}
    print_info(f"Idea: {payload['idea'][:80]}...")

    status, data = tester.post("/api/decompose-idea", payload)

    if status != 200:
        print_error(f"Decompose failed: {status}")
        if data:
            print(f"Response: {json.dumps(data, indent=2)}")
        return None

    print_success("Decompose successful!")
    print_info(f"Business Type: {data.get('business_type')}")
    print_info(f"Location: {data['location']['city']}, {data['location']['state']}")
    print_info(f"Price Tier: {data.get('price_tier')}")
    print_info(f"Target Customers: {', '.join(data.get('target_customers', [])[:3])}")
    print_info(f"Subreddits to search: {', '.join(data.get('subreddits', [])[:4])}")
    print_info(f"Search queries: {len(data.get('search_queries', []))} created")

    return data


def test_discover(tester: APITester, decompose_output: dict) -> Optional[dict]:
    """Test MODULE 1: Discover Insights."""
    print_header("TEST 2: DISCOVER - Find Market Insights")

    payload = {"decomposition": decompose_output}
    print_info(f"Searching subreddits: {', '.join(decompose_output['subreddits'][:3])}...")
    print_info(f"Running {len(decompose_output['search_queries'])} Google searches...")

    status, data = tester.post("/api/discover-insights", payload)

    if status != 200:
        print_error(f"Discover failed: {status}")
        if data:
            print(f"Response: {json.dumps(data, indent=2)}")
        return None

    print_success("Discover successful!")
    insights = data.get('insights', [])
    print_info(f"Insights found: {len(insights)}")

    for i, insight in enumerate(insights[:3], 1):
        print(f"\n  Insight {i}: {insight.get('title')}")
        print(f"    Type: {insight.get('type')}")
        print(f"    Score: {insight.get('score')}/10")
        print(f"    Evidence: {len(insight.get('evidence', []))} sources")

    sources = data.get('sources', [])
    print_info(f"Data sources: {len(sources)} (Reddit + Google)")

    return data


def test_analyze_opportunity(tester: APITester, decompose_output: dict) -> Optional[dict]:
    """Test MODULE 2A: Analyze - Opportunity."""
    print_header("TEST 3A: ANALYZE - Market Opportunity (TAM/SAM/SOM)")

    payload = {
        "section": "opportunity",
        "insight": SAMPLE_INSIGHT,
        "decomposition": decompose_output
    }
    print_info("Fetching market sizing data from Serper...")

    status, data = tester.post("/api/analyze-section", payload)

    if status != 200:
        print_error(f"Analyze (opportunity) failed: {status}")
        if data:
            print(f"Response: {json.dumps(data, indent=2)}")
        return None

    print_success("Opportunity analysis successful!")
    analysis = data.get('data', {})
    tam = analysis.get('tam', {})
    sam = analysis.get('sam', {})
    som = analysis.get('som', {})

    print_info(f"TAM (Total Addressable Market): {tam.get('formatted')} ({tam.get('confidence')} confidence)")
    print_info(f"SAM (Serviceable Available): {sam.get('formatted')}")
    print_info(f"SOM (Serviceable Obtainable): {som.get('formatted')}")

    return data


def test_analyze_customers(tester: APITester, decompose_output: dict) -> Optional[dict]:
    """Test MODULE 2B: Analyze - Customers."""
    print_header("TEST 3B: ANALYZE - Customer Segments")

    payload = {
        "section": "customers",
        "insight": SAMPLE_INSIGHT,
        "decomposition": decompose_output
    }

    status, data = tester.post("/api/analyze-section", payload)

    if status != 200:
        print_error(f"Analyze (customers) failed: {status}")
        return None

    print_success("Customer analysis successful!")
    analysis = data.get('data', {})
    segments = analysis.get('segments', [])

    for i, segment in enumerate(segments[:3], 1):
        print(f"\n  Segment {i}: {segment.get('name')}")
        print(f"    Size: {segment.get('estimated_size'):,}")
        print(f"    Pain Intensity: {segment.get('pain_intensity')}/10")
        print(f"    Primary Need: {segment.get('primary_need')}")
        print(f"    Spending: {segment.get('spending_pattern')}")

    return data


def test_analyze_competitors(tester: APITester, decompose_output: dict) -> Optional[dict]:
    """Test MODULE 2C: Analyze - Competitors."""
    print_header("TEST 3C: ANALYZE - Competitive Landscape")

    payload = {
        "section": "competitors",
        "insight": SAMPLE_INSIGHT,
        "decomposition": decompose_output
    }
    print_info("Searching for competitors in Austin...")

    status, data = tester.post("/api/analyze-section", payload)

    if status != 200:
        print_error(f"Analyze (competitors) failed: {status}")
        return None

    print_success("Competitive analysis successful!")
    analysis = data.get('data', {})
    competitors = analysis.get('competitors', [])

    for i, comp in enumerate(competitors[:3], 1):
        print(f"\n  Competitor {i}: {comp.get('name')}")
        print(f"    Rating: {comp.get('rating')}/5.0")
        print(f"    Price Range: {comp.get('price_range')}")
        print(f"    Key Strength: {comp.get('key_strength')}")
        print(f"    Key Gap: {comp.get('key_gap')}")
        print(f"    Threat Level: {comp.get('threat_level')}")

    gaps = analysis.get('unfilled_gaps', [])
    print(f"\n  Unfilled Gaps: {len(gaps)} found")
    for gap in gaps[:2]:
        print(f"    - {gap}")

    return data


def test_setup(tester: APITester, decompose_output: dict) -> Optional[dict]:
    """Test MODULE 3: Setup - Launch Plan."""
    print_header("TEST 4: SETUP - Launch Plan (Cost, Team, Timeline)")

    payload = {
        "insight": SAMPLE_INSIGHT,
        "decomposition": decompose_output
    }
    print_info("Generating launch plan with cost tiers, suppliers, team, and timeline...")

    status, data = tester.post("/api/generate-setup", payload)

    if status != 200:
        print_error(f"Setup failed: {status}")
        if data:
            print(f"Response: {json.dumps(data, indent=2)}")
        return None

    print_success("Setup generation successful!")

    # Cost tiers
    cost_tiers = data.get('cost_tiers', [])
    print_info(f"Cost Tiers: {len(cost_tiers)} provided")
    for tier in cost_tiers:
        total = tier.get('total_range', {})
        print(f"  - {tier.get('tier')}: ${total.get('min'):,}-${total.get('max'):,}")

    # Suppliers
    suppliers = data.get('suppliers', [])
    print_info(f"Suppliers: {len(suppliers)} recommended")
    for supp in suppliers[:2]:
        print(f"  - {supp.get('name')} ({supp.get('category')})")

    # Team
    team = data.get('team', [])
    print_info(f"Team: {len(team)} roles needed")
    for role in team[:2]:
        salary = role.get('salary_range', {})
        print(f"  - {role.get('title')}: ${salary.get('min'):,}-${salary.get('max'):,}")

    # Timeline
    timeline = data.get('timeline', [])
    print_info(f"Timeline: {len(timeline)} phases")
    for phase in timeline[:2]:
        print(f"  - {phase.get('phase')}: {phase.get('weeks')} weeks")

    return data


def test_validate(tester: APITester, decompose_output: dict) -> Optional[dict]:
    """Test MODULE 4: Validate - Validation Toolkit."""
    print_header("TEST 5: VALIDATE - Validation Toolkit (Landing Page, Survey, Communities)")

    payload = {
        "channels": ["landing_page", "survey", "whatsapp"],
        "insight": SAMPLE_INSIGHT,
        "decomposition": decompose_output
    }
    print_info("Generating validation toolkit...")

    status, data = tester.post("/api/generate-validation", payload)

    if status != 200:
        print_error(f"Validate failed: {status}")
        if data:
            print(f"Response: {json.dumps(data, indent=2)}")
        return None

    print_success("Validation toolkit generated!")

    # Landing page
    lp = data.get('landing_page', {})
    if lp:
        print_info(f"Landing Page: {lp.get('headline')}")
        print(f"  Subheadline: {lp.get('subheadline')}")
        print(f"  CTA: {lp.get('cta_text')}")
        benefits = lp.get('benefits', [])
        print(f"  Benefits: {len(benefits)} listed")

    # Survey
    survey = data.get('survey', {})
    if survey:
        print_info(f"Survey: '{survey.get('title')}'")
        questions = survey.get('questions', [])
        print(f"  Questions: {len(questions)}")

    # WhatsApp
    wa = data.get('whatsapp_message', {})
    if wa:
        print_info(f"WhatsApp Message: {wa.get('message')[:60]}...")

    # Communities
    communities = data.get('communities', [])
    print_info(f"Communities: {len(communities)} found")
    for comm in communities[:3]:
        print(f"  - {comm.get('name')} ({comm.get('platform')}): {comm.get('member_count')} members")

    # Scorecard
    scorecard = data.get('scorecard', {})
    print_info(f"Success Metrics:")
    print(f"  - Waitlist Target: {scorecard.get('waitlist_target')}")
    print(f"  - Survey Target: {scorecard.get('survey_target')}")
    print(f"  - Price Tolerance: {scorecard.get('price_tolerance_target')}")

    return data


# ═══ MAIN RUNNER ═══

def main():
    """Run complete test workflow."""
    print(f"\n{Colors.BOLD}{Colors.OKBLUE}")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║                   LaunchLens AI Backend Test Suite                  ║")
    print("║                  Testing all 5 modules with mock data               ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}")

    # Initialize API tester
    tester = APITester()

    try:
        # Test 0: Health Check
        if not test_health_check(tester):
            print_error("Cannot reach API. Make sure backend is running:")
            print_warning("  uvicorn app.main:app --reload")
            return False

        # Test 1: Decompose
        decompose_data = test_decompose(tester)
        if not decompose_data:
            return False

        # Test 2: Discover
        discover_data = test_discover(tester, decompose_data)
        if not discover_data:
            return False

        # Test 3A: Analyze - Opportunity
        opportunity_data = test_analyze_opportunity(tester, decompose_data)
        if not opportunity_data:
            return False

        # Test 3B: Analyze - Customers
        customers_data = test_analyze_customers(tester, decompose_data)
        if not customers_data:
            return False

        # Test 3C: Analyze - Competitors
        competitors_data = test_analyze_competitors(tester, decompose_data)
        if not competitors_data:
            return False

        # Test 4: Setup
        setup_data = test_setup(tester, decompose_data)
        if not setup_data:
            return False

        # Test 5: Validate
        validate_data = test_validate(tester, decompose_data)
        if not validate_data:
            return False

        # Summary
        print_header("✓ ALL TESTS PASSED!")
        print_success("All 5 modules working correctly")
        print(f"\n{Colors.OKGREEN}Data pipeline:{Colors.ENDC}")
        print(f"  1. Decompose: Parsed idea into structure")
        print(f"  2. Discover: Found {len(discover_data.get('insights', []))} market insights")
        print(f"  3. Analyze: Generated 3 analysis sections (opportunity, customers, competitors)")
        print(f"  4. Setup: Created launch plan with cost tiers and timeline")
        print(f"  5. Validate: Generated validation toolkit")

        return True

    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        return False
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        tester.close()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
