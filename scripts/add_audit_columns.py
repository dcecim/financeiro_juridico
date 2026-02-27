import asyncio
import sys
import os

# Add the parent directory to sys.path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine
from sqlalchemy import text

async def add_audit_columns():
    async with engine.begin() as conn:
        print("Adding 'criado_em' column to tables...")
        
        # Add column to lancamentos if not exists
        try:
            await conn.execute(text("""
                ALTER TABLE lancamentos 
                ADD COLUMN IF NOT EXISTS criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW();
            """))
            print("Added 'criado_em' to 'lancamentos'.")
        except Exception as e:
            print(f"Error adding to 'lancamentos': {e}")

        # Add column to centros_custo if not exists
        try:
            await conn.execute(text("""
                ALTER TABLE centros_custo 
                ADD COLUMN IF NOT EXISTS criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW();
            """))
            print("Added 'criado_em' to 'centros_custo'.")
        except Exception as e:
            print(f"Error adding to 'centros_custo': {e}")
            
        print("Migration Complete.")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(add_audit_columns())
