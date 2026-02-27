
import uuid
from typing import Annotated
from datetime import date, timedelta
from decimal import Decimal
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case, and_, cast, Date
from app.core.database import get_db
from app.models.lancamento import Lancamento
from app.models.processo import Processo
from app.models.centro_custo import CentroCusto
from app.models.enums import StatusProcesso, TipoLancamento, NaturezaLancamento, StatusLancamento
from app.api.auth import get_current_user
from app.models.usuario import Usuario
from app.api.deps import RoleChecker
from pydantic import BaseModel

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

class DashboardCards(BaseModel):
    saldo_atual: float
    burn_rate: float
    ticket_medio_exito: float
    pipeline_recebiveis: float

class CashFlowPoint(BaseModel):
    date: str
    entradas: float
    saidas: float

class ProjectedFlowPoint(BaseModel):
    date: str
    realizado: float
    projetado: float

class ExpenseCategory(BaseModel):
    name: str
    value: float

class DashboardData(BaseModel):
    cards: DashboardCards
    cash_flow: list[CashFlowPoint]
    projected_flow: list[ProjectedFlowPoint]
    expenses_by_category: list[ExpenseCategory]

@router.get("/analytics", response_model=DashboardData, dependencies=[Depends(RoleChecker(["ADMIN", "ANALISTA"]))])
async def get_dashboard_analytics(
    db: Annotated[AsyncSession, Depends(get_db)],
    data_inicio: date | None = None,
    data_fim: date | None = None,
    status_processo: StatusProcesso | None = None,
    centro_custo_id: uuid.UUID | None = None,
    data_inclusao: date | None = None,
    current_user: Usuario = Depends(get_current_user)
):
    # Default to last 30 days if not provided
    if not data_inicio and not data_inclusao:
        data_inicio = date.today() - timedelta(days=30)
    if not data_fim and not data_inclusao:
        data_fim = date.today()

    # --- Base Queries ---
    
    # Lancamentos Filter
    lanc_filter = [
        Lancamento.status != StatusLancamento.CANCELADO
    ]
    
    if data_inclusao:
        lanc_filter.append(cast(Lancamento.criado_em, Date) == data_inclusao)
    elif data_inicio and data_fim:
        lanc_filter.append(Lancamento.data_vencimento >= data_inicio)
        lanc_filter.append(Lancamento.data_vencimento <= data_fim)

    if centro_custo_id:
        lanc_filter.append(Lancamento.centro_custo_id == centro_custo_id)
    
    if status_processo:
        lanc_filter.append(Lancamento.processo.has(Processo.status == status_processo))

    # --- 1. Cards Calculation ---
    
    # Saldo: Sum(Receitas) - Sum(Despesas)
    stmt_saldo = select(
        func.sum(case((Lancamento.tipo == TipoLancamento.RECEITA, Lancamento.valor), else_=0)),
        func.sum(case((Lancamento.tipo == TipoLancamento.DESPESA, Lancamento.valor), else_=0))
    ).where(*lanc_filter)
    
    row_saldo = (await db.execute(stmt_saldo)).first()
    receitas_periodo = row_saldo[0] or Decimal(0)
    despesas_periodo = row_saldo[1] or Decimal(0)
    saldo_atual = float(receitas_periodo - despesas_periodo)

    # Burn Rate: Sum(Despesas where Natureza == FIXO)
    stmt_burn = select(func.sum(Lancamento.valor)).where(
        *lanc_filter,
        Lancamento.tipo == TipoLancamento.DESPESA,
        Lancamento.natureza == NaturezaLancamento.FIXO
    )
    burn_rate = float((await db.execute(stmt_burn)).scalar() or 0)

    # Ticket Médio de Êxito: Sum(Receitas Exito) / Count(Receitas Exito)
    stmt_ticket = select(
        func.sum(Lancamento.valor),
        func.count(Lancamento.id)
    ).where(
        *lanc_filter,
        Lancamento.tipo == TipoLancamento.RECEITA,
        Lancamento.natureza == NaturezaLancamento.EXITO
    )
    row_ticket = (await db.execute(stmt_ticket)).first()
    total_exito = row_ticket[0] or Decimal(0)
    count_exito = row_ticket[1] or 0
    ticket_medio = float(total_exito / count_exito) if count_exito > 0 else 0.0

    # Pipeline de Recebíveis (Incerteza/Êxito)
    pipeline_query = select(
        func.sum(Processo.valor_causa_estimado * Processo.percentual_exito / 100)
    ).where(Processo.status == StatusProcesso.ATIVO)
    
    if status_processo:
         pipeline_query = pipeline_query.where(Processo.status == status_processo)
         
    pipeline_recebiveis = float((await db.execute(pipeline_query)).scalar() or 0)

    # --- 2. Charts ---

    # Gráfico de Barras Empilhadas (Entradas vs. Saídas) per Day/Month
    stmt_timeline = select(
        Lancamento.data_vencimento,
        func.sum(case((Lancamento.tipo == TipoLancamento.RECEITA, Lancamento.valor), else_=0)).label("entradas"),
        func.sum(case((Lancamento.tipo == TipoLancamento.DESPESA, Lancamento.valor), else_=0)).label("saidas")
    ).where(*lanc_filter).group_by(Lancamento.data_vencimento).order_by(Lancamento.data_vencimento)
    
    timeline_rows = (await db.execute(stmt_timeline)).all()
    
    cash_flow_data = []
    projected_data = [] 
    
    cumulative_realized = 0.0
    
    for row in timeline_rows:
        dt = row.data_vencimento
        entradas = float(row.entradas or 0)
        saidas = float(row.saidas or 0)
        
        cash_flow_data.append(CashFlowPoint(
            date=dt.isoformat(),
            entradas=entradas,
            saidas=saidas
        ))
        
        net = entradas - saidas
        cumulative_realized += net
        
        projected_data.append(ProjectedFlowPoint(
            date=dt.isoformat(),
            realizado=cumulative_realized,
            projetado=cumulative_realized + pipeline_recebiveis
        ))

    # Gráfico de Rosca (Composição de Despesas)
    stmt_expenses = select(
        CentroCusto.nome,
        func.sum(Lancamento.valor)
    ).select_from(Lancamento).join(CentroCusto).where(
        *lanc_filter,
        Lancamento.tipo == TipoLancamento.DESPESA
    ).group_by(CentroCusto.nome)
    
    expense_rows = (await db.execute(stmt_expenses)).all()
    expenses_data = [
        ExpenseCategory(name=row[0], value=float(row[1]))
        for row in expense_rows
    ]

    return DashboardData(
        cards=DashboardCards(
            saldo_atual=saldo_atual,
            burn_rate=burn_rate,
            ticket_medio_exito=ticket_medio,
            pipeline_recebiveis=pipeline_recebiveis
        ),
        cash_flow=cash_flow_data,
        projected_flow=projected_data,
        expenses_by_category=expenses_data
    )
