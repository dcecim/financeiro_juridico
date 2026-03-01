import httpx
import asyncio
import sys

async def login():
    async with httpx.AsyncClient() as client:
        try:
            print("Attempting login to http://127.0.0.1:8000/auth/token...")
            response = await client.post(
                "http://127.0.0.1:8000/auth/token",
                data={"username": "divino.cecim@gmail.com", "password": "teste001"},
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(login())
