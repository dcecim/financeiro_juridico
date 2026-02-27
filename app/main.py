
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.core.audit import setup_audit_listeners

# Setup audit listeners for Session (underlying AsyncSession)
setup_audit_listeners(Session)

from app.api import auth
from app.api import participantes
from app.api import processos
from app.api import lancamentos
from app.api import cartoes
from app.api import centros_custo
from app.api import conciliacao
from app.api import dashboard

app = FastAPI(title="Sistema Financeiro Jurídico")

# Configuração de CORS
origins = [
    "http://localhost:5173",  # Frontend Vite
    "http://localhost:3000",  # React padrão (caso use)
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(participantes.router)
app.include_router(processos.router)
app.include_router(lancamentos.router)
app.include_router(cartoes.router)
app.include_router(centros_custo.router)
app.include_router(conciliacao.router)
app.include_router(dashboard.router)

@app.get("/")
async def root():
    return {"message": "Sistema Financeiro Jurídico API"}
