
import uuid
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from app.core.database import get_db
from app.models.centro_custo import CentroCusto
from app.schemas.centro_custo import CentroCustoCreate, CentroCustoUpdate, CentroCustoPublic
from app.api.auth import get_current_user
from app.models.usuario import Usuario
from app.api.deps import RoleChecker
from app.models.enums import TipoLancamento

router = APIRouter(prefix="/centros-custo", tags=["centros-custo"])

async def get_next_code(db: AsyncSession) -> str:
    """Calculates the next available code (MAX + 1)."""
    # Cast to integer for correct numerical sorting, then get max
    # Note: We assume codes are numeric strings. If not, this might need adjustment.
    # Since we control generation, they should be '000000'.
    
    # Simple MAX on string works if length is constant, but casting is safer for '9' vs '10'
    # However, user specified '000001', so string sort works too.
    stmt = select(func.max(CentroCusto.codigo))
    result = await db.execute(stmt)
    max_code = result.scalar()
    
    if max_code:
        try:
            next_val = int(max_code) + 1
            return f"{next_val:06d}"
        except ValueError:
            # Fallback if non-numeric code exists
            return "000001"
    else:
        return "000001"

@router.get("/next-code", response_model=str)
async def get_next_centro_custo_code(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Usuario = Depends(get_current_user)
):
    return await get_next_code(db)

@router.get("/", response_model=list[CentroCustoPublic], dependencies=[Depends(RoleChecker(["ADMIN", "ANALISTA"]))])
async def read_centros_custo(
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = 0,
    limit: int = 100,
    tipo: TipoLancamento | None = None,
    current_user: Usuario = Depends(get_current_user)
):
    stmt = select(CentroCusto)
    if tipo:
        stmt = stmt.where(CentroCusto.tipo == tipo)
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("/", response_model=CentroCustoPublic, status_code=status.HTTP_201_CREATED, dependencies=[Depends(RoleChecker(["ADMIN", "ANALISTA"]))])
async def create_centro_custo(
    centro_custo: CentroCustoCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Usuario = Depends(get_current_user)
):
    # Check for existing name
    stmt = select(CentroCusto).where(CentroCusto.nome == centro_custo.nome)
    result = await db.execute(stmt)
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Centro de Custo name already registered"
        )
    
    # Auto-generate code if not provided
    if not centro_custo.codigo:
        centro_custo.codigo = await get_next_code(db)
        
        # Simple retry logic for race conditions (optimistic locking)
        for _ in range(3):
            stmt = select(CentroCusto).where(CentroCusto.codigo == centro_custo.codigo)
            result = await db.execute(stmt)
            if not result.scalars().first():
                break
            # If exists, increment and try again
            try:
                next_val = int(centro_custo.codigo) + 1
                centro_custo.codigo = f"{next_val:06d}"
            except:
                break # Should not happen if we generated it

    db_centro_custo = CentroCusto(**centro_custo.model_dump())
    db.add(db_centro_custo)
    try:
        await db.commit()
        await db.refresh(db_centro_custo)
    except Exception as e:
        await db.rollback()
        # Check for unique constraint violation explicitly if needed, but generic error is ok for now
        raise HTTPException(status_code=400, detail=f"Error creating Centro de Custo: {str(e)}")
        
    return db_centro_custo

@router.get("/{centro_custo_id}", response_model=CentroCustoPublic)
async def read_centro_custo(
    centro_custo_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Usuario = Depends(get_current_user)
):
    stmt = select(CentroCusto).where(CentroCusto.id == centro_custo_id)
    result = await db.execute(stmt)
    centro_custo = result.scalars().first()
    if centro_custo is None:
        raise HTTPException(status_code=404, detail="Centro de Custo not found")
    return centro_custo

@router.put("/{centro_custo_id}", response_model=CentroCustoPublic)
async def update_centro_custo(
    centro_custo_id: uuid.UUID,
    centro_custo_in: CentroCustoUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Usuario = Depends(get_current_user)
):
    stmt = select(CentroCusto).where(CentroCusto.id == centro_custo_id)
    result = await db.execute(stmt)
    db_centro_custo = result.scalars().first()
    
    if db_centro_custo is None:
        raise HTTPException(status_code=404, detail="Centro de Custo not found")
    
    update_data = centro_custo_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_centro_custo, field, value)
    
    await db.commit()
    await db.refresh(db_centro_custo)
    return db_centro_custo

@router.delete("/{centro_custo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_centro_custo(
    centro_custo_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Usuario = Depends(get_current_user)
):
    stmt = select(CentroCusto).where(CentroCusto.id == centro_custo_id)
    result = await db.execute(stmt)
    db_centro_custo = result.scalars().first()
    
    if db_centro_custo is None:
        raise HTTPException(status_code=404, detail="Centro de Custo not found")
    
    await db.delete(db_centro_custo)
    await db.commit()
