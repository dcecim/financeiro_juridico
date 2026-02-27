
import uuid
from pydantic import BaseModel
from app.models.enums import TipoLancamento

class CentroCustoBase(BaseModel):
    nome: str
    codigo: str | None = None
    descricao: str | None = None
    tipo: TipoLancamento | None = None
    parent_id: uuid.UUID | None = None

class CentroCustoCreate(CentroCustoBase):
    pass

class CentroCustoUpdate(BaseModel):
    nome: str | None = None
    codigo: str | None = None
    descricao: str | None = None
    tipo: TipoLancamento | None = None
    parent_id: uuid.UUID | None = None

class CentroCustoPublic(CentroCustoBase):
    id: uuid.UUID
    
    class Config:
        from_attributes = True
