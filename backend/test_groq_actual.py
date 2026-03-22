"""
Test Groq with actual model from config
"""

import asyncio
import httpx
from app.core.config import settings

async def test_groq():
    """Test Groq with actual configured model"""
    print("\n" + "="*80)
    print("  GROQ API TEST - Actual Configured Model")
    print("="*80)

    print(f"\nGROQ_API_KEY: {settings.GROQ_API_KEY[:20]}...")
    print(f"GROQ_MODEL: {settings.GROQ_MODEL}")

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            print("\nSending test request...")

            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": settings.GROQ_MODEL,
                    "messages": [{"role": "user", "content": "Say OK"}],
                    "max_tokens": 10,
                    "temperature": 0.1,
                },
            )

            print(f"Status: {response.status_code}")

            if response.status_code == 200:
                print("[SUCCESS] Groq API is working!")
                data = response.json()
                print(f"Response: {data['choices'][0]['message']['content']}")
                return True
            else:
                print(f"[ERROR] Status {response.status_code}")
                print(f"Response: {response.text}")
                return False

    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return False

asyncio.run(test_groq())
