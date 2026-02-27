
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.conciliacao import ConciliacaoService
from app.services.ofx_parser import OfxParserService
from app.schemas.ofx import OfxTransactionSchema, ConciliacaoResult
from app.api.auth import get_current_user
from app.models.usuario import Usuario
from app.api.deps import RoleChecker

router = APIRouter(prefix="/conciliacao", tags=["conciliacao"])

@router.post("/processar", response_model=list[ConciliacaoResult], dependencies=[Depends(RoleChecker(["ADMIN", "ANALISTA"]))])
async def processar_conciliacao(
    transacoes: list[OfxTransactionSchema],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Usuario = Depends(get_current_user)
):
    service = ConciliacaoService(db)
    resultados = await service.processar_ofx(transacoes)
    return resultados

@router.post("/upload", response_model=list[ConciliacaoResult], dependencies=[Depends(RoleChecker(["ADMIN", "ANALISTA"]))])
async def upload_ofx(
    file: Annotated[UploadFile, File(...)],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Usuario = Depends(get_current_user)
):
    """
    Recebe um arquivo .ofx, extrai as transações e realiza a conciliação.
    """
    if not file.filename.lower().endswith('.ofx'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Arquivo inválido. Deve ser um arquivo .ofx"
        )
    
    try:
        content = await file.read()
        transacoes = OfxParserService.parse_file(content)
        
        service = ConciliacaoService(db)
        resultados = await service.processar_ofx(transacoes)
        return resultados
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao processar arquivo OFX: {str(e)}"
        )
