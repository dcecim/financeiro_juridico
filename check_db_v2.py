import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import urllib.parse

async def check(user, password, db, host="127.0.0.1", port="5432"):
    # Encode password to handle special chars if any (though 0102 is safe)
    safe_password = urllib.parse.quote_plus(password)
    url = f"postgresql+psycopg://{user}:{safe_password}@{host}:{port}/{db}"
    print(f"Connecting to postgresql+psycopg://{user}:***@{host}:{port}/{db}...", flush=True)
    
    engine = create_async_engine(url)
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        print(f"SUCCESS: Connected to {db} as {user}", flush=True)
        return True
    except Exception as e:
        print(f"FAILURE: {e}", flush=True)
        return False
    finally:
        await engine.dispose()

async def main():
    # 1. Test postgres user, 0102 password, postgres db
    print("--- Test 1: postgres/0102/postgres ---")
    await check("postgres", "0102", "postgres")
    
    # 2. Test postgres user, 0102 password, financeiro_juridico db
    print("\n--- Test 2: postgres/0102/financeiro_juridico ---")
    await check("postgres", "0102", "financeiro_juridico")

    # 3. Test with other common passwords just in case
    print("\n--- Test 3: postgres/postgres/postgres ---")
    await check("postgres", "postgres", "postgres")

    # 4. Test with admin/0102/postgres
    print("\n--- Test 4: admin/0102/postgres ---")
    await check("admin", "0102", "postgres")

if __name__ == "__main__":
    import sys
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
