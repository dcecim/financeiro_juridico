
import uuid
from decimal import Decimal
from sqlalchemy import String, ForeignKey, Uuid, Numeric, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.enums import StatusProcesso

class Processo(Base):
    __tablename__ = "processos"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    numero: Mapped[str] = mapped_column(String, unique=True, index=True)
    numero_cnj: Mapped[str | None] = mapped_column(String(30), unique=True, nullable=True)
    titulo_causa: Mapped[str | None] = mapped_column(String, nullable=True)
    descricao: Mapped[str | None] = mapped_column(String, nullable=True)
    
    # Campos Financeiros
    percentual_exito: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    valor_pro_labore: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    valor_causa_atualizado: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    valor_causa_estimado: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    
    status: Mapped[StatusProcesso] = mapped_column(Enum(StatusProcesso), default=StatusProcesso.ATIVO)
    
    cliente_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("participantes.id"))

    # Relacionamentos
    cliente: Mapped["Participante"] = relationship(back_populates="processos")
    lancamentos: Mapped[list["Lancamento"]] = relationship(back_populates="processo")

if False:
    from app.models.participante import Participante
    from app.models.lancamento import Lancamento
