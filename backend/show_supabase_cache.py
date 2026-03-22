"""
Query Supabase cache tables and display all cached queries
"""

import json
from datetime import datetime
from app.core.config import settings
from supabase import create_client

def display_cache_contents():
    """Display all cached queries in Supabase."""

    # Initialize Supabase
    try:
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
    except Exception as e:
        print(f"[ERROR] Failed to connect to Supabase: {e}")
        return

    print("\n" + "="*100)
    print("SUPABASE CACHE CONTENTS - All Cached Queries")
    print("="*100)

    # ===== DECOMPOSE CACHE =====
    print("\n\n[TABLE 1: decompose_cache]")
    print("-"*100)

    try:
        result = supabase.table("decompose_cache").select("*").execute()
        decompose_entries = result.data if result.data else []

        if not decompose_entries:
            print("(Empty - no decompose queries cached)")
        else:
            print(f"Total entries: {len(decompose_entries)}\n")

            for idx, entry in enumerate(decompose_entries, 1):
                idea = entry.get("idea", "N/A")
                created = entry.get("created_at", "N/A")
                expires = entry.get("expires_at", "N/A")
                result_data = entry.get("result", {})

                print(f"\n[{idx}] IDEA: {idea}")
                print(f"    Created: {created}")
                print(f"    Expires: {expires}")

                if result_data:
                    print(f"    Business Type: {result_data.get('business_type', 'N/A')}")
                    loc = result_data.get('location', {})
                    if loc:
                        print(f"    Location: {loc.get('city', 'N/A')}, {loc.get('state', 'N/A')}")
                    customers = result_data.get('target_customers', [])
                    if customers:
                        print(f"    Target Customers: {', '.join(customers[:2])}...")
                    tier = result_data.get('price_tier', '')
                    if tier:
                        print(f"    Price Tier: {tier}")

    except Exception as e:
        print(f"[ERROR] Failed to fetch decompose cache: {e}")

    # ===== DISCOVER CACHE =====
    print("\n\n" + "="*100)
    print("[TABLE 2: discover_insights_cache]")
    print("-"*100)

    try:
        result = supabase.table("discover_insights_cache").select("*").execute()
        discover_entries = result.data if result.data else []

        if not discover_entries:
            print("(Empty - no discover insights cached)")
        else:
            print(f"Total entries: {len(discover_entries)}\n")

            for idx, entry in enumerate(discover_entries, 1):
                business_type = entry.get("business_type", "N/A")
                city = entry.get("city", "")
                state = entry.get("state", "")
                created = entry.get("created_at", "N/A")
                expires = entry.get("expires_at", "N/A")
                insights = entry.get("insights", [])
                sources = entry.get("sources", [])

                location = f"{city}, {state}".strip(", ") if city or state else "N/A"

                print(f"\n[{idx}] BUSINESS TYPE: {business_type}")
                print(f"    Location: {location}")
                print(f"    Created: {created}")
                print(f"    Expires: {expires}")
                print(f"    Sources Found: {len(sources)}")
                print(f"    Insights Found: {len(insights)}")

                if insights:
                    for i, insight in enumerate(insights[:3], 1):
                        insight_type = insight.get('type', 'N/A')
                        title = insight.get('title', 'N/A')[:60]
                        score = insight.get('score', 0)
                        print(f"      • Insight {i}: {insight_type} (score: {score}) - {title}...")

    except Exception as e:
        print(f"[ERROR] Failed to fetch discover cache: {e}")

    # ===== SUMMARY =====
    print("\n\n" + "="*100)
    print("[CACHE SUMMARY]")
    print("="*100)

    try:
        decompose_result = supabase.table("decompose_cache").select("id").execute()
        discover_result = supabase.table("discover_insights_cache").select("id").execute()

        decompose_count = len(decompose_result.data) if decompose_result.data else 0
        discover_count = len(discover_result.data) if discover_result.data else 0

        print(f"\nDecompose Queries Cached: {decompose_count}")
        print(f"Discover Insights Cached: {discover_count}")
        print(f"Total Cache Entries: {decompose_count + discover_count}")
        print(f"\nCache Type: Persistent database cache (Supabase)")
        print(f"TTL: 24 hours (24-hour expiration)")
        print(f"Auto-cleanup: Expired entries removed on query attempt")

    except Exception as e:
        print(f"[ERROR] Failed to get summary: {e}")

    print("\n" + "="*100 + "\n")

if __name__ == "__main__":
    display_cache_contents()
