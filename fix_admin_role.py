import asyncio
from app.core.database import async_session
from app.models.usuario import Usuario
from sqlalchemy import select

async def fix_admin_role():
    async with async_session() as session:
        # Busca o usuário admin
        result = await session.execute(select(Usuario).where(Usuario.email == "admin@financas.com"))
        user = result.scalar_one_or_none()
        
        if user:
            print(f"Usuario encontrado. Role atual: {user.role}")
            if user.role != "ADMIN":
                print("Atualizando role para ADMIN...")
                user.role = "ADMIN"
                session.add(user)
                await session.commit()
                print("Role atualizado com sucesso!")
            else:
                print("Role ja esta correto (ADMIN).")
        else:
            print("Usuario admin@financas.com nao encontrado.")

if __name__ == "__main__":
    asyncio.run(fix_admin_role())
