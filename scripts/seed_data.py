import asyncio
import sys
import os
import uuid
import random
from datetime import date, datetime, timedelta
from faker import Faker

# Adicionar diretório raiz ao path para importar app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.security import get_password_hash
from app.models.usuario import Usuario
from app.models.participante import Participante
from app.models.processo import Processo
from app.models.lancamento import Lancamento
from app.models.enums import (
    TipoParticipante, 
    StatusProcesso, 
    TipoLancamento, 
    NaturezaLancamento, 
    StatusLancamento
)

fake = Faker('pt_BR')

async def seed():
    print("Iniciando seed de dados volumoso...")
    
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # 1. Criar Usuário Admin
        stmt = select(Usuario).where(Usuario.email == "admin@exemplo.com")
        result = await session.execute(stmt)
        user = result.scalars().first()
        
        if not user:
            print("Criando usuário admin...")
            user = Usuario(
                email="admin@exemplo.com",
                password_hash=get_password_hash("admin123"),
                role="ADMIN"
            )
            session.add(user)
            await session.commit()
            print("Usuário admin criado.")
        else:
            print("Usuário admin já existe.")
            
        # 2. Criar Participantes (20 novos)
        print("Gerando participantes...")
        created_participantes = []
        
        # Recuperar existentes primeiro
        result = await session.execute(select(Participante))
        existing_participantes = result.scalars().all()
        created_participantes.extend(existing_participantes)
        
        tipos = [TipoParticipante.CLIENTE, TipoParticipante.FORNECEDOR, TipoParticipante.AMBOS]
        
        for _ in range(20):
            tipo = random.choice(tipos)
            if tipo == TipoParticipante.FORNECEDOR:
                nome = fake.company()
                doc = fake.cnpj()
            else:
                nome = fake.name()
                doc = fake.cpf()
            
            # Verificar se já existe (faker pode repetir ou colidir com existentes)
            stmt = select(Participante).where(Participante.documento == doc)
            result = await session.execute(stmt)
            if not result.scalars().first():
                p = Participante(
                    nome=nome,
                    documento=doc,
                    email=fake.email(),
                    tipo=tipo,
                    telefone=fake.phone_number()
                )
                session.add(p)
                created_participantes.append(p)
        
        await session.commit()
        for p in created_participantes:
            await session.refresh(p) # Atualizar IDs
            
        print(f"Total de participantes agora: {len(created_participantes)}")

        # 3. Criar Processos (50 novos)
        print("Gerando processos...")
        created_processos = []
        
        # Recuperar existentes
        result = await session.execute(select(Processo))
        existing_processos = result.scalars().all()
        created_processos.extend(existing_processos)
        
        status_opts = list(StatusProcesso)
        
        clientes = [p for p in created_participantes if p.tipo in [TipoParticipante.CLIENTE, TipoParticipante.AMBOS]]
        if not clientes:
            print("ERRO: Nenhum cliente disponível para criar processos.")
            return

        for _ in range(50):
            # Gerar número CNJ fake: NNNNNNN-DD.AAAA.J.TR.OROO
            numero = f"{random.randint(1000000, 9999999)}-{random.randint(10, 99)}.{random.randint(2010, 2025)}.8.26.{random.randint(1000, 9999)}"
            
            # Verificar duplicidade
            stmt = select(Processo).where(Processo.numero == numero)
            if not (await session.execute(stmt)).scalars().first():
                cliente = random.choice(clientes)
                valor = round(random.uniform(1000, 500000), 2)
                
                proc = Processo(
                    numero=numero,
                    titulo_causa=f"Ação de {fake.word().capitalize()} vs {fake.company()}",
                    cliente_id=cliente.id,
                    status=random.choice(status_opts),
                    valor_causa_estimado=valor,
                    valor_causa_atualizado=valor,
                    percentual_exito=random.choice([10, 20, 30]),
                    descricao=fake.text(max_nb_chars=100)
                )
                print(f"DEBUG: Creating Processo {proc.numero} with titulo_causa='{proc.titulo_causa}'")
                session.add(proc)
                created_processos.append(proc)
        
        await session.commit()
        for p in created_processos:
            await session.refresh(p)
            
        print(f"Total de processos agora: {len(created_processos)}")

        # 4. Criar Lançamentos (200 novos)
        print("Gerando lançamentos...")
        
        naturezas = list(NaturezaLancamento)
        status_lanc = list(StatusLancamento)
        tipos_lanc = list(TipoLancamento)
        
        for _ in range(200):
            tipo = random.choice(tipos_lanc)
            natureza = random.choice(naturezas)
            
            # Regra: Se for ÊXITO, precisa de processo
            if natureza == NaturezaLancamento.EXITO and not created_processos:
                natureza = NaturezaLancamento.PONTUAL
            
            processo = None
            if created_processos and (natureza == NaturezaLancamento.EXITO or random.random() > 0.5):
                processo = random.choice(created_processos)
            
            # Regra: Se for ÊXITO, precisa de processo (garantia)
            if natureza == NaturezaLancamento.EXITO and not processo:
                 # Se não tiver processo, muda natureza
                 natureza = NaturezaLancamento.PONTUAL

            participante = random.choice(created_participantes)
            
            # Data entre 6 meses atrás e 2 meses no futuro
            data_base = date.today() + timedelta(days=random.randint(-180, 60))
            
            status = random.choice(status_lanc)
            data_pagamento = data_base if status == StatusLancamento.PAGO else None
            
            valor = round(random.uniform(50, 50000), 2)
            
            descricao = ""
            if tipo == TipoLancamento.RECEITA:
                descricao = f"Honorários {natureza.value.capitalize()}"
                if processo:
                    descricao += f" - Proc. {processo.numero}"
            else:
                descricao = random.choice(["Reembolso de Despesas", "Taxa Judiciária", "Material de Escritório", "Aluguel", "Internet", "Software Jurídico", "Reembolso de Custas"])
            
            lanc = Lancamento(
                descricao=descricao,
                valor=valor,
                tipo=tipo,
                natureza=natureza,
                status=status,
                participante_id=participante.id,
                processo_id=processo.id if processo else None,
                data_vencimento=data_base,
                data_pagamento=data_pagamento,
                reembolsavel=random.choice([True, False]) if tipo == TipoLancamento.DESPESA else False
            )
            session.add(lanc)
        
        await session.commit()
        print("Lançamentos criados.")

    await engine.dispose()
    print("Seed volumoso concluído com sucesso!")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(seed())
