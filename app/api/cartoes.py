
import uuid
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.cartao_credito import CartaoCredito
from app.schemas.cartao_credito import CartaoCreditoCreate, CartaoCreditoUpdate, CartaoCreditoPublic
from app.api.auth import get_current_user
from app.models.usuario import Usuario
from app.api.deps import RoleChecker

router = APIRouter(prefix="/cartoes", tags=["cartoes"])

@router.get("/", response_model=list[CartaoCreditoPublic], dependencies=[Depends(RoleChecker(["ADMIN", "ANALISTA"]))])
async def read_cartoes(
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = 0,
    limit: int = 100,
    current_user: Usuario = Depends(get_current_user)
):
    stmt = select(CartaoCredito).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("/", response_model=CartaoCreditoPublic, status_code=status.HTTP_201_CREATED, dependencies=[Depends(RoleChecker(["ADMIN", "ANALISTA"]))])
async def create_cartao(
    cartao: CartaoCreditoCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Usuario = Depends(get_current_user)
):
    db_cartao = CartaoCredito(**cartao.model_dump())
    db.add(db_cartao)
    await db.commit()
    await db.refresh(db_cartao)
    return db_cartao

@router.get("/{cartao_id}", response_model=CartaoCreditoPublic, dependencies=[Depends(RoleChecker(["ADMIN", "ANALISTA"]))])
async def read_cartao(
    cartao_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Usuario = Depends(get_current_user)
):
    stmt = select(CartaoCredito).where(CartaoCredito.id == cartao_id)
    result = await db.execute(stmt)
    cartao = result.scalars().first()
    if cartao is None:
        raise HTTPException(status_code=404, detail="Cartao not found")
    return cartao

@router.put("/{cartao_id}", response_model=CartaoCreditoPublic, dependencies=[Depends(RoleChecker(["ADMIN", "ANALISTA"]))])
async def update_cartao(
    cartao_id: uuid.UUID,
    cartao_in: CartaoCreditoUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Usuario = Depends(get_current_user)
):
    stmt = select(CartaoCredito).where(CartaoCredito.id == cartao_id)
    result = await db.execute(stmt)
    db_cartao = result.scalars().first()
    
    if db_cartao is None:
        raise HTTPException(status_code=404, detail="Cartao not found")
    
    update_data = cartao_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_cartao, field, value)
    
    await db.commit()
    await db.refresh(db_cartao)
    return db_cartao

@router.delete("/{cartao_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(RoleChecker(["ADMIN", "ANALISTA"]))])
async def delete_cartao(
    cartao_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Usuario = Depends(get_current_user)
):
    stmt = select(CartaoCredito).where(CartaoCredito.id == cartao_id)
    result = await db.execute(stmt)
    db_cartao = result.scalars().first()
    
    if db_cartao is None:
        raise HTTPException(status_code=404, detail="Cartao not found")
    
    await db.delete(db_cartao)
    await db.commit()
