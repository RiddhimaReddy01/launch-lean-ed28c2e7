"""
Simple key test - check if Groq API key works
"""

import asyncio
import httpx
from app.core.config import settings

async def test_groq_key():
    """Test if Groq API key is valid and responsive"""
    print("\n" + "="*80)
    print("  GROQ API KEY VALIDATION TEST")
    print("="*80)

    if not settings.GROQ_API_KEY:
        print("\n[FAILED] GROQ_API_KEY not set in environment")
        return False

    print(f"\nKey loaded: {settings.GROQ_API_KEY[:20]}...")

    # Simple test request to Groq
    try:
        async with httpx.AsyncClient() as client:
            print("\nSending test request to Groq API...")

            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "mixtral-8x7b-32768",
                    "messages": [{"role": "user", "content": "Say 'OK' in JSON: {\"status\": \"ok\"}"}],
                    "max_tokens": 10,
                    "temperature": 0.1,
                },
                timeout=10
            )

            print(f"Status: {response.status_code}")

            if response.status_code == 200:
                print("[SUCCESS] Groq API key is valid and working!")
                print(f"Response: {response.text[:100]}")
                return True
            elif response.status_code == 429:
                print("[RATE LIMITED] Groq returned 429 - Rate limit hit")
                print("Your free tier key may have immediate rate limits")
                return False
            elif response.status_code == 401:
                print("[INVALID KEY] Groq returned 401 - Key is invalid or expired")
                return False
            else:
                print(f"[ERROR] Groq returned {response.status_code}")
                print(f"Response: {response.text}")
                return False

    except Exception as e:
        print(f"[ERROR] Failed to test key: {str(e)}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_groq_key())
    print("\n" + "="*80 + "\n")
