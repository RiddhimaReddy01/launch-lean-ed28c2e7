import asyncio
from app.services.llm_client import call_llm

async def main():
    try:
        res = await call_llm(
            system_prompt="You are a helpful assistant.",
            user_prompt="Return {\"status\": \"ok\", \"model\": \"key_working\"}.",
            json_mode=True
        )
        print("SUCCESS:", res)
    except Exception as e:
        print("FAILED:", e)

if __name__ == "__main__":
    asyncio.run(main())
