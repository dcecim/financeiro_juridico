
import asyncio
import random
import sys
import os
from datetime import date, timedelta
from decimal import Decimal
from faker import Faker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select

# Ensure app can be imported
sys.path.append(os.getcwd())

from app.core.config import settings
from app.core.database import Base
from app.models.participante import Participante
from app.models.processo import Processo
from app.models.lancamento import Lancamento
from app.models.usuario import Usuario
from app.models.cartao_credito import CartaoCredito
from app.models.centro_custo import CentroCusto
from app.core.security import get_password_hash
from app.models.enums import TipoParticipante, TipoLancamento, NaturezaLancamento, StatusLancamento

fake = Faker('pt_BR')

async def seed():
    print(f"Connecting to database: {settings.DATABASE_URL}")
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    
    # Create tables if they don't exist
    async with engine.begin() as conn:
        # Note: In production, use Alembic migrations. This is for dev convenience.
        await conn.run_sync(Base.metadata.create_all)
        
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    
    async with async_session() as session:
        # Create Admin User
        print("Creating Admin User...")
        admin_email = "admin@example.com"
        result = await session.execute(select(Usuario).where(Usuario.email == admin_email))
        if not result.scalars().first():
            admin_user = Usuario(
                email=admin_email,
                password_hash=get_password_hash("admin123"),
                role="ADMIN",
                is_2fa_enabled=False
            )
            session.add(admin_user)
            print(f"Admin user created: {admin_email} / admin123")
        else:
            print("Admin user already exists.")

        print("Creating Participants...")
        clientes = []
        for _ in range(5):
            p = Participante(
                nome=fake.name(),
                documento=fake.cpf(),
                tipo=TipoParticipante.CLIENTE
            )
            clientes.append(p)
            session.add(p)
            
        fornecedores = []
        for _ in range(3):
            p = Participante(
                nome=fake.company(),
                documento=fake.cnpj(),
                tipo=TipoParticipante.FORNECEDOR
            )
            fornecedores.append(p)
            session.add(p)
            
        await session.flush()
        
        print("Creating Processes...")
        processos = []
        for _ in range(10):
            cliente = random.choice(clientes)
            proc = Processo(
                numero=fake.bothify(text='#######-##.####.#.##.####'),
                descricao=fake.sentence(),
                cliente_id=cliente.id
            )
            processos.append(proc)
            session.add(proc)
            
        await session.flush()
        
        print("Creating Financial Entries...")
        
        # 3 Success Fees (Estimated, Null Date)
        for _ in range(3):
            processo = random.choice(processos)
            lanc = Lancamento(
                descricao=f"Honorários Êxito - Proc. {processo.numero}",
                valor=Decimal(random.randint(5000, 50000)),
                valor_previsto=Decimal(random.randint(5000, 50000)),
                tipo=TipoLancamento.RECEITA,
                natureza=NaturezaLancamento.EXITO,
                status=StatusLancamento.AGUARDANDO_TRANSITO,
                data_vencimento=None,
                participante_id=processo.cliente_id,
                processo_id=processo.id
            )
            session.add(lanc)
            
        # Remaining 17: Fixed and One-off
        for _ in range(17):
            tipo_natureza = random.choice([NaturezaLancamento.FIXO, NaturezaLancamento.PONTUAL])
            
            if tipo_natureza == NaturezaLancamento.FIXO:
                # Mensalidade (Receita)
                cliente = random.choice(clientes)
                lanc = Lancamento(
                    descricao="Honorários Mensais",
                    valor=Decimal(random.randint(1000, 5000)),
                    tipo=TipoLancamento.RECEITA,
                    natureza=NaturezaLancamento.FIXO,
                    status=random.choice([StatusLancamento.PENDENTE, StatusLancamento.PAGO]),
                    data_vencimento=fake.date_between(start_date='-30d', end_date='+30d'),
                    participante_id=cliente.id
                )
            else:
                # Reembolso
                if random.random() > 0.5:
                    participante = random.choice(fornecedores)
                    tipo = TipoLancamento.DESPESA
                    desc = "Reembolso de Custas"
                else:
                    participante = random.choice(clientes)
                    tipo = TipoLancamento.RECEITA
                    desc = "Reembolso de Despesas"
                    
                lanc = Lancamento(
                    descricao=desc,
                    valor=Decimal(random.randint(100, 1000)),
                    tipo=tipo,
                    natureza=NaturezaLancamento.PONTUAL,
                    status=StatusLancamento.PENDENTE,
                    data_vencimento=fake.date_between(start_date='-30d', end_date='+30d'),
                    participante_id=participante.id
                )
            session.add(lanc)
            
        # Specific Transaction for Manual Testing
        print("Creating Specific Transaction for Manual Testing...")
        cliente_manual = clientes[0]
        lanc_manual = Lancamento(
            descricao="Lançamento para Teste de Conciliação",
            valor=Decimal("500.00"),
            tipo=TipoLancamento.RECEITA,
            natureza=NaturezaLancamento.FIXO,
            status=StatusLancamento.PENDENTE,
            data_vencimento=date.today(),
            participante_id=cliente_manual.id
        )
        session.add(lanc_manual)
        
        await session.commit()
        print("Seed completed successfully!")
    
    await engine.dispose()

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(seed())
