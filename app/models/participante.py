
import uuid
from sqlalchemy import String, Enum, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.enums import TipoParticipante

class Participante(Base):
    __tablename__ = "participantes"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome: Mapped[str] = mapped_column(String, index=True)
    documento: Mapped[str] = mapped_column(String, unique=True, index=True) # CPF/CNPJ
    tipo: Mapped[TipoParticipante] = mapped_column(Enum(TipoParticipante), default=TipoParticipante.CLIENTE)
    email: Mapped[str | None] = mapped_column(String, nullable=True)
    telefone: Mapped[str | None] = mapped_column(String, nullable=True)
    
    # Relacionamentos
    # Removed cascade="all, delete-orphan" to prevent accidental deletion of participants with history
    processos: Mapped[list["Processo"]] = relationship(back_populates="cliente")
    lancamentos: Mapped[list["Lancamento"]] = relationship(back_populates="participante")
