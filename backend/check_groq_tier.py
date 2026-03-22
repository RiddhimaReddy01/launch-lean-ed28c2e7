"""
Check Groq Account Tier by testing rate limits
Free vs Paid tiers have different limits
"""

import asyncio
import httpx
import time
from app.core.config import settings

async def check_tier():
    """Test Groq tier by making sequential requests"""
    print("\n" + "="*80)
    print("  GROQ ACCOUNT TIER CHECK")
    print("="*80)

    print(f"\nKey: {settings.GROQ_API_KEY[:30]}...")
    print(f"Model: {settings.GROQ_MODEL}")

    successful = 0
    failed = 0
    rate_limited = 0

    print("\nMaking 5 sequential requests to check tier...\n")

    async with httpx.AsyncClient(timeout=15) as client:
        for i in range(1, 6):
            try:
                print(f"Request {i}...", end=" ", flush=True)

                response = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": settings.GROQ_MODEL,
                        "messages": [{"role": "user", "content": "Say 'OK'"}],
                        "max_tokens": 5,
                        "temperature": 0.1,
                    },
                )

                if response.status_code == 200:
                    print("SUCCESS")
                    successful += 1
                elif response.status_code == 429:
                    print("RATE LIMITED (429)")
                    rate_limited += 1
                else:
                    print(f"ERROR ({response.status_code})")
                    failed += 1

                # Small delay between requests
                await asyncio.sleep(1)

            except Exception as e:
                print(f"FAILED ({str(e)[:40]})")
                failed += 1

    print("\n" + "="*80)
    print("  RESULTS")
    print("="*80)

    print(f"\nSuccessful: {successful}/5")
    print(f"Rate Limited: {rate_limited}/5")
    print(f"Failed: {failed}/5")

    print("\n[TIER ANALYSIS]")
    if successful == 5:
        print("Status: PAID TIER - All requests succeeded")
        print("Action: Ready to deploy, can handle production queries")
    elif successful >= 3:
        print("Status: MIXED - Some requests work, some rate limit")
        print("Action: Might be paid tier with low limits, or free tier in good state")
    elif rate_limited >= 3:
        print("Status: FREE TIER - Immediate rate limiting")
        print("Action: Need paid upgrade or API key switch")
    else:
        print("Status: UNKNOWN - Check API key validity")
        print("Action: Verify key in Groq console")

    print("\n" + "="*80 + "\n")

asyncio.run(check_tier())
