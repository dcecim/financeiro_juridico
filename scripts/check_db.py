import asyncio
import sys
import os
# Adicionar diretório raiz
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.core.config import settings
import psycopg

async def check():
    print(f"CWD: {os.getcwd()}")
    print(f"Files in CWD: {[f for f in os.listdir('.') if f.startswith('.env')]}")
    
    # Force reload of settings if needed, but let's check first what we have
    url = settings.DATABASE_URL.replace("postgresql+psycopg://", "postgresql://")
    print(f"URL from settings: {url}")
    
    # Try to connect
    try:
        async with await psycopg.AsyncConnection.connect(url) as conn:
            print("Conexão bem sucedida!")
            async with conn.cursor() as cur:
                await cur.execute("SELECT 1")
                print(await cur.fetchone())
    except Exception as e:
        print(f"Erro ao conectar: {e}")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(check())
