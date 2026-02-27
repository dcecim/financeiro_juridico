
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/financeiro_juridico"
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str | None) -> str:
        if isinstance(v, str):
            if v.startswith("postgresql://"):
                v = v.replace("postgresql://", "postgresql+psycopg://")
            if v.startswith("postgresql+psycopg2://"):
                v = v.replace("postgresql+psycopg2://", "postgresql+psycopg://")
            if "@localhost" in v:
                v = v.replace("@localhost", "@127.0.0.1")
        return v
    
    SECRET_KEY: str = "f45e1c49a195269de9152c81c86b4f1421933c45b19892e915bb396a19356d07"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

settings = Settings()
