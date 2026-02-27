
import uuid
from pydantic import BaseModel
from app.models.enums import TipoParticipante

class ParticipanteBase(BaseModel):
    nome: str
    documento: str
    tipo: TipoParticipante = TipoParticipante.CLIENTE
    email: str | None = None
    telefone: str | None = None

class ParticipanteCreate(ParticipanteBase):
    pass

class ParticipanteUpdate(BaseModel):
    nome: str | None = None
    documento: str | None = None
    tipo: TipoParticipante | None = None
    email: str | None = None
    telefone: str | None = None

class ParticipantePublic(ParticipanteBase):
    id: uuid.UUID
    
    class Config:
        from_attributes = True
