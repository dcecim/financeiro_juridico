
import uuid
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import String, Date, Numeric, Enum, ForeignKey, Uuid, CheckConstraint, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from sqlalchemy.sql import func
from app.core.database import Base
from app.models.enums import TipoLancamento, NaturezaLancamento, StatusLancamento

if False: # Type hinting only
    from app.models.participante import Participante
    from app.models.processo import Processo
    from app.models.cartao_credito import CartaoCredito
    from app.models.centro_custo import CentroCusto

class Lancamento(Base):
    __tablename__ = "lancamentos"
    __table_args__ = (
        CheckConstraint(
            "(natureza != 'EXITO') OR (processo_id IS NOT NULL)",
            name="check_exito_requires_processo"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    descricao: Mapped[str] = mapped_column(String)
    valor: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    valor_realizado: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    valor_previsto: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True) # Para êxito
    
    data_vencimento: Mapped[date | None] = mapped_column(Date, nullable=True) # Null para êxito aguardando
    data_pagamento: Mapped[date | None] = mapped_column(Date, nullable=True)
    
    tipo: Mapped[TipoLancamento] = mapped_column(Enum(TipoLancamento))
    natureza: Mapped[NaturezaLancamento] = mapped_column(Enum(NaturezaLancamento))
    status: Mapped[StatusLancamento] = mapped_column(Enum(StatusLancamento), default=StatusLancamento.PENDENTE)
    
    participante_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("participantes.id"))
    processo_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("processos.id"), nullable=True)
    cartao_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("cartoes_credito.id"), nullable=True)
    centro_custo_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("centros_custo.id"), nullable=False)
    
    # Controle de Reembolso
    reembolsavel: Mapped[bool] = mapped_column(Boolean, default=False)
    lancamento_pai_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("lancamentos.id"), nullable=True)
    
    # Auditoria
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relacionamentos
    participante: Mapped["Participante"] = relationship(back_populates="lancamentos")
    processo: Mapped["Processo"] = relationship(back_populates="lancamentos")
    cartao: Mapped["CartaoCredito"] = relationship(back_populates="lancamentos")
    centro_custo: Mapped["CentroCusto"] = relationship(back_populates="lancamentos")
    
    lancamento_pai: Mapped["Lancamento"] = relationship("Lancamento", remote_side=[id], backref="reembolsos_gerados")
