import httpx
import asyncio
import sys
import os

# Adicionar diretório raiz
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

BASE_URL = "http://127.0.0.1:8000"
LOGIN_URL = "http://127.0.0.1:8000/auth/token"

async def verify():
    async with httpx.AsyncClient() as client:
        # 1. Login
        print("1. Tentando login...")
        response = await client.post(
            LOGIN_URL,
            data={"username": "divino.cecim@gmail.com", "password": "teste001"},
            headers={"content-type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code != 200:
            print(f"Erro no login (divino): {response.status_code} - {response.text}")
            # Tentar com admin se falhar
            print("Tentando com admin...")
            response = await client.post(
                LOGIN_URL,
                data={"username": "admin@exemplo.com", "password": "admin123"},
                headers={"content-type": "application/x-www-form-urlencoded"}
            )
            if response.status_code != 200:
                print(f"Erro no login (admin): {response.status_code} - {response.text}")
                return
            
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("Login com sucesso!")

        # 2. Participantes
        print("\n2. Buscando Participantes...")
        resp = await client.get(f"{BASE_URL}/participantes/", headers=headers)
        if resp.status_code == 200:
            parts = resp.json()
            print(f"Encontrados {len(parts)} participantes.")
            if len(parts) > 0:
                print(f"Exemplo: {parts[0]['nome']} ({parts[0]['tipo']})")
        else:
            print(f"Erro ao buscar participantes: {resp.status_code} - {resp.text}")

        # 3. Processos
        print("\n3. Buscando Processos...")
        resp = await client.get(f"{BASE_URL}/processos/", headers=headers)
        if resp.status_code == 200:
            procs = resp.json()
            print(f"Encontrados {len(procs)} processos.")
            if len(procs) > 0:
                print(f"Exemplo: {procs[0]['numero']}: {procs[0].get('titulo_causa', 'Sem título')}")
                import json
                print(json.dumps(procs[0], indent=2, default=str))
        else:
            print(f"Erro ao buscar processos: {resp.status_code} - {resp.text}")

        # 4. Lançamentos
        print("\n4. Buscando Lançamentos...")
        resp = await client.get(f"{BASE_URL}/lancamentos/", headers=headers)
        if resp.status_code == 200:
            lancs = resp.json()
            print(f"Encontrados {len(lancs)} lançamentos.")
            if len(lancs) > 0:
                print(f"Exemplo: {lancs[0]['descricao']}: R$ {lancs[0]['valor']}")
        else:
            print(f"Erro ao buscar lançamentos: {resp.status_code} - {resp.text}")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(verify())
