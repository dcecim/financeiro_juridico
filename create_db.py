import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config import settings

# Parse the database name from the URL
db_url = settings.DATABASE_URL
db_name = db_url.split("/")[-1]
base_url = db_url.rsplit("/", 1)[0] + "/postgres"  # Connect to default 'postgres' db

async def create_database():
    print(f"Connecting to 'postgres' to create '{db_name}'...")
    # Use isolation_level="AUTOCOMMIT" to allow CREATE DATABASE
    engine = create_async_engine(base_url, isolation_level="AUTOCOMMIT", echo=True)
    
    async with engine.connect() as conn:
        # Check if database exists
        result = await conn.execute(
            text(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
        )
        exists = result.scalar()
        
        if not exists:
            print(f"Creating database '{db_name}'...")
            await conn.execute(text(f"CREATE DATABASE {db_name}"))
            print(f"Database '{db_name}' created successfully!")
        else:
            print(f"Database '{db_name}' already exists.")
            
    await engine.dispose()

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(create_database())
