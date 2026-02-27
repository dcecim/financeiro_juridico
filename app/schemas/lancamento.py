
import uuid
from datetime import date
from decimal import Decimal
from pydantic import BaseModel, Field
from app.models.enums import TipoLancamento, NaturezaLancamento, StatusLancamento
from app.schemas.participante import ParticipantePublic
from app.schemas.processo import ProcessoPublic
from app.schemas.cartao_credito import CartaoCreditoPublic
from app.schemas.centro_custo import CentroCustoPublic

class LancamentoBase(BaseModel):
    descricao: str
    valor: Decimal = Field(..., max_digits=10, decimal_places=2)
    valor_realizado: Decimal | None = None
    valor_previsto: Decimal | None = None
    data_vencimento: date | None = None
    data_pagamento: date | None = None
    tipo: TipoLancamento
    natureza: NaturezaLancamento
    status: StatusLancamento = StatusLancamento.PENDENTE
    participante_id: uuid.UUID
    processo_id: uuid.UUID | None = None
    cartao_id: uuid.UUID | None = None
    centro_custo_id: uuid.UUID
    
    reembolsavel: bool = False
    lancamento_pai_id: uuid.UUID | None = None

class LancamentoCreate(LancamentoBase):
    pass

class LancamentoUpdate(BaseModel):
    descricao: str | None = None
    valor: Decimal | None = None
    valor_realizado: Decimal | None = None
    valor_previsto: Decimal | None = None
    data_vencimento: date | None = None
    data_pagamento: date | None = None
    tipo: TipoLancamento | None = None
    natureza: NaturezaLancamento | None = None
    status: StatusLancamento | None = None
    participante_id: uuid.UUID | None = None
    processo_id: uuid.UUID | None = None
    cartao_id: uuid.UUID | None = None
    centro_custo_id: uuid.UUID | None = None
    reembolsavel: bool | None = None
    lancamento_pai_id: uuid.UUID | None = None

class LancamentoPublic(LancamentoBase):
    id: uuid.UUID
    participante: ParticipantePublic | None = None
    processo: ProcessoPublic | None = None
    cartao: CartaoCreditoPublic | None = None
    centro_custo: CentroCustoPublic | None = None
    
    class Config:
        from_attributes = True
