import asyncio
import sys
import os

# Adicionar diretório raiz
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.security import get_password_hash
from app.models.usuario import Usuario

async def create_user():
    print("Iniciando cadastro do usuário divino.cecim@gmail.com...")
    
    # Using settings.DATABASE_URL directly
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Check if user exists
        stmt = select(Usuario).where(Usuario.email == "divino.cecim@gmail.com")
        result = await session.execute(stmt)
        existing_user = result.scalars().first()
        
        if not existing_user:
            print("Usuário não encontrado. Criando novo...")
            new_user = Usuario(
                email="divino.cecim@gmail.com",
                password_hash=get_password_hash("teste001"),
                role="ADMIN" # Granting ADMIN access as requested for testing
            )
            session.add(new_user)
            await session.commit()
            print("Usuário criado com sucesso!")
        else:
            print("Usuário já existe. Atualizando senha...")
            existing_user.password_hash = get_password_hash("teste001")
            # Ensure role is ADMIN if needed, or leave as is
            # existing_user.role = "ADMIN" 
            session.add(existing_user)
            await session.commit()
            print("Senha atualizada com sucesso!")

    await engine.dispose()

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(create_user())
