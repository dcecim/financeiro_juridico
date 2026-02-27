
import uuid
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.lancamento import Lancamento
from app.models.processo import Processo
from app.models.enums import TipoLancamento, NaturezaLancamento, StatusLancamento
from app.schemas.lancamento import LancamentoCreate, LancamentoUpdate

class LancamentoService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, lancamento_in: LancamentoCreate) -> Lancamento:
        db_lancamento = Lancamento(**lancamento_in.model_dump())
        self.db.add(db_lancamento)
        await self.db.commit()
        await self.db.refresh(db_lancamento)
        
        # Verificar se é reembolsável
        if db_lancamento.reembolsavel and db_lancamento.tipo == TipoLancamento.DESPESA:
            await self._gerar_reembolso(db_lancamento)
            
        # Reload with relationships
        stmt = select(Lancamento).options(
            selectinload(Lancamento.participante),
            selectinload(Lancamento.processo),
            selectinload(Lancamento.cartao),
            selectinload(Lancamento.centro_custo)
        ).where(Lancamento.id == db_lancamento.id)
        
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def update(self, lancamento_id: uuid.UUID, lancamento_in: LancamentoUpdate) -> Lancamento | None:
        stmt = select(Lancamento).where(Lancamento.id == lancamento_id)
        result = await self.db.execute(stmt)
        db_lancamento = result.scalars().first()
        
        if db_lancamento is None:
            return None
        
        update_data = lancamento_in.model_dump(exclude_unset=True)
        
        # Check if reembolso status changed
        was_reembolsavel = db_lancamento.reembolsavel
        
        for field, value in update_data.items():
            setattr(db_lancamento, field, value)
        
        await self.db.commit()
        await self.db.refresh(db_lancamento)
        
        # Se tornou reembolsável na edição
        if not was_reembolsavel and db_lancamento.reembolsavel and db_lancamento.tipo == TipoLancamento.DESPESA:
             await self._gerar_reembolso(db_lancamento)
        
        # Se já era reembolsável e teve valor alterado, atualizar o reembolso se estiver pendente
        if was_reembolsavel and db_lancamento.reembolsavel and 'valor' in update_data:
             stmt_reembolso = select(Lancamento).where(Lancamento.lancamento_pai_id == db_lancamento.id)
             result_reembolso = await self.db.execute(stmt_reembolso)
             reembolso_existente = result_reembolso.scalars().first()
             
             if reembolso_existente and reembolso_existente.status == StatusLancamento.PENDENTE:
                 reembolso_existente.valor = db_lancamento.valor
                 self.db.add(reembolso_existente)
                 await self.db.commit()

        # Reload with relationships
        stmt = select(Lancamento).options(
            selectinload(Lancamento.participante),
            selectinload(Lancamento.processo),
            selectinload(Lancamento.cartao),
            selectinload(Lancamento.centro_custo)
        ).where(Lancamento.id == lancamento_id)
        
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def _gerar_reembolso(self, despesa: Lancamento):
        """
        Gera um lançamento de receita (Reembolso) correspondente à despesa.
        """
        # Verificar se já existe reembolso gerado para evitar duplicidade
        stmt = select(Lancamento).where(Lancamento.lancamento_pai_id == despesa.id)
        result = await self.db.execute(stmt)
        existente = result.scalars().first()
        
        if existente:
            return

        cliente_id = None
        
        # Tentar obter cliente via Processo
        if despesa.processo_id:
            stmt_proc = select(Processo).where(Processo.id == despesa.processo_id)
            result_proc = await self.db.execute(stmt_proc)
            processo = result_proc.scalars().first()
            if processo:
                cliente_id = processo.cliente_id
        
        if not cliente_id:
            # Se não tiver processo vinculado, não conseguimos determinar o cliente para reembolso
            # Poderíamos tentar usar o participante da despesa se fosse o caso, mas geralmente é o fornecedor.
            return

        reembolso = Lancamento(
            descricao=f"Reembolso - {despesa.descricao}",
            valor=despesa.valor,
            tipo=TipoLancamento.RECEITA,
            natureza=NaturezaLancamento.PONTUAL,
            status=StatusLancamento.PENDENTE,
            participante_id=cliente_id,
            processo_id=despesa.processo_id,
            lancamento_pai_id=despesa.id,
            centro_custo_id=despesa.centro_custo_id,
            data_vencimento=despesa.data_vencimento
        )
        
        self.db.add(reembolso)
        await self.db.commit()
