import asyncio
import sys
from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings

async def inspect_db():
    # Use sync engine for inspection as inspect is sync
    # But settings.DATABASE_URL is async.
    # We need to convert it to sync for create_engine or use run_sync
    
    url = "postgresql+psycopg://postgres:0102@127.0.0.1:5432/financeiro_juridico"
    print(f"Connecting to {url}")
    
    # We use psycopg (v3) which supports sync too
    engine = create_engine(url)
    
    inspector = inspect(engine)
    
    print("\nColumns in 'processos':")
    for col in inspector.get_columns("processos"):
        print(f"- {col['name']} ({col['type']})")

    print("\nColumns in 'usuarios':")
    for col in inspector.get_columns("usuarios"):
        print(f"- {col['name']} ({col['type']})")

    print("\nColumns in 'lancamentos':")
    for col in inspector.get_columns("lancamentos"):
        print(f"- {col['name']} ({col['type']})")

    print("\nAlembic Version:")
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM alembic_version"))
            for row in result:
                print(row)
    except Exception as e:
        print(f"Error checking alembic_version: {e}")

if __name__ == "__main__":
    from sqlalchemy import text
    asyncio.run(inspect_db())
