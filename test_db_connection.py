import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

database_url = os.getenv("DATABASE_URL")
print(f"Testing connection to: {database_url}")

# Extract parts for psycopg (just to be clear)
# Or use the string directly if supported by psycopg 3

try:
    # Attempt to connect using the connection string format
    # The format in .env is for sqlalchemy: postgresql+psycopg://...
    # psycopg expects: postgresql://...
    
    # Let's parse manually to be sure or just use the raw params
    user = "postgres"
    password = "0102"
    host = "127.0.0.1"
    port = "5432"
    dbname = "financeiro_juridico"
    
    conn_str = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
    print(f"Connecting with: {conn_str}")
    
    with psycopg.connect(conn_str) as conn:
        print("Connection successful!")
        with conn.cursor() as cur:
            cur.execute("SELECT version()")
            print(cur.fetchone())

except Exception as e:
    print(f"Connection failed: {e}")
