
import uuid
from decimal import Decimal
from pydantic import BaseModel

class CartaoCreditoBase(BaseModel):
    nome: str
    dia_fechamento: int
    dia_vencimento: int
    limite: Decimal

class CartaoCreditoCreate(CartaoCreditoBase):
    pass

class CartaoCreditoUpdate(BaseModel):
    nome: str | None = None
    dia_fechamento: int | None = None
    dia_vencimento: int | None = None
    limite: Decimal | None = None

class CartaoCreditoPublic(CartaoCreditoBase):
    id: uuid.UUID
    
    class Config:
        from_attributes = True
