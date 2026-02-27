
import uuid
from pydantic import BaseModel, EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None

class UsuarioBase(BaseModel):
    email: EmailStr
    is_2fa_enabled: bool = False
    role: str = "ANALISTA"

class UsuarioCreate(UsuarioBase):
    password: str

class UsuarioPublic(UsuarioBase):
    id: uuid.UUID
    
    class Config:
        from_attributes = True

class UsuarioLogin(BaseModel):
    email: EmailStr
    password: str
