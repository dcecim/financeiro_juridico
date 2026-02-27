
from datetime import timedelta
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.lancamento import Lancamento, StatusLancamento
from app.schemas.ofx import OfxTransactionSchema, ConciliacaoResult

class ConciliacaoService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def processar_ofx(self, transacoes: list[OfxTransactionSchema]) -> list[ConciliacaoResult]:
        resultados = []
        
        for tx in transacoes:
            # Busca lançamentos pendentes próximos à data (+/- 3 dias)
            data_min = tx.data - timedelta(days=3)
            data_max = tx.data + timedelta(days=3)
            
            stmt = select(Lancamento).where(
                and_(
                    Lancamento.status == StatusLancamento.PENDENTE,
                    Lancamento.data_vencimento >= data_min,
                    Lancamento.data_vencimento <= data_max
                )
            )
            
            result = await self.db.execute(stmt)
            candidatos = result.scalars().all()
            
            match_encontrado = None
            melhor_candidato_parcial = None
            menor_diferenca_percentual = Decimal("100") # Inicializa com 100%

            # Primeiro passo: procurar correspondência exata
            # Compara valores absolutos para evitar problemas com sinais (crédito/débito)
            valor_tx_abs = abs(tx.valor)
            
            for lancamento in candidatos:
                if abs(lancamento.valor) == valor_tx_abs:
                    match_encontrado = ConciliacaoResult(
                        ofx_id=tx.id,
                        lancamento_id=str(lancamento.id),
                        tipo_match="EXACT",
                        mensagem="Correspondência exata encontrada."
                    )
                    break
            
            # Segundo passo: se não houver exata, procurar melhor parcial
            if not match_encontrado:
                for lancamento in candidatos:
                    valor_lanc_abs = abs(lancamento.valor)
                    diferenca = abs(valor_lanc_abs - valor_tx_abs)
                    
                    # Evita divisão por zero
                    if valor_lanc_abs == 0:
                        continue
                        
                    percentual = (diferenca / valor_lanc_abs) * 100
                    
                    if percentual < 10:
                        # Mantém o candidato com a menor diferença percentual
                        if percentual < menor_diferenca_percentual:
                            menor_diferenca_percentual = percentual
                            melhor_candidato_parcial = (lancamento, diferenca)

                if melhor_candidato_parcial:
                    lancamento, diferenca = melhor_candidato_parcial
                    match_encontrado = ConciliacaoResult(
                        ofx_id=tx.id,
                        lancamento_id=str(lancamento.id),
                        tipo_match="PARTIAL",
                        valor_taxa_sugerida=diferenca,
                        mensagem=f"Diferença de {menor_diferenca_percentual:.2f}% detectada. Sugestão de lançamento de taxa/imposto."
                    )

            if match_encontrado:
                resultados.append(match_encontrado)
            else:
                resultados.append(ConciliacaoResult(
                    ofx_id=tx.id,
                    tipo_match="NONE",
                    mensagem="Nenhum lançamento correspondente encontrado."
                ))
                
        return resultados
