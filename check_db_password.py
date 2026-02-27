
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def check_connection(password):
    url = f"postgresql+psycopg://postgres:{password}@127.0.0.1:5432/financeiro_juridico"
    print(f"Testing password: '{password}'")
    try:
        engine = create_async_engine(url)
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        print(f"SUCCESS with password: '{password}'")
        return True
    except Exception as e:
        # print(f"Failed: {e}")
        return False

async def main():
    passwords = ["postgres", "admin", "123456", "password", "root", ""]
    # Also try the one currently in .env
    passwords.insert(0, "0102") 
    
    for pwd in passwords:
        if await check_connection(pwd):
            print(f"FOUND PASSWORD: {pwd}")
            break
    else:
        print("Could not find correct password in common list.")

if __name__ == "__main__":
    asyncio.run(main())
