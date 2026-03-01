import asyncio
from app.core.database import async_session
from app.models.usuario import Usuario
from app.core.security import get_password_hash
from sqlalchemy import select

async def create_initial_user():
    async with async_session() as session:
        # Verifica se já existe
        result = await session.execute(select(Usuario).where(Usuario.email == "admin@financas.com"))
        user = result.scalar_one_or_none()
        
        if not user:
            print("Criando usuario inicial...")
            new_user = Usuario(
                email="admin@financas.com",
                password_hash=get_password_hash("admin123"),
                role="ADMIN",
                is_2fa_enabled=False
            )
            session.add(new_user)
            await session.commit()
            print("Usuario criado com sucesso: admin@financas.com / admin123")
        else:
            print("Usuario admin@financas.com ja existe.")

if __name__ == "__main__":
    asyncio.run(create_initial_user())
