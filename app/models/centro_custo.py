
import uuid
from datetime import datetime
from sqlalchemy import String, Uuid, Enum, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.core.database import Base
from app.models.enums import TipoLancamento

class CentroCusto(Base):
    __tablename__ = "centros_custo"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome: Mapped[str] = mapped_column(String(50), unique=True)
    codigo: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True)
    descricao: Mapped[str | None] = mapped_column(String(255), nullable=True)
    tipo: Mapped[TipoLancamento] = mapped_column(Enum(TipoLancamento), nullable=True)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("centros_custo.id"), nullable=True)
    
    # Auditoria
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    lancamentos: Mapped[list["Lancamento"]] = relationship(back_populates="centro_custo")
    parent: Mapped["CentroCusto"] = relationship("CentroCusto", remote_side=[id], back_populates="children")
    children: Mapped[list["CentroCusto"]] = relationship("CentroCusto", back_populates="parent")

if False:
    from app.models.lancamento import Lancamento
