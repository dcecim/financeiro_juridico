
import sys
import os
import traceback

try:
    sys.path.append(os.getcwd())
    print("Added path", flush=True)
    
    from app.core.config import settings
    print(f"URL: {settings.DATABASE_URL}", flush=True)
    
    try:
        import asyncpg
        print("asyncpg is installed", flush=True)
    except ImportError:
        print("asyncpg is NOT installed", flush=True)
    
    from sqlalchemy.ext.asyncio import create_async_engine
    try:
        engine = create_async_engine(settings.DATABASE_URL)
        print("Engine created successfully", flush=True)
    except Exception as e:
        print(f"Error creating engine: {e}", flush=True)
        traceback.print_exc()
        
except Exception as e:
    print(f"Top level error: {e}", flush=True)
    traceback.print_exc()
