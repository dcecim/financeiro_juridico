
import uuid
from decimal import Decimal
from pydantic import BaseModel
from app.models.enums import StatusProcesso
from app.schemas.participante import ParticipantePublic

class ProcessoBase(BaseModel):
    numero: str
    numero_cnj: str | None = None
    titulo_causa: str | None = None
    descricao: str | None = None
    
    # Campos Financeiros
    percentual_exito: Decimal | None = None
    valor_pro_labore: Decimal | None = None
    valor_causa_atualizado: Decimal | None = None
    valor_causa_estimado: Decimal | None = None
    
    status: StatusProcesso = StatusProcesso.ATIVO
    
    cliente_id: uuid.UUID

class ProcessoCreate(ProcessoBase):
    pass

class ProcessoUpdate(BaseModel):
    numero: str | None = None
    numero_cnj: str | None = None
    titulo_causa: str | None = None
    descricao: str | None = None
    
    percentual_exito: Decimal | None = None
    valor_pro_labore: Decimal | None = None
    valor_causa_atualizado: Decimal | None = None
    valor_causa_estimado: Decimal | None = None
    
    status: StatusProcesso | None = None
    
    cliente_id: uuid.UUID | None = None

class ProcessoPublic(ProcessoBase):
    id: uuid.UUID
    cliente: ParticipantePublic | None = None
    
    class Config:
        from_attributes = True
