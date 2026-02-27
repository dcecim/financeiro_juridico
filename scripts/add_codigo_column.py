import asyncio
import sys
import os

# Add the parent directory to sys.path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine
from sqlalchemy import text

async def add_codigo_column():
    async with engine.begin() as conn:
        print("Checking 'codigo' column in 'centros_custo'...")
        
        # Check if column exists
        result = await conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='centros_custo' AND column_name='codigo';
        """))
        exists = result.scalar()
        
        if not exists:
            print("Adding 'codigo' column...")
            await conn.execute(text("""
                ALTER TABLE centros_custo 
                ADD COLUMN codigo VARCHAR(6);
            """))
            print("Column added.")
        else:
            print("'codigo' column already exists.")

        # Populate existing rows with sequential codes
        print("Populating 'codigo' for existing rows...")
        
        # Fetch all IDs ordered by name (deterministic)
        rows = await conn.execute(text("SELECT id FROM centros_custo ORDER BY nome"))
        ids = rows.scalars().all()
        
        for index, row_id in enumerate(ids):
            # Generate code starting from 1
            code = f"{index + 1:06d}"
            await conn.execute(text("""
                UPDATE centros_custo 
                SET codigo = :code 
                WHERE id = :id AND (codigo IS NULL OR codigo = '')
            """), {"code": code, "id": row_id})
            
        print(f"Updated {len(ids)} rows.")

        # Add unique constraint if not exists
        try:
            await conn.execute(text("""
                ALTER TABLE centros_custo 
                ADD CONSTRAINT uq_centros_custo_codigo UNIQUE (codigo);
            """))
            print("Unique constraint added.")
        except Exception as e:
            print(f"Unique constraint might already exist or failed: {e}")

        print("Migration Complete.")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(add_codigo_column())
