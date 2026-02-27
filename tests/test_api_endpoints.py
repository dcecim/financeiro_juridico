
import pytest
import uuid
from decimal import Decimal
from app.api.auth import get_current_user
from app.models.usuario import Usuario

# Mock user for authentication bypass
async def mock_get_current_user():
    return Usuario(id=uuid.uuid4(), email="test@example.com", role="ADMIN")

@pytest.fixture
def override_auth(client):
    from app.main import app
    app.dependency_overrides[get_current_user] = mock_get_current_user
    yield
    app.dependency_overrides.pop(get_current_user, None)

@pytest.mark.asyncio
async def test_create_participante(client, override_auth):
    response = await client.post("/participantes/", json={
        "nome": "Cliente Teste API",
        "documento": "99988877766",
        "tipo": "CLIENTE"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["nome"] == "Cliente Teste API"
    assert "id" in data
    
    # Test duplicate document
    response = await client.post("/participantes/", json={
        "nome": "Cliente Duplicate",
        "documento": "99988877766",
        "tipo": "CLIENTE"
    })
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_create_processo(client, override_auth):
    # Create client first
    resp_cliente = await client.post("/participantes/", json={
        "nome": "Cliente Processo",
        "documento": "11122233344",
        "tipo": "CLIENTE"
    })
    cliente_id = resp_cliente.json()["id"]
    
    response = await client.post("/processos/", json={
        "numero": "1234567-89.2024.8.26.0000",
        "cliente_id": cliente_id,
        "descricao": "Processo Teste API"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["numero"] == "1234567-89.2024.8.26.0000"
    assert data["cliente_id"] == cliente_id

@pytest.mark.asyncio
async def test_create_lancamento(client, override_auth):
    # Create client
    resp_cliente = await client.post("/participantes/", json={
        "nome": "Cliente Lancamento",
        "documento": "55566677788",
        "tipo": "CLIENTE"
    })
    cliente_id = resp_cliente.json()["id"]
    
    response = await client.post("/lancamentos/", json={
        "descricao": "Honorários Teste",
        "valor": 1500.50,
        "tipo": "RECEITA",
        "natureza": "PONTUAL",
        "participante_id": cliente_id
    })
    assert response.status_code == 201
    data = response.json()
    assert data["valor"] == "1500.50"
    assert data["participante"]["id"] == cliente_id

@pytest.mark.asyncio
async def test_conciliacao_endpoint(client, override_auth):
    # Setup data
    resp_cliente = await client.post("/participantes/", json={
        "nome": "Cliente Conciliacao",
        "documento": "99900099900",
        "tipo": "CLIENTE"
    })
    cliente_id = resp_cliente.json()["id"]
    
    # Create pending lancamento
    await client.post("/lancamentos/", json={
        "descricao": "Mensalidade",
        "valor": 500.00,
        "tipo": "RECEITA",
        "natureza": "FIXO",
        "status": "PENDENTE",
        "data_vencimento": "2024-01-15",
        "participante_id": cliente_id
    })
    
    # Call conciliation endpoint
    response = await client.post("/conciliacao/processar", json=[{
        "id": "ofx-1",
        "data": "2024-01-15",
        "valor": 500.00,
        "descricao": "Deposito"
    }])
    
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["tipo_match"] == "EXACT"
