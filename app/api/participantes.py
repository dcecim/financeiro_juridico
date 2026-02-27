
import uuid
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.participante import Participante
from app.schemas.participante import ParticipanteCreate, ParticipanteUpdate, ParticipantePublic
from app.api.auth import get_current_user
from app.models.usuario import Usuario
from app.api.deps import RoleChecker

router = APIRouter(prefix="/participantes", tags=["participantes"])

@router.get("/", response_model=list[ParticipantePublic], dependencies=[Depends(RoleChecker(["ADMIN", "ANALISTA", "ADVOGADO"]))])
async def read_participantes(
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = 0,
    limit: int = 100,
    current_user: Usuario = Depends(get_current_user)
):
    stmt = select(Participante).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("/", response_model=ParticipantePublic, status_code=status.HTTP_201_CREATED, dependencies=[Depends(RoleChecker(["ADMIN", "ANALISTA", "ADVOGADO"]))])
async def create_participante(
    participante: ParticipanteCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Usuario = Depends(get_current_user)
):
    # Check for existing document
    stmt = select(Participante).where(Participante.documento == participante.documento)
    result = await db.execute(stmt)
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Documento already registered"
        )
    
    db_participante = Participante(**participante.model_dump())
    db.add(db_participante)
    await db.commit()
    await db.refresh(db_participante)
    return db_participante

@router.get("/{participante_id}", response_model=ParticipantePublic, dependencies=[Depends(RoleChecker(["ADMIN", "ANALISTA", "ADVOGADO"]))])
async def read_participante(
    participante_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Usuario = Depends(get_current_user)
):
    stmt = select(Participante).where(Participante.id == participante_id)
    result = await db.execute(stmt)
    participante = result.scalars().first()
    if participante is None:
        raise HTTPException(status_code=404, detail="Participante not found")
    return participante

@router.put("/{participante_id}", response_model=ParticipantePublic, dependencies=[Depends(RoleChecker(["ADMIN", "ANALISTA", "ADVOGADO"]))])
async def update_participante(
    participante_id: uuid.UUID,
    participante_in: ParticipanteUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Usuario = Depends(get_current_user)
):
    stmt = select(Participante).where(Participante.id == participante_id)
    result = await db.execute(stmt)
    db_participante = result.scalars().first()
    
    if db_participante is None:
        raise HTTPException(status_code=404, detail="Participante not found")
    
    update_data = participante_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_participante, field, value)
    
    await db.commit()
    await db.refresh(db_participante)
    return db_participante

@router.delete("/{participante_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(RoleChecker(["ADMIN", "ANALISTA", "ADVOGADO"]))])
async def delete_participante(
    participante_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Usuario = Depends(get_current_user)
):
    stmt = select(Participante).where(Participante.id == participante_id)
    result = await db.execute(stmt)
    db_participante = result.scalars().first()
    
    if db_participante is None:
        raise HTTPException(status_code=404, detail="Participante not found")
    
    await db.delete(db_participante)
    await db.commit()
