
import uuid
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.processo import Processo
from app.schemas.processo import ProcessoCreate, ProcessoUpdate, ProcessoPublic
from app.api.auth import get_current_user
from app.models.usuario import Usuario
from app.services.financeiro import FinanceiroService
from app.api.deps import RoleChecker

from sqlalchemy.orm import selectinload

router = APIRouter(prefix="/processos", tags=["processos"])

@router.get("/", response_model=list[ProcessoPublic], dependencies=[Depends(RoleChecker(["ADMIN", "ANALISTA", "ADVOGADO"]))])
async def read_processos(
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = 0,
    limit: int = 1000,
    current_user: Usuario = Depends(get_current_user)
):
    stmt = select(Processo).options(selectinload(Processo.cliente)).order_by(Processo.numero.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("/", response_model=ProcessoPublic, status_code=status.HTTP_201_CREATED, dependencies=[Depends(RoleChecker(["ADMIN", "ANALISTA", "ADVOGADO"]))])
async def create_processo(
    processo: ProcessoCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Usuario = Depends(get_current_user)
):
    # Check for existing numero
    stmt = select(Processo).where(Processo.numero == processo.numero)
    result = await db.execute(stmt)
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Processo number already registered"
        )
    
    db_processo = Processo(**processo.model_dump())
    db.add(db_processo)
    await db.commit()
    
    # Gerar previsão financeira se aplicável
    valor_base = db_processo.valor_causa_atualizado or db_processo.valor_causa_estimado
    if valor_base and db_processo.percentual_exito:
        await FinanceiroService.atualizar_previsao_honorarios(
            db, 
            db_processo.id, 
            valor_base, 
            db_processo.percentual_exito,
            db_processo.cliente_id,
            db_processo.numero
        )
    
    # Refresh and load relationship
    # refresh() reloads attributes, but for relationship we need to query or use refresh with loading options?
    # SQLAlchemy refresh doesn't support options directly in async?
    # Better to select it again with options.
    
    stmt = select(Processo).options(selectinload(Processo.cliente)).where(Processo.id == db_processo.id)
    result = await db.execute(stmt)
    return result.scalars().first()

@router.get("/{processo_id}", response_model=ProcessoPublic)
async def read_processo(
    processo_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Usuario = Depends(get_current_user)
):
    stmt = select(Processo).options(selectinload(Processo.cliente)).where(Processo.id == processo_id)
    result = await db.execute(stmt)
    processo = result.scalars().first()
    if processo is None:
        raise HTTPException(status_code=404, detail="Processo not found")
    return processo

@router.put("/{processo_id}", response_model=ProcessoPublic, dependencies=[Depends(RoleChecker(["ADMIN", "ANALISTA", "ADVOGADO"]))])
async def update_processo(
    processo_id: uuid.UUID,
    processo_in: ProcessoUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Usuario = Depends(get_current_user)
):
    stmt = select(Processo).options(selectinload(Processo.cliente)).where(Processo.id == processo_id)
    result = await db.execute(stmt)
    db_processo = result.scalars().first()
    
    if db_processo is None:
        raise HTTPException(status_code=404, detail="Processo not found")
    
    update_data = processo_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_processo, field, value)
    
    await db.commit()
    
    # Atualizar previsão financeira se houve mudança em valores relevantes
    if any(k in update_data for k in ["valor_causa_atualizado", "valor_causa_estimado", "percentual_exito"]):
        valor_base = db_processo.valor_causa_atualizado or db_processo.valor_causa_estimado
        if valor_base and db_processo.percentual_exito:
            await FinanceiroService.atualizar_previsao_honorarios(
                db, 
                db_processo.id, 
                valor_base, 
                db_processo.percentual_exito,
                db_processo.cliente_id,
                db_processo.numero
            )
            
    # No need to refresh if we just updated simple fields, but if we updated foreign keys, we might need to reload relationship.
    # To be safe, reload.
    
    stmt = select(Processo).options(selectinload(Processo.cliente)).where(Processo.id == processo_id)
    result = await db.execute(stmt)
    return result.scalars().first()

@router.delete("/{processo_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(RoleChecker(["ADMIN", "ANALISTA", "ADVOGADO"]))])
async def delete_processo(
    processo_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Usuario = Depends(get_current_user)
):
    stmt = select(Processo).where(Processo.id == processo_id)
    result = await db.execute(stmt)
    db_processo = result.scalars().first()
    
    if db_processo is None:
        raise HTTPException(status_code=404, detail="Processo not found")
    
    await db.delete(db_processo)
    await db.commit()
