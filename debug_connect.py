
import asyncio
import asyncpg
import sys
import os
import ssl

# ... (rest same as before, but modify test_connect)

# Try to get DATABASE_URL from environment or fallback
url = os.environ.get("DATABASE_URL")
if not url:
    print("DATABASE_URL not found in env", flush=True)
    # This is the one from env var reported in logs
    url = "postgresql://postgres:postgres@localhost:5432/crm"

print(f"Testing URL: {url}", flush=True)

# Parse URL to get params
try:
    from urllib.parse import urlparse
    parsed = urlparse(url)
    user = parsed.username
    password = parsed.password
    host = parsed.hostname
    port = parsed.port
    database = parsed.path.lstrip('/')
    
    print(f"User: {user}, Host: {host}, Port: {port}, DB: {database}", flush=True)
except Exception as e:
    print(f"Error parsing URL: {e}", flush=True)
    sys.exit(1)

async def test_connect(host_override=None, ssl_mode=None):
    target_host = host_override or host
    print(f"Connecting to {target_host} with SSL={ssl_mode}...", flush=True)
    
    ssl_context = None
    if ssl_mode == "require":
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
    elif ssl_mode == "disable":
        ssl_context = False # asyncpg takes False for no SSL
    
    try:
        conn = await asyncpg.connect(
            user=user,
            password=password,
            database=database,
            host=target_host,
            port=port,
            ssl=ssl_context
        )
        print(f"SUCCESS connecting to {target_host} with SSL={ssl_mode}!", flush=True)
        await conn.close()
    except Exception as e:
        print(f"FAILED connecting to {target_host} with SSL={ssl_mode}: {e}", flush=True)

async def main():
    print("--- Test 1: 127.0.0.1 (Default SSL) ---", flush=True)
    await test_connect("127.0.0.1")
    
    print("\n--- Test 2: 127.0.0.1 (SSL Disabled) ---", flush=True)
    await test_connect("127.0.0.1", "disable")
    
    print("\n--- Test 3: 127.0.0.1 (SSL Require - Relaxed) ---", flush=True)
    await test_connect("127.0.0.1", "require")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
