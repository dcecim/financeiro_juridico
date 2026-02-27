
import uuid
from datetime import datetime
from sqlalchemy import String, Uuid, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.core.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tabela: Mapped[str] = mapped_column(String(50), index=True)
    registro_id: Mapped[str] = mapped_column(String(36), index=True)
    acao: Mapped[str] = mapped_column(String(10)) # INSERT, UPDATE, DELETE
    usuario_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True) # Pode ser NULL se for sistema
    dados_antigos: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    dados_novos: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
