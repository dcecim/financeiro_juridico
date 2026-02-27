import pyotp
from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.config import settings
from app.core.security import verify_password, get_password_hash, create_access_token
from app.models.usuario import Usuario
from app.schemas.usuario import Token, UsuarioCreate, UsuarioPublic, UsuarioLogin
from app.api.deps import RoleChecker, get_current_user

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
    otp_code: str | None = Query(None, description="Código de autenticação de dois fatores (2FA)")
):
    result = await db.execute(select(Usuario).where(Usuario.email == form_data.username))
    user = result.scalars().first()
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Validação de 2FA
    if user.is_2fa_enabled:
        if not otp_code:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="2FA code required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        totp = pyotp.TOTP(user.secret_2fa)
        if not totp.verify(otp_code):
             raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid 2FA code",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UsuarioPublic)
async def read_users_me(
    current_user: Annotated[Usuario, Depends(get_current_user)]
):
    return current_user

@router.post("/2fa/setup")
async def setup_2fa(
    current_user: Annotated[Usuario, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Gera um novo segredo para 2FA e retorna a URI para configurar no app autenticador.
    """
    if current_user.is_2fa_enabled:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is already enabled"
        )
        
    secret = pyotp.random_base32()
    
    # Salva temporariamente o segredo (ou apenas retorna e espera ativar)
    # Aqui vamos salvar logo, mas só marcar como enabled após verificação
    current_user.secret_2fa = secret
    db.add(current_user)
    await db.commit()
    
    # Gera URI para QR Code
    uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=current_user.email,
        issuer_name="Contas a Pagar e Receber"
    )
    
    return {"secret": secret, "otpauth_url": uri}

@router.post("/2fa/activate")
async def activate_2fa(
    otp_code: str,
    current_user: Annotated[Usuario, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Verifica o código OTP e ativa o 2FA para o usuário.
    """
    if current_user.is_2fa_enabled:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is already enabled"
        )
        
    if not current_user.secret_2fa:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA setup not initiated"
        )
        
    totp = pyotp.TOTP(current_user.secret_2fa)
    if not totp.verify(otp_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid 2FA code"
        )
        
    current_user.is_2fa_enabled = True
    db.add(current_user)
    await db.commit()
    
    return {"message": "2FA enabled successfully"}

@router.post("/2fa/disable")
async def disable_2fa(
    otp_code: str,
    current_user: Annotated[Usuario, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Desativa o 2FA (requer código atual válido por segurança).
    """
    if not current_user.is_2fa_enabled:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is not enabled"
        )
        
    totp = pyotp.TOTP(current_user.secret_2fa)
    if not totp.verify(otp_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid 2FA code"
        )
        
    current_user.is_2fa_enabled = False
    current_user.secret_2fa = None
    db.add(current_user)
    await db.commit()
    
    return {"message": "2FA disabled successfully"}

@router.post("/register", response_model=UsuarioPublic, dependencies=[Depends(RoleChecker(["ADMIN"]))])
async def register_user(
    user_in: UsuarioCreate,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    # Check if user already exists
    result = await db.execute(select(Usuario).where(Usuario.email == user_in.email))
    existing_user = result.scalars().first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_in.password)
    new_user = Usuario(
        email=user_in.email,
        password_hash=hashed_password,
        nome_completo=user_in.nome_completo,
        role=user_in.role
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return new_user
