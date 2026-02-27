"""add_processo_financial_fields_and_reimbursement

Revision ID: cd51a38de7af
Revises: 513451cf69aa
Create Date: 2026-02-25 15:23:37.406036

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cd51a38de7af'
down_revision: Union[str, Sequence[str], None] = '513451cf69aa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Processo
    op.add_column('processos', sa.Column('titulo_causa', sa.String(), nullable=True))
    # op.add_column('processos', sa.Column('percentual_exito', sa.Numeric(precision=5, scale=2), nullable=True)) # Already exists
    op.add_column('processos', sa.Column('valor_pro_labore', sa.Numeric(precision=15, scale=2), nullable=True))
    op.add_column('processos', sa.Column('valor_causa_atualizado', sa.Numeric(precision=15, scale=2), nullable=True))
    op.add_column('processos', sa.Column('valor_causa_estimado', sa.Numeric(precision=15, scale=2), nullable=True))
    
    # Enum creation for StatusProcesso
    # Note: name='statusprocesso' matches the Postgres type name
    status_processo = sa.Enum('ATIVO', 'SUSPENSO', 'ENCERRADO', 'TRANSITO_JULGADO', name='statusprocesso')
    status_processo.create(op.get_bind(), checkfirst=True)
    op.add_column('processos', sa.Column('status', status_processo, server_default='ATIVO', nullable=False))

    # Participante
    op.add_column('participantes', sa.Column('email', sa.String(), nullable=True))
    op.add_column('participantes', sa.Column('telefone', sa.String(), nullable=True))

    # CentroCusto
    op.add_column('centros_custo', sa.Column('codigo', sa.String(length=20), nullable=True))
    op.create_unique_constraint('uq_centros_custo_codigo', 'centros_custo', ['codigo'])

    # Lancamento
    op.add_column('lancamentos', sa.Column('reembolsavel', sa.Boolean(), server_default=sa.text('false'), nullable=False))
    op.add_column('lancamentos', sa.Column('lancamento_pai_id', sa.Uuid(), nullable=True))
    op.create_foreign_key('fk_lancamentos_lancamento_pai_id', 'lancamentos', 'lancamentos', ['lancamento_pai_id'], ['id'])

    # Usuario (2FA) - Already exists
    # op.add_column('usuarios', sa.Column('secret_2fa', sa.String(length=64), nullable=True))
    # op.add_column('usuarios', sa.Column('is_2fa_enabled', sa.Boolean(), server_default=sa.text('false'), nullable=False))


def downgrade() -> None:
    # Usuario (2FA)
    op.drop_column('usuarios', 'is_2fa_enabled')
    op.drop_column('usuarios', 'secret_2fa')

    # Lancamento
    op.drop_constraint('fk_lancamentos_lancamento_pai_id', 'lancamentos', type_='foreignkey')
    op.drop_column('lancamentos', 'lancamento_pai_id')
    op.drop_column('lancamentos', 'reembolsavel')

    # CentroCusto
    op.drop_constraint('uq_centros_custo_codigo', 'centros_custo', type_='unique')
    op.drop_column('centros_custo', 'codigo')

    # Participante
    op.drop_column('participantes', 'telefone')
    op.drop_column('participantes', 'email')

    # Processo
    op.drop_column('processos', 'status')
    
    # Drop enum type
    status_processo = sa.Enum('ATIVO', 'SUSPENSO', 'ENCERRADO', 'TRANSITO_JULGADO', name='statusprocesso')
    status_processo.drop(op.get_bind(), checkfirst=True)
    
    op.drop_column('processos', 'valor_causa_estimado')
    op.drop_column('processos', 'valor_causa_atualizado')
    op.drop_column('processos', 'valor_pro_labore')
    op.drop_column('processos', 'percentual_exito')
    op.drop_column('processos', 'titulo_causa')
