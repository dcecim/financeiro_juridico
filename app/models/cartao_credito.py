
import uuid
from decimal import Decimal
from sqlalchemy import String, Integer, Numeric, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class CartaoCredito(Base):
    __tablename__ = "cartoes_credito"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome: Mapped[str] = mapped_column(String(50)) # Ex: Visa Escritório
    dia_fechamento: Mapped[int] = mapped_column(Integer)
    dia_vencimento: Mapped[int] = mapped_column(Integer)
    limite: Mapped[Decimal] = mapped_column(Numeric(15, 2))
    
    # Relacionamentos
    lancamentos: Mapped[list["Lancamento"]] = relationship(back_populates="cartao")

if False:
    from app.models.lancamento import Lancamento
