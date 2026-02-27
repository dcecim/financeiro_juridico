
import uuid
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.lancamento import Lancamento
from app.models.enums import NaturezaLancamento, StatusLancamento, TipoLancamento

class FinanceiroService:
    @staticmethod
    def calcular_previsao_exito(valor_causa: Decimal, percentual: Decimal) -> Decimal:
        """
        Calcula o valor previsto de honorários de êxito.
        """
        if percentual < 0 or percentual > 100:
            raise ValueError("Percentual deve estar entre 0 e 100")
        
        return (valor_causa * (percentual / Decimal("100"))).quantize(Decimal("0.01"))

    @staticmethod
    async def atualizar_previsao_honorarios(
        db: AsyncSession, 
        processo_id: uuid.UUID, 
        valor_causa: Decimal, 
        percentual_exito: Decimal,
        cliente_id: uuid.UUID,
        numero_processo: str
    ):
        """
        Cria ou atualiza o lançamento de previsão de honorários para um processo.
        """
        if valor_causa is None or percentual_exito is None:
            return None

        valor_previsto = FinanceiroService.calcular_previsao_exito(valor_causa, percentual_exito)
        
        # Verificar se já existe um lançamento de previsão para este processo
        stmt = select(Lancamento).where(
            Lancamento.processo_id == processo_id,
            Lancamento.natureza == NaturezaLancamento.EXITO,
            Lancamento.status == StatusLancamento.AGUARDANDO_TRANSITO
        )
        result = await db.execute(stmt)
        lancamento = result.scalars().first()
        
        descricao_padrao = f"Previsão de Honorários - Processo {numero_processo}"

        if lancamento:
            # Atualizar existente
            lancamento.valor_previsto = valor_previsto
            lancamento.valor = valor_previsto # O valor principal também reflete a previsão
            # Se a descrição for genérica, atualizar para o padrão novo
            if "Previsão de Honorários" in lancamento.descricao:
                lancamento.descricao = descricao_padrao
            
            db.add(lancamento)
            await db.commit()
            await db.refresh(lancamento)
            return lancamento
        else:
            # Criar novo
            novo_lancamento = Lancamento(
                descricao=descricao_padrao,
                valor=valor_previsto,
                valor_previsto=valor_previsto,
                tipo=TipoLancamento.RECEITA,
                natureza=NaturezaLancamento.EXITO,
                status=StatusLancamento.AGUARDANDO_TRANSITO,
                processo_id=processo_id,
                participante_id=cliente_id,
                data_vencimento=None # Sem data definida
            )
            db.add(novo_lancamento)
            await db.commit()
            await db.refresh(novo_lancamento)
            return novo_lancamento
