
from decimal import Decimal
from datetime import date
from pydantic import BaseModel

class OfxTransactionSchema(BaseModel):
    id: str
    data: date
    valor: Decimal
    descricao: str

class ConciliacaoResult(BaseModel):
    ofx_id: str
    lancamento_id: str | None = None
    tipo_match: str  # EXACT, PARTIAL, NONE
    valor_taxa_sugerida: Decimal | None = None
    mensagem: str
