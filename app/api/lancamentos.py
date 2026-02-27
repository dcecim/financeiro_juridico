
import uuid
from typing import Annotated
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.lancamento import Lancamento
from app.models.processo import Processo
from app.models.enums import StatusLancamento, TipoLancamento, NaturezaLancamento
from app.schemas.lancamento import LancamentoCreate, LancamentoUpdate, LancamentoPublic
from app.models.usuario import Usuario
from app.services.lancamento import LancamentoService
from app.api.deps import RoleChecker, get_current_user

router = APIRouter(prefix="/lancamentos", tags=["lancamentos"])

@router.get("/", response_model=list[LancamentoPublic], dependencies=[Depends(RoleChecker(["ADMIN", "ANALISTA", "ADVOGADO"]))])
async def read_lancamentos(
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = 0,
    limit: int = 100,
    data_inicio: date | None = None,
    data_fim: date | None = None,
    status: StatusLancamento | None = None,
    tipo: TipoLancamento | None = None,
    natureza: NaturezaLancamento | None = None,
    centro_custo_id: uuid.UUID | None = None,
    current_user: Usuario = Depends(get_current_user)
):
    query = select(Lancamento).options(
        selectinload(Lancamento.participante),
        selectinload(Lancamento.processo).selectinload(Processo.cliente),
        selectinload(Lancamento.cartao),
        selectinload(Lancamento.centro_custo)
    )
    
    if data_inicio:
        query = query.where(Lancamento.data_vencimento >= data_inicio)
    if data_fim:
        query = query.where(Lancamento.data_vencimento <= data_fim)
    if status:
        query = query.where(Lancamento.status == status)
    if tipo:
        query = query.where(Lancamento.tipo == tipo)
    if natureza:
        query = query.where(Lancamento.natureza == natureza)
    if centro_custo_id:
        query = query.where(Lancamento.centro_custo_id == centro_custo_id)
        
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/", response_model=LancamentoPublic, status_code=status.HTTP_201_CREATED, dependencies=[Depends(RoleChecker(["ADMIN", "ANALISTA"]))])
async def create_lancamento(
    lancamento: LancamentoCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Usuario = Depends(get_current_user)
):
    service = LancamentoService(db)
    return await service.create(lancamento)

@router.get("/{lancamento_id}", response_model=LancamentoPublic)
async def read_lancamento(
    lancamento_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Usuario = Depends(get_current_user)
):
    stmt = select(Lancamento).options(
        selectinload(Lancamento.participante),
        selectinload(Lancamento.processo).selectinload(Processo.cliente),
        selectinload(Lancamento.cartao),
        selectinload(Lancamento.centro_custo)
    ).where(Lancamento.id == lancamento_id)
    result = await db.execute(stmt)
    lancamento = result.scalars().first()
    if lancamento is None:
        raise HTTPException(status_code=404, detail="Lancamento not found")
    return lancamento

@router.put("/{lancamento_id}", response_model=LancamentoPublic, dependencies=[Depends(RoleChecker(["ADMIN", "ANALISTA"]))])
async def update_lancamento(
    lancamento_id: uuid.UUID,
    lancamento_in: LancamentoUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Usuario = Depends(get_current_user)
):
    service = LancamentoService(db)
    updated_lancamento = await service.update(lancamento_id, lancamento_in)
    
    if updated_lancamento is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lancamento not found")
        
    return updated_lancamento

@router.delete("/{lancamento_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(RoleChecker(["ADMIN", "ANALISTA"]))])
async def delete_lancamento(
    lancamento_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Usuario = Depends(get_current_user)
):
    stmt = select(Lancamento).where(Lancamento.id == lancamento_id)
    result = await db.execute(stmt)
    db_lancamento = result.scalars().first()
    
    if db_lancamento is None:
        raise HTTPException(status_code=404, detail="Lancamento not found")
    
    await db.delete(db_lancamento)
    await db.commit()
