
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings

engine = None
try:
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
except Exception as e:
    # Allow import to proceed even if engine creation fails (e.g. missing driver or bad URL during tests)
    print(f"Warning: Failed to create global engine: {e}")

async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with async_session() as session:
        yield session
